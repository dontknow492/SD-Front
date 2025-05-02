from PySide6.QtCore import Signal
from PySide6.QtGui import QIcon, QColor, Qt, QCursor
from qfluentwidgets import ToolButton, FluentIconBase, FluentIcon, setCustomStyleSheet, qconfig, themeColor, PushButton, \
    TeachingTip, InfoBarIcon, TeachingTipTailPosition
from typing import Union



class CustomToolButton(ToolButton):
    info_signal = Signal(str, str, QIcon)
    hide_signal = Signal()

    def __init__(
        self,
        icon: Union[FluentIconBase, QIcon, str, None] = None,
        title: Union[str, None] = None,
        description: Union[str, None] = None,
        info_icon: Union[QIcon, None] = None,
        show_info_on_focus: bool = False,
        parent=None
    ):
        super().__init__(parent)

        if icon:
            self.setIcon(icon)

        if title:
            self.setToolTip(title)

        self.title = title or ""
        self.description = description or ""
        self.info_icon = info_icon or QIcon()
        self.show_info_on_focus = show_info_on_focus

        self.focus_border_color = QColor("#F0F0F0")
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._apply_default_style()

    def _apply_default_style(self):
        """Reset to default border (no highlight)"""
        default_style = f"CustomToolButton {{ border-width: 1px; border-style: solid; border-color: rgba(22,22, 22, 50);}} CustomToolButton:hover {{ background: {self.focus_border_color.name()}; }}"
        setCustomStyleSheet(self, default_style, default_style)

    def focusInEvent(self, e, /):
        print("focus in button")
        # super().focusInEvent(e)
        style = f"CustomToolButton {{ border: 1px solid {self.focus_border_color.name()}; }} CustomToolButton:hover {{ background: {self.focus_border_color.name()}; }}"
        # hover_style = f""
        setCustomStyleSheet(self, style, style)
        # setCustomStyleSheet(self, hover_style, hover_style)
        if self.show_info_on_focus:
            self.info_signal.emit(self.title, self.description, self.info_icon)

    def focusOutEvent(self, e, /):
        print("focus out button")
        # super().focusOutEvent(e)
        self._apply_default_style()
        if self.show_info_on_focus:
            self.hide_signal.emit()

    def enterEvent(self, e):
        super().enterEvent(e)
        self._apply_default_style()

    def enable_info_on_focus(self, enabled: bool):
        self.show_info_on_focus = enabled

    def set_focus_border_color(self, color: QColor):
        self.focus_border_color = color

    def set_info_content(self, title: str, description: str, icon: QIcon = None):
        self.title = title
        self.description = description
        if icon:
            self.info_icon = icon


class ThemedToolButton(CustomToolButton):
    def __init__(
            self,
            icon: Union[FluentIconBase, QIcon, str, None] = None,
            title: Union[str, None] = None,
            description: Union[str, None] = None,
            info_icon: Union[QIcon, None] = None,
            show_info_on_focus: bool = False,
            parent=None
    ):
        super().__init__(icon, title, description, info_icon, show_info_on_focus, parent)
        qconfig.themeChanged.connect(self.on_theme_changed)
        qconfig.themeColorChanged.connect(self.on_theme_changed)

        self.on_theme_changed()

    def on_theme_changed(self):
        self.set_focus_border_color(themeColor())
        self.update()



if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QFrame
    from gui.common.myFrame import VerticalFrame
    app = QApplication([])
    window = QFrame()
    window.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
    window.setLayout(QVBoxLayout())
    button = ThemedToolButton(icon=FluentIcon.SAVE)
    window.show()

    app.exec()