from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QGridLayout

from gui.common import VerticalCard, HorizontalCard, VerticalFrame, HorizontalFrame, FlowFrame, GridFrame
from gui.common.card import FlowTitleCard
from gui.components import ComboBoxCard, SliderCard, CheckBoxCard, DoubleSliderCard

from gui.elements import ResizeBox

class GFPGANBox(GridFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.strength = DoubleSliderCard(
            "GFPFGAN Strength",
            description="Strength of the GFPGAN",
            show_info_on_focus=True,
            parent=self
        )

        self.addWidget(self.strength)


if  __name__ == "__main__":
    from PySide6.QtWidgets import QApplication, QWidget
    app = QApplication([])
    window = GFPGANBox()
    window.show()
    app.exec()
