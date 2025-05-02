from typing import Callable, Union

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from qfluentwidgets import TextEdit, FluentIconBase, FluentIcon, toggleTheme, ComboBox
from gui.common.splitter import HoverSplitter
from gui.common.myFrame import VerticalFrame, HorizontalFrame
from gui.common import VerticalScrollWidget
from gui.common.button import ThemedToolButton
from gui.components import TextEditCard

from api import api_manager
from PySide6.QtWidgets import QHBoxLayout, QCompleter


def create_tool_button(icon: Union[FluentIconBase, QIcon, str, None] = None,
        title: Union[str, None] = None,
        description: Union[str, None] = None,
        info_icon: Union[QIcon, None] = None,
        show_info_on_focus: bool = False,
        parent=None):
    button = ThemedToolButton(icon, title, description, info_icon, show_info_on_focus, parent)
    return button

class PromptBox(VerticalFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        # self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.prompt = TextEditCard("Prompt", "Enter your prompt here", placeholder="Enter your prompt here", resizable=False)
        self.prompt.set_hover_effect_enabled(False)
        self.prompt.set_focus_style_enabled(False)
        self.negative_prompt = TextEditCard("Negative Prompt", "Enter your negative prompt here", placeholder="Negative Prompt")
        self.negative_prompt.set_hover_effect_enabled(False)
        self.negative_prompt.set_focus_style_enabled(False)
        # self.negative_prompt.setPlaceholderText('Negative Prompt')
        api_manager.style_fetched.connect(self.set_styles)

        self._setup_ui()

    def _setup_ui(self):
        option_container = HorizontalFrame()
        option_container.setContentsMargins(0, 0, 0, 0)
        option_container.setLayoutMargins(0, 0, 0, 0)
        # option_container.setFocusPolicy(Qt.FocusPolicy.ClickFocus)

        restore_button = create_tool_button(FluentIcon.HISTORY, "Restore",  "Restore to previous saved text")
        delete_prompt_button = create_tool_button(FluentIcon.DELETE, "Delete", "Clear current prompt")
        refresh_style_button = create_tool_button(FluentIcon.SYNC, "Refresh", "Refresh style")
        refresh_style_button.clicked.connect(toggleTheme)
        paste_style_button = create_tool_button(FluentIcon.PASTE, "Paste", "Paste style to prompt")
        save_style_button = create_tool_button(FluentIcon.SAVE_AS, "Save", "Save current prompt as style")
        self.style_box = ComboBox()
        self.style_box.setMaxVisibleItems(5)
        self.style_box.setPlaceholderText('Style')


        #adding to option container
        option_container.addWidgets([restore_button, delete_prompt_button, self.style_box, refresh_style_button, paste_style_button, save_style_button])

        spliter = HoverSplitter(Qt.Orientation.Vertical)
        spliter.setHandleWidth(2)
        spliter.setContentsMargins(0, 0, 0, 0)
        # spliter.
        prompt_container = VerticalFrame(spliter)
        prompt_container.setLayoutMargins(0, 0, 0, 9)
        prompt_container.addWidget(self.prompt)

        negative_container = VerticalFrame(spliter)
        negative_container.setLayoutMargins(0, 9, 0, 0)
        negative_container.addWidget(self.negative_prompt)

        self.addWidget(option_container)
        self.addWidget(spliter)

    def get_prompt(self):
        return self.prompt.get_text()

    def get_negative_prompt(self):
        return self.negative_prompt.get_text()

    def get_payload(self):
        return {
            "prompt": self.get_prompt(),
            "negative_prompt": self.get_negative_prompt(),
            "styles":  ["" if self.style_box.currentText() == "" else self.style_box.currentText()]
        }

    def set_payload(self, data: dict):
        if "prompt" in data:
            self.prompt.set_value(data["prompt"])
        if "negative_prompt" in data:
            self.negative_prompt.set_value(data["negative_prompt"])
        if "styles" in data:
            self.style_box.setCurrentText(data["styles"][0])

    def set_styles(self, styles: list[dict]):
        self.style_box.clear()
        self.style_box.addItem("")
        for style in styles:
            name = style["name"]
            self.style_box.addItem(name)


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication, QWidget
    app = QApplication([])
    window = PromptBox()
    # api_manager.fetch_style()
    print(window.get_payload())
    window.show()
    app.exec()