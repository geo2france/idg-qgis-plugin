# -*- coding: utf-8 -*-

from idg.toolbelt.singleton import Singleton
from idg.toolbelt.preferences import PlgOptionsManager
from idg.__about__ import DIR_PLUGIN_ROOT


@Singleton
class PluginGlobals:
    """ """

    iface = None
    plugin_path = None
    PLUGIN_TAG = "IDG"
    CONFIG_DIR_NAME = "config"
    CONFIG_FILE_NAMES = []
    DOWNLOAD_FILES_AT_STARTUP = PlgOptionsManager().get_value_from_key(
        "download_files_at_startup"
    )
    DEFAULT_CONFIG_FILE_NAME = "default_idg.json"
    DEFAULT_CONFIG_FILE_URL = (
        "https://raw.githubusercontent.com/geo2france/idg-qgis-plugin/dev/plugin/"
        f"idg/config/{DEFAULT_CONFIG_FILE_NAME}"
    )
    BROWSER_PROVIDER_NAME = "IDG Provider"

    def __init__(self):
        self.default_qsettings = {"CONFIG_FILE_NAMES": self.CONFIG_FILE_NAMES}
        self.config_dir_path = None
        self.config_file_path = None
        self.images_dir_path = None
        self.logo_file_path = None

    def reload_globals_from_qgis_settings(self):
        """
        Reloads the global variables of the plugin
        """

        # Read the qgis plugin settings
        from idg.toolbelt import PlgOptionsManager

        self.plg_settings = PlgOptionsManager()
        settings = self.plg_settings.get_plg_settings()
        self.DOWNLOAD_FILES_AT_STARTUP = settings.download_files_at_startup

        plugin_path = DIR_PLUGIN_ROOT.resolve()

        self.config_dir_path = (plugin_path / self.CONFIG_DIR_NAME).resolve()
        self.config_file_path = (
            self.config_dir_path / self.DEFAULT_CONFIG_FILE_NAME
        ).resolve()
