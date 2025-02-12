import shutil
from pathlib import Path
from typing import Optional

from qgis.core import QgsFileDownloader, QgsTask
from qgis.PyQt.QtCore import QEventLoop, QUrl


class QgsTaskDownloadFile(QgsTask):
    """
    QgsTask for file downloading.
    """
    def __init__(self, url: str = None, local_file: Path = None, empty_local_path: bool = False):
        """
        Parameters
        ----------
        url : str
            The url of the remote file
        local_file : Path
            The local file path
        empty_local_path : bool, optional
            Empty the local folder before download
        """
        super().__init__()
        self.local_file = local_file
        self.empty_local_path = empty_local_path
        self.url = url
        self.downloader: Optional[QgsFileDownloader] = None

    def cancel(self):
        try:
            self.downloader.cancelDownload()
        except AttributeError:
            pass
        finally:
            super().cancel()

    def run(self):
        self.local_file = Path(self.local_file)  # Raise error if None ✔️
        self.downloader = QgsFileDownloader(QUrl(self.url),
                                            str(self.local_file),
                                            delayStart=True)
        is_completed: bool = False

        if self.empty_local_path:
            shutil.rmtree(self.local_file.parent, ignore_errors=True)

        self.local_file.parent.mkdir(exist_ok=True)

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
