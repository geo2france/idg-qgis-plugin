import logging
import shutil
from pathlib import Path

from qgis.core import QgsFileDownloader, QgsTask
from qgis.PyQt.QtCore import QEventLoop, QUrl

from idg.toolbelt.log_handler import PlgLogger

logger = logging.getLogger(__name__)


class QgsTaskDownloadFile(QgsTask):
    """
    QgsTask for file downloading.
    """
    def __init__(self, url: str, local_path: Path, empty_local_path:bool = False ):
        """
        Parameters
        ----------
        url : str
            The url of the remote file
        local_path : Path
            The local path (including filename !)
        empty_local_path : bool, optional
            Empty the local folder before download
        """
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

        def on_error():
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
