#! python3  # noqa: E265

"""
    Perform network request.
    (from https://github.com/geotribu/qtribu/blob/main/qtribu/toolbelt/network_manager.py)
"""

# ############################################################################
# ########## Imports ###############
# ##################################

# Standard library
import logging
import shutil
from os import remove, path
from shutil import copy
from pathlib import Path

# PyQGIS
from qgis.core import QgsBlockingNetworkRequest, QgsFileDownloader, QgsTask
from qgis.PyQt.QtCore import QByteArray, QCoreApplication, QEventLoop, QUrl

# project
from idg.toolbelt.log_handler import PlgLogger


# ############################################################################
# ########## Globals ###############
# ##################################

logger = logging.getLogger(__name__)

# ############################################################################
# ########## Classes ###############
# ##################################


class NetworkRequestsManager:
    """Helper on network operations.

    :param tr: method to translate
    :type tr: func
    """

    def __init__(self):
        """Initialization."""
        self.log = PlgLogger().log
        self.ntwk_requester = QgsBlockingNetworkRequest()

    def tr(self, message: str) -> str:
        """Get the translation for a string using Qt translation API.

        :param message: string to be translated.
        :type message: str

        :returns: Translated version of message.
        :rtype: str
        """
        return QCoreApplication.translate(self.__class__.__name__, message)

    def download_file(self, remote_url: str, local_path: str) -> str:
        """Download a file from a remote web server accessible through HTTP.

        :param remote_url: remote URL
        :type remote_url: str
        :param local_path: path to the local file
        :type local_path: str
        :return: output path
        :rtype: str
        """

        def dlCompleted():
            self.log(
                message=f"Download of {remote_url} to {local_path} succeedeed",
                log_level=3,
            )
            copy(local_path + "_tmp", local_path)
            remove(local_path + "_tmp")

        self.log(
            message=f"Downloading file from {remote_url} to {local_path}", log_level=4
        )
        # download it
        loop = QEventLoop()
        file_downloader = QgsFileDownloader(
            url=QUrl(remote_url),
            outputFileName=local_path + "_tmp",
            delayStart=True,  # Le téléchargement se fait dans un fichier temporaire, pour garder l'ancien fichier en cas d'échec
        )
        file_downloader.downloadCompleted.connect(dlCompleted)
        file_downloader.downloadError.connect(
            lambda e: self.log(
                message=f"Download of {remote_url} to {local_path} error {e}",
                log_level=1,
            )
        )
        file_downloader.downloadExited.connect(loop.quit)
        file_downloader.startDownload()
        loop.exec_()

        return local_path

class QgsTaskDownloadFile(QgsTask):
    def __init__(self, url: str, local_path: Path, empty_local_path:bool = False ):
        super(QgsTask, self).__init__()
        self.local_path = Path(local_path) # Ensure var is a Path
        self.empty_local_path = empty_local_path
        self.url = url
        self.log = PlgLogger().log
        self.downloader = QgsFileDownloader(QUrl(self.url),
                                            str(self.local_path),
                                            delayStart=True)

    def cancel(self):
        self.downloader.cancelDownload()
        super().cancel()

    def run(self):
        is_completed: bool = None

        if self.empty_local_path:
            shutil.rmtree(self.local_path.parent, ignore_errors=True)

        self.local_path.parent.mkdir(exist_ok=True) #Attention, local_path est un chemin de FICHIER !

        loop = QEventLoop()

        def on_completed():
            nonlocal is_completed
            is_completed = True
            self.setProgress(100)

        def on_error(): # Ici ?
            print('error', self.url)
            nonlocal is_completed
            is_completed = False

        def on_progress(received, total):
            try:
                self.setProgress((received / total) * 100)
            except ZeroDivisionError:
                pass

        self.downloader.downloadError.connect(on_error)
        self.downloader.downloadCompleted.connect(on_completed)
        self.downloader.downloadProgress.connect(on_progress)
        self.downloader.downloadExited.connect(lambda: loop.quit())
        self.downloader.startDownload()
        loop.exec()
        return is_completed
