#! python3  # noqa: E265

"""
Main plugin module.
"""
from pathlib import Path
from urllib.parse import urlparse

from idg.browser.network_manager import QgsTaskDownloadFile
# PyQGIS
from qgis.core import QgsApplication, Qgis, QgsTask
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
from idg.gui.actions import PluginActions
from idg.browser.remote_platforms import RemotePlatforms, Plateform
from idg.browser.browser import IdgProvider
from idg.browser.tree_node_factory import (
    DownloadDefaultIdgIndex, DownloadIcon,
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
        self.taskManager = QgsApplication.taskManager()

        PluginGlobals.REMOTE_DIR_PATH.mkdir(exist_ok=True) # Create remote dir if no exists
        # self.iface.initializationCompleted.connect(self.post_ui_init)
        self.post_ui_init()

    def post_ui_init(self):
        """Run after plugin's UI has been initialized."""
        self.registry.addProvider(self.provider)

        self.download_all_config_files()

    def initGui(self):
        """Set up plugin UI elements."""

        # settings page within the QGIS preferences menu
        self.options_factory = PlgOptionsFactory(
            self.settings_updated_slot, self.download_all_config_files
        )
        self.iface.registerOptionsWidgetFactory(self.options_factory)

        # -- Actions
        PluginActions.action_show_help = QAction(
            QgsApplication.getThemeIcon("mActionHelpContents.svg"),
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
            QgsApplication.getThemeIcon("mActionRefresh.svg"),
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
        """Function called when the settings are updated"""
        self.download_all_config_files() # Provoque aussi le refresh du browser

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

    def download_all_config_files(self, end_slot=None):
        """Download the plugin config file and all the files of the active platforms.
        Hidden platform files are not downloaded."""

        self.log(self.tr("Reloading all remotes files..."), log_level=Qgis.Info)

        settings = PlgOptionsManager().get_plg_settings()
        config_file_url = settings.config_file_url

        if not end_slot:
            end_slot = self.refresh_data_provider

        def dl_projects():
            task_dl_index.taskCompleted.disconnect(dl_projects)
            active_platforms = self._get_active_remote_plateforms()
            for idg_id, url in active_platforms.items():
                project_file_name = Path(urlparse(url).path).name
                local_file_path = PluginGlobals.REMOTE_DIR_PATH / idg_id / project_file_name
                platform = Plateform(url=url, idg_id=idg_id, read_project=False)
                task_dl_project = QgsTaskDownloadFile(url, local_file_path, empty_local_path=True)
                task_dl_icon = DownloadIcon(platform)
                task_dl_icon.setDescription(f"Downloading {idg_id}")

                # Téléchargement du fichier projet <idg>.qgz, PUIS de l'icon
                task_dl_icon.addSubTask(task_dl_project, [], QgsTask.ParentDependsOnSubTask)

                self.taskManager.addTask(
                    task_dl_icon
                )
            self.taskManager.allTasksFinished.connect(all_finished)

        task_dl_index = DownloadDefaultIdgIndex(url=config_file_url) # Tâche pour télécharger default_idg.json

        task_dl_index.taskCompleted.connect(dl_projects) # Dl project after index download
        self.taskManager.addTask(task_dl_index)

        def all_finished():
            self.log(self.tr('All remotes files downloaded'), log_level=Qgis.Info)
            self.refresh_data_provider()
            self.taskManager.allTasksFinished.disconnect(all_finished)

    def refresh_data_provider(self):
        self.log(self.tr("refresh data provider"), log_level=Qgis.Info)
        if self.provider and self.provider.root:
            self.provider.root.refresh()
