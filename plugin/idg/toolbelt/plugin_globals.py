# -*- coding: utf-8 -*-

import sys
import os
import json
from .singleton import Singleton
from .preferences import PlgOptionsManager
from qgis.PyQt.QtCore import QSettings


@Singleton
class PluginGlobals:
    """ """

    iface = None
    plugin_path = None
    PLUGIN_TAG = "IDG"
    CONFIG_DIR_NAME = "config"
    CONFIG_FILE_NAMES = ["projet_idg.qgs"]
    CONFIG_FILES_DOWNLOAD_AT_STARTUP = PlgOptionsManager().get_value_from_key(
        "config_files_download_at_startup"
    )

    def __init__(self):
        self.default_qsettings = {"CONFIG_FILE_NAMES": self.CONFIG_FILE_NAMES}
        self.config_dir_path = None
        self.config_file_path = None
        self.images_dir_path = None
        self.logo_file_path = None

    def set_plugin_path(self, plugin_path):
        self.plugin_path = plugin_path

    def reload_globals_from_qgis_settings(self):
        """
        Reloads the global variables of the plugin
        """

        # Read the qgis plugin settings
        s = QSettings()
        self.CONFIG_FILES_DOWNLOAD_AT_STARTUP = (
            True
            if s.value(
                "{0}/config_files_download_at_startup".format(self.PLUGIN_TAG),
                self.CONFIG_FILES_DOWNLOAD_AT_STARTUP,
            )
            == "1"
            else False
        )

        self.CONFIG_DIR_NAME = s.value(
            "{0}/config_dir_name".format(self.PLUGIN_TAG), self.CONFIG_DIR_NAME
        )

        self.CONFIG_FILE_NAMES = s.value(
            "{0}/config_file_names".format(self.PLUGIN_TAG), self.CONFIG_FILE_NAMES
        )

        self.config_dir_path = os.path.join(self.plugin_path, self.CONFIG_DIR_NAME)
        self.config_file_path = os.path.join(
            self.config_dir_path, self.CONFIG_FILE_NAMES[0]
        )
