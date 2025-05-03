from typing import Union

from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QFrame
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import Qt
from qfluentwidgets import SubtitleLabel, StrongBodyLabel, IconWidget, FluentIconBase, \
    TransparentToolButton, FluentIcon, themeColor

from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QGraphicsDropShadowEffect
)
from PySide6.QtGui import QIcon, QColor
from PySide6.QtCore import Qt
from typing import Union

class NotificationWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName("NotificationWidget")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        # self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )

        # Drop shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 5)
        shadow.setColor(QColor(0, 0, 0, 120))
        self.setGraphicsEffect(shadow)

        # Layouts
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)

        title_layout = QHBoxLayout()
        title_layout.setSpacing(10)

        # Widgets
        self.icon_widget = IconWidget(self)
        self.title_label = SubtitleLabel(self)
        self.description_label = StrongBodyLabel(self)
        self.description_label.setWordWrap(True)

        self.close_button = TransparentToolButton(FluentIcon.CLOSE, self)
        self.close_button.clicked.connect(self.close)

        # Add widgets to layouts
        title_layout.addWidget(self.icon_widget)
        title_layout.addWidget(self.title_label, 1, alignment=Qt.AlignmentFlag.AlignVCenter)
        title_layout.addWidget(self.close_button)

        main_layout.addLayout(title_layout)
        main_layout.addWidget(self.description_label)

        # Style
        self.setStyleSheet(f"""
            #NotificationWidget {{
                background-color: {themeColor().name()};
                border-radius: 10px;
            }}
        """)

    def setIcon(self, icon: Union[QIcon, str, FluentIconBase]):
        self.icon_widget.setIcon(icon)

    def setTitle(self, title: str):
        self.title_label.setText(title)
        min_width = self.title_label.fontMetrics().horizontalAdvance(title) + 120
        self.setMinimumWidth(min_width)

    def setDescription(self, description: str):
        self.description_label.setText(description)






if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    app = QApplication([])
    widget = NotificationWidget()
    widget.setIcon(QIcon("path/to/icon.png"))
    widget.setTitle("Notification Title")
    widget.setDescription("This is a notification description.")
    widget.show()
    app.exec()