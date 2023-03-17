#! python3  # noqa: E265

"""
    Main plugin module.
"""

# PyQGIS
from qgis.core import QgsApplication
from qgis.gui import QgisInterface
from qgis.PyQt.QtCore import QCoreApplication, Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QMenu
from qgis.utils import showPluginHelp

# project
from idg.__about__ import __title__
from idg.gui.dlg_settings import PlgOptionsFactory

from idg.toolbelt import PlgLogger, PlgTranslator, PluginGlobals


from idg.toolbelt import PluginGlobals, PlgOptionsManager, IdgProvider
from idg.gui.dock import DockWidget
from idg.gui.about_box import AboutBox
from idg.gui.param_box import ParamBox
from idg.toolbelt.tree_node_factory import TreeNodeFactory, download_tree_config_file, download_all_config_files

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

        # translation
        plg_translation_mngr = PlgTranslator()
        translator = plg_translation_mngr.get_translator()
        if translator:
            QCoreApplication.installTranslator(translator)
        self.tr = plg_translation_mngr.tr
        
        PluginGlobals.instance().set_plugin_path(os.path.dirname(os.path.abspath(__file__)))
        PluginGlobals.instance().set_plugin_iface(self.iface)
        PluginGlobals.instance().reload_globals_from_qgis_settings()

        config_struct = None
        config_string = ""
        
        # Download the config if needed
        #if self.need_download_tree_config_file():
        #    download_tree_config_file(PluginGlobals.instance().CONFIG_FILE_URLS[0])
        
        # Read the resources tree file and update the GUI
        self.ressources_tree = TreeNodeFactory(PluginGlobals.instance().config_file_path).root_node

        download_all_config_files(PluginGlobals.instance().IDGS)

    def need_download_tree_config_file(self):
        """
        Do we need to download a new version of the resources tree file?
        2 possible reasons:
        - the user wants it to be downloading at plugin start up
        - the file is currently missing
        """

        return (PluginGlobals.instance().CONFIG_FILES_DOWNLOAD_AT_STARTUP > 0 or
                not os.path.isfile(PluginGlobals.instance().config_file_path))

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

        # Create a dockable panel with a tree of resources
        self.dock = DockWidget()
        self.dock.set_tree_content(self.ressources_tree)
        self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dock)

    # Add browser provider
        self.registry = QgsApplication.dataItemProviderRegistry()       
        self.provider = IdgProvider()
        self.registry.addProvider(self.provider)

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
        self.iface.removeDockWidget(self.dock)
        del self.dock
        
        #Clean-up browser
        self.registry.removeProvider(self.provider)
        
        
    def createPluginMenu(self):
        """
        Creates the plugin main menu
        """
        plugin_menu = self.iface.pluginMenu()
        self.plugin_menu = QMenu(__title__, plugin_menu)
        plugin_menu.addMenu(self.plugin_menu)

        show_panel_action = QAction(u'Afficher le panneau latéral', self.iface.mainWindow())
        show_panel_action.triggered.connect(self.showPanelMenuTriggered)
        self.plugin_menu.addAction(show_panel_action)

        param_action = QAction(u'Paramétrer le plugin…', self.iface.mainWindow())
        param_action.triggered.connect(self.paramMenuTriggered)
        self.plugin_menu.addAction(param_action)

        about_action = QAction(u'À propos…', self.iface.mainWindow())
        about_action.triggered.connect(self.aboutMenuTriggered)
        self.plugin_menu.addAction(about_action)

        self.plugin_menu.addAction(self.action_settings)
        self.plugin_menu.addAction(self.action_help)


    def showPanelMenuTriggered(self):
        """
        Shows the dock widget
        """
        self.dock.show()
        pass

    def aboutMenuTriggered(self):
        """
        Shows the About box
        """
        dialog = AboutBox(self.iface.mainWindow())
        dialog.exec_()

    def paramMenuTriggered(self):
        """
        Shows the Param box
        """
        dialog = ParamBox(self.iface.mainWindow(), self.dock)
        dialog.exec_()
        

    def run(self):
        """Main process.

        :raises Exception: if there is no item in the feed
        """
        try:
            self.log(
                message=self.tr(
                    text="Everything ran OK.",
                    context="IdgPlugin",
                ),
                log_level=3,
                push=False,
            )
        except Exception as err:
            self.log(
                message=self.tr(
                    text="Houston, we've got a problem: {}".format(err),
                    context="IdgPlugin",
                ),
                log_level=2,
                push=True,
            )
