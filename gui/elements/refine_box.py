from gui.common import GridFrame, ThemedToolButton
from gui.components import CheckBoxCard, ComboBoxCard, SliderCard, TextEditCard, DoubleSliderCard
from api import sd_api_manager
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
            parent=self
        )

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
            self.refine_negative_prompt
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

        sd_api_manager.sampler_fetched.connect(self.set_samplers)

    def get_payload(self) -> dict:
        """Returns the current payload of the refine box."""
        if not self.enable_refine_pass.isChecked():
            return {}
        return {

            # "hr_sampler_name": self.refine_samplers.currentText(),
            "refiner_start": self.refine_start.value(),
            "refiner_steps": self.refine_steps.value(),
            "refiner_prompt": self.refine_prompt.toPlainText(),
            "refiner_negative": self.refine_negative_prompt.toPlainText()
        }
    def set_payload(self, data: dict):
        """Sets the payload of the refine box."""
        if "hr_force" in data:
            self.force_hires.setChecked(data["hr_force"])
        if "hr_resize_mode" in data:
            self.resize_mode.setCurrentText(data["hr_resize_mode"])
        if "hr_steps" in data:
            self.hires_steps.setValue(data["hr_steps"])
        if "hr_scale" in data:
            self.strength.setValue(data["hr_scale"])
        if "denoising_strength" in data:
            self.strength.setValue(data["denoising_strength"])
        if "hr_upscaler" in data:
            self.resize_method.setCurrentText(data["hr_upscaler"])
        if "hr_second_pass_steps" in data:
            self.hires_steps.setValue(data["hr_second_pass_steps"])
        if "hr_resize_x" in data:
            self.resize_width.setValue(data["hr_resize_x"])
        if "hr_resize_y" in data:
            self.resize_height.setValue(data["hr_resize_y"])
        if "refine_start" in data:
            self.refine_start.setValue(data["refine_start"])
        if "refine_steps" in data:
            self.refine_steps.setValue(data["refine_steps"])
        if "refine_prompt" in data:
            self.refine_prompt.setPlainText(data["refine_prompt"])
        if "refine_negative" in data:
            self.refine_negative_prompt.setPlainText(data["refine_negative"])

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


