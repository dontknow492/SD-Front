from qfluentwidgets import getFont, themeColor, FluentLabelBase, \
    toggleTheme, isDarkTheme
from PySide6.QtCore import Qt, Signal
from qfluentwidgets import BodyLabel, setCustomStyleSheet

class ThemedLabel(FluentLabelBase):
    def __init__(self, text: str, parent=None):
        super().__init__(parent)
        self.setText(text)
        self._set_color()

    def getFont(self):
        return getFont(16)

    def _set_color(self):
        if isDarkTheme():
            self.setTextColor(dark=themeColor())
        else:
            self.setTextColor(light=themeColor())




class ChipBodyLabel(BodyLabel):
    clicked = Signal(str)
    def __init__(self, text: str, parent=None):
        super().__init__(parent)
        self.setText(text)
        self.setObjectName("ChipBodyLabel")

        self.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        self.setWordWrap(True)
        qss = "ChipBodyLabel {background-color: #f0f0f0 ; border-radius: 5px; padding: 2px 5px 2px 5px;}"
        dark_qss = "ChipBodyLabel {background-color: #202020; border-radius: 5px;  padding: 2px 5px 2px 5px;}"
        setCustomStyleSheet(self, qss, dark_qss)

    def mousePressEvent(self, ev, /):
        super().mousePressEvent(ev)
        self.clicked.connect(lambda: self.clicked.emit(self.text()))




if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget
    import sys
    from qfluentwidgets import setTheme, Theme
    # setTheme(Theme.DARK)

    app = QApplication(sys.argv)
    widget = QWidget()
    layout = QVBoxLayout(widget)

    body_label = ChipBodyLabel("This is a custom BodyLabel with selectable text.")
    layout.addWidget(body_label)
    layout.addWidget(ChipBodyLabel("This is another custom BodyLabel."))

    widget.show()
    sys.exit(app.exec())