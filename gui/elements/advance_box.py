from gui.common import GridFrame, ThemedToolButton
from gui.components import CheckBoxCard, ComboBoxCard, SliderCard, TextEditCard, DoubleSliderCard
from qfluentwidgets import TogglePushButton


class AdvanceBox(GridFrame):
    def __init__(self, parent = None, spacing: int = 12, margins: tuple[int, int, int, int] = (8, 8, 8, 8)):
        super().__init__(parent, spacing, margins)
        self.setContentsMargins(0, 0, 0, 0)

        self.vae_type = ComboBoxCard(
            "VAE Type",
            description="""Choose the Variational Autoencoder type:
            - Auto: Automatically selects the best VAE for your model (recommended)
            - Custom: Manually specify a VAE file (for specialized models)
            - None: Bypass VAE processing (faster but lower quality)

            Note: Using the correct VAE significantly impacts color accuracy and detail""",
            show_info_on_focus=True,
            parent=self
        )

        self.enable_texture_tiling = CheckBoxCard(
            "Texture Tiling",
            description="""Enable for tileable/texture creation:
            ✓ Enabled: Creates repeatable patterns (ideal for textures/materials)
            ✗ Disabled: Standard image generation

            Tip: Essential for game textures, wallpaper designs, or any tiled content""",
            show_info_on_focus=True,
            parent=self
        )

        self.enable_hi_diffusion = CheckBoxCard(
            "High-Frequency Diffusion",
            description="""Enable for enhanced detail generation:
            ✓ Enabled: Better fine details and textures (recommended for high-res)
            ✗ Disabled: Smoother but less detailed results

            Warning: Increases VRAM usage by ~15%""",
            show_info_on_focus=True,
            parent=self
        )

        self.guidance_scale = SliderCard(
            "Guidance Scale",
            description="""Controls how strictly the AI follows your text prompt:
            7-10: Strict interpretation (good for precise concepts)
            5-7: Balanced creativity (recommended default)
            3-5: Loose interpretation (more artistic freedom)
            <3: Highly unpredictable

            Note: Values above 10 often cause artifacts""",
            show_info_on_focus=True,
            parent=self
        )
        self.guidance_scale.set_range(0, 30)
        self.guidance_scale.setValue(6)

        self.guidance_end = DoubleSliderCard(
            "Guidance End",
            description="""When to stop applying prompt guidance (as % of total steps):
            0.8-1.0: Full duration (maximum prompt adherence)
            0.6-0.8: Balanced (recommended for most cases)
            0.4-0.6: Early release (allows more AI creativity)
            <0.4: Minimal guidance

            Use lower values for more artistic freedom""",
            show_info_on_focus=True,
            parent=self
        )
        self.guidance_end.set_range(0, 1, 2)
        self.guidance_end.set_value(1)

        self.refine_guidance_scale = SliderCard(
            "Refine Guidance Scale",
            description="""How strongly refinement follows your enhance prompt:
            5-7: Strong refinement (recommended for detail work)
            3-5: Moderate refinement
            1-3: Subtle tweaks only

            Tip: Use higher values when your refine prompt specifies exact details""",
            show_info_on_focus=True,
            parent=self
        )
        self.refine_guidance_scale.set_range(0, 30)
        self.refine_guidance_scale.setValue(6)

        self.rescale_guidance = DoubleSliderCard(
            "Rescale Guidance",
            description="""Automatically adjusts prompt strength during generation:
            0.0: No rescaling (constant strength)
            0.3-0.5: Moderate adjustment (recommended)
            0.5-0.7: Aggressive dynamic scaling

            Helps prevent over-processing in later stages""",
            show_info_on_focus=True,
            parent=self
        )
        self.rescale_guidance.set_range(0, 1, 2)
        self.rescale_guidance.set_value(0)

        self.attention_guidance = DoubleSliderCard(
            "Attention Guidance",
            description="""How much the AI focuses on prompt keywords:
            0.3-0.5: Balanced attention (recommended)
            0.5-0.7: Strong keyword focus
            0.7-1.0: May over-emphasize specific terms

            Lower values create more balanced compositions""",
            show_info_on_focus=True,
            parent=self
        )
        self.attention_guidance.set_range(0, 1, 2)
        self.attention_guidance.set_value(0)

        self.adaptive_scaling = DoubleSliderCard(
            "Adaptive Scaling",
            description="""Automatically optimizes guidance per generation step:
            0.4-0.6: Moderate adaptation (recommended)
            0.6-0.8: Strong adaptation (good for complex prompts)
            0.8-1.0: May cause instability

            Helps maintain consistency in long generations""",
            show_info_on_focus=True,
            parent=self
        )
        self.adaptive_scaling.set_range(0, 1, 2)
        self.adaptive_scaling.set_value(0.5)

        self.clip_skip = DoubleSliderCard(
            "CLIP Layer Skipping",
            description="""How many CLIP neural network layers to bypass:
            1: Full processing (most accurate)
            2: Recommended balance of speed/quality
            3-4: Faster but may misinterpret prompts

            Higher values can create more stylized results""",
            show_info_on_focus=True,
            parent=self
        )
        self.clip_skip.set_range(0, 12, 1)
        self.clip_skip.setValue(1)

        self.addFullWidthWidget(self.vae_type)

        self.addWidget(self.enable_texture_tiling)
        self.addWidget(self.enable_hi_diffusion)
        self.addWidget(self.guidance_scale)
        self.addWidget(self.guidance_end)
        self.addWidget(self.refine_guidance_scale)
        self.addWidget(self.rescale_guidance)
        self.addWidget(self.attention_guidance)
        self.addWidget(self.adaptive_scaling)

        self.addFullWidthWidget(self.clip_skip)

    def get_payload(self) -> dict:
        """Returns current values from the UI as a dict."""
        return {
            "vae_type": self.vae_type.currentText(),  # or `.value()` if custom
            "tiling": self.enable_texture_tiling.isChecked(),
            "hidiffusion": self.enable_hi_diffusion.isChecked(),
            "cfg_scale": self.guidance_scale.value(),
            "cfg_end": self.guidance_end.value(),  # assuming DoubleSliderCard has .value()
            "refiner_steps": self.refine_guidance_scale.value(),
            "diffusers_guidance_rescale": self.rescale_guidance.value(),
            "pag_scale": self.attention_guidance.value(),
            "pag_adaptive": self.adaptive_scaling.value(),
            "clip_skip": self.clip_skip.value()
        }

    def set_payload(self, payload: dict):
        """Populates the UI from a dict."""
        if not isinstance(payload, dict):
            return

        self.vae_type.setCurrentText(payload.get("vae_type", self.vae_type.currentText()))
        self.enable_texture_tiling.setChecked(payload.get("tiling", self.enable_texture_tiling.isChecked()))
        self.enable_hi_diffusion.setChecked(payload.get("hidiffusion", self.enable_hi_diffusion.isChecked()))
        self.guidance_scale.set_value(payload.get("cfg_scale", self.guidance_scale.value()))
        self.guidance_end.set_value(payload.get("cfg_end", self.guidance_end.value()))
        self.refine_guidance_scale.set_value(payload.get("refiner_steps", self.refine_guidance_scale.value()))
        self.rescale_guidance.set_value(payload.get("diffusers_guidance_rescale", self.rescale_guidance.value()))
        self.attention_guidance.set_value(payload.get("pag_scale", self.attention_guidance.value()))
        self.adaptive_scaling.set_value(payload.get("pag_adaptive", self.adaptive_scaling.value()))
        self.clip_skip.set_value(payload.get("clip_skip", self.clip_skip.value()))

if __name__  == "__main__":
    from PySide6.QtWidgets import QApplication, QWidget
    app = QApplication([])
    window = AdvanceBox()
    window.show()
    # window.set_payload({
    #     "vae_type": "Auto",
    #     "tiling": True,
    #     "hidiffusion": True,
    #     "cfg_scale": 7,
    #     "cfg_end": 0.8,
    #     "refiner_steps": 5,
    #     "diffusers_guidance_rescale": 0.6,
    #     "pag_scale": 0.5,
    #     "pag_adaptive": 0.8,
    #     "clip_skip": 2
    # })
    # print(window.get_payload())
    app.exec()