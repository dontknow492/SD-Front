from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PySide6.QtCore import QUrl, QByteArray, QObject, Signal, Slot, QTimer, QEventLoop
import json

class Txt2ImgPayloadBuilder:
    def __init__(self):
        # Default payload
        self.payload = {
            "prompt": "",
            "negative_prompt": "",
            "seed": -1,
            "subseed": -1,
            "subseed_strength": 0,
            "seed_resize_from_h": 0,
            "seed_resize_from_w": 0,
            "batch_size": 1,
            "n_iter": 1,
            "steps": 20,
            "clip_skip": None,
            "width": 512,
            "height": 512,
            "sampler_name": "Euler a",
            "hr_sampler_name": None,
            "eta": None,
            "cfg_scale": 7,
            "cfg_end": None,
            "diffusers_guidance_rescale": 0,
            "pag_scale": None,
            "pag_adaptive": None,
            "styles": [],
            "tiling": False,
            "vae_type": None,
            "hidiffusion": None,
            "do_not_reload_embeddings": False,
            "restore_faces": False,
            "detailer_enabled": False,
            "detailer_prompt": "",
            "detailer_negative": "",
            "detailer_steps": 0,
            "detailer_strength": 0,
            "hdr_mode": None,
            "hdr_brightness": 1,
            "hdr_color": 1,
            "hdr_sharpen": 1,
            "hdr_clamp": 1,
            "hdr_boundary": 0,
            "hdr_threshold": 1,
            "hdr_maximize": False,
            "hdr_max_center": 0,
            "hdr_max_boundry": 0,
            "hdr_color_picker": None,
            "hdr_tint_ratio": 0,
            "init_images": [],
            "resize_mode": 0,
            "resize_name": None,
            "resize_context": None,
            "denoising_strength": None,
            "image_cfg_scale": None,
            "initial_noise_multiplier": 1,
            "scale_by": 1,
            "selected_scale_tab": None,
            "mask": None,
            "latent_mask": None,
            "mask_for_overlay": None,
            "mask_blur": 4,
            "paste_to": None,
            "inpainting_fill": 0,
            "inpaint_full_res": True,
            "inpaint_full_res_padding": 0,
            "inpainting_mask_invert": 0,
            "overlay_images": [],
            "enable_hr": False,
            "firstphase_width": 0,
            "firstphase_height": 0,
            "hr_scale": 2,
            "hr_force": False,
            "hr_resize_mode": 0,
            "hr_resize_context": None,
            "hr_upscaler": None,
            "hr_second_pass_steps": 0,
            "hr_resize_x": 0,
            "hr_resize_y": 0,
            "hr_denoising_strength": None,
            "refiner_steps": None,
            "refiner_start": None,
            "refiner_prompt": None,
            "refiner_negative": None,
            "hr_refiner_start": None,
            "enhance_prompt": False,
            "do_not_save_samples": False,
            "do_not_save_grid": False,
            "script_args": [],
            "override_settings": {},
            "override_settings_restore_afterwards": True,
            "script_name": "",
            "alwayson_scripts": {},
            "ip_adapter": None,
            "face": None,
            "extra": None,
            "checkpoint": None,
            "vae": None
        }

    def set(self, key, value):
        """Update a payload field if it exists."""
        if key in self.payload:
            self.payload[key] = value
        else:
            raise KeyError(f"Field '{key}' not in payload")

    def get_payload(self):
        """Return full payload dictionary."""
        return self.payload

    def update(self, **kwargs):
        """Update multiple fields at once."""
        for key, value in kwargs.items():
            self.set(key, value)


class SDAPIHelper(QObject):
    def __init__(self, base_url="http://127.0.0.1:7860", parent=None):
        super().__init__(parent)
        self.base_url = base_url
        self.network_manager = QNetworkAccessManager(self)
        self.network_manager.finished.connect(self._on_request_finished)

    def get_styles(self):
        url = f"{self.base_url}/sdapi/v1/prompt-styles"
        request = QNetworkRequest(QUrl(url))
        self.network_manager.get(request)

    def _on_request_finished(self, reply):
        try:
            response_data = json.loads(bytes(reply.readAll().data()).decode('utf-8'))
            print("API Response:", response_data)
        except json.JSONDecodeError as e:
            print("Error decoding JSON:", e)
        except Exception as e:
            print("An error occurred:", e)

class StableDiffusionAPI(QObject):
    # Signals
    image_generated = Signal(str)  # emits base64 image string
    error_occurred = Signal(str)  # emits error message
    progress_updated = Signal(float, int, int, str)  # progress, current_step, total_steps, current_image_b64

    def __init__(self, base_url="http://127.0.0.1:7860", parent=None):
        super().__init__(parent)
        self.base_url = base_url
        self.network_manager = QNetworkAccessManager(self)
        self.network_manager.finished.connect(self._on_request_finished)
        self.progress_timer = QTimer(self)
        self.progress_timer.timeout.connect(self._check_progress)
        self.active_generation = False

    def generate_image(self, prompt: str, negative_prompt: str = "",
                       steps: int = 20, width: int = 512, height: int = 512):
        """Generate an image asynchronously using the Stable Diffusion API."""
        url = f"{self.base_url}/sdapi/v1/txt2img"

        payload = {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "steps": steps,
            "width": width,
            "height": height,
            "sampler_name": "Euler a"
        }

        request = QNetworkRequest(QUrl(url))
        request.setHeader(QNetworkRequest.ContentTypeHeader, "application/json")
        json_payload = QByteArray(json.dumps(payload).encode('utf-8'))

        self.active_generation = True
        self.progress_timer.start(500)  # Check progress every 500ms
        self.network_manager.post(request, json_payload)

    def _check_progress(self):
        """Check the current generation progress."""
        if not self.active_generation:
            self.progress_timer.stop()
            return

        url = f"{self.base_url}/sdapi/v1/progress"
        request = QNetworkRequest(QUrl(url))
        self.network_manager.get(request)

    @Slot(QNetworkReply)
    def _on_request_finished(self, reply):
        """Handle API responses."""
        try:
            url = reply.url().toString()
            response_data = json.loads(bytes(reply.readAll().data()).decode('utf-8'))

            if "sdapi/v1/progress" in url:
                # Handle progress response
                progress = response_data.get("progress", 0.0)
                state = response_data.get("state", {})
                step = state.get("sampling_step", 0)
                total_steps = state.get("sampling_steps", 0)
                current_image = response_data.get("current_image", "")

                self.progress_updated.emit(progress, step, total_steps, current_image)

                # Stop checking progress if generation is complete
                if progress >= 1.0:
                    self.active_generation = False
            elif "sdapi/v1/txt2img" in url:
                # Handle image generation response
                self.active_generation = False
                if "images" in response_data and response_data["images"]:
                    self.image_generated.emit(response_data["images"][0])
                else:
                    self.error_occurred.emit("No image returned from API")

        except json.JSONDecodeError:
            self.error_occurred.emit("Invalid JSON response from server")
        except Exception as e:
            self.error_occurred.emit(f"Unexpected error: {str(e)}")
        finally:
            reply.deleteLater()

    # Synchronous versions (optional)
    def generate_image_sync(self, *args, **kwargs):
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
        self.error_occurred.connect(on_error)

        self.generate_image(*args, **kwargs)
        loop.exec()

        self.image_generated.disconnect(on_success)
        self.error_occurred.disconnect(on_error)

        if error[0] is not None:
            raise error[0]
        return result[0]

    def get_progress_sync(self):
        """Synchronous version of progress check."""
        loop = QEventLoop()
        result = [None]

        def on_progress(progress, step, total_steps, current_image):
            result[0] = {
                'progress': progress,
                'current_step': step,
                'total_steps': total_steps,
                'current_image': current_image
            }
            loop.quit()

        self.progress_updated.connect(on_progress)
        self._check_progress()
        loop.exec()
        self.progress_updated.disconnect(on_progress)

        return result[0]