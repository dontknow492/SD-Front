from typing import override, Union, Any

from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QIcon
from qfluentwidgets import ComboBox, EditableComboBox, StrongBodyLabel, FluentIconBase

from gui.common import VerticalTitleCard

class ComboBoxCard(VerticalTitleCard):
    currentIndexChanged = Signal(int)

    def __init__(self, title: str = "DropBox", description: str = None, info_icon: Union[QIcon, FluentIconBase, str, None]= None, show_info_on_focus: bool = False, parent = None):
        super().__init__(title, description, info_icon, show_info_on_focus, parent=parent)
        self.comboBox = self._get_comboBox()
        self.comboBox.currentIndexChanged.connect(self.on_current_index_changed)
        self.addWidget(self.comboBox, alignment=Qt.AlignmentFlag.AlignBottom, stretch=1)

    def on_current_index_changed(self, index):
        self.currentIndexChanged.emit(index)

    def _get_comboBox(self) -> ComboBox:
        return ComboBox(self)

    def get_value(self):
        return self.comboBox.currentText()

    def set_value(self, value):
        self.comboBox.setCurrentText(value)

    def get_index(self):
        return self.comboBox.currentIndex()

    def set_items(self, items):
        self.comboBox.clear()
        self.comboBox.addItems(items)

    def currentText(self):
        return self.comboBox.currentText()

    def currentIndex(self):
        return self.comboBox.currentIndex()

    def setCurrentText(self, text):
        self.comboBox.setCurrentText(text)

    def addItem(self,
            text: str,
            icon: str | QIcon | FluentIconBase | None = None,
            userData: Any = None,
            is_selected: bool = False) -> None:
        self.comboBox.addItem(text, icon, userData)
        if is_selected:
            self.comboBox.setCurrentText(text)

    def clear(self):
        self.comboBox.clear()


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication, QWidget, QCompleter

    app = QApplication([])
    window = ComboBoxCard(parent=None)
    items = ["item 1", "item 2", "item 3"]
    window.set_items(items)
    window.show()
    app.exec()
