from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QGridLayout

from gui.common import VerticalCard, HorizontalCard, VerticalFrame, HorizontalFrame, FlowFrame, GridFrame
from gui.common.card import FlowTitleCard
from gui.components import ComboBoxCard, SliderCard, CheckBoxCard, DoubleSliderCard

from gui.elements import ResizeBox

class UpscaleBox(GridFrame):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.resize_box = ResizeBox()

        self.upscaler = ComboBoxCard(
            "Upscaler",
            description="Select the upscaler model",
            parent=self
        )

        self.refine_upscale = CheckBoxCard(
            "Refine Upscale",
            description="Refine the upscale result",
            parent=self
        )

        self.upscaler_visibility = DoubleSliderCard(
            "Upscaler Visibility",
            description="Show the upscaler result",
            parent=self
        )

        self.addFullWidthWidget(self.resize_box)
        self.addWidget(self.upscaler)
        self.addWidget(self.refine_upscale)
        self.addFullWidthWidget(self.upscaler_visibility)

if  __name__ == "__main__":
    from PySide6.QtWidgets import QApplication, QWidget
    app = QApplication([])
    window = UpscaleBox()
    window.show()
    app.exec()
