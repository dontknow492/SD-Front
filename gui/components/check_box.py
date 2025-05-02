from typing import Union

from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QIcon

from gui.common import HorizontalCard
from qfluentwidgets import CheckBox, FluentIconBase


class CheckBoxCard(HorizontalCard):
    clicked = Signal()
    stateChanged = Signal(bool)

    def __init__(self, title: str = "DropBox", description: str = None,
                 info_icon: Union[QIcon, FluentIconBase, str, None] = None, show_info_on_focus: bool = False,
                 parent=None):
        super().__init__(title, description, info_icon, show_info_on_focus, parent=parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.checkbox = CheckBox(title, self)
        self.checkbox.clicked.connect(self.clicked.emit)
        self.checkbox.stateChanged.connect(self.stateChanged.emit)
        self.addWidget(self.checkbox,  alignment=Qt.AlignmentFlag.AlignBottom)

    def mousePressEvent(self, e):
        self.checkbox.setChecked(not self.checkbox.isChecked())
        super().mousePressEvent(e)

    def get_state(self):
        return self.checkbox.isChecked()

    def setChecked(self, checked: bool):
        self.checkbox.setChecked(checked)

    def isChecked(self):
        return self.checkbox.isChecked()


if  __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    app = QApplication([])
    window = CheckBoxCard("Check Box")
    window.stateChanged.connect(lambda x: print(x))
    window.show()
    app.exec()