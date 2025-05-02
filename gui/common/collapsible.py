from PySide6.QtGui import QResizeEvent
from PySide6.QtWidgets import (QWidget, QSizePolicy, QVBoxLayout)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from qfluentwidgets import TransparentToggleToolButton

class CollapsibleBase(QWidget):
    def __init__(self, title: str, expanded: bool = False, parent=None):
        super().__init__(parent)

        self.toggle_button = TransparentToggleToolButton(title)
        self.toggle_button.setChecked(expanded)
        self.toggle_button.setText(title)
        self.toggle_button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.toggle_button.setArrowType(Qt.RightArrow)
        self.toggle_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.toggle_button.clicked.connect(self.toggle)

        self.content_area = self.get_content_widget()
        self.content_area.setMaximumHeight(0)  # Start collapsed

        self.toggle_animation = QPropertyAnimation(self.content_area, b"maximumHeight")
        self.toggle_animation.setDuration(500)
        self.toggle_animation.setEasingCurve(QEasingCurve.InOutCubic)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.toggle_button)
        layout.addWidget(self.content_area, stretch=1)

        self._content_height = 0  # Will be updated when content is set

        self.toggle()
        layout.addStretch(1)


    def get_content_widget(self) -> QWidget:
        widget = QWidget()
        return widget

    def toggle(self):
        checked = self.toggle_button.isChecked()
        self.toggle_button.setArrowType(Qt.DownArrow if checked else Qt.RightArrow)

        self.toggle_animation.stop()

        if checked:
            # Ensure we measure the actual content height
            self._content_height = self.content_area.sizeHint().height()
            self.toggle_animation.setStartValue(0)
            self.toggle_animation.setEndValue(self._content_height)
        else:
            self.toggle_animation.setStartValue(self.content_area.maximumHeight())
            self.toggle_animation.setEndValue(0)

        self.toggle_animation.start()

    def set_content_height(self, height: int):
        """Set the height for the content area when expanded."""
        self._content_height = height
        if self.toggle_button.isChecked():
            self.content_area.setMaximumHeight(height)

    def resizeEvent(self, event: QResizeEvent) -> None:
        """Update content height when widget is resized."""
        if self._content_height == 0 and self.content_area.height() > 0:
            self._content_height = self.content_area.height()
        super().resizeEvent(event)

    def set_animation_duration(self, duration: int):
        """Set the animation duration in milliseconds."""
        self.toggle_animation.setDuration(duration)

    def set_animation_curve(self, curve: QEasingCurve):
        """Set the animation curve."""
        self.toggle_animation.setEasingCurve(curve)


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout

    app = QApplication([])

    main = QWidget()
    layout = QVBoxLayout(main)

    collapsible = CollapsibleBase("Adbance setting")

    # inner_layout = QVBoxLayout()
    # inner_layout.addWidget(QLabel("Option 1"))
    # inner_layout.addWidget(QLabel("Option 2"))

    layout.addWidget(collapsible)
    layout.addStretch()
    main.show()
    app.exec()