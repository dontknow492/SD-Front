from typing import Dict, Any
from PySide6.QtCore import Signal, QObject, Slot, Qt
from loguru import logger

from api.generator import ImageGenerator
from api.fetcher import ProgressTracker, BaseFetcher


class StableDiffusionAPI(QObject):
    # Success signals
    sampler_fetched = Signal(list)
    checkpoint_fetched = Signal(list)
    embedding_fetched = Signal(list)
    hypernetwork_fetched = Signal(list)
    lora_fetched = Signal(list)
    style_fetched = Signal(list)
    upscaler_fetched = Signal(list)
    vae_fetched = Signal(list)

    # Error signals
    sampler_fetch_error = Signal(str, int)
    checkpoint_fetch_error = Signal(str, int)
    embedding_fetch_error = Signal(str, int)
    hypernetwork_fetch_error = Signal(str, int)
    lora_fetch_error = Signal(str, int)
    style_fetch_error = Signal(str, int)
    upscaler_fetch_error = Signal(str, int)
    vae_fetch_error = Signal(str, int)

    #img
    image_progress_updated = Signal(dict)
    image_generated = Signal(dict)
    image_generation_error = Signal(str, int)

    #message
    messageSignal = Signal(str, str) #lvl, msg

    # Operation signals
    models_refreshed = Signal()
    loras_refreshed = Signal()
    server_status_changed = Signal(bool)  # True when available

    def __init__(self, base_url="http://127.0.0.1:7860", parent=None):
        super().__init__(parent)

        self.base_url = base_url
        self.cache_limit = 100 * 1024 * 1024
        self.auth_token = None
        self.image_generator = ImageGenerator(base_url, self)
        self.info_fetcher = BaseFetcher(base_url, self.auth_token, self.cache_limit, self)
        self.progress_tracker = ProgressTracker(self.info_fetcher)
        self.active_generation = False

        self._signal_mapping()

    def _signal_mapping(self):
        #image
        self.image_generator.generation_failed.connect(self.image_generation_error.emit)
        self.image_generator.generation_failed.connect(lambda : self._on_generation_finished())
        self.image_generator.generation_completed.connect(self.image_generated.emit)
        self.image_generator.generation_completed.connect(lambda : self._on_generation_finished())
        self.image_generator.generation_started.connect(self.gen_started)
        #progress
        self.progress_tracker.progressData.connect(self.image_progress_updated.emit)
        #fetcher
        self.info_fetcher.dataFetched.connect(self._handle_response)
        self.info_fetcher.fetchFailed.connect(self._handle_error)
        self.info_fetcher.serverAvailable.connect(self.server_status_changed)


        # === Public API Methods ===
    @property
    def url(self):
        return self.base_url

    @url.setter
    def url(self, url):
        self.base_url = url

    @Slot()
    def refresh_models(self):
        """Force refresh of model list"""
        self.info_fetcher.refresh_models()
        self.info_fetcher.dataFetched.connect(
            lambda _, uuid: self.models_refreshed.emit(),
            Qt.ConnectionType.SingleShotConnection)

    @Slot()
    def refresh_loras(self):
        """Force refresh of LoRA list"""
        self.info_fetcher.refresh_loras()
        self.info_fetcher.dataFetched.connect(
            lambda _, uuid: self.loras_refreshed.emit(),
            Qt.ConnectionType.SingleShotConnection)

    @Slot()
    def fetch_all_resources(self):
        """Pre-fetch all common resources"""
        self.get_models()
        self.get_vaes()
        self.get_embeddings()
        self.get_loras()
        self.get_styles()

    @Slot()
    def check_server_status(self):
        """Check if the server is available"""
        self.info_fetcher.check_server()

    @Slot()
    def get_models(self):
        """Fetch available models"""
        uuid = self.info_fetcher.fetch_models()
        self._pending_requests[uuid] = 'models'

    @Slot()
    def get_vaes(self):
        """Fetch available VAEs"""
        uuid = self.info_fetcher.fetch_vaes()
        self._pending_requests[uuid] = 'vaes'

    @Slot()
    def get_embeddings(self):
        """Fetch loaded embeddings"""
        uuid = self.info_fetcher.fetch_embeddings()
        self._pending_requests[uuid] = 'embeddings'

    @Slot()
    def get_loras(self):
        """Fetch available LoRAs"""
        uuid = self.info_fetcher.fetch_loras()
        self._pending_requests[uuid] = 'loras'

    @Slot()
    def get_styles(self):
        """Fetch prompt styles"""
        uuid = self.info_fetcher.fetch_styles()
        self._pending_requests[uuid] = 'styles'

    @Slot()
    def get_upscalers(self):
        """Fetch available upscalers"""
        uuid = self.info_fetcher.fetch_upscalers()
        self._pending_requests[uuid] = 'upscalers'

    @Slot()
    def get_samplers(self):
        """Fetch available samplers"""
        uuid = self.info_fetcher.fetch_samplers()
        self._pending_requests[uuid] = 'samplers'

    @Slot(int)
    def start_progress_monitoring(self, interval_ms=500):
        """Begin tracking generation progress"""
        self.progress_tracker.start_monitoring(interval_ms)

    @Slot()
    def stop_progress_monitoring(self):
        """Stop progress updates"""
        self.progress_tracker.stop_monitoring()

    @Slot()
    def _on_generation_finished(self):
        self.active_generation = False
        self.progress_tracker.stop_monitoring()

    # === Internal Handlers ===
    def _handle_response(self, data: Dict[str, Any], request_uuid: str):
        """Route successful responses to appropriate signals"""
        endpoint = self._pending_requests.pop(request_uuid, None)

        if not endpoint:
            return

        if endpoint == 'models':
            self.checkpoint_fetched.emit(data)
        elif endpoint == 'vaes':
            self.vae_fetched.emit(data)
        elif endpoint == 'embeddings':
            self.embedding_fetched.emit(data)
        elif endpoint == 'loras':
            self.lora_fetched.emit(data)
        elif endpoint == 'styles':
            self.style_fetched.emit(data)
        elif endpoint == 'upscalers':
            self.upscaler_fetched.emit(data)
        elif endpoint  == 'samplers':
            self.sampler_fetched.emit(data)

    def _handle_error(self, error_msg: str, status_code: int, request_uuid: str):
        """Route errors to appropriate signals"""
        endpoint = self._pending_requests.pop(request_uuid, None)

        if not endpoint:
            return

        if endpoint == 'models':
            self.checkpoint_fetch_error.emit(error_msg, status_code)
        elif endpoint == 'vaes':
            self.vae_fetch_error.emit(error_msg, status_code)
        elif endpoint == 'embeddings':
            self.embedding_fetch_error.emit(error_msg, status_code)
        elif endpoint == 'loras':
            self.lora_fetch_error.emit(error_msg, status_code)
        elif endpoint == 'styles':
            self.style_fetch_error.emit(error_msg, status_code)
        elif endpoint == 'upscalers':
            self.upscaler_fetch_error.emit(error_msg, status_code)
        elif endpoint == 'samplers':
            self.sampler_fetch_error.emit(error_msg, status_code)

    #generate helper
    def generate_txt_image(self, payload: dict):
        if self.gen_status:
            logger.info("Generation already in progress")
            return
        self.image_generator.txt2img(payload)

    def generate_img2img_image(self, payload: dict):
        if self.gen_status:
            logger.info("Generation already in progress")
            return
        self.image_generator.img2img(payload)

    # Synchronous versions
    def generate_sync(self, payload: dict, endpoint: str):
        """Synchronous version that blocks until response is received."""
        self.image_generator.generate_sync(payload, endpoint)

    def gen_started(self):
        self.active_generation = True
        self.progress_tracker.start_monitoring()

    @property
    def gen_status(self):
        return self.active_generation

    @property
    def _pending_requests(self) -> Dict[str, str]:
        """Lazy initialization of request tracking dict"""
        if not hasattr(self, '_internal_pending'):
            self._internal_pending = {}
        return self._internal_pending

    def close(self):
        self.info_fetcher.cancel()
        self.progress_tracker.stop_monitoring()


sd_api_manager = StableDiffusionAPI()

if __name__ ==  "__main__":
    from PySide6.QtWidgets import QApplication
    app = QApplication([])
    payload = {
        "prompt": "a cat",
        "steps": 10,
        "width": 512,
        "height": 512,
    }
    # sd_api_manager.generate_txt_image(payload)
    sd_api_manager.image_progress_updated.connect(lambda data: print(data.keys()))
    sd_api_manager.style_fetched.connect(lambda data: print(len(data)))
    sd_api_manager.get_styles()
    app.exec()