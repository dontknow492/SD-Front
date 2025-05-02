from PySide6.QtWidgets import QSplitter, QSplitterHandle, QTextEdit, QVBoxLayout, QWidget, QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QColor, QBrush
from qfluentwidgets import themeColor, qconfig


class HoverSplitterHandle(QSplitterHandle):
    def __init__(self, orientation, parent):
        super().__init__(orientation, parent)
        self.hovered = False
        self.hover_color = QColor("red")  # default highlight color
        self.setMouseTracking(True)

    def enterEvent(self, event):
        self.hovered = True
        self.update()

    def leaveEvent(self, event):
        self.hovered = False
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        color = QColor("#888888") if not self.hovered else self.hover_color  # default vs highlight
        painter.setBrush(QBrush(color))
        painter.setPen(Qt.NoPen)
        painter.drawRect(self.rect())

    def set_hover_color(self, color: QColor):
        self.hover_color = color
        self.update()

class ThemedHoverSplitterHandler(HoverSplitterHandle):

    def __init__(self, orientation, parent):
        super().__init__(orientation, parent)
        self._update_hover_color()
        # default highlight color
        qconfig.themeChanged.connect(self._update_hover_color)
        qconfig.themeColorChanged.connect(self._update_hover_color)

    def _update_hover_color(self):
        self.set_hover_color(themeColor())

class HoverSplitter(QSplitter):
    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)

    def createHandle(self):
        return ThemedHoverSplitterHandler(self.orientation(), self)


# Test UI
if __name__ == "__main__":
    app = QApplication([])

    main_widget = QWidget()
    layout = QVBoxLayout(main_widget)

    splitter = HoverSplitter(Qt.Horizontal)
    splitter.setHandleWidth(1)

    text1 = QTextEdit("Left")
    text2 = QTextEdit("Right")

    splitter.addWidget(text1)
    splitter.addWidget(text2)
    # splitter.setHandleWidth(6)

    layout.addWidget(splitter)
    main_widget.resize(600, 400)
    main_widget.show()

    app.exec()
