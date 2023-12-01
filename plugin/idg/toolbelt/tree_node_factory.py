# -*- coding: utf-8 -*-

import os

from qgis.core import QgsProject

from qgis.PyQt.QtCore import QThread, pyqtSignal

from idg.toolbelt import PluginGlobals
from .network_manager import NetworkRequestsManager


class DownloadDefaultIdgListAsync(QThread):
    finished = pyqtSignal()

    def __init__(
        self,
        url="https://raw.githubusercontent.com/geo2france/idg-qgis-plugin/dev/plugin/idg/config"
        "/default_idg.json",
    ):
        super(QThread, self).__init__()
        self.url = url

    def run(self):
        qntwk = NetworkRequestsManager()
        qntwk.download_file(
            self.url,
            os.path.join(PluginGlobals.instance().config_dir_path, "default_idg.json"),
        )
        self.finished.emit()


class DownloadAllConfigFilesAsync(QThread):
    finished = pyqtSignal()

    def __init__(self, idgs):
        super(QThread, self).__init__()
        self.idgs = idgs

    def run(self):
        qntwk = NetworkRequestsManager()

        for idg_id, url in self.idgs.items():
            # continue si l'IDG est masquée
            idg_id = str(idg_id)
            suffix = os.path.splitext(os.path.basename(url))[-1]
            local_file_name = qntwk.download_file(
                url,
                os.path.join(PluginGlobals.instance().config_dir_path, idg_id + suffix),
            )
            if local_file_name:
                project = QgsProject()
                project.read(
                    local_file_name,
                    QgsProject.ReadFlags()
                    | QgsProject.FlagDontResolveLayers
                    | QgsProject.FlagDontLoadLayouts,
                )
                for link in project.metadata().links():
                    if link.name.lower().strip() == "icon":
                        suffix = os.path.splitext(os.path.basename(link.url))[-1]
                        qntwk.download_file(
                            link.url,
                            os.path.join(
                                PluginGlobals.instance().config_dir_path,
                                idg_id + suffix,
                            ),
                        )
                        break
        self.finished.emit()
