from qfluentwidgets import NavigationWidget
from qfluentwidgets import isDarkTheme
from PySide6.QtCore import Qt, QRect, QSize
from PySide6.QtGui import QPainter, QColor, QFont, QImage, QBrush


from qfluentwidgets import NavigationWidget, isDarkTheme
from PySide6.QtCore import Qt, QRect, QSize
from PySide6.QtGui import QPainter, QColor, QFont, QImage, QBrush


class NaviAvatarWidget(NavigationWidget):
    """ Avatar widget with online/offline status and base URL display """

    def __init__(self, parent=None):
        super().__init__(isSelectable=False, parent=parent)
        self.avatar = QImage(r"D:\Program\SD Front\cover_demo.jpg").scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.status_color = QColor(128, 128, 128)  # Default to offline
        self._text = "http://127.0.0.1:7860"

    def set_status(self, online: bool):
        self.status_color = QColor(0, 200, 0) if online else QColor(128, 128, 128)
        self.update()

    def set_base_url(self, url: str):
        self._text = url
        self.update()

    def set_avatar(self, image: QImage | str):
        if isinstance(image, str):
            image = QImage(image)
        self.avatar = image.scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.update()

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.SmoothPixmapTransform | QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)

        if self.isPressed:
            painter.setOpacity(0.7)

        # draw hover background
        if self.isEnter:
            c = 255 if isDarkTheme() else 0
            painter.setBrush(QColor(c, c, c, 10))
            painter.drawRoundedRect(self.rect(), 5, 5)

        # draw avatar image as circle
        painter.setBrush(QBrush(self.avatar))
        painter.translate(8, 6)
        painter.drawEllipse(0, 0, 24, 24)

        # draw status dot (bottom right of avatar)
        painter.setBrush(self.status_color)
        painter.setPen(Qt.white)
        painter.drawEllipse(16, 16, 8, 8)
        painter.translate(-8, -6)

        # draw base URL text
        if not self.isCompacted:
            painter.setPen(Qt.white if isDarkTheme() else Qt.black)
            font = QFont("Segoe UI")
            font.setPixelSize(14)
            painter.setFont(font)
            painter.drawText(QRect(44, 0, 255, 36), Qt.AlignVCenter, self._text)

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, url: str):
        self._text = url
        self.update()


if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication
    import sys
    # from qfluentwidgets import setTheme, Theme
    # from qfluentwidgets import FluentWindow
    # from PySide6.QtWidgets import QApplication, QHBoxLayout

    app = QApplication(sys.argv)
    # w = FluentWindow()

    # setTheme(Theme.DARK)

    widget = NaviAvatarWidget()
    widget.setCompacted(False)
    widget.set_status(True)
    # widget.setFixedWidth(300)
    # w.setWidget(widget)
    widget.show()
    sys.exit(app.exec())
