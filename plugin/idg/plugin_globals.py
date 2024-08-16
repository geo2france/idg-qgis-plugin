# -*- coding: utf-8 -*-

from idg.__about__ import DIR_PLUGIN_ROOT
from pathlib import Path


class PluginGlobals:
    """ """

    PLUGIN_TAG: str = "IDG"
    CONFIG_DIR_NAME: str = "config"
    DEFAULT_CONFIG_FILE_NAME: str = "default_idg.json"
    DEFAULT_CONFIG_FILE_URL: str = (
        "https://raw.githubusercontent.com/geo2france/idg-qgis-plugin/dev/plugin/"
        f"idg/config/{DEFAULT_CONFIG_FILE_NAME}"
    )
    BROWSER_PROVIDER_NAME: str = "IDG Provider"
    CONFIG_DIR_PATH: Path
    CONFIG_FILE_PATH: Path
    PLUGIN_PATH: Path

    def __init__(self):
        self.init_constants()

    @classmethod
    def init_constants(cls):
        """
        Init calculated class variables
        """

        PluginGlobals.PLUGIN_PATH = DIR_PLUGIN_ROOT.resolve()

        PluginGlobals.CONFIG_DIR_PATH = (
            PluginGlobals.PLUGIN_PATH / PluginGlobals.CONFIG_DIR_NAME
        ).resolve()
        PluginGlobals.CONFIG_FILE_PATH = (
            PluginGlobals.CONFIG_DIR_PATH / PluginGlobals.DEFAULT_CONFIG_FILE_NAME
        ).resolve()
