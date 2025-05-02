from gui.common import HorizontalFrame, VerticalFrame
from gui.components import DoubleSliderCard, SliderCard, RadioCard

from qfluentwidgets import TogglePushButton
from PySide6.QtWidgets import QButtonGroup

from gui.common import HorizontalFrame, VerticalFrame
from gui.components import SliderCard
from qfluentwidgets import TogglePushButton
from PySide6.QtWidgets import QButtonGroup, QWidget

from gui.common import HorizontalFrame, VerticalFrame
from gui.components import SliderCard
from qfluentwidgets import TogglePushButton
from PySide6.QtWidgets import QButtonGroup, QWidget
from PySide6.QtCore import Signal


class ResizeBox(HorizontalFrame):
    """Custom widget for resizing using either 'Scale' or exact 'Width & Height'."""

    mode_changed = Signal(str)

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.setLayoutMargins(0, 0, 0, 0)
        self.setContentSpacing(0)

        # === Mode Toggle Buttons ===
        self.mode_group = QButtonGroup(self)
        self.resize_by_button = TogglePushButton("Resize by")
        self.resize_to_button = TogglePushButton("Resize to")

        self.resize_by_button.setChecked(True)
        self.mode_group.addButton(self.resize_by_button)
        self.mode_group.addButton(self.resize_to_button)

        # Button Layout
        mode_container = VerticalFrame()
        mode_container.layout().setSpacing(0)
        mode_container.layout().setContentsMargins(0, 0, 0, 0)
        mode_container.addWidgets([
            self.resize_by_button,
            self.resize_to_button
        ])
        #spacer
        mode_container.layout().addStretch(1)

        # === Sliders ===
        self.resize_scale = SliderCard("Scale", "Scale")
        self.resize_width = SliderCard("Width", "Width")
        self.resize_height = SliderCard("Height", "Height")

        slider_container = VerticalFrame()
        slider_container.layout().setSpacing(0)
        slider_container.layout().setContentsMargins(0, 0, 0, 0)
        slider_container.addWidgets([
            self.resize_scale,
            self.resize_width,
            self.resize_height
        ])

        self.addWidget(mode_container)
        self.addWidget(slider_container)
        slider_container.layout().addStretch(1)

        # === Signal Connections ===
        self.resize_by_button.clicked.connect(lambda: self.set_mode("by"))
        self.resize_to_button.clicked.connect(lambda: self.set_mode("to"))

        # Initial State
        self.set_mode("by")

    def set_mode(self, mode: str):
        """Set the resize mode: 'by' = scale, 'to' = width/height."""
        if mode not in ("by", "to"):
            raise ValueError(f"Invalid mode: {mode}")

        is_by_mode = mode == "by"

        self.resize_by_button.setChecked(is_by_mode)
        self.resize_to_button.setChecked(not is_by_mode)

        self.resize_scale.setVisible(is_by_mode)

        self.resize_scale.setEnabled(is_by_mode)

        self.resize_width.setVisible(not is_by_mode)
        self.resize_height.setVisible(not is_by_mode)
        self.resize_width.setEnabled(not is_by_mode)
        self.resize_height.setEnabled(not is_by_mode)

        self.adjustSize()
        self.mode_changed.emit(mode)



    def current_mode(self) -> str:
        """Returns current resize mode as 'by' or 'to'."""
        return "by" if self.resize_by_button.isChecked() else "to"

    def values(self) -> dict:
        """Returns the current resize values based on mode."""
        if self.current_mode() == "by":
            return {"scale": self.resize_scale.value()}
        else:
            return {
                "width": self.resize_width.value(),
                "height": self.resize_height.value()
            }


if   __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    window = ResizeBox()
    window.show()
    sys.exit(app.exec())


