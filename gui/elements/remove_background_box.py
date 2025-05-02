from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QGridLayout

from gui.common import VerticalCard, HorizontalCard, VerticalFrame, HorizontalFrame, FlowFrame, GridFrame
from gui.common.card import FlowTitleCard
from gui.components import ComboBoxCard, SliderCard, CheckBoxCard, DoubleSliderCard

from gui.elements import ResizeBox

class RemoveBackgroundBox(GridFrame):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.model = ComboBoxCard(
            "Model",
            description="Select the background removal model",
            parent=self
        )
        self.enable_post_process_mask =  CheckBoxCard(
            "Enable Post-Process Mask",
            description="Apply post-processing to the mask",
            parent=self
        )
        self.enable_alpha_matting = CheckBoxCard(
            "Enable Alpha Matting",
            description="Apply alpha matting to the mask",
            parent=self
        )
        self.erode_size = SliderCard(
            "Erode Size",
            description="Size of the erode operation",
            parent=self
        )
        self.foreground_threshold = SliderCard(
            "Foreground Threshold",
            description="Threshold for foreground",
            parent=self
        )
        self.background_threshold = SliderCard(
            "Background Threshold",
            description="Threshold for background",
            parent=self
        )

        self.addFullWidthWidget(self.model)
        self.addWidget(self.enable_post_process_mask)
        self.addWidget(self.enable_alpha_matting)
        self.addWidget(self.erode_size)
        self.addWidget(self.foreground_threshold)
        self.addFullWidthWidget(self.background_threshold)

if  __name__ == "__main__":
    from PySide6.QtWidgets import QApplication, QWidget
    app = QApplication([])
    window = RemoveBackgroundBox()
    window.show()
    app.exec()
