# -*- coding: utf-8 -*-
import shutil
from pathlib import Path
from urllib.parse import urlparse

from PyQt5.QtCore import QUrl, QEventLoop
from idg.browser.remote_platforms import Plateform
from qgis.core import QgsProject, Qgis, QgsTask, QgsMessageLog, QgsFileDownloader
from qgis.PyQt.QtCore import QThread, pyqtSignal
from idg.toolbelt import PlgLogger
from idg.plugin_globals import PluginGlobals
from idg.browser.network_manager import NetworkRequestsManager, QgsTaskDownloadFile


class DownloadDefaultIdgListAsync(QgsTaskDownloadFile):

    def __init__(self, url: str):
        super().__init__(url, local_path=PluginGlobals.REMOTE_DIR_PATH / PluginGlobals.DEFAULT_CONFIG_FILE_NAME)
        self.setDescription(self.tr("Plugin IDG : Download platforms index"))
        self.log = PlgLogger().log

    def finished(self, result):
        self.log(self.tr(f'Platforms index download completed'), log_level=Qgis.Info)


class DownloadIcon(QgsTaskDownloadFile):
    def __init__(self, platform: Plateform):
        super().__init__('', # The URL is not known at initialization time
                             local_path=Path())
        self.platform = platform

    def run(self):
        if self.platform.project is None :
            self.platform.read_project()
        icon_file_name = Path(urlparse(self.platform.icon_url).path).name
        super().__init__(self.platform.icon_url, # Reinit superclass with knowed url
                             local_path=PluginGlobals.REMOTE_DIR_PATH / self.platform.idg_id / icon_file_name)
        return super().run()

class DownloadAllIdgFilesAsync(QgsTask):

    def __init__(self, idgs): # A typer
        super(QgsTask, self).__init__()
        self.idgs = idgs
        self.setDescription(self.tr("Download platforms projects"))
        self.log = PlgLogger().log

    def finished(self, result):
        pass

    def run(self):
        qntwk = NetworkRequestsManager()
        nb_items = len(self.idgs.items())
        subtask_list=[]
        for iteration,(idg_id, url) in enumerate(self.idgs.items(), start=1):
            # Clean and create dest folder
            local_file_path = PluginGlobals.REMOTE_DIR_PATH / idg_id
            print(url)
            subtask_list.append(QgsTaskDownloadFile(url, str(local_file_path), empty_local_path=False ))

        for t in subtask_list:
            self.addSubTask(t)

        """for iteration,(idg_id, url) in enumerate(self.idgs.items(), start=1): # Une subtask serait pertinente ?
            if self.isCanceled():
                return False
            # continue si l'IDG est masquée
            idg_id = str(idg_id)
            suffix = Path(url).suffix
            local_file_name = idg_id + suffix
            local_file_path = PluginGlobals.REMOTE_DIR_PATH / idg_id
            shutil.rmtree(local_file_path, ignore_errors=True)
            local_file_path.mkdir(exist_ok=True)
            self.log(f'Downloading {idg_id}... ({url})', log_level=Qgis.Info)
            local_file = qntwk.download_file(url, str(local_file_path / local_file_name))
            if local_file:
                self.log(self.tr(f'Reading {idg_id}...'), log_level=Qgis.Info)
                project = QgsProject()
                project.read(
                    local_file,
                    QgsProject.ReadFlags()
                    | QgsProject.FlagDontResolveLayers
                    | QgsProject.FlagDontLoadLayouts | QgsProject.FlagDontStoreOriginalStyles | QgsProject.FlagTrustLayerMetadata,
                )
                for link in project.metadata().links():
                    if link.name.lower().strip() == "icon":
                        icon_suffix = Path(link.url).suffix
                        icon_file_name = idg_id + icon_suffix
                        icon_file_path = (
                            PluginGlobals.REMOTE_DIR_PATH / idg_id / icon_file_name
                        )
                        qntwk.download_file(link.url, str(icon_file_path))
                        break
                project.clear() # Sinon, le nettoyage de la task est trop long
                self.log(self.tr(f'{idg_id} OK'), log_level=Qgis.Info, push=False)
            self.setProgress((iteration / nb_items) * 100)

        self.setProgress(100)"""
        return True
