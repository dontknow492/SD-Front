from PySide6.QtGui import QPainter, QFont, Qt, QColor
from qfluentwidgets import isDarkTheme, ProgressBar


class MyProgressBar(ProgressBar):
    def __init__(self, parent=None, useAni=True):
        super().__init__(parent, useAni)
        self._barColor = super().barColor()

    def set_bar_color(self, color: QColor):
        self._barColor = color
        self.update()

    def reset_bar_color(self):
        self._barColor = super().barColor()
        self.update()

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing)

        # draw background
        bc = self.darkBackgroundColor if isDarkTheme() else self.lightBackgroundColor
        painter.setPen(bc)

        if self.minimum() >= self.maximum():
            return

        # draw bar

        w = int(self.val / (self.maximum() - self.minimum()) * self.width())
        r = self.height() / 2
        painter.drawRoundedRect(0, 0, self.width(), self.height(), r, r)

        painter.setPen(Qt.NoPen)
        painter.setBrush(self._barColor)
        painter.drawRoundedRect(0, 0, w, self.height(), r, r)


if  __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    app = QApplication([])
    window = MyProgressBar()
    window.setFixedHeight(30)
    window.show()
    app.exec()
