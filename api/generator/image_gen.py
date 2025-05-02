import json
from typing import Dict, Any, Optional

from PySide6.QtCore import QObject, QEventLoop, Slot, QByteArray, QUrl, Signal
from PySide6.QtNetwork import QNetworkReply, QNetworkRequest, QNetworkAccessManager


class ImageGenerator(QObject):
    """
    Handles core image generation functionality for Stable Diffusion API.
    Designed to work with a separate ProgressTracker class.
    """

    # Signals
    generation_started = Signal(str)  # endpoint name
    generation_completed = Signal(dict)  # full response
    generation_failed = Signal(str, int)  # error message, status code

    # Specialized completion signals
    txt2img_completed = Signal(dict)
    img2img_completed = Signal(dict)

    def __init__(self, base_url: str = "http://127.0.0.1:7860", parent=None):
        super().__init__(parent)
        self.base_url = base_url.rstrip('/')
        self._setup_network()

    def _setup_network(self):
        """Initialize network components"""
        self.network_manager = QNetworkAccessManager(self)
        self.network_manager.finished.connect(self._handle_response)

    # Public API
    def txt2img(self, payload: Dict[str, Any]) -> bool:
        """Start text-to-image generation asynchronously."""
        return self._generate(payload, "txt2img")

    def img2img(self, payload: Dict[str, Any]) -> bool:
        """Start image-to-image generation asynchronously."""
        return self._generate(payload, "img2img")

    def generate_sync(self, payload: Dict[str, Any], endpoint: str = "txt2img") -> Dict[str, Any]:
        """
        Synchronous generation that blocks until completion.

        Args:
            payload: Generation parameters
            endpoint: Either 'txt2img' or 'img2img'

        Returns:
            The API response dictionary

        Raises:
            RuntimeError: If generation fails
        """
        loop = QEventLoop()
        result = [None]
        error = [None]

        def on_success(data):
            result[0] = data
            loop.quit()

        def on_failure(msg, code):
            error[0] = RuntimeError(f"{msg} (code: {code})")
            loop.quit()

        self.generation_completed.connect(on_success, Qt.DirectConnection)
        self.generation_failed.connect(on_failure, Qt.DirectConnection)

        if not self._generate(payload, endpoint):
            raise RuntimeError("Failed to start generation")

        loop.exec()

        self.generation_completed.disconnect(on_success)
        self.generation_failed.disconnect(on_failure)

        if error[0]:
            raise error[0]
        return result[0]

    # Core generation
    def _generate(self, payload: Dict[str, Any], endpoint: str) -> bool:
        """Internal method to initiate generation request."""
        url = QUrl(f"{self.base_url}/sdapi/v1/{endpoint}")
        request = QNetworkRequest(url)
        request.setHeader(QNetworkRequest.ContentTypeHeader, "application/json")

        try:
            json_data = json.dumps(payload).encode('utf-8')
            self.network_manager.post(request, QByteArray(json_data))
            self.generation_started.emit(endpoint)
            return True
        except Exception as e:
            self.generation_failed.emit(f"Request failed: {str(e)}", 0)
            return False

    # Response handling
    @Slot(QNetworkReply)
    def _handle_response(self, reply: QNetworkReply):
        """Handle API responses."""
        try:
            if reply.error() != QNetworkReply.NoError:
                status_code = reply.attribute(QNetworkRequest.HttpStatusCodeAttribute) or 0
                self.generation_failed.emit(reply.errorString(), status_code)
                return

            response = json.loads(bytes(reply.readAll().data()).decode('utf-8'))
            endpoint = reply.url().path().split('/')[-1]

            self.generation_completed.emit(response)

            if endpoint == "txt2img":
                self.txt2img_completed.emit(response)
            elif endpoint == "img2img":
                self.img2img_completed.emit(response)

        except json.JSONDecodeError:
            self.generation_failed.emit("Invalid JSON response", 500)
        except Exception as e:
            self.generation_failed.emit(f"Processing error: {str(e)}", 0)
        finally:
            reply.deleteLater()

    # def cancel_generation(self):
        """Cancel any ongoing generation."""
        # self.network_manager.


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication

    app = QApplication([])

    generator = ImageGenerator()

    # Example usage
    generator.txt2img_completed.connect(
        lambda r: print("Generation complete!", r["images"][0][:20] + "...")
    )

    payload = {
        "prompt": "a cute cat",
        "steps": 20,
        "width": 512,
        "height": 512
    }
    generator.txt2img(payload)

    app.exec()