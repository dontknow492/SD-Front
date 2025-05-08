import uuid
import json
from typing import Optional, Dict, Any, List, Tuple

from PySide6.QtCore import QObject, Signal, QUrl, QTimer, QUrlQuery, QByteArray, QDateTime, Slot
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply, QNetworkDiskCache
from loguru import logger


class BaseFetcher(QObject):
    # API Endpoints (reusable constants)
    _ENDPOINT_VERSION = "/sdapi/v1/version"
    _ENDPOINT_MODELS = "/sdapi/v1/sd-models"
    _ENDPOINT_VAES = "/sdapi/v1/sd-vae"
    _ENDPOINT_EMBEDDINGS = "/sdapi/v1/embeddings"
    _ENDPOINT_LORAS = "/sdapi/v1/lora"
    _ENDPOINT_STYLES = "/sdapi/v1/prompt-styles"
    _ENDPOINT_REFRESH_CHECKPOINTS = "/sdapi/v1/refresh-checkpoints"
    _ENDPOINT_REFRESH_LORAS = "/sdapi/v1/refresh-loras"
    _ENDPOINT_PROGRESS = "/sdapi/v1/progress"
    _ENDPOINT_OPTIONS = "/sdapi/v1/options"
    _ENDPOINT_UPSCALERS = "/sdapi/v1/upscalers"
    _ENDPOINT_SAMPLERS = "/sdapi/v1/samplers"
    _ENDPOINT_STATUS = "/sdapi/v1/status"

    # Signals
    dataFetched = Signal(object, str)  # data, request_uuid
    fetchFailed = Signal(str, int, str)  # error_msg, status_code, request_uuid
    progressUpdated = Signal(int, int, str)  # bytes_received, bytes_total, request_uuid
    serverAvailable = Signal(bool)  # is_available
    cacheUsed = Signal(bool)  # was_cache_hit
    authenticationRequired = Signal()  # Emitted on 401/403 errors

    def __init__(self, base_url: str = "http://127.0.0.1:7860",
                 auth_token: Optional[str] = None, cache_ttl_seconds: int = 3600, cache_size: int = 104857600, parent=None):
        super().__init__(parent)
        self.base_url = base_url.rstrip('/')
        self.auth_token = auth_token
        self.cache_ttl_seconds = cache_ttl_seconds
        self.cache_size = cache_size

        self.manager = QNetworkAccessManager(self)
        self._setup_cache()

        # Per-request timers instead of single timer
        self._request_timers: Dict[str, QTimer] = {}  # request_uuid -> timer

        self._active_requests: Dict[str, str] = {}  # endpoint -> request_uuid
        self._request_metadata: Dict[str, dict] = {}  # request_uuid -> metadata (includes retries_left)
        self._pending_replies: Dict[QNetworkReply, Tuple[str, str]] = {}  # reply -> (endpoint, request_uuid)

        self.manager.finished.connect(self._on_finished)

    def _setup_cache(self):
        """Initialize and configure the disk cache"""
        self.cache = QNetworkDiskCache(self)
        self.cache.setCacheDirectory(".cache")
        self.cache.setMaximumCacheSize(self.cache_size)
        self.manager.setCache(self.cache)

    def clear_cache(self):
        """Clear all cached responses"""
        logger.info(f"Clearing cache. Current size: {self.cache.cacheSize() / 1024 / 1024:.2f} MB")
        self.cache.clear()

    def fetch(self, endpoint: str, method: str = "GET", headers: Optional[Dict[str, str]] = None,
              body: Optional[Dict[str, Any]] = None, params: Optional[Dict[str, Any]] = None,
              timeout_ms: int = 10000, retries: int = 3, use_cache: bool = True) -> str:
        """Main method to initiate a request. Returns a request UUID for tracking."""
        request_uuid = str(uuid.uuid4())
        logger.debug(f"Starting request {request_uuid} for endpoint {endpoint}")

        if endpoint in self._active_requests:
            existing_uuid = self._active_requests[endpoint]
            logger.warning(f"Request {request_uuid} ignored: active request {existing_uuid} for {endpoint}")
            return existing_uuid

        # Store metadata including retry count
        self._request_metadata[request_uuid] = {
            "endpoint": endpoint,
            "method": method,
            "headers": headers,
            "body": body,
            "params": params,
            "timeout_ms": timeout_ms,
            "use_cache": use_cache,
            "retries_left": retries
        }
        self._active_requests[endpoint] = request_uuid

        self._do_fetch(request_uuid)
        return request_uuid

    def _do_fetch(self, request_uuid: str):
        """Internal method to execute the actual network request"""
        metadata = self._request_metadata.get(request_uuid)
        if not metadata:
            logger.exception(f"Invalid request UUID: {request_uuid}")
            return

        endpoint = metadata["endpoint"]
        method = metadata["method"].upper()
        headers = metadata["headers"] or {}
        body = metadata["body"]
        params = metadata["params"]
        timeout_ms = metadata["timeout_ms"]
        use_cache = metadata["use_cache"]

        # Build URL with query parameters
        url = QUrl(f"{self.base_url}{endpoint}")
        if params:
            query = QUrlQuery()
            for key, value in params.items():
                query.addQueryItem(key, str(value))
            url.setQuery(query)

        # Prepare request
        request = QNetworkRequest(url)

        # Add auth header if available
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"

        # Set headers
        for key, value in headers.items():
            request.setRawHeader(key.encode(), value.encode())

        # Prepare body data
        if body:
            request.setHeader(QNetworkRequest.KnownHeaders.ContentTypeHeader, "application/json")
            data = json.dumps(body).encode()
        else:
            data = QByteArray()

        # Configure caching
        cache_control = QNetworkRequest.CacheLoadControl.AlwaysNetwork
        if use_cache:
            cache_control = QNetworkRequest.CacheLoadControl.AlwaysCache
            # Force revalidation if cached entry is expired
            if self._is_cached_entry_expired(url):
                logger.debug("Cache is Expired so renewing it..")
                cache_control = QNetworkRequest.CacheLoadControl.AlwaysNetwork

        request.setAttribute(QNetworkRequest.Attribute.CacheLoadControlAttribute, cache_control)

        # Execute request
        try:
            if method == "GET":
                reply = self.manager.get(request)
            elif method == "POST":
                reply = self.manager.post(request, data)
            elif method == "PUT":
                reply = self.manager.put(request, data)
            elif method == "DELETE":
                reply = self.manager.deleteResource(request)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            # Store reply reference
            self._pending_replies[reply] = (endpoint, request_uuid)

            # Connect progress signal
            reply.downloadProgress.connect(
                lambda received, total, uuid=request_uuid: self._on_progress(received, total, uuid))

            # Setup per-request timeout
            self._setup_request_timeout(request_uuid, timeout_ms)

        except Exception as e:
            self.fetchFailed.emit(f"Failed to initiate request: {str(e)}", 0, request_uuid)
            self._cleanup_request(request_uuid)

    def _is_cached_entry_expired(self, url: QUrl) -> bool:
        """Check if a cached entry exists and is expired"""
        logger.debug("Checking if cache entry is expired")
        meta_data = self.cache.metaData(url)
        if not meta_data.isValid():
            return False

        expiration_date = meta_data.expirationDate()
        if not expiration_date.isValid():
            return False

        return expiration_date.secsTo(QDateTime.currentDateTime()) >= 0

    def _setup_request_timeout(self, request_uuid: str, timeout_ms: int):
        """Create and start a timeout timer for the request"""
        timer = QTimer(self)
        timer.setSingleShot(True)
        timer.timeout.connect(lambda: self._on_timeout(request_uuid))
        timer.start(timeout_ms)
        self._request_timers[request_uuid] = timer

    def _on_timeout(self, request_uuid: str):
        """Handle request timeout"""
        timer = self._request_timers.pop(request_uuid, None)
        if timer:
            timer.deleteLater()

        # Find and abort the associated reply
        for reply, (endpoint, uuid) in list(self._pending_replies.items()):
            if uuid == request_uuid:
                reply.abort()
                self.fetchFailed.emit("Request timed out", 0, request_uuid)
                self._cleanup_request(request_uuid)
                del self._pending_replies[reply]
                break

    def _on_progress(self, bytes_received: int, bytes_total: int, request_uuid: str):
        """Handle download progress updates"""
        self.progressUpdated.emit(bytes_received, bytes_total, request_uuid)

    def _on_finished(self, reply: QNetworkReply):
        """Handle completed network requests"""
        if reply not in self._pending_replies:
            reply.deleteLater()
            return

        endpoint, request_uuid = self._pending_replies.pop(reply)

        # Clean up timeout timer
        timer = self._request_timers.pop(request_uuid, None)
        if timer:
            timer.stop()
            timer.deleteLater()

        # Verify this is still the active request for the endpoint
        if self._active_requests.get(endpoint) != request_uuid:
            logger.warning(f"Ignoring stale response for {endpoint}: {request_uuid}")
            reply.deleteLater()
            return

        status_code = reply.attribute(QNetworkRequest.HttpStatusCodeAttribute) or 0
        cache_hit = reply.attribute(QNetworkRequest.SourceIsFromCacheAttribute) or False
        self.cacheUsed.emit(cache_hit)
        logger.info(f"Response for {endpoint} (UUID: {request_uuid}): {'Cache hit' if cache_hit else 'Network fetch'}")

        # Handle server availability checks
        if endpoint == self._ENDPOINT_VERSION:
            self.serverAvailable.emit(reply.error() == QNetworkReply.NoError)
            self._cleanup_request(request_uuid)
            reply.deleteLater()
            return

        # Handle authentication errors
        if status_code in (401, 403):
            self.authenticationRequired.emit()
            self.fetchFailed.emit("Authentication required", status_code, request_uuid)
            self._cleanup_request(request_uuid)
            reply.deleteLater()
            return

        # Handle errors (including network errors and server errors)
        if reply.error() != QNetworkReply.NoError or status_code >= 500:
            error_msg = self._get_error_message(reply, status_code)
            metadata = self._request_metadata.get(request_uuid, {})

            self._handle_error(reply, request_uuid)

            # Attempt retry if configured
            if metadata.get("retries_left", 0) > 0:
                metadata["retries_left"] -= 1
                logger.warning(f"Retrying request {request_uuid} ({metadata['retries_left']} retries left)")
                self._do_fetch(request_uuid)
                reply.deleteLater()
                return

            self.fetchFailed.emit(error_msg, status_code, request_uuid)
            self._cleanup_request(request_uuid)
            reply.deleteLater()
            return

        # Process successful response
        content_type = reply.header(QNetworkRequest.KnownHeaders.ContentTypeHeader)
        try:
            data = reply.readAll().data().decode()
            if content_type and "application/json" in content_type.lower():
                parsed_data = json.loads(data)
                self.dataFetched.emit(parsed_data, request_uuid)
            else:
                self.dataFetched.emit({"raw": data}, request_uuid)
        except Exception as e:
            self.fetchFailed.emit(f"Failed to process response: {str(e)}", status_code, request_uuid)
        finally:
            self._cleanup_request(request_uuid)
            reply.deleteLater()

    def _handle_error(self, reply: QNetworkReply):
        """Classify and handle network-related errors from QNetworkReply."""
        status_code = reply.attribute(QNetworkRequest.HttpStatusCodeAttribute) or 0
        error_string = reply.errorString()

        error = reply.error()
        server_down = False

        match error:
            case QNetworkReply.NetworkError.ConnectionRefusedError:
                message = "Connection refused by the server. Is the server running?"
                server_down = True
            case QNetworkReply.NetworkError.RemoteHostClosedError:
                message = "Server closed the connection unexpectedly."
            case QNetworkReply.NetworkError.HostNotFoundError:
                message = "Host not found. Check your server address or network."
                server_down = True
            case QNetworkReply.NetworkError.TimeoutError:
                message = "Request timed out. Server might be overloaded or unreachable."
            case QNetworkReply.NetworkError.OperationCanceledError:
                message = "The request was cancelled before completion."
            case QNetworkReply.NetworkError.SslHandshakeFailedError:
                message = "SSL handshake failed. Check SSL configuration or certificates."
            case QNetworkReply.NetworkError.TemporaryNetworkFailureError:
                message = "Temporary network failure. Please try again."
            case QNetworkReply.NetworkError.ProtocolFailure:
                message = "Protocol error. The server returned an invalid response."
            case QNetworkReply.NetworkError.ContentAccessDenied:
                message = f"Access denied (HTTP {status_code}). Check credentials or permissions."
            case QNetworkReply.NetworkError.ContentNotFoundError:
                message = f"Resource not found (HTTP {status_code}). The endpoint or file may not exist."
            case QNetworkReply.NetworkError.AuthenticationRequiredError:
                message = f"Authentication required (HTTP {status_code}). Provide valid credentials."
            case QNetworkReply.NetworkError.ContentConflictError:
                message = f"Request conflict (HTTP {status_code}). Possibly duplicate or invalid data."
            case QNetworkReply.NetworkError.InternalServerError:
                message = f"Internal server error (HTTP {status_code}). Try again later."
            case _:
                message = f"Unknown network error occurred (HTTP {status_code})."

        full_message = f"{message} | Details: {error_string}"
        logger.exception(full_message)
        self.fetchFailed.emit(full_message, status_code)

        if server_down:
            self.serverAvailable.emit(False)

    def _get_error_message(self, reply: QNetworkReply, status_code: int) -> str:
        """Generate appropriate error message based on reply error"""
        error_map = {
            QNetworkReply.ConnectionRefusedError: "Stable Diffusion server is not running",
            QNetworkReply.HostNotFoundError: "Cannot find server at specified URL",
            QNetworkReply.TimeoutError: "Server took too long to respond",
            QNetworkReply.AuthenticationRequiredError: "Authentication required",
        }

        if status_code >= 400:
            return f"Server error: {status_code}"
        return error_map.get(reply.error(), reply.errorString() or "Network error")

    def _cleanup_request(self, request_uuid: str):
        """Clean up all resources associated with a request"""
        # Remove from active requests
        for endpoint, uuid in list(self._active_requests.items()):
            if uuid == request_uuid:
                del self._active_requests[endpoint]
                break

        # Remove metadata
        self._request_metadata.pop(request_uuid, None)

        # Clean up timer if it exists
        timer = self._request_timers.pop(request_uuid, None)
        if timer:
            timer.stop()
            timer.deleteLater()

    def cancel(self):
        """Cancel all pending requests"""
        for reply in list(self._pending_replies.keys()):
            reply.abort()
            endpoint, request_uuid = self._pending_replies.pop(reply)
            if self._active_requests.get(endpoint) == request_uuid:
                del self._active_requests[endpoint]
            self._request_metadata.pop(request_uuid, None)

        for timer in self._request_timers.values():
            timer.stop()
            timer.deleteLater()
        self._request_timers.clear()

    def cancel_request(self, request_uuid: str):
        """Cancel a specific request by UUID"""
        for reply, (endpoint, uuid) in list(self._pending_replies.items()):
            if uuid == request_uuid:
                reply.abort()
                del self._pending_replies[reply]
                if self._active_requests.get(endpoint) == uuid:
                    del self._active_requests[endpoint]
                self._request_metadata.pop(uuid, None)
                break

        timer = self._request_timers.pop(request_uuid, None)
        if timer:
            timer.stop()
            timer.deleteLater()

    def warm_up_cache(self):
        """Pre-fetch common API endpoints to populate cache"""
        endpoints = [
            self._ENDPOINT_MODELS,
            self._ENDPOINT_VAES,
            self._ENDPOINT_EMBEDDINGS,
            self._ENDPOINT_LORAS,
            self._ENDPOINT_STYLES
        ]

        for endpoint in endpoints:
            request_uuid = self.fetch(endpoint=endpoint)
            logger.info(f"Warming up cache for {endpoint} (UUID: {request_uuid})")

    # Simplified endpoint methods using constants
    def fetch_models(self, timeout_ms: int = 10000, use_cache: bool = True) -> str:
        return self.fetch(endpoint=self._ENDPOINT_MODELS, timeout_ms=timeout_ms, use_cache=use_cache)

    def fetch_vaes(self, timeout_ms: int = 10000, use_cache: bool = True) -> str:
        return self.fetch(endpoint=self._ENDPOINT_VAES, timeout_ms=timeout_ms, use_cache=use_cache)

    def fetch_embeddings(self, timeout_ms: int = 10000, use_cache: bool = True) -> str:
        return self.fetch(endpoint=self._ENDPOINT_EMBEDDINGS, timeout_ms=timeout_ms, use_cache=use_cache)

    def fetch_loras(self, timeout_ms: int = 10000, use_cache: bool = True) -> str:
        return self.fetch(endpoint=self._ENDPOINT_LORAS, timeout_ms=timeout_ms, use_cache=use_cache)

    def fetch_styles(self, timeout_ms: int = 10000, use_cache: bool = True) -> str:
        return self.fetch(endpoint=self._ENDPOINT_STYLES, timeout_ms=timeout_ms, use_cache=use_cache)

    def fetch_upscalers(self, timeout_ms: int = 10000, use_cache: bool = True) -> str:
        return self.fetch(endpoint=self._ENDPOINT_UPSCALERS, timeout_ms=timeout_ms, use_cache=use_cache)

    def fetch_samplers(self, timeout_ms: int = 10000, use_cache: bool = True) -> str:
        return self.fetch(endpoint=self._ENDPOINT_SAMPLERS, timeout_ms=timeout_ms, use_cache=use_cache)

    def refresh_models(self, timeout_ms: int = 10000):
        self.fetch(endpoint=self._ENDPOINT_REFRESH_CHECKPOINTS, method="POST", timeout_ms=timeout_ms, use_cache=False)
        self.clear_cache()

    def refresh_loras(self, timeout_ms: int = 10000):
        self.fetch(endpoint=self._ENDPOINT_REFRESH_LORAS, method="POST", timeout_ms=timeout_ms, use_cache=False)
        self.clear_cache()

    def check_server(self, timeout_ms: int = 5000) -> str:
        return self.fetch(endpoint=self._ENDPOINT_VERSION, timeout_ms=timeout_ms, use_cache=False)

    def fetch_progress(self, timeout_ms=1000, retries: int = 1) -> str:
        """Specialized progress fetcher with shorter default timeout"""
        return self.fetch(
            endpoint=self._ENDPOINT_PROGRESS,
            timeout_ms=timeout_ms,
            use_cache=False,
            retries=retries  # Fewer retries for progress updates
        )

    def fetch_status(self, timeout_ms = 1000, retries: int = 1)->str:
        return self.fetch(endpoint=self._ENDPOINT_STATUS, timeout_ms=timeout_ms, use_cache=False, retries=retries)

    def __del__(self):
        self.cancel()


# from PySide6.QtCore import QObject, Signal, QTimer, Slot


class ProgressTracker(QObject):
    """
    Handles real-time progress updates from the Stable Diffusion API.
    Uses BaseFetcher internally but manages its own polling and state.

    Signals:
        progressUpdated (float): Emits progress value between 0.0 and 1.0.
        progressData (dict): Emits full progress response dictionary.
        stalled (): Emits if no progress is detected within stall timeout.
        completed (): Emits when progress reaches 1.0 and monitoring stops.
    """

    progressUpdated = Signal(float)
    progressData = Signal(dict)
    stalled = Signal()
    completed = Signal()

    def __init__(self, base_fetcher, parent=None):
        super().__init__(parent)
        self.fetcher = base_fetcher
        self._poll_timer = QTimer(self)
        self._stall_timer = QTimer(self)
        self._last_progress = 0.0
        self._active = False

        # Configure timers
        self._poll_timer.setInterval(500)       # How often to poll the API
        self._stall_timer.setInterval(3000)     # Stall detection timeout
        self._poll_timer.timeout.connect(self._poll)
        self._stall_timer.timeout.connect(self._handle_stall)

        # Connect fetcher responses to local handlers
        self.fetcher.dataFetched.connect(self._handle_progress_response)
        self.fetcher.fetchFailed.connect(self._handle_progress_failure)

    def start_monitoring(self, interval_ms=500):
        """
        Begin polling for progress updates.
        Args:
            interval_ms (int): Interval between progress checks in milliseconds.
        """
        if not self._active:
            self._active = True
            self._poll_timer.setInterval(interval_ms)
            self._poll_timer.start()
            self._stall_timer.start()
            self._poll()  # Initial fetch

    def stop_monitoring(self):
        """
        Stop all polling and internal timers.
        """
        self._active = False
        self._poll_timer.stop()
        self._stall_timer.stop()

    @Slot()
    def _poll(self):
        """
        Internal: Triggers a fetch from the /progress endpoint.
        """
        if self._active:
            self.fetcher.fetch(
                endpoint="/sdapi/v1/progress",
                use_cache=False,
                timeout_ms=1000,
                retries=1
            )

    @Slot(object, str)
    def _handle_progress_response(self, data, _):
        """
        Processes successful progress response from BaseFetcher.
        Emits progress signals and handles stall detection.
        """
        if not self._active:
            return

        progress = float(data.get("progress", 0.0))
        self.progressUpdated.emit(progress)
        self.progressData.emit(data)

        # if progress >= 1.0:
        #     self.completed.emit()
        #     self.stop_monitoring()
        # else:
        #     self._stall_timer.start()

        self._last_progress = progress

    @Slot(str, int, str)
    def _handle_progress_failure(self, error, code, _):
        """
        Handles fetch failure for /progress.
        Retries if error is not an auth issue.
        """
        if self._active and code not in (401, 403):
            self._poll()  # Retry immediately

    @Slot()
    def _handle_stall(self):
        """
        Emits stalled signal if no progress change is detected.
        Still attempts to re-poll to avoid getting stuck.
        """
        self.stalled.emit()
        if self._active:
            self._poll()


class StatusTracker(QObject):
    """
    Handles real-time progress updates from the Stable Diffusion API.
    Uses BaseFetcher internally but manages its own polling and state.

    Signals:
        progressUpdated (float): Emits progress value between 0.0 and 1.0.
        progressData (dict): Emits full progress response dictionary.
        stalled (): Emits if no progress is detected within stall timeout.
        completed (): Emits when progress reaches 1.0 and monitoring stops.
    """

    statusData = Signal(dict)
    stalled = Signal()
    completed = Signal()

    def __init__(self, base_fetcher: BaseFetcher, parent=None):
        super().__init__(parent)
        self.fetcher = base_fetcher
        self._poll_timer = QTimer(self)
        self._stall_timer = QTimer(self)
        self._active = False

        # Configure timers
        self._poll_timer.setInterval(1500)       # How often to poll the API
        self._stall_timer.setInterval(3000)     # Stall detection timeout
        self._poll_timer.timeout.connect(self._poll)
        self._stall_timer.timeout.connect(self._handle_stall)

        # Connect fetcher responses to local handlers
        self.fetcher.dataFetched.connect(self._handle_status_response)
        self.fetcher.fetchFailed.connect(self._handle_status_failure)

    def start_monitoring(self, interval_ms=500):
        """
        Begin polling for progress updates.
        Args:
            interval_ms (int): Interval between progress checks in milliseconds.
        """
        if not self._active:
            self._active = True
            self._poll_timer.setInterval(interval_ms)
            self._poll_timer.start()
            self._stall_timer.start()
            self._poll()  # Initial fetch

    def stop_monitoring(self):
        """
        Stop all polling and internal timers.
        """
        self._active = False
        self._poll_timer.stop()
        self._stall_timer.stop()

    @Slot()
    def _poll(self):
        """
        Internal: Triggers a fetch from the /progress endpoint.
        """
        if self._active:
            self.fetcher.fetch_status()

    @Slot(object, str)
    def _handle_status_response(self, data, _):
        """
        Processes successful progress response from BaseFetcher.
        Emits progress signals and handles stall detection.
        """
        if not self._active:
            return

        self.statusData.emit(data)

    @Slot(str, int, str)
    def _handle_status_failure(self, error, code, _):
        """
        Handles fetch failure for /progress.
        Retries if error is not an auth issue.
        """
        if self._active and code not in (401, 403):
            self._poll()  # Retry immediately

    @Slot()
    def _handle_stall(self):
        """
        Emits stalled signal if no progress change is detected.
        Still attempts to re-poll to avoid getting stuck.
        """
        self.stalled.emit()
        if self._active:
            self._poll()


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    fetcher = BaseFetcher()
    fetcher.dataFetched.connect(lambda data, uuid: print(f"Data fetched (UUID: {uuid}): {data}"))
    fetcher.fetchFailed.connect(lambda error, code, uuid: print(f"Fetch failed (UUID: {uuid}): {error} (Code: {code})"))
    fetcher.progressUpdated.connect(lambda received, total, uuid: print(f"Progress (UUID: {uuid}): {received}/{total}"))
    fetcher.serverAvailable.connect(lambda available: print(f"Server is {'available' if available else 'unavailable'}"))
    # fetcher.check_server()
    # fetcher.fetch_models()
    sys.exit(app.exec())
