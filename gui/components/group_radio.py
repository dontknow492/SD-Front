from typing import Union, Optional

from PySide6.QtCore import Signal
from qfluentwidgets import RadioButton, FluentIconBase
from gui.common import FlowTitleCard
from PySide6.QtWidgets import QButtonGroup

from PySide6.QtGui import QIcon


class RadioCard(FlowTitleCard):
    selection_changed = Signal(str)
    index_changed = Signal(int)
    def __init__(
            self,
            title: str = None,
            description: str = None,
            info_icon: Union[FluentIconBase, QIcon, str, None] = None,
            show_info_on_focus: bool = False,
            parent=None
    ):
        super().__init__(title, description, info_icon, show_info_on_focus, parent)

        self._button_index: int = 0
        self.button_group = QButtonGroup(self)

    def add_option(self, text: str, icon: Union[FluentIconBase, str, QIcon] = None, is_selected: bool = True):
        radio_button = RadioButton(text, self)
        if icon:
            radio_button.setIcon(icon)
        self.add_radio_button(radio_button,  is_selected)
        return radio_button

    def add_radio_button(self, radio_button: RadioButton, is_selected: bool = True):
        self.button_group.addButton(radio_button)
        self.button_group.setId(radio_button, self._button_index)
        self._button_index += 1
        radio_button.clicked.connect(lambda: self.selection_changed.emit(radio_button.text()))
        radio_button.clicked.connect(lambda: self.index_changed.emit(self.button_group.id(radio_button)))

        radio_button.adjustSize()
        radio_button.setChecked(is_selected)
        self.addWidget(radio_button)

    def current_text(self) -> Optional[str]:
        button = self.button_group.checkedButton()
        return button.text() if button else None

    def current_index(self) -> int:
        button = self.button_group.checkedButton()
        return self.button_group.id(button) if button else -1

    def clear_options(self):
        for button in self.button_group.buttons():
            self.button_group.removeButton(button)
            button.setParent(None)

    def set_selected_index(self, index: int):
        button = self.button_group.button(index)
        if button:
            button.setChecked(True)

    def set_selected_text(self, text: str):
        for button in self.button_group.buttons():
            if button.text() == text:
                button.setChecked(True)
                break

if  __name__ == "__main__":
    from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout
    app = QApplication([])
    window = QWidget()
    layout = QVBoxLayout()
    window.setLayout(layout)

    radio_card = RadioCard("Radio Time")
    radio_card.add_option("Option 1")
    radio_card.add_option("Option 2")
    radio_card.add_option("Option 3")

    radio_card.selection_changed.connect(lambda text: print(f"Selected: {text}"))
    radio_card.index_changed.connect(lambda index: print(f"Index: {index}"))

    layout.addWidget(radio_card)

    window.show()
    app.exec()
