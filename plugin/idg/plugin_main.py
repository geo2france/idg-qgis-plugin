#! python3  # noqa: E265

"""
    Main plugin module.
"""

# PyQGIS
from qgis.core import QgsApplication
from qgis.gui import QgisInterface
from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QMenu
from qgis.utils import showPluginHelp

# project
from idg.__about__ import __title__
from idg.gui.dlg_settings import PlgOptionsFactory

from idg.toolbelt import PlgLogger, PlgTranslator


from idg.toolbelt import PluginGlobals, IdgProvider
from idg.toolbelt.remote_platforms import RemotePlatforms
from idg.toolbelt.tree_node_factory import (
    DownloadAllConfigFilesAsync,
    DownloadDefaultIdgListAsync,
)

import os
import json

# ############################################################################
# ########## Classes ###############
# ##################################


class IdgPlugin:
    def __init__(self, iface: QgisInterface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class which \
        provides the hook by which you can manipulate the QGIS application at run time.
        :type iface: QgsInterface
        """
        self.iface = iface
        self.log = PlgLogger().log
        self.dock = None
        plg_translation_mngr = PlgTranslator()
        translator = plg_translation_mngr.get_translator()
        if translator:
            QCoreApplication.installTranslator(translator)
        self.tr = plg_translation_mngr.tr

        PluginGlobals.instance().set_plugin_path(
            os.path.dirname(os.path.abspath(__file__))
        )
        # PluginGlobals.instance().set_plugin_iface(self.iface)
        PluginGlobals.instance().reload_globals_from_qgis_settings()

        config_struct = None
        config_string = ""

        self.registry = QgsApplication.instance().dataItemProviderRegistry()
        self.provider = IdgProvider(self.iface)

        # self.iface.initializationCompleted.connect(self.post_ui_init)
        self.post_ui_init()

    def post_ui_init(self):
        """Run after plugin's UI has been initialized."""
        items ={c.idg_id : c.url for c in RemotePlatforms(read_projects=False).plateforms if not c.is_hidden()}
        self.task1 = DownloadDefaultIdgListAsync()
        self.task2 = DownloadAllConfigFilesAsync(
            items
        )
        self.task1.finished.connect(self.task2.start)
        self.task2.finished.connect(lambda : self.registry.addProvider(self.provider))

        self.task1.start()

    def need_download_tree_config_file(self):
        """
        Do we need to download a new version of the resources tree file?
        2 possible reasons:
        - the user wants it to be downloading at plugin start up
        - the file is currently missing
        """

        return (
            PluginGlobals.instance().CONFIG_FILES_DOWNLOAD_AT_STARTUP > 0
            or not os.path.isfile(PluginGlobals.instance().config_file_path)
        )

    def initGui(self):
        """Set up plugin UI elements."""

        # settings page within the QGIS preferences menu
        self.options_factory = PlgOptionsFactory()
        self.iface.registerOptionsWidgetFactory(self.options_factory)

        # -- Actions
        self.action_help = QAction(
            QIcon(":/images/themes/default/mActionHelpContents.svg"),
            self.tr("Help", context="IdgPlugin"),
            self.iface.mainWindow(),
        )
        self.action_help.triggered.connect(
            lambda: showPluginHelp(filename="resources/help/index")
        )

        self.action_settings = QAction(
            QgsApplication.getThemeIcon("console/iconSettingsConsole.svg"),
            self.tr("Settings"),
            self.iface.mainWindow(),
        )
        self.action_settings.triggered.connect(
            lambda: self.iface.showOptionsDialog(
                currentPage="mOptionsPage{}".format(__title__)
            )
        )

        # -- Menu

        # Create a menu
        self.createPluginMenu()


    def unload(self):
        """Cleans up when plugin is disabled/uninstalled."""
        # -- Clean up menu
        self.iface.removePluginMenu(__title__, self.action_help)
        self.iface.removePluginMenu(__title__, self.action_settings)

        # -- Clean up preferences panel in QGIS settings
        self.iface.unregisterOptionsWidgetFactory(self.options_factory)

        # remove actions
        del self.action_settings
        del self.action_help
        """
        Removes the plugin menu
        """
        self.iface.pluginMenu().removeAction(self.plugin_menu.menuAction())

        # Clean-up browser
        self.registry.removeProvider(self.provider)

    def createPluginMenu(self):
        """
        Creates the plugin main menu
        """
        plugin_menu = self.iface.pluginMenu()
        self.plugin_menu = QMenu(__title__, plugin_menu)
        plugin_menu.addMenu(self.plugin_menu)

        self.plugin_menu.addAction(self.action_settings)
        self.plugin_menu.addAction(self.action_help)
