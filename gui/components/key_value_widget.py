from PySide6.QtWidgets import (
    QWidget, QLabel, QHBoxLayout, QApplication, QPushButton, QToolTip
)
from PySide6.QtGui import QFont, QFontMetrics
from PySide6.QtCore import Qt, QSize
import sys
from qfluentwidgets import StrongBodyLabel, BodyLabel, TeachingTip, InfoBarIcon, TeachingTipTailPosition, \
    TransparentToolButton, FluentIcon

from gui.common import HorizontalFrame


class KeyValueWidget(HorizontalFrame):
    def __init__(self, key: str, value: str, max_width=200, parent=None):
        super().__init__(parent)

        self.key = key
        self.value = value
        self.max_width = max_width

        # Key label
        self.key_label = StrongBodyLabel(f"{key}: ")
        self.key_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        # self.key_label.setStyleSheet("color: #555;")

        # Value label with elided text
        self.value_label = BodyLabel()
        self.value_label.setWordWrap(True)
        self.value_label.setFont(QFont("Segoe UI", 10))
        # self.value_label.setStyleSheet("color: #2c3e50;")


        # Button to show full text
        self.show_button = TransparentToolButton(FluentIcon.MORE)
        self.show_button.setFixedSize(QSize(24, 24))
        self.show_button.setToolTip("Show full text")
        self.show_button.setCursor(Qt.PointingHandCursor)
        self.show_button.clicked.connect(self.show_full_text)

        # Layout
        self.addWidget(self.key_label)
        self.addWidget(self.value_label, 1)
        self.addWidget(self.show_button)
        self.setContentSpacing(0)
        self.setLayoutMargins(0, 0, 0, 0)

        self.set_elided_text(value)
        self.adjustSize()

    def set_elided_text(self, text: str):
        font_metrics = QFontMetrics(self.value_label.font())
        elided = font_metrics.elidedText(text, Qt.ElideRight, self.max_width)
        self.value_label.setText(elided)
        if elided.endswith("..."):
            self.show_button.show()
        else:
            self.show_button.hide()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.max_width  = self.width() - self.key_label.width() - self.show_button.width() - 30
        self.set_elided_text(self.value)

    def show_full_text(self):
        TeachingTip.create(
            target=self.show_button,
            icon=InfoBarIcon.SUCCESS,
            title=self.key,
            content=self.value,
            isClosable=True,
            tailPosition=TeachingTipTailPosition.BOTTOM,
            duration=2000,
            parent=self
        )

# Example usage
if __name__ == "__main__":
    app = QApplication(sys.argv)

    long_text = "aa"
    widget = KeyValueWidget("Filename", long_text, max_width=300)
    widget.resize(400, 40)
    widget.show()

    sys.exit(app.exec())
