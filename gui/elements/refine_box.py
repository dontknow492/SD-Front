from gui.common import GridFrame, ThemedToolButton
from gui.components import CheckBoxCard, ComboBoxCard, SliderCard, TextEditCard, DoubleSliderCard
from api import sd_api_manager
from gui.elements.resize_box import ResizeBox
from qfluentwidgets import TogglePushButton

class RefineBox(GridFrame):
    def __init__(self, parent = None, spacing: int = 12, margins: tuple[int, int, int, int] = (8, 8, 8, 8)):
        super().__init__(parent, spacing, margins)
        self.setContentsMargins(0, 0, 0, 0)

        # Toggle to enable or disable refine pass
        self.enable_refine_pass = CheckBoxCard(
            "Enable Refine Pass",
            description="""Activate a secondary processing stage that carefully enhances details and cleans up artifacts.
            Recommended for:
            - Fixing minor imperfections
            - Adding subtle details
            - Improving overall coherence
            Note: Increases processing time but typically yields higher quality results""",
            show_info_on_focus=True,
            parent=self
        )

        self.force_hires = CheckBoxCard(
            "Force High Resolution",
            description="""Override automatic resolution detection to always output high-res images.
            Use when:
            - Source quality is poor but you need sharp output
            - You want maximum detail regardless of input
            - Working with specialized high-res models
            Warning: Significantly increases VRAM usage and processing time""",
            show_info_on_focus=True,
            parent=self
        )

        self.refine_samplers = ComboBoxCard(
            "Refinement Sampler",
            description="""Select the algorithm for quality enhancement:
            - Euler: Fast with decent quality (default)
            - DPM++: Balanced speed/quality
            - LMS: Best for smooth gradients
            - Heun: Highest quality but slow
            Tip: For faces, try DPM++ 2M Karras""",
            show_info_on_focus=True,
            parent=self
        )

        self.hires_steps = SliderCard(
            "High-Res Steps",
            description="""Control the refinement intensity in the high-res phase:
            10-20: Quick touch-up
            20-40: Good balance (recommended)
            40-60: High quality
            60+: Extreme quality (diminishing returns)
            Higher values reduce artifacts but increase render time""",
            show_info_on_focus=True,
            parent=self
        )
        self.hires_steps.set_range(0, 100)
        self.hires_steps.set_value(20)

        self.strength = DoubleSliderCard(
            "Refinement Strength",
            description="""Determine how much the refine pass modifies your image:
            0.1-0.3: Subtle polish
            0.4-0.6: Noticeable improvement (sweet spot)
            0.7-0.9: Strong enhancement
            1.0: Complete rework
            Adjust based on how much you want to preserve the original""",
            show_info_on_focus=True,
            parent=self
        )
        self.strength.set_range(0, 1, 2)
        self.strength.set_value(0.3)

        self.resize_mode = ComboBoxCard(
            "Resize Mode",
            description="""Choose how to handle aspect ratio changes:
            - Crop: Maintains proportions by trimming edges
            - Pad: Adds borders to fit dimensions
            - Stretch: Forces exact size (may distort)
            - Letterbox: Smart padding (recommended for video)
            Best practice: Use 'Crop' for social media, 'Letterbox' for print""",
            show_info_on_focus=True,
            parent=self
        )

        self.resize_method = ComboBoxCard(
            "Resize Method",
            description="""Select the scaling algorithm:
            - Lanczos: Sharpest for downscaling
            - Bicubic: Balanced quality
            - Bilinear: Fastest but blurry
            - Nearest: Pixel art preservation
            For AI work, Lanczos usually gives best results""",
            show_info_on_focus=True,
            parent=self
        )

        self.resize_width = SliderCard(
            "Resize Width",
            description="""Set output width in pixels:
            - 512-768: Fast generation
            - 768-1024: Standard quality
            - 1024-1536: High detail
            - 1536+: Professional grade
            Note: Width × Height affects VRAM usage exponentially""",
            show_info_on_focus=True,
            parent=self
        )
        self.resize_width.set_range(512, 8192)
        self.resize_width.set_value(512)

        self.resize_height = SliderCard(
            "Resize Height",
            description="""Set output height in pixels:
            - 512-768: Fast generation
            - 768-1024: Standard quality
            - 1024-1536: High detail
            - 1536+: Professional grade
            Maintain aspect ratio for best results""",
            show_info_on_focus=True,
            parent=self
        )
        self.resize_height.set_range(512, 8192)
        self.resize_height.set_value(512)

        self.refine_start = DoubleSliderCard(
            "Refinement Start Point",
            description="""When to begin refinement (as % of total process):
            20-40%: Early refinement (more creative changes)
            40-60%: Balanced approach (recommended)
            60-80%: Late refinement (preserves composition)
            Earlier starts allow more dramatic changes""",
            show_info_on_focus=True,
            parent=self
        )
        self.refine_start.set_range(0, 1, 2)
        self.refine_start.set_value(0.2)

        self.refine_steps = SliderCard(
            "Refinement Steps",
            description="""Dedicated processing steps for refinement:
            5-10: Quick polish
            10-20: Standard improvement
            20-30: Detailed enhancement
            30+: Ultra-refinement
            Allocate more steps for complex scenes""",
            show_info_on_focus=True,
            parent=self
        )
        self.refine_steps.set_range(0, 100)
        self.refine_steps.set_value(20)

        self.refine_prompt = TextEditCard(
            "Refinement Prompt",
            description="""Special instructions for the refine pass:
            Example: "4k textures, cinematic lighting, pore detail"
            Focus on:
            - Specific details to enhance
            - Style adjustments
            - Quality descriptors
            Keep concise (1-2 lines works best)""",
            placeholder="ultra-detailed, sharp focus, professional color grading",
            show_info_on_focus=True,
            parent=self
        )

        self.refine_negative_prompt = TextEditCard(
            "Refinement Exclusions",
            description="""What the refine pass should specifically avoid:
            Example: "blurry, noise, artifacts, over-saturation"
            Common uses:
            - Remove specific artifacts
            - Prevent over-processing
            - Maintain original characteristics
            Separate terms with commas""",
            placeholder="blurry, deformed, over-smoothed, jpeg artifacts",
            show_info_on_focus=True,
            parent=self
        )

        self.resize_box = ResizeBox(self)

        widgets = [
            self.enable_refine_pass,
            self.force_hires,
            self.refine_samplers,
            self.hires_steps,
            self.strength,
            self.resize_mode,
            self.resize_method,
            self.resize_width,
            self.resize_height,
            self.refine_start,
            self.refine_steps,
            self.refine_prompt,
            self.refine_negative_prompt,
            self.resize_box
        ]
        self.addWidget(self.enable_refine_pass)
        self.addWidget(self.force_hires)
        self.addWidget(self.refine_samplers)
        self.addWidget(self.hires_steps)
        self.addFullWidthWidget(self.strength)
        self.addWidget(self.resize_mode)
        self.addWidget(self.resize_method)
        self.addWidget(self.resize_width)
        self.addWidget(self.resize_height)
        self.addWidget(self.refine_start)
        self.addWidget(self.refine_steps)
        self.addFullWidthWidget(self.refine_prompt)
        self.addFullWidthWidget(self.refine_negative_prompt)
        self.addFullWidthWidget(self.resize_box)

        sd_api_manager.sampler_fetched.connect(self.set_samplers)

    def get_payload(self) -> dict:
        """Returns the current payload of the refine box."""
        if not self.enable_refine_pass.isChecked():
            return {}
        return {
            # "hr_sampler_name": self.refine_samplers.currentText(),
            "hr_force": self.force_hires.isChecked(),
            "hr_second_pass_steps": self.hires_steps.value(),
            "hr_sampler_name": self.refine_samplers.currentText(),
            "hr_resize_x": self.resize_box.getWidth(),
            "hr_resize_y": self.resize_box.getHeight(),
            "hr_resize_mode": self.resize_mode.currentText(),
            "hr_upscaler": self.resize_method.currentText(),
            "refiner_start": self.refine_start.value(),
            "refiner_steps": self.refine_steps.value(),
            "refiner_prompt": self.refine_prompt.toPlainText(),
            "refiner_negative": self.refine_negative_prompt.toPlainText()
        }
    def set_payload(self, data: dict):
        """Sets the payload of the refine box."""
        self.refine_start.setValue(data.get("refiner_start", self.refine_start.value()))
        self.refine_steps.setValue(data.get("refiner_steps", self.refine_steps.value()))
        self.refine_prompt.setPlainText(data.get("refiner_prompt", self.refine_prompt.toPlainText()))
        self.refine_negative_prompt.setPlainText(data.get("refiner_negative", self.refine_negative_prompt.toPlainText()))

    def set_samplers(self, samplers: list[dict]):
        self.refine_samplers.clear()
        sampler = samplers[0]
        for sampler in samplers:
            self.refine_samplers.addItem(sampler["name"])
        self.refine_samplers.setCurrentText(sampler["name"])

if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication, QWidget
    app = QApplication([])
    window = RefineBox(None, 6)
    window.set_payload({
        "hr_force": True,
        "hr_resize_mode": "Crop",
        "hr_steps": 20,
        "hr_scale": 0.3,
        "denoising_strength": 0.3,
        "hr_upscaler": "Lanczos",
        "hr_second_pass_steps": 20,
        "hr_resize_x": 512,
        "hr_resize_y": 512,
        "refine_start": 0.2,
        "refine_steps": 20,
        "refine_prompt": "4k textures, cinematic lighting, pore detail",
        "refine_negative": "blurry, deformed, over-smoothed, jpeg artifacts"
    })
    print(window.get_payload())
    window.show()
    app.exec()


