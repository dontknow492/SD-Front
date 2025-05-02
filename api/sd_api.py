import json

from PySide6.QtCore import Signal, QObject, QEventLoop, Slot, QByteArray, QUrl, QTimer
from PySide6.QtNetwork import QNetworkReply, QNetworkRequest, QNetworkAccessManager

from api.fetcher import *


class StableDiffusionAPI(QObject):
    # Samplers
    sampler_fetched = Signal(list)
    sampler_fetch_error = Signal(str, int)

    # Checkpoints
    checkpoint_fetched = Signal(list)
    checkpoint_fetch_error = Signal(str, int)

    # Embeddings
    embedding_fetched = Signal(list)
    embedding_fetch_error = Signal(str, int)

    # Hypernetworks
    hypernetwork_fetched = Signal(list)
    hypernetwork_fetch_error = Signal(str, int)

    # LoRA
    lora_fetched = Signal(list)
    lora_fetch_error = Signal(str, int)

    # Styles
    style_fetched = Signal(list)
    style_fetch_error = Signal(str, int)

    # Upscalers
    upscaler_fetched = Signal(list)
    upscaler_fetch_error = Signal(str, int)

    # VAE
    vae_fetched = Signal(list)
    vae_fetch_error = Signal(str, int)

    #img
    image_progress_updated = Signal(dict)
    image_generated = Signal(dict)
    image_generation_error = Signal(str)

    def __init__(self, base_url="http://127.0.0.1:7860", parent=None):
        super().__init__(parent)

        self.base_url = base_url
        self.network_manager = QNetworkAccessManager(self)
        self.network_manager.finished.connect(self._on_request_finished)
        self.progress_timer = QTimer(self)
        self.progress_timer.timeout.connect(self._check_progress)
        self.active_generation = False

        self.cache_limit = 100 * 1024 * 1024
        self.auth_token = None

        self.progress_fetcher = ProgressFetcher(base_url)
        self.progress_fetcher.dataFetched.connect(self.on_progress_updated)
        self.progress_update_time = 500
        self.sampler_fetcher = SamplerFetcher(base_url, self.auth_token, self.cache_limit, self)
        self.checkpoint_fetcher = ModelFetcher(base_url, self.auth_token, self.cache_limit, self)
        self.embedding_fetcher = EmbeddingFetcher(base_url, self.auth_token, self.cache_limit, self)
        self.hypernetwork_fetcher = HypernetworkFetcher(base_url, self.auth_token, self.cache_limit, self)
        self.lora_fetcher = LoraFetcher(base_url, self.auth_token, self.cache_limit, self)
        self.style_fetcher = StyleFetcher(base_url, self.auth_token, self.cache_limit, self)
        self.upscaler_fetcher = UpscalerFetcher(base_url, self.auth_token, self.cache_limit, self)
        self.vae_fetcher = VaeFetcher(base_url, self.auth_token, self.cache_limit, self)

        #generator
        self._fetcher_signal_listener()


    def _fetcher_signal_listener(self):
        # Sampler
        self.sampler_fetcher.dataFetched.connect(self.sampler_fetched)
        self.sampler_fetcher.fetchFailed.connect(self.sampler_fetch_error)

        # Checkpoint
        self.checkpoint_fetcher.dataFetched.connect(self.checkpoint_fetched)
        self.checkpoint_fetcher.fetchFailed.connect(self.checkpoint_fetch_error)

        # Embedding
        self.embedding_fetcher.dataFetched.connect(self.embedding_fetched)
        self.embedding_fetcher.fetchFailed.connect(self.embedding_fetch_error)

        # Hypernetwork
        self.hypernetwork_fetcher.dataFetched.connect(self.hypernetwork_fetched)
        self.hypernetwork_fetcher.fetchFailed.connect(self.hypernetwork_fetch_error)

        # LoRA
        self.lora_fetcher.dataFetched.connect(self.lora_fetched)
        self.lora_fetcher.fetchFailed.connect(self.lora_fetch_error)

        # Styles
        self.style_fetcher.dataFetched.connect(self.style_fetched)
        self.style_fetcher.fetchFailed.connect(self.style_fetch_error)

        # Upscaler
        self.upscaler_fetcher.dataFetched.connect(self.upscaler_fetched)
        self.upscaler_fetcher.fetchFailed.connect(self.upscaler_fetch_error)

        # VAE
        self.vae_fetcher.dataFetched.connect(self.vae_fetched)
        self.vae_fetcher.fetchFailed.connect(self.vae_fetch_error)

    def fetch_style(self):
        self.style_fetcher.fetch()

    def fetch_upscaler(self):
        self.upscaler_fetcher.fetch()

    def fetch_vae(self):
        self.vae_fetcher.fetch()

    def fetch_sampler(self):
        self.sampler_fetcher.fetch()

    def fetch_model(self):
        self.checkpoint_fetcher.fetch()

    def fetch_embedding(self):
        self.embedding_fetcher.fetch()

    def fetch_hypernetwork(self):
        self.hypernetwork_fetcher.fetch()

    def fetch_lora(self):
        self.lora_fetcher.fetch()


    #generate helper
    def generate_txt_image(self, payload: dict):
        self.generate_image(payload, endpoint="txt2img")

    def generate_img2img_image(self, payload: dict):
        self.generate_image(payload, endpoint="img2img")

    #generate image
    def generate_image(self, payload: dict, endpoint: str = "txt2img"):
        """Generate an image asynchronously using the specified SD API endpoint."""
        url = f"{self.base_url}/sdapi/v1/{endpoint}"
        request = QNetworkRequest(QUrl(url))
        request.setHeader(QNetworkRequest.ContentTypeHeader, "application/json")
        json_payload = QByteArray(json.dumps(payload).encode('utf-8'))

        self.active_generation = True
        self.progress_timer.start(self.progress_update_time)
        self.network_manager.post(request, json_payload)

    def _check_progress(self):
        """Check the current generation progress."""
        if not self.active_generation:
            self.progress_timer.stop()
            return

        self.progress_fetcher.fetch(force_fetch=True)

    def on_progress_updated(self, data):
        """Handle progress updates."""

        progress = data.get("progress", 0.0)

        # Stop checking progress if generation is complete
        if progress >= 1.0 or not self.active_generation:
            self.active_generation = False
        else:
            self.image_progress_updated.emit(data)


    @Slot(QNetworkReply)
    def _on_request_finished(self, reply):
        """Handle API responses."""
        try:
            url = reply.url().toString()
            response_data = json.loads(bytes(reply.readAll().data()).decode('utf-8'))
            if "sdapi/v1/txt2img" in url:
                # Handle image generation response
                self.active_generation = False
                if "images" in response_data and response_data["images"]:
                    self.image_generated.emit(response_data)
                else:
                    self.image_generation_error.emit("No image returned from API")

        except json.JSONDecodeError:
            self.image_generation_error.emit("Invalid JSON response from server")
        except Exception as e:
            self.image_generation_error.emit(f"Unexpected error: {str(e)}")
        finally:
            reply.deleteLater()

    # Synchronous versions
    def generate_sync(self, payload: dict, endpoint: str):
        """Synchronous version that blocks until response is received."""
        loop = QEventLoop()
        result = [None]
        error = [None]

        def on_success(img_data):
            result[0] = img_data
            loop.quit()

        def on_error(err_msg):
            error[0] = ValueError(err_msg)
            loop.quit()

        self.image_generated.connect(on_success)
        self.image_generation_error.connect(on_error)

        self.generate_image(payload, endpoint=endpoint)
        loop.exec()

        self.image_generated.disconnect(on_success)
        self.image_generation_error.disconnect(on_error)

        if error[0] is not None:
            raise error[0]
        return result[0]


api_manager = StableDiffusionAPI()

if __name__ ==  "__main__":
    from PySide6.QtWidgets import QApplication
    app = QApplication([])
    payload = {
        "prompt": "a cat",
        "steps": 10,
        "width": 512,
        "height": 512,
    }
    # api_manager.generate_txt_image(payload)
    api_manager.generate_txt_image(payload)

    app.exec()