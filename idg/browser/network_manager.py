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
    def __init__(self, url: str = None, local_path: Path = None, empty_local_path:bool = False ):
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
        self.local_path = local_path
        self.empty_local_path = empty_local_path
        self.url = url
        self.log = PlgLogger().log


    def cancel(self):
        try :
            self.downloader.cancelDownload()
        except AttributeError:
            pass
        finally:
            super().cancel()

    def run(self):
        self.local_path = Path(self.local_path) # Raise error if None ✔️
        self.downloader = QgsFileDownloader(QUrl(self.url),
                                            str(self.local_path),
                                            delayStart=True)
        is_completed: bool = False

        if self.empty_local_path:
            shutil.rmtree(self.local_path.parent, ignore_errors=True)

        self.local_path.parent.mkdir(exist_ok=True) # local_path est un chemin de FICHIER !

        loop = QEventLoop()

        def on_completed():
            nonlocal is_completed
            is_completed = True
            self.setProgress(100)
            self.taskCompleted.emit()

        def on_error():
            self.taskTerminated.emit()


        def on_progress(received, total):
            try:
                self.setProgress((received / total) * 100)
            except ZeroDivisionError:
                pass

        self.downloader.downloadError.connect(on_error)
        self.downloader.downloadCompleted.connect(on_completed)
        self.downloader.downloadProgress.connect(on_progress)
        self.downloader.downloadExited.connect(loop.quit)
        self.downloader.startDownload()
        loop.exec()
        return is_completed
