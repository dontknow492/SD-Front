from typing import override, overload, Union

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QColor
from qfluentwidgets import SimpleCardWidget,  themeColor, toggleTheme, FlowLayout, StrongBodyLabel, \
    FluentIconBase,  ComboBox

from PySide6.QtWidgets import QVBoxLayout, QWidget, QHBoxLayout, QFrame


from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon
from typing import Union
from manager import info_view_manager
from config import sd_config



class CardBase(SimpleCardWidget):
    info_signal = Signal(str, str, QIcon)
    hide_signal = Signal()

    def __init__(
        self,
        title: str = "",
        description: str = "",
        info_icon: Union[FluentIconBase, QIcon, str, None] = None,
        show_info_on_focus: bool = True,
        parent=None
    ):
        super().__init__(parent)
        self.title = title
        self.description = description
        self.info_icon = QIcon(info_icon) if isinstance(info_icon, str) else info_icon or QIcon()
        self.show_info_on_focus = show_info_on_focus

        self._is_focused = False
        self._hover_enabled = True
        self._focus_style_enabled = True
        self._custom_stylesheet = None
        self._theme_color = themeColor()

        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.main_layout = self.init_layout()
        self.setLayout(self.main_layout)

        sd_config.themeChanged.connect(self._on_theme_changed)
        sd_config.themeColorChanged.connect(self._on_theme_changed)

        self.setStyleSheet(self.get_default_stylesheet())

    def get_default_stylesheet(self):
        return f"""
                    CardBase {{
                        border: 1px solid transparent;
                        border-radius: {self._borderRadius}px;
                    }}
                """

    def init_layout(self):
        """Must be implemented in subclasses to initialize the layout."""
        raise NotImplementedError("Subclasses must implement init_layout()")

    # ---------- Theme Updates ----------

    def _on_theme_changed(self):
        self._theme_color = themeColor()
        if self._is_focused:
            self.clear_style()
            self.apply_style()

    # ---------- Event Overrides ----------

    def enterEvent(self, event):
        print('enter', self.show_info_on_focus)
        if self._hover_enabled:
            self.apply_style()
        if self.show_info_on_focus:
            print('show')
            info_view_manager.set_info(self.title, self.description, self.info_icon)
            # self.info_signal.emit(self.title, self.description, self.info_icon)
        super().enterEvent(event)

    def leaveEvent(self, event):
        if self._hover_enabled and not self._is_focused:
            self.clear_style()
        if self.show_info_on_focus:
            # self.hide_signal.emit()
            print('hide')
            info_view_manager.hide_info()
        super().leaveEvent(event)

    def focusInEvent(self, event):
        self._is_focused = True
        print("Focus in")
        if self._focus_style_enabled:
            self.apply_style()
        super().focusInEvent(event)

    def focusOutEvent(self, event):
        self._is_focused = False
        print("Focus out")
        self.clear_style()
        super().focusOutEvent(event)

    # ---------- Style Methods ----------

    def apply_style(self):
        """Apply hover or focus styles."""
        if self._custom_stylesheet:
            self.setStyleSheet(self._custom_stylesheet)
        else:
            self.setStyleSheet(f"""
                CardBase {{
                    border: 1px solid {self._theme_color.name()};
                    border-radius: {self._borderRadius}px;
                }}
            """)

    def clear_style(self):
        """Clear applied styles."""
        self.setStyleSheet(self._custom_stylesheet or self.get_default_stylesheet())

    def set_hover_effect_color(self, color: QColor):
        """Set the hover effect color."""
        self._theme_color = color
        self.apply_style()

    def set_focus_style_color(self, color: QColor):
        """Set the focus style color."""
        self._theme_color = color
        self.apply_style()

    def set_hover_effect_enabled(self, enabled: bool):
        """Enable or disable hover border effect."""
        self._hover_enabled = enabled
        if not enabled and not self._is_focused:
            self.clear_style()

    def set_focus_style_enabled(self, enabled: bool):
        """Enable or disable border styling on focus."""
        self._focus_style_enabled = enabled
        if not enabled and self._is_focused:
            self.clear_style()

    def set_custom_stylesheet(self, qss: str):
        """Set a custom QSS stylesheet to override the default styling."""
        self._custom_stylesheet = qss
        self.setStyleSheet(qss)

    # def setBorderRadius(self, radius: int):
    #     super().setBorderRadius(radius)

    # ---------- Layout Helpers ----------

    def addWidget(self, widget: QWidget, stretch: int = 0, alignment: Qt.AlignmentFlag | None = None):
        """Add a widget to the layout."""
        self.main_layout.addWidget(widget, stretch, alignment or Qt.Alignment())

    def insertWidget(self, index: int, widget: QWidget, stretch: int = 0, alignment: Qt.AlignmentFlag | None = None):
        """Insert a widget into the layout at a specific index."""
        self.main_layout.insertWidget(index, widget, stretch, alignment or Qt.Alignment())

class VerticalCard(CardBase):
    def __init__(
            self,
            title: str = None,
            description: str = None,
            info_icon: Union[FluentIconBase, QIcon, str, None] = None,
            show_info_on_focus: bool = False,
            parent=None
    ):
        super().__init__(title, description, info_icon, show_info_on_focus, parent = parent)
        self.setObjectName("VerticalCard")

    def init_layout(self):
        return QVBoxLayout(self)

class HorizontalCard(CardBase):
    def __init__(
            self,
            title: str = None,
            description: str = None,
            info_icon: Union[FluentIconBase, QIcon, str, None] = None,
            show_info_on_focus: bool = False,
            parent=None
    ):
        super().__init__(title, description, info_icon, show_info_on_focus, parent = parent)
        self.setObjectName("HorizontalCard")

    def init_layout(self):
        return QHBoxLayout(self)

class FlowCard(CardBase):
    def __init__(
            self,
            title: str = None,
            description: str = None,
            info_icon: Union[FluentIconBase, QIcon, str, None] = None,
            show_info_on_focus: bool = False,
            parent=None
    ):
        super().__init__(title, description, info_icon, show_info_on_focus, parent = parent)
        self.setObjectName("FlowCard")

    def init_layout(self):
        return FlowLayout(self)

    @override
    def addWidget(self, widget: QWidget):
        self.main_layout.addWidget(widget)


class TitleCardBase(VerticalCard):

    def __init__(
            self,
            title: str = "Title Card",
            description: str = None,
            info_icon: Union[FluentIconBase, QIcon, str, None] = None,
            show_info_on_focus: bool = False,
            parent=None
    ):
        title = title or "Title Card"
        super().__init__(title, description, info_icon, show_info_on_focus, parent = parent)
        self.setObjectName("TitleCard")

        self.title = title
        title_label = StrongBodyLabel(text = self.title)
        title_label.setObjectName("TitleLabel")
        title_label.setWordWrap(True)

        #widget container
        self.container = QFrame(self)
        self.container.setContentsMargins(0, 0, 0, 0)
        self.container_layout =  self._get_layout()
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.container.setLayout(self.container_layout)

        super().addWidget(title_label, alignment=Qt.AlignmentFlag.AlignTop)
        super().addWidget(self.container,  stretch=1)
    @override
    def addWidget(self, widget: QWidget, stretch=0, alignment: Qt.AlignmentFlag | None = None):
        if alignment is not None:
            self.container_layout.addWidget(widget, stretch, alignment)
        else:
            if stretch != 0:
                self.container_layout.addWidget(widget, stretch)
            else:
                self.container_layout.addWidget(widget)

    @override
    def insertWidget(self, index, widget, stretch = 0, alignment: Qt.AlignmentFlag | None = None):
        if alignment is not None:
            self.container_layout.insertWidget(index, widget, stretch, alignment)
        else:
            if stretch != 0:
                self.container_layout.insertWidget(index, widget, stretch)
            else:
                self.container_layout.insertWidget(index, widget)

    def _get_layout(self):
        raise NotImplementedError("init_layout() must be implemented in subclass  return layout_type:")

class VerticalTitleCard(TitleCardBase):
    def __init__(
            self,
            title: str = 'Vertical Card',
            description: str = None,
            info_icon: Union[FluentIconBase, QIcon, str, None] = None,
            show_info_on_focus: bool = False,
            parent=None
    ):
        title = title or "Vertical Card"
        super().__init__(title = title, description = description, info_icon = info_icon, show_info_on_focus = show_info_on_focus, parent = parent)
        self.setObjectName("VerticalTitleCard")

    @override
    def _get_layout(self):
        return QVBoxLayout()

class HorizontalTitleCard(TitleCardBase):
    def __init__(
            self,
            title: str = "Horizontal Card",
            description: str = None,
            info_icon: Union[FluentIconBase, QIcon, str, None] = None,
            show_info_on_focus: bool = False,
            parent=None
    ):
        title = title or "Horizontal Card"
        super().__init__(title, description, info_icon, show_info_on_focus, parent = parent)
        self.setObjectName("HorizontalTitleCard")

    @override
    def _get_layout(self):
        return QHBoxLayout()

class FlowTitleCard(TitleCardBase):
    def __init__(
            self,
            title: str = "Horizontal Card",
            description: str = None,
            info_icon: Union[FluentIconBase, QIcon, str, None] = None,
            show_info_on_focus: bool = False,
            parent=None
    ):
        title = title or "Flow Card"
        super().__init__(title, description, info_icon, show_info_on_focus, parent=parent)
        self.setObjectName("FlowTitleCard")

    @override
    def _get_layout(self):
        return FlowLayout()

class DropDownCard(VerticalCard):
    def __init__(
            self,
            drop_down_widget: QWidget,
            title: str = "Drop Down Card",
            description: str = None,
            info_icon: Union[FluentIconBase, QIcon, str, None] = None,
            show_info_on_focus: bool = False,
            parent=None
    ):
        title = title or "Drop Down Card"
        super().__init__(title, description, info_icon, show_info_on_focus, parent = parent)
        self.setObjectName("DropDownCard")

        self.button = ComboBox()
        self.button.setText(title)
        self.drop_down_widget = drop_down_widget

        if isinstance(drop_down_widget, CardBase):
            self.drop_down_widget.set_hover_effect_enabled(False)
            self.drop_down_widget.set_focus_style_enabled(False)

        self.button.clicked.connect(lambda: self.drop_down_widget.setHidden(not self.drop_down_widget.isHidden()))

        self.addWidget(self.button, alignment=Qt.AlignmentFlag.AlignTop)
        self.addWidget(self.drop_down_widget, alignment=Qt.AlignmentFlag.AlignTop)
        self.drop_down_widget.setHidden(True)
        self.layout().setSpacing(0)

if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication, QWidget
    app = QApplication([])
    button = VerticalTitleCard("String bro")
    info_view_manager.showInfo.connect(lambda title, description, icon: print(title, description, icon))
    # window = DropDownCard(drop_down_widget=button, title="Drop Down Card")
    # window.toggled_hover_effect(False)
    # window.setFocusPolicy(Qt.FocusPolicy.NoFocus)
    # button = VerticalTitleCard("String bro", parent = window)
    # button.clicked.connect(lambda: toggleTheme())
    # button_2 = FlowTitleCard(title="Flow Card", parent = window)
    # button_2.set_hover_effect_enabled(False)
    # button_2.set_focus_style_enabled(False)

    # window.addWidget(button)
    # window.addWidget(button_2)
    button.show()
    app.exec()