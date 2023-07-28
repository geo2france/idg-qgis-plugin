# -*- coding: utf-8 -*-

import os
import json
import traceback
from urllib.parse import parse_qs, urlparse

from qgis.core import (
    Qgis,
    QgsMessageLog,
    QgsProject,
    QgsNetworkAccessManager,
    QgsNetworkReplyContent,
)
from qgis.PyQt.QtNetwork import QNetworkRequest, QNetworkReply
from qgis.PyQt.QtCore import QUrl, QThread, pyqtSignal

from idg.toolbelt import PluginGlobals
from .network_manager import NetworkRequestsManager



def download_default_idg_list(url='https://raw.githubusercontent.com/geo2france/idg-qgis-plugin/dev/plugin/idg/config/default_idg.json'):
    local_file = os.path.join(PluginGlobals.instance().config_dir_path, 'default_idg.json')
    request = QNetworkRequest(QUrl(url))
    manager = QgsNetworkAccessManager.instance()
    request.setTransferTimeout(5000)
    response: QgsNetworkReplyContent = manager.blockingGet(
        request, forceRefresh=True
    )
    qntwk = NetworkRequestsManager()
    local_file_name = qntwk.download_file(url, os.path.join(PluginGlobals.instance().config_dir_path, 'default_idg.json'))
    if local_file_name is not None:
        #try:
        #    os.remove(local_file)
        #except OSError:
        #    pass
        with open(local_file, "r") as local_config_file:
            out = json.load(local_config_file)
        return out
    #TOD gérer les erreur (garder le fichier précédent + avertissement)

def download_all_config_files(idgs): #remplacer la list par un dict ({idg_id:url})
    """Download all config file in dict
        key = IDG_id, value = url
        rename local file
    """
    #TODO a passer dans RemotePlatforms
    qntwk = NetworkRequestsManager()
    for idg_id, url in idgs.items():
        #continue si l'IDG est masquée
        idg_id = str(idg_id)
        local_file_name = qntwk.download_file(url, os.path.join(PluginGlobals.instance().config_dir_path, idg_id + suffix))
        if local_file_name :
            # Download icon if custom TODO a factoriser
            project = QgsProject()
            project.read(local_file_name, QgsProject.ReadFlags()|QgsProject.FlagDontResolveLayers|QgsProject.FlagDontLoadLayouts)
            for l in project.metadata().links():
                if l.name.lower().strip() == 'icon':
                    suffix = os.path.splitext(os.path.basename(l.url))[-1]
                    qntwk.download_file(l.url, os.path.join(PluginGlobals.instance().config_dir_path, idg_id + suffix) )
                    break
        else :
            short_message = "Le téléchargement du fichier projet {0} a échoué.".format(idg_id)
            PluginGlobals.instance().iface.messageBar().pushMessage(
                "Erreur", short_message, level=Qgis.Warning
            )

class DownloadAllConfigFilesAsync(QThread):
    finished = pyqtSignal()
    def __init__(self, idgs):
        super(QThread, self).__init__()
        self.idgs=idgs
    def run(self):
        qntwk = NetworkRequestsManager()

        for idg_id, url in self.idgs.items():
            # continue si l'IDG est masquée
            idg_id = str(idg_id)
            suffix = os.path.splitext(os.path.basename(url))[-1]
            local_file_name = qntwk.download_file(url, os.path.join(PluginGlobals.instance().config_dir_path,
                                                                    idg_id + suffix))
            if local_file_name:
                project = QgsProject()
                project.read(local_file_name,
                             QgsProject.ReadFlags() | QgsProject.FlagDontResolveLayers | QgsProject.FlagDontLoadLayouts)
                for l in project.metadata().links():
                    if l.name.lower().strip() == 'icon':
                        suffix = os.path.splitext(os.path.basename(l.url))[-1]
                        qntwk.download_file(l.url,
                                            os.path.join(PluginGlobals.instance().config_dir_path, idg_id + suffix))
                        break
        self.finished.emit()


