# -*- coding: utf-8 -*-
import shutil
from pathlib import Path
from urllib.parse import urlparse

from idg.browser.remote_platforms import Plateform
from qgis.core import Qgis
from idg.toolbelt import PlgLogger
from idg.plugin_globals import PluginGlobals
from idg.browser.network_manager import QgsTaskDownloadFile


class DownloadDefaultIdgIndex(QgsTaskDownloadFile):

    def __init__(self, url: str):
        super().__init__(url, local_path=PluginGlobals.REMOTE_DIR_PATH / PluginGlobals.DEFAULT_CONFIG_FILE_NAME)
        self.setDescription(self.tr("Plugin IDG : Download platforms index"))
        self.log = PlgLogger().log

    def finished(self, result):
        self.log(self.tr(f'Platforms index download completed'), log_level=Qgis.Info)


class DownloadIcon(QgsTaskDownloadFile):
    def __init__(self, platform: Plateform):
        super().__init__('',  # The URL is not known at initialization time
                         local_path=Path())
        self.platform = platform

    def run(self):
        if self.platform.project is None:
            self.platform.read_project()
        if self.platform.icon_url is None :
            return True # No icon to download
        icon_file_name = Path(urlparse(self.platform.icon_url).path).name
        super().__init__(self.platform.icon_url,  # Reinit superclass with knowed url
                         local_path=PluginGlobals.REMOTE_DIR_PATH / self.platform.idg_id / icon_file_name)
        return super().run()
