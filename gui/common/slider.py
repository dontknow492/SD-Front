from PySide6.QtWidgets import QApplication, QSlider, QWidget, QVBoxLayout, QLabel, QStyleOptionSlider, QStyle
from PySide6.QtCore import Qt, QRect, QPoint
from PySide6.QtGui import QPainter, QPen, QColor, QRadialGradient, QMouseEvent


# from PyQt5.QtWidgets import QSlider
# from PyQt5.QtCore import QRect, Qt, QPoint
# from PyQt5.QtGui import QPainter, QColor, QPen,

from qfluentwidgets import themeColor, SystemThemeListener, toggleTheme, setThemeColor
from PySide6.QtWidgets import QSlider
from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QPainter, QColor


class CustomSlider(QSlider):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tick_color = QColor(Qt.GlobalColor.white)
        self.tick_interval = 5
        self._groove_thickness = 20
        self.fill_color = themeColor()
        self.setMinimumHeight(40)
        self._handler_inside_radius = 3
        self.setStyleSheet("QSlider { background: transparent; }")

    def set_fill_color(self, color):
        self.fill_color = QColor(color)
        self.update()

    def set_tick_color(self, color):
        self.tick_color = QColor(color)
        self.update()

    def set_tick_interval(self, interval):
        self.tick_interval = interval
        self.update()

    def set_groove_thickness(self, thickness):
        self._groove_thickness = thickness
        self.update()

    def wheelEvent(self, event):
        event.ignore()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect()
        groove_padding = 10

        if self.orientation() == Qt.Orientation.Horizontal:
            groove_rect = QRect(
                groove_padding,
                (rect.height() - self._groove_thickness) // 2,
                rect.width() - 2 * groove_padding,
                self._groove_thickness
            )
        else:
            groove_rect = QRect(
                (rect.width() - self._groove_thickness) // 2,
                groove_padding,
                self._groove_thickness,
                rect.height() - 2 * groove_padding
            )

        groove_border_radius = self._calcuate_border_radius(groove_rect)

        # Draw groove background
        # painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(200, 200, 200))
        painter.drawRoundedRect(groove_rect, groove_border_radius, groove_border_radius)

        # Draw filled portion
        # painter.setPen(Qt.PenStyle.NoPen)

        pen = painter.pen()
        pen_width = pen.width()
        pen.setColor(self.fill_color)
        pen.setWidth(0)  # Set pen width (optional)
        # pen.setStyle(Qt.PenStyle.DashLine)

        painter.setPen(pen)
        painter.setBrush(self.fill_color)
        handle_pos = self._handle_position(groove_rect)

        if self.orientation() == Qt.Orientation.Horizontal:
            fill_rect = QRect(groove_rect.left() + pen_width, groove_rect.top() + pen_width , max(handle_pos - pen_width * 2, 0), groove_rect.height() - pen_width * 2)
            if fill_rect.width() == 0:
                return
        else:
            fill_rect = QRect(groove_rect.left() + pen_width, handle_pos + pen_width, groove_rect.width() - pen_width*2, max(groove_rect.bottom() - handle_pos + 1 - pen_width*2, 0))
            if fill_rect.height() == 0:
                return

        painter.drawRoundedRect(fill_rect, groove_border_radius, groove_border_radius)

    def _handle_position(self, groove_rect):
        """Return the position in pixels for the current value relative to the groove."""
        value_range = self.maximum() - self.minimum()
        if value_range == 0:
            return 0

        ratio = (self.value() - self.minimum()) / value_range

        if self.orientation() == Qt.Orientation.Horizontal:
            return int(ratio * groove_rect.width())
        else:
            # For vertical sliders, invert the direction
            return groove_rect.top() + int((1 - ratio) * groove_rect.height())

    def _calcuate_border_radius(self, groove_rect):
        """Calculate the border radius based on the groove's height."""
        rect = groove_rect
        return min(rect.width(), rect.height()) / 4


class ThemedSlider(CustomSlider):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.theme_listener = SystemThemeListener()
        self.fill_color = themeColor()

    def paintEvent(self, event):
        self.fill_color = themeColor()
        super().paintEvent(event)



if __name__ == "__main__":
    app = QApplication([])
    window = ThemedSlider(Qt.Orientation.Horizontal)
    # window.set_fill_color(QColor('red'))
    # setThemeColor(QColor("red"))
    window.show()
    window.set_groove_thickness(40)
    print(window.rect())
    app.exec()
