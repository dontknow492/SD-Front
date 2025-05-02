import json
import uuid
from typing import Optional

from PySide6.QtCore import QObject, Signal, QTimer, QUrl
from PySide6.QtNetwork import (
    QNetworkDiskCache, QNetworkAccessManager,
    QNetworkRequest, QNetworkReply
)
from loguru import logger


class BaseFetcher(QObject):
    dataFetched = Signal(str, object)        # uid, data
    fetchFailed = Signal(str, int, str)      # uid, status, error
    requestStarted = Signal(str)             # uid

    def __init__(self, auth_token: Optional[str] = None,
                 cache_limit: int = 100 * 1024 * 1024, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.base_url = "https://civitai.com/api/v1/models"
        self.auth_token = auth_token
        self.cache_limit = cache_limit

        self.cache = QNetworkDiskCache(self)
        self.cache.setCacheDirectory("./.cache")
        self.cache.setMaximumCacheSize(self.cache_limit)

        self.manager = QNetworkAccessManager(self)
        self.manager.setCache(self.cache)
        self.manager.finished.connect(self._on_finished)

        self.timeout_timer = QTimer(self)
        self.timeout_timer.setSingleShot(True)
        self.timeout_timer.timeout.connect(self._on_timeout)

        self._retries_left = {}
        self._last_request = {}
        self.active_requests: dict[str, QNetworkReply] = {}
        self.current_uid = None

    def set_retry_count(self, uid: str, count: int):
        self._retries_left[uid] = count

    def fetch_model_info(self, model_id: Optional[str] = None,
                         model_hash: Optional[str] = None,
                         deduplicate: bool = True, force_fetch: bool = True) -> str:
        if model_id is None and model_hash is None:
            dummy_uid = str(uuid.uuid4())
            self.fetchFailed.emit(dummy_uid, 0, "Either model_id or model_hash must be provided")
            return dummy_uid

        if model_id is not None:
            url = f"{self.base_url}/{model_id}"
        else:
            url = f"{self.base_url}/by-hash/{model_hash}"

        uid = str(uuid.uuid4())

        if deduplicate:
            for existing_uid, reply in self.active_requests.items():
                if reply.request().url().toString() == url:
                    logger.info(f"Duplicate request detected for URL: {url}")
                    return existing_uid

        self._last_request[uid] = (url, False)
        self._retries_left[uid] = 2
        self._fetch(uid, url, force_fetch)
        return uid

    def _fetch(self, uid: str, url: str, force_fetch: bool = False):
        request = QNetworkRequest(QUrl(url))
        headers = {"Accept": "application/json"}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        for key, value in headers.items():
            request.setRawHeader(key.encode(), value.encode())

        if force_fetch:
            request.setAttribute(QNetworkRequest.CacheLoadControlAttribute,
                                 QNetworkRequest.AlwaysNetwork)

        try:
            reply = self.manager.get(request)
            self.active_requests[uid] = reply
            self.current_uid = uid

            reply.downloadProgress.connect(lambda r, t: self._on_progress(uid, r, t))
            reply.setProperty("uid", uid)

            self.requestStarted.emit(uid)
            self.timeout_timer.start(5000)  # 5 seconds timeout
        except Exception as e:
            logger.exception("Error initiating request")
            self.fetchFailed.emit(uid, 0, f"Failed to initiate request: {str(e)}")

    def cancel(self, uid: str):
        reply = self.active_requests.pop(uid, None)
        if reply:
            logger.info(f"Cancelling request {uid}")
            reply.abort()
            self.timeout_timer.stop()

    def _on_timeout(self):
        if self.current_uid:
            logger.warning(f"Request {self.current_uid} timed out")
            self.cancel(self.current_uid)
            self.fetchFailed.emit(self.current_uid, 0, "Request timed out")
            self.current_uid = None

    def _on_progress(self, uid: str, received: int, total: int):
        logger.debug(f"[{uid}] Download progress: {received}/{total} bytes")

    def _on_finished(self, reply: QNetworkReply):
        uid = reply.property("uid")
        self.timeout_timer.stop()

        if uid not in self.active_requests:
            reply.deleteLater()
            return

        del self.active_requests[uid]
        self.current_uid = None

        status_code = reply.attribute(QNetworkRequest.HttpStatusCodeAttribute)
        if status_code is None:
            status_code = 0

        error_code = reply.error()
        error_string = reply.errorString()

        from_cache = reply.attribute(QNetworkRequest.SourceIsFromCacheAttribute) is True
        logger.debug(f"[{uid}] From cache: {from_cache}")

        if error_code != QNetworkReply.NetworkError.NoError or status_code >= 500:
            logger.warning(f"[{uid}] Request to {reply.url().toString()} failed: {error_string} "
                           f"(code {error_code}), status: {status_code}")
            if self._retries_left.get(uid, 0) > 0 and uid in self._last_request:
                self._retries_left[uid] -= 1
                logger.info(f"[{uid}] Retrying... ({self._retries_left[uid]} retries left)")
                self._fetch(uid, *self._last_request[uid])
            else:
                self.fetchFailed.emit(uid, status_code, error_string or "Server error")
            reply.deleteLater()
            return

        try:
            content_type = reply.header(QNetworkRequest.ContentTypeHeader)
            data = reply.readAll().data().decode()
            if content_type and "application/json" in str(content_type).lower():
                parsed_data = json.loads(data)
                self.dataFetched.emit(uid, parsed_data)
            else:
                self.dataFetched.emit(uid, {"raw": data})
        except Exception as e:
            logger.exception("Error while decoding response")
            self.fetchFailed.emit(uid, status_code, f"Failed to process response: {str(e)}")
        finally:
            reply.deleteLater()
            self._last_request.pop(uid, None)
            self._retries_left.pop(uid, None)


def save_json(uid, data):
    with open(f"{uid}.json", "w") as f:
        json.dump(data, f, indent=4)
    sys.exit()

if __name__  == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    fetcher = BaseFetcher()
    fetcher.dataFetched.connect(lambda uid, data: save_json(uid, data))
    request_id  = fetcher.fetch_model_info("827184")
    sys.exit(app.exec())
