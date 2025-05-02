import math

from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QWidget, QVBoxLayout, QGraphicsOpacityEffect

from gui.common import WaitingSpinner
from qfluentwidgets import isDarkTheme


class LoadingOverlay(QWidget):
    def __init__(
            self,
            parent: QWidget = None,
            center_on_parent: bool = True,
            disable_parent_when_spinning: bool = False,
            modality: Qt.WindowModality = Qt.NonModal,
            roundness: float = 100.0,
            fade: float = 80.0,
            lines: int = 20,
            line_length: int = 10,
            line_width: int = 2,
            radius: int = 10,
            speed: float = math.pi / 2,
            color: QColor = QColor(0, 0, 0),
    ) -> None:
        super().__init__(parent)
        self._radius = (0, 0, 0, 0)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        # self.setStyleSheet("background-color: rgba(255, 255, 255, 200);")
        self.setVisible(False)
        self.setFixedSize(parent.size())

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.spinner = WaitingSpinner(self, center_on_parent, disable_parent_when_spinning, modality, roundness, fade, lines,
                                    line_length, line_width, radius, speed, color)
        self.spinner.start()
        layout.addWidget(self.spinner)

        # Opacity effect and animation
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)

        self.fade_anim = QPropertyAnimation(self.opacity_effect, b"opacity", self)
        self.fade_anim.setDuration(800)
        self.fade_anim.setEasingCurve(QEasingCurve.OutCubic)

        self.fade_anim.finished.connect(self._on_fade_finished)

        self._hiding = False

    def show_overlay(self):
        self.setVisible(True)
        self._hiding = False
        self.spinner.start()
        self.fade_anim.stop()
        self.fade_anim.setStartValue(0.0)
        self.fade_anim.setEndValue(1.0)
        self.fade_anim.start()

    def hide_overlay(self):
        self._hiding = True
        self.spinner.stop()
        self.fade_anim.stop()
        self.fade_anim.setStartValue(1.0)
        self.fade_anim.setEndValue(0.0)
        self.fade_anim.start()

    def _on_fade_finished(self):
        if self._hiding:
            self.spinner.stop()
            self.setVisible(False)

    def resizeEvent(self, event):
        self.setFixedSize(self.parent().size())
        super().resizeEvent(event)

    def paintEvent(self, event, /):
        if isDarkTheme():
            self.spinner.color = Qt.white
            self.setStyleSheet(
                f"""
                    background-color: rgba(0, 0, 0, 200);
                    border-top-left-radius: {self._radius[0]}px;
                    border-top-right-radius: {self._radius[1]}px;
                    border-bottom-right-radius: {self._radius[2]}px;
                    border-bottom-left-radius: {self._radius[3]}px;
                """
            )
        else:
            self.spinner.color = Qt.black
            self.setStyleSheet(
                f"""
                background-color: rgba(255, 255, 255, 200);
                border-top-left-radius: {self._radius[0]}px;
                border-top-right-radius: {self._radius[1]}px;
                border-bottom-right-radius: {self._radius[2]}px;
                border-bottom-left-radius: {self._radius[3]}px;
                """
            )

    @property
    def getSpinner(self):
        return self.spinner

    def setBorderRadius(self, topleft: int, topright: int, bottomright: int, bottomleft: int):
        self._radius = (topleft, topright, bottomright, bottomleft)



