# -*- coding: utf-8 -*-
import copy
from pathlib import Path
from urllib.parse import urlparse


from idg.browser.remote_platforms import Plateform
from qgis.core import Qgis, QgsApplication
from idg.toolbelt import PlgLogger
from idg.plugin_globals import PluginGlobals
from idg.browser.network_manager import QgsTaskDownloadFile

log = PlgLogger().log


class DownloadDefaultIdgIndex(QgsTaskDownloadFile):
    def __init__(self, url: str):
        super().__init__(url, local_file=PluginGlobals.REMOTE_DIR_PATH / PluginGlobals.DEFAULT_CONFIG_FILE_NAME)
        self.setDescription(self.tr("Plugin IDG : Download platforms index"))

    def finished(self, result):
        if result :
            log(self.tr("Platforms index download completed"), log_level=Qgis.Success)
        else :
            log(self.tr("Cannot download platforms index"), log_level=Qgis.Warning, push=True)


class DownloadIcon(QgsTaskDownloadFile):
    def __init__(self, platform: Plateform):
        super().__init__()
        self.platform = platform

    def run(self):
        platform_copy = copy.deepcopy(self.platform)
        if platform_copy.project is None:
            platform_copy.read_project()
        if platform_copy.icon_url is None :
            return True  # No icon to download
        icon_file_name = Path(urlparse(platform_copy.icon_url).path).name
        self.url = platform_copy.icon_url
        self.local_file = PluginGlobals.REMOTE_DIR_PATH / platform_copy.idg_id / icon_file_name
        return super().run()
