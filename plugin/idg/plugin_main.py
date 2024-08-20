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
from idg.toolbelt import PlgOptionsManager
from idg.plugin_globals import PluginGlobals
from idg.plugin_actions import PluginActions
from idg.browser.remote_platforms import RemotePlatforms
from idg.browser.browser import IdgProvider
from idg.browser.tree_node_factory import (
    DownloadAllIdgFilesAsync,
    DownloadDefaultIdgListAsync,
)


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

        PluginGlobals.init_constants()

        self.registry = QgsApplication.instance().dataItemProviderRegistry()
        self.provider = IdgProvider(self.iface)

        # self.iface.initializationCompleted.connect(self.post_ui_init)
        self.post_ui_init()

    def post_ui_init(self):
        """Run after plugin's UI has been initialized."""
        self.registry.addProvider(self.provider)

        self.download_all_config_files()

    def initGui(self):
        """Set up plugin UI elements."""

        # settings page within the QGIS preferences menu
        self.options_factory = PlgOptionsFactory(self.settings_updated_slot)
        self.iface.registerOptionsWidgetFactory(self.options_factory)

        # -- Actions
        PluginActions.action_show_help = QAction(
            QIcon(":/images/themes/default/mActionHelpContents.svg"),
            self.tr("Help…", context="IdgPlugin"),
            self.iface.mainWindow(),
        )
        PluginActions.action_show_help.triggered.connect(
            lambda: showPluginHelp(filename="resources/help/index")
        )

        PluginActions.action_show_settings = QAction(
            QgsApplication.getThemeIcon("console/iconSettingsConsole.svg"),
            self.tr("Settings…"),
            self.iface.mainWindow(),
        )
        PluginActions.action_show_settings.triggered.connect(self.show_settings_dialog)

        PluginActions.action_reload_idgs = QAction(
            self.tr("Reload files"),
            self.iface.mainWindow(),
        )
        PluginActions.action_reload_idgs.triggered.connect(
            self.download_all_config_files
        )

        # -- Menu

        # Create a menu
        self.createPluginMenu()

    def show_settings_dialog(self):
        self.iface.showOptionsDialog(currentPage="mOptionsPage{}".format(__title__))

    def unload(self):
        """Cleans up when plugin is disabled/uninstalled."""
        # -- Clean up menu
        self.iface.removePluginMenu(__title__, PluginActions.action_show_help)
        self.iface.removePluginMenu(__title__, PluginActions.action_show_settings)

        # -- Clean up preferences panel in QGIS settings
        self.iface.unregisterOptionsWidgetFactory(self.options_factory)

        # remove actions
        del PluginActions.action_show_settings
        del PluginActions.action_reload_idgs
        del PluginActions.action_show_help
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

        self.plugin_menu.addAction(PluginActions.action_show_settings)
        self.plugin_menu.addAction(PluginActions.action_reload_idgs)
        self.plugin_menu.addAction(PluginActions.action_show_help)

    def settings_updated_slot(self):
        """Slot receiveing the signal emitted on settings update"""

        self.download_all_config_files()

    def _get_active_remote_plateforms(self):
        """Get the list of the active platforms (non-hidden ones)."""
        active_platforms = {
            pf.idg_id: pf.url
            for pf in RemotePlatforms(read_projects=False).plateforms
            if not pf.is_hidden()
        }

        return active_platforms

    def _need_download_tree_config_file(self):
        """
        Do we need to download a new version of the resources tree file?
        2 possible reasons:
        - the user wants it to be downloading at plugin start up
        - the file is currently missing
        """
        config_file_exists = PluginGlobals.CONFIG_FILE_PATH.is_file()

        settings = PlgOptionsManager().get_plg_settings()

        return settings.download_files_at_startup > 0 or not config_file_exists

    def download_all_config_files(self):
        """Download the plugin config file and all the files of the active platforms.
        Hidden platform files are not downloaded."""

        self.log(
            message="DEBUG - prepare threads for downloading files...",
            log_level=4,
        )

        active_platforms = self._get_active_remote_plateforms()

        self.task1 = DownloadDefaultIdgListAsync()
        self.task2 = DownloadAllIdgFilesAsync(active_platforms)
        self.task1.finished.connect(self.task2.start)
        self.task2.finished.connect(self.refresh_data_provider)

        self.task1.start()

    def refresh_data_provider(self):
        if __debug__:
            self.log(
                message="DEBUG - refresh_data_provider.",
                log_level=4,
            )

        if self.provider and self.provider.root:
            self.provider.root.refresh()
