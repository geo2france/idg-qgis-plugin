# -*- coding: utf-8 -*-

from pathlib import Path

from qgis.core import QgsProject

from qgis.PyQt.QtCore import QThread, pyqtSignal

from idg.plugin_globals import PluginGlobals
from idg.browser.network_manager import NetworkRequestsManager


class DownloadDefaultIdgListAsync(QThread):
    finished = pyqtSignal()

    def __init__(self, url: str):
        super(QThread, self).__init__()
        self.url = url

    def run(self):
        qntwk = NetworkRequestsManager()
        qntwk.download_file(
            self.url,
            str(PluginGlobals.CONFIG_FILE_PATH),
        )
        self.finished.emit()


class DownloadAllIdgFilesAsync(QThread):
    finished = pyqtSignal()

    def __init__(self, idgs):
        super(QThread, self).__init__()
        self.idgs = idgs

    def run(self):
        qntwk = NetworkRequestsManager()

        for idg_id, url in self.idgs.items():
            # continue si l'IDG est masquée
            idg_id = str(idg_id)
            suffix = Path(url).suffix
            local_file_name = idg_id + suffix
            local_file_path = PluginGlobals.CONFIG_DIR_PATH / local_file_name
            local_file = qntwk.download_file(url, str(local_file_path))
            if local_file:
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
        self.finished.emit()
