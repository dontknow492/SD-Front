from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QGridLayout

from gui.common import VerticalCard, HorizontalCard, VerticalFrame, HorizontalFrame, FlowFrame, GridFrame
from gui.common.card import FlowTitleCard
from gui.components import ComboBoxCard, SliderCard, CheckBoxCard, DoubleSliderCard

from gui.elements import ResizeBox

class CodeformerBox(GridFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.strength = DoubleSliderCard(
            "Codeformer Strength",
            description="Strength of the codeformer",
            parent=self
        )
        self.weight = DoubleSliderCard(
            "Weight",
            description="Weight of the codeformer",
            parent=self
        )

        self.addWidget(self.strength)
        self.addWidget(self.weight)


if  __name__ == "__main__":
    from PySide6.QtWidgets import QApplication, QWidget
    app = QApplication([])
    window = CodeformerBox()
    window.show()
    app.exec()
