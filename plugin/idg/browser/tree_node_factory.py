# -*- coding: utf-8 -*-

from pathlib import Path

from qgis.core import QgsProject, Qgis, QgsTask, QgsMessageLog
from qgis.PyQt.QtCore import QThread, pyqtSignal

from idg.plugin_globals import PluginGlobals
from idg.browser.network_manager import NetworkRequestsManager


class DownloadDefaultIdgListAsync(QgsTask):

    def __init__(self, url: str):
        super(QgsTask, self).__init__()
        self.url = url
        self.setDescription("Plugin IDG : Downloading IDG index")

    def finished(self, result):
        QgsMessageLog.logMessage(f'IDG : Downloading IDG index Finished', level=Qgis.Info)

    def run(self):
        qntwk = NetworkRequestsManager()
        qntwk.download_file(
            self.url,
            str(PluginGlobals.CONFIG_FILE_PATH),
        )
        self.setProgress(100)
        return True


class DownloadAllIdgFilesAsync(QgsTask):

    def __init__(self, idgs): # A typer
        super(QgsTask, self).__init__()
        self.idgs = idgs
        self.setDescription("IDG : Downloading plateforms project's")

    def finished(self, result):
        QgsMessageLog.logMessage("IDG : Downloading plateforms project's finished", level=Qgis.Info)

    def run(self):
        qntwk = NetworkRequestsManager()
        nb_items = len(self.idgs.items())
        for iteration,(idg_id, url) in enumerate(self.idgs.items(), start=1): # Une subtask serait pertinente ?
            if self.isCanceled():
                return False
            # continue si l'IDG est masquée
            idg_id = str(idg_id)
            suffix = Path(url).suffix
            local_file_name = idg_id + suffix
            local_file_path = PluginGlobals.CONFIG_DIR_PATH / local_file_name
            QgsMessageLog.logMessage(f'Downloading {idg_id}... ({url})', level=Qgis.Info)
            local_file = qntwk.download_file(url, str(local_file_path))
            if local_file:
                QgsMessageLog.logMessage(f'Reading {idg_id}...', level=Qgis.Info)
                project = QgsProject()
                project.read(
                    local_file,
                    QgsProject.ReadFlags()
                    | QgsProject.FlagDontResolveLayers
                    | QgsProject.FlagDontLoadLayouts,
                )
                for link in project.metadata().links():
                    if link.name.lower().strip() == "icon":
                        icon_suffix = Path(link.url).suffix
                        icon_file_name = idg_id + icon_suffix
                        icon_file_path = (
                            PluginGlobals.CONFIG_DIR_PATH / icon_file_name
                        )
                        qntwk.download_file(link.url, str(icon_file_path))
                        break
                project.clear() # Sinon, le nettoyage de la task est trop long
                QgsMessageLog.logMessage(f'{idg_id} OK', level= Qgis.Info)
            self.setProgress((iteration / nb_items) * 100)

        self.setProgress(100)
        return True
