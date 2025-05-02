from gui.common import GridFrame, ThemedToolButton
from gui.components import CheckBoxCard, ComboBoxCard, SliderCard, TextEditCard, DoubleSliderCard
from qfluentwidgets import TogglePushButton

class DetailerBox(GridFrame):
    def __init__(self, parent=None, spacing: int = 12, margins: tuple[int, int, int, int] = (8, 8, 8, 8)):
        super().__init__(parent, spacing, margins)

        self.enable_detailer = CheckBoxCard(
            "Enable Detailer",
            description="""Activate this to enable the detail enhancement processor.
            When enabled, the system will apply additional processing to refine image details
            based on the parameters below.""",
            parent=self
        )

        self.detailer_classes = TextEditCard(
            "Target Classes",
            description="""Specify which object classes should receive detail enhancement.
            Enter one class per line (e.g., 'face', 'hand', 'text').
            Leave empty to process all detectable classes.""",
            placeholder="face\nhand\ntext",
            parent=self
        )

        self.detailer_prompt = TextEditCard(
            "Enhancement Prompt",
            description="""Guide the detailer with specific instructions about what to enhance.
            Example: 'high detail skin pores, sharp eyes, detailed hair strands'
            The more specific your prompt, the better the results.""",
            placeholder="high detail skin, sharp facial features",
            parent=self
        )

        self.detailer_negative_prompt = TextEditCard(
            "Negative Prompt",
            description="""Specify what artifacts to avoid during enhancement.
            Example: 'blurry, over-smoothed, plastic look, distorted features'
            Helps prevent common enhancement artifacts.""",
            placeholder="blurry, over-smoothed, distorted",
            parent=self
        )

        self.detailer_strength = DoubleSliderCard(
            "Strength",
            description="""Control how aggressively details are enhanced.
            Lower values (0.1-0.3): Subtle refinement
            Medium values (0.4-0.7): Noticeable improvement
            High values (0.8-1.0): Dramatic enhancement (may introduce artifacts)""",
            parent=self
        )
        self.detailer_strength.set_range(0.1, 1.0, 2)
        self.detailer_strength.set_value(0.3)

        self.detailer_step = SliderCard(
            "Steps",
            description="""Number of refinement iterations (quality vs speed trade-off).
            10-20 steps: Fast but basic
            20-40 steps: Balanced quality
            40+ steps: Highest quality (slowest)""",
            parent=self
        )
        self.detailer_step.set_range(0, 100)
        self.detailer_step.set_value(10)

        self.max_detect = SliderCard(
            "Maximum Detections",
            description="""Limit how many objects get processed in one image.
            Helps manage processing time in complex scenes.
            Lower values prioritize the most prominent objects.""",
            parent=self
        )
        self.max_detect.set_range(0, 10)
        self.max_detect.set_value(2)

        self.edge_padding = SliderCard(
            "Detection Padding",
            description="""ExtraInterface margin around detected objects (in pixels).
            Prevents cropping too tightly around edges.
            Increase if details near edges are being clipped.""",
            parent=self
        )
        self.edge_padding.set_range(0, 100)
        self.edge_padding.set_value(20)

        self.edge_blur = SliderCard(
            "Edge Blur",
            description="""How smoothly enhanced areas blend with surroundings.
            Lower values: Sharp transitions
            Higher values: Softer blending
            Helps avoid visible seams between processed and unprocessed areas.""",
            parent=self
        )
        self.edge_blur.set_range(0, 100)
        self.edge_blur.set_value(10)

        self.min_confidence = DoubleSliderCard(
            "Minimum Confidence",
            description="""Only process detections with this confidence score or higher.
            0.7-0.8: Only very certain detections
            0.5-0.7: Moderate confidence
            Below 0.5: May include false positives""",
            parent=self
        )
        self.min_confidence.set_range(0, 1.0, 2)
        self.min_confidence.set_value(0.6)

        self.max_overlay = DoubleSliderCard(
            "Overlay Opacity",
            description="""Control how much the enhanced version overlays the original.
            1.0: Complete replacement
            0.7-0.9: Strong enhancement but preserves some original texture
            0.5-0.7: Balanced mix
            Below 0.5: Very subtle effect""",
            parent=self
        )
        self.max_overlay.set_range(0, 1.0, 2)
        self.max_overlay.set_value(0.5)

        self.min_size = DoubleSliderCard(
            "Minimum Object Size",
            description="""Skip objects smaller than this size (relative to image).
            Prevents wasting resources on tiny details.
            0.01: 1% of image area
            0.05: 5% of image area (typical face in portrait)""",
            parent=self
        )
        self.min_size.set_range(0, 1.0, 2)
        self.min_size.set_value(0)

        self.max_size = DoubleSliderCard(
            "Maximum Object Size",
            description="""Skip objects larger than this size (relative to image).
            Prevents over-processing large background elements.
            0.5: 50% of image area
            1.0: No size limit""",
            parent=self
        )
        self.max_size.set_range(0, 1.0, 2)
        self.max_size.set_value(0.9)


        self.addFullWidthWidget(self.enable_detailer)
        self.addFullWidthWidget(self.detailer_classes)
        self.addFullWidthWidget(self.detailer_prompt)
        self.addFullWidthWidget(self.detailer_negative_prompt)

        self.addWidget(self.detailer_strength)
        self.addWidget(self.detailer_step)
        # self.addWidget(self.max_detect)
        self.addFullWidthWidget(self.max_detect)
        self.addWidget(self.edge_padding)
        self.addWidget(self.edge_blur)
        self.addWidget(self.min_confidence)
        self.addWidget(self.max_overlay)
        self.addWidget(self.min_size)
        self.addWidget(self.max_size)

    def get_payload(self) -> dict:
        """Returns the payload of the detailer box."""
        return {
            "detailer_enabled": self.enable_detailer.isChecked(),
            "detailer_prompt": self.detailer_prompt.toPlainText(),
            "detailer_negative": self.detailer_negative_prompt.toPlainText(),
            "detailer_strength": self.detailer_strength.value(),
            "detailer_steps": self.detailer_step.value(),
            "override_settings":{
                "detailer_classes": self.detailer_classes.toPlainText(),
                "detailer_max": self.max_detect.value(),
                "detailer_padding": self.edge_padding.value(),
                "detailer_blur": self.edge_blur.value(),
                "detailer_conf": self.min_confidence.value(),
                "detailer_iou": self.max_overlay.value(),
                "detailer_min_size": self.min_size.value(),
                "detailer_max_size": self.max_size.value()
            }

        }

    def set_payload(self, payload: dict):
        """Sets the payload of the detailer box."""
        if not payload:
            return

        if "detailer_enabled" in payload:
            self.enable_detailer.setChecked(payload["detailer_enabled"])
        if "detailer_prompt" in payload:
            self.detailer_prompt.setPlainText(payload["detailer_prompt"])
        if "detailer_negative" in payload:
            self.detailer_negative_prompt.setPlainText(payload["detailer_negative"])
        if "detailer_strength" in payload:
            self.detailer_strength.set_value(payload["detailer_strength"])
        if "detailer_steps" in payload:
            self.detailer_step.set_value(payload["detailer_steps"])

        override = payload.get("override_settings", {})
        if "detailer_classes" in override:
            self.detailer_classes.setPlainText(override["detailer_classes"])
        if "detailer_max" in override:
            self.max_detect.set_value(override["detailer_max"])
        if "detailer_padding" in override:
            self.edge_padding.set_value(override["detailer_padding"])
        if "detailer_blur" in override:
            self.edge_blur.set_value(override["detailer_blur"])
        if "detailer_conf" in override:
            self.min_confidence.set_value(override["detailer_conf"])
        if "detailer_iou" in override:
            self.max_overlay.set_value(override["detailer_iou"])
        if "detailer_min_size" in override:
            self.min_size.set_value(override["detailer_min_size"])
        if "detailer_max_size" in override:
            self.max_size.set_value(override["detailer_max_size"])



if __name__  == "__main__":
    from PySide6.QtWidgets import QApplication, QWidget
    app = QApplication([])
    window = DetailerBox(None, 6)
    window.show()
    window.set_payload({
        "override_settings":{
         "detailer_classes": ["face", "hand", "text"], "detailer_max": 2, "detailer_padding": 20, "detailer_blur": 10, "detailer_conf": 0.6, "detailer_iou": 0.5, "detailer_min_size": 0, "detailer_max_size": 0.9
    }}
    )
    print(window.get_payload())
    window.setFixedSize(600, 700)
    app.exec()

