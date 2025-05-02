from typing import Union, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QSizeGrip, QTextEdit, QSpacerItem, QSizePolicy, QVBoxLayout, QWidget
from PySide6.QtGui import QIcon
from qfluentwidgets import FluentIconBase, TextEdit  # if you're using fluent icons
from gui.common import VerticalTitleCard, MyTextEdit  # Replace with actual paths


class TextEditCard(VerticalTitleCard):
    """
    A card widget with a title, optional description, and a text input area.
    Includes an optional resize handle in the bottom-right corner.

    Args:
        title (str): The title displayed above the text editor.
        description (Optional[str]): A description shown below the title.
        info_icon (Optional[Union[QIcon, FluentIconBase, str]]): Icon or tooltip for info.
        show_info_on_focus (bool): Whether to show the description only on focus.
        placeholder (Optional[str]): Placeholder text inside the text editor.
        parent (QWidget): Parent widget.
        resizable (bool): If True, adds a resize grip in the bottom-right corner.
    """
    def __init__(
        self,
        title: str = "DropBox",
        description: Optional[str] = None,
        info_icon: Optional[Union[QIcon, FluentIconBase, str]] = None,
        show_info_on_focus: bool = False,
        placeholder: Optional[str] = None,
        parent=None,
        resizable: bool = True
    ):
        super().__init__(title, description, info_icon, show_info_on_focus, parent=parent)

        # Create and configure text edit
        self.textEdit: QTextEdit = TextEdit(self)
        placeholder = placeholder or "Type here."
        self.textEdit.setPlaceholderText(placeholder)
        self.addWidget(self.textEdit, stretch=10)

        self.resizable = resizable
        self.size_grip: Optional[QSizeGrip] = None

        if self.resizable:
            self._add_size_grip()

        self.toggle_grip(True)
        self.update()

    def _add_size_grip(self):
        """Internal helper to add a resize grip to the bottom-right corner."""
        # Create a container for the size grip to align it to bottom-right
        self.size_grip  = QSizeGrip(self.textEdit)
        grip_container = QWidget()
        grip_layout = QVBoxLayout(grip_container)
        grip_layout.setContentsMargins(0, 0, 0, 0)
        grip_layout.addStretch()
        grip_layout.addWidget(self.size_grip, 0, Qt.AlignmentFlag.AlignRight)

        self.addWidget(grip_container, stretch=0)
        # self.setMinimumSize(100, 100)


    def get_value(self) -> str:
        """
        Get the current text content.

        Returns:
            str: The plain text inside the text editor.
        """
        return self.textEdit.toPlainText()

    def set_value(self, value: str):
        """
        Set the content of the text editor.

        Args:
            value (str): Text to insert into the editor.
        """
        self.textEdit.setPlainText(value)

    def toggle_grip(self, visible: bool):
        """
        Toggle visibility of the resize grip.

        Args:
            visible (bool): True to show the grip, False to hide it.
        """
        self.resizable = visible
        if visible:
            if not self.size_grip:
                self._add_size_grip()
            self.size_grip.show()
        else:
            if self.size_grip:
                self.size_grip.hide()

    def get_text_edit(self) -> QTextEdit:
        """
        Access the internal QTextEdit widget directly.

        Returns:
            QTextEdit: The internal text editor.
        """
        return self.textEdit

    def resizeEvent(self, event, /):
        event.ignore()

    def get_text_edit(self) -> QTextEdit:
        """
        Access the internal QTextEdit widget directly.

        Returns:
            QTextEdit: The internal text editor.
        """
        return self.textEdit

    def get_text(self) -> str:
        """
        Get the current text content.

        Returns:
            str: The plain text inside the text editor.
        """
        return self.textEdit.toPlainText()

    def toPlainText(self):
        return self.get_text()

    def setPlainText(self, text: str):
        self.textEdit.setPlainText(text)


if  __name__ == "__main__":
    from PySide6.QtWidgets import QApplication, QWidget

    app = QApplication([])
    window = TextEditCard(parent=None)
    window.show()
    app.exec()
