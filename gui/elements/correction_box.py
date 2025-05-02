from PySide6.QtGui import QColor

from gui.common import GridFrame, ThemedToolButton
from gui.components import CheckBoxCard, ComboBoxCard, SliderCard, TextEditCard, DoubleSliderCard
from qfluentwidgets import TogglePushButton, ColorPickerButton


class CorrectionBox(GridFrame):
    def __init__(self, parent = None, spacing: int = 12, margins: tuple[int, int, int, int] = (8, 8, 8, 8)):
        super().__init__(parent, spacing, margins)
        self.setContentsMargins(0, 0, 0, 0)

        self.value_type =  ComboBoxCard(
            "Value Type",
            description="""Choose the type of value to be corrected:
            - Relative: Adjust color values
            - Absolute: Adjust numeric values
            parent=self""")

        self.brightness = DoubleSliderCard(
            "Brightness",
            description="""Adjust the overall brightness of the image:
            0.0 - -1.0: Darken
            0.0 - 1.0: Brighten
            0.0: No change""",
            parent=self
        )
        self.brightness.set_range(-1, 1, 1)
        self.brightness.set_value(0)

        self.sharpness = DoubleSliderCard(
            "Sharpness",
            description="""Adjust the sharpness of the image:
            0.0 - -1.0: Blur
            0.0 - 1.0: Sharpen
            0.0: No change""",
            parent=self
        )
        self.sharpness.set_range(-1, 1, 1)
        self.sharpness.set_value(0)

        self.color = DoubleSliderCard(
            "Color",
            description="""Adjust the overall color balance of the image:""",
            parent=self
        )
        self.color.set_range(0, 4, 1)
        self.color.set_value(0)

        self.enable_hdr_clamp = CheckBoxCard(
            "HDR Clamp",
            description="""Prevent overexposure in HDR images:
            - Enabled: Limits exposure to prevent overexposure
            - Disabled: Allows overexposure in HDR images""",
            parent=self
        )

        self.hdr_clamp_range = DoubleSliderCard(
            "HDR Clamp Range",
            description="""Set the exposure range for HDR images:
            0.0 - 1.0: Adjusts exposure to prevent overexposure
            0.0: No change""",
            parent=self
        )
        self.hdr_clamp_range.set_range(0, 10, 1)
        self.hdr_clamp_range.set_value(4)

        self.hdr_clamp_threshold = DoubleSliderCard(
            "HDR Clamp Threshold",
            description="""Set the threshold for HDR clamping:
            0.0 - 1.0: Adjusts exposure to prevent overexposure
            0.0: No change""",
            parent=self
        )
        self.hdr_clamp_threshold.set_range(0, 1, 2)
        self.hdr_clamp_threshold.set_value(0.95)

        self.enable_hdr_maximize =  CheckBoxCard(
            "HDR Maximize",
            description="""Maximize dynamic range in HDR images:
            - Enabled: Increases dynamic range to maximize exposure
            - Disabled: Maintains current dynamic range""",
            parent=self
        )

        self.hdr_maximize_center = DoubleSliderCard(
            "HDR Maximize Center",
            description="""Set the center point for HDR maximization:
            0.0 - 1.0: Adjusts dynamic range to maximize exposure
            0.0: No change""",
            parent=self
        )
        self.hdr_maximize_center.set_range(0, 2, 1)
        self.hdr_maximize_center.set_value(0.6)

        self.hdr_max_range = DoubleSliderCard(
            "HDR Max Range",
            description="""Set the dynamic range for HDR maximization:
            0.0 - 1.0: Adjusts dynamic range to maximize exposure
            0.0: No change""",
            parent=self
        )
        self.hdr_max_range.set_range(0.5, 2, 1)
        self.hdr_max_range.set_value(1)

        self.color_grading = SliderCard(
            "Color Grading",
            description="""Adjust the color grading of the image:
            0.0 - 1.0: Adjusts color grading
            0.0: No change""",
            parent=self
        )
        self.color_grading.set_range(-1, 1)
        self.color_grading.set_value(0)

        self.color_button =  ColorPickerButton(QColor("#000000"), "Pick Color", parent=self)


        self.addWidget(self.value_type)
        self.addWidget(self.brightness)
        self.addWidget(self.sharpness)
        self.addWidget(self.color)
        self.addWidget(self.enable_hdr_clamp)
        self.addWidget(self.enable_hdr_maximize)
        self.addWidget(self.hdr_clamp_range)
        self.addWidget(self.hdr_maximize_center)
        self.addWidget(self.hdr_clamp_threshold)
        self.addWidget(self.hdr_max_range)
        self.addWidget(self.color_grading)
        self.addWidget(self.color_button)

    def get_payload(self) -> dict:
        """Returns current values from the UI as a dict."""
        return {
            # Previous fields

            # New fields
            "value_type": self.value_type.currentText(),
            "hdr_mode": self.enable_hdr_clamp.isChecked(),
            "hdr_clamp": self.enable_hdr_clamp.isChecked(),
            "hdr_boundary": self.hdr_clamp_range.value(),
            "hdr_threshold": self.hdr_clamp_threshold.value(),
            "hdr_maximize": self.enable_hdr_maximize.isChecked(),
            "hdr_max_center": self.hdr_maximize_center.value(),
            "hdr_max_boundary": self.hdr_max_range.value(),
            "hdr_color": self.color_grading.value(),
            "hdr_brightness": self.brightness.value(),
            "hdr_sharpen": self.sharpness.value(),
            "hdr_color_picker": self.color_button.color.name(),
            "hdr_tint_ratio":  self.color.value()
        }

    def set_payload(self, payload: dict):
        """Populates the UI from a dict."""
        if "hdr_mode" in payload:
            self.enable_hdr_clamp.setChecked(payload["hdr_mode"])
        if "hdr_clamp" in payload:
            self.enable_hdr_clamp.setChecked(payload["hdr_clamp"])  # Redundant but present in mapping
        if "hdr_boundary" in payload:
            self.hdr_clamp_range.setValue(payload["hdr_boundary"])
        if "hdr_threshold" in payload:
            self.hdr_clamp_threshold.setValue(payload["hdr_threshold"])
        if "hdr_maximize" in payload:
            self.enable_hdr_maximize.setChecked(payload["hdr_maximize"])
        if "hdr_max_center" in payload:
            self.hdr_maximize_center.setValue(payload["hdr_max_center"])
        if "hdr_max_boundary" in payload:
            self.hdr_max_range.setValue(payload["hdr_max_boundary"])
        if "hdr_color" in payload:
            self.color_grading.setValue(payload["hdr_color"])
        if "hdr_brightness" in payload:
            self.brightness.setValue(payload["hdr_brightness"])
        if "hdr_sharpen" in payload:
            self.sharpness.setValue(payload["hdr_sharpen"])
        if "hdr_color_picker" in payload:
            self.color_button.setColor(payload["hdr_color_picker"])
        if "hdr_tint_ratio" in payload:
            self.color.setValue(payload["hdr_tint_ratio"])


if __name__  == "__main__":
    from PySide6.QtWidgets import QApplication, QWidget
    app = QApplication([])
    window = CorrectionBox()
    # window.set_payload({
    #     "value_type": "Relative",
    #     "hdr_mode": True,
    #     "hdr_clamp": True,
    #     "hdr_threshold": 0.5,
    #     "hdr_maximize": True,
    #     "hdr_max_center": 0.5,
    #     "hdr_max_boundary": 0.5,
    #     "hdr_color": 0.5,
    #     "hdr_brightness": 0.5,
    #     "hdr_sharpen": 0.5,
    #     "hdr_color_picker": "#000000"
    # })
    print(window.get_payload())

    window.show()
    app.exec()

