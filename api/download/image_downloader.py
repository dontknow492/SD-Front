import os
from PySide6.QtCore import QObject, Signal, QTimer, QUrl
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PySide6.QtGui import QImage
import uuid
from loguru import logger


class ImageDownloader(QObject):
    imageDownloaded = Signal(str, QImage, str)  # (uid, QImage, save_path)
    downloadFailed = Signal(str, str, str)  # (uid, error message, image_url)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.manager = QNetworkAccessManager(self)
        self.active_requests = {}  # Tracks {uid: (reply, timer, url, save_path, retries_left)}

    def _get_unique_save_path(self, save_path: str) -> str:
        """
        Generate a unique save path by appending a number if the file already exists.
        Example: If 'image.jpg' exists, try 'image_1.jpg', 'image_2.jpg', etc.
        """
        if not os.path.exists(save_path):
            return save_path

        base, ext = os.path.splitext(save_path)
        counter = 1
        while True:
            new_path = f"{base}_{counter}{ext}"
            if not os.path.exists(new_path):
                return new_path
            counter += 1

    def download_image(self, image_url: str, save_path: str, force_fetch: bool = False) -> str:
        """
        Downloads the image from the URL and saves it to the specified path.
        :param image_url: URL of the image to download
        :param save_path: Local path where the image should be saved
        :param force_fetch: Whether to force a fresh fetch (ignore cache)
        :return: Unique ID for this download request
        """
        uid = str(uuid.uuid4())
        url = QUrl(image_url)
        if not url.isValid():
            self.downloadFailed.emit(uid, "Invalid URL", image_url)
            return uid

        request = QNetworkRequest(url)
        if force_fetch:
            request.setRawHeader(b"Cache-Control", b"no-cache")  # Bypass cache if force_fetch

        reply = self.manager.get(request)
        timer = QTimer(self)
        timer.setSingleShot(True)
        timer.timeout.connect(lambda: self._on_timeout(uid))
        timer.start(5000)  # 5 seconds timeout

        # Store request info
        self.active_requests[uid] = {
            "reply": reply,
            "timer": timer,
            "url": image_url,
            "save_path": save_path,
            "retries_left": 2
        }

        # Connect reply's finished signal
        reply.finished.connect(lambda: self._on_finished(uid))
        logger.info(f"Started download for {uid}: {image_url}")
        return uid

    def cancel(self, uid: str):
        """Cancel an ongoing image download by uid."""
        if uid in self.active_requests:
            request_info = self.active_requests[uid]
            request_info["reply"].abort()
            request_info["timer"].stop()
            request_info["reply"].deleteLater()
            del self.active_requests[uid]
            logger.info(f"Download with uid {uid} cancelled.")

    def _on_timeout(self, uid: str):
        """Handle timeout for the download."""
        if uid not in self.active_requests:
            return

        request_info = self.active_requests[uid]
        logger.warning(f"Download timed out for {uid}: {request_info['url']}")
        request_info["reply"].abort()
        self._retry_or_fail(uid, "Download timed out")

    def _on_finished(self, uid: str):
        """Handle the completion of the download."""
        if uid not in self.active_requests:
            return

        request_info = self.active_requests[uid]
        reply = request_info["reply"]
        timer = request_info["timer"]
        timer.stop()

        error_code = reply.error()
        if error_code != QNetworkReply.NetworkError.NoError:
            error_string = reply.errorString()
            logger.error(f"Download failed for {uid}: {error_string}")
            self._retry_or_fail(uid, f"Error: {error_string}")
            reply.deleteLater()
            return

        # Get image data from the reply
        image_data = reply.readAll()
        image = QImage()
        if image.loadFromData(image_data):
            self._save_image(uid, image)
        else:
            logger.error(f"Failed to load image for {uid}")
            self._retry_or_fail(uid, "Failed to load image")

        reply.deleteLater()

    def _save_image(self, uid: str, image: QImage):
        """Save the downloaded image to disk, appending a number if the file exists."""
        save_path = self.active_requests[uid]["save_path"]
        # Get a unique save path if the file already exists
        unique_save_path = self._get_unique_save_path(save_path)
        self.active_requests[uid]["save_path"] = unique_save_path  # Update save_path in active_requests

        try:
            if image.save(unique_save_path):
                logger.info(f"Image saved for {uid}: {unique_save_path}")
                self.imageDownloaded.emit(uid, image, unique_save_path)
            else:
                logger.error(f"Failed to save image for {uid}: {unique_save_path}")
                self.downloadFailed.emit(uid, "Failed to save image", self.active_requests[uid]["url"])
        except Exception as e:
            logger.error(f"Exception while saving image for {uid}: {str(e)}")
            self.downloadFailed.emit(uid, f"Exception: {str(e)}", self.active_requests[uid]["url"])

        # Clean up
        del self.active_requests[uid]

    def _retry_or_fail(self, uid: str, error_message: str):
        """Retry the download if retries are available, otherwise emit failure."""
        request_info = self.active_requests[uid]
        if request_info["retries_left"] > 0:
            request_info["retries_left"] -= 1
            logger.info(f"Retrying download for {uid} ({request_info['retries_left']} retries left)")
            del self.active_requests[uid]  # Clean up before retry
            self.download_image(
                request_info["url"],
                request_info["save_path"],
                force_fetch=True  # Force fetch on retry
            )
        else:
            logger.error(f"Max retries reached for {uid}")
            self.downloadFailed.emit(uid, f"{error_message} (max retries reached)", request_info["url"])
            del self.active_requests[uid]


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys
    index = 0
    def on_image_downloaded(uid: str, image: QImage, save_path: str):
        global index
        print(f"Download succeeded for {uid}: Saved to {save_path}, index: {index}")
        index += 1
        # if index >=3:
        #     sys.exit(0)

    def on_download_failed(uid: str, error: str, url: str):
        print(f"Download failed for {uid}: {error} (URL: {url})")

    app = QApplication(sys.argv)
    downloader = ImageDownloader()
    downloader.imageDownloaded.connect(on_image_downloaded)
    downloader.downloadFailed.connect(on_download_failed)
    # url = "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/c4f1f56c-face-40f4-bc86-96780dc86d6b/width=1344/32982544.jpeg"
    # uid = downloader.download_image(url, "image.jpg")
    images = ["https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/4790674c-e16d-4dc7-b384-af4381fcfa3f/width=1200/5706937.jpeg",
            "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/ca18d37e-be8b-4a32-99d4-24e25b061a97/width=950/5275260.jpeg",
            "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/f1d3824f-5dae-4139-86cc-ad755fb93463/width=1152/5305869.jpeg",
            "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/7a167c45-98c0-4bb2-a752-d0c2f59416bb/width=896/5306294.jpeg"]
    for url in images:
        uid = downloader.download_image(url, "827184.jpg")
        print(f"Started download with UID: {uid}")
    sys.exit(app.exec())