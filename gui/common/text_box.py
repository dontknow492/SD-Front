from qfluentwidgets import TextEdit
from PySide6.QtCore import QSize

class MyTextEdit(TextEdit):
    def __init__(self, parent=None, max_height=300, min_height=30):
        super().__init__(parent)
        if max_height == -1:
            max_height = 9999
        self._max_height = max_height
        self._min_height = min_height


        self.document().contentsChanged.connect(self.adjust_height)

        self.setMinimumHeight(min_height)
        self.setMaximumHeight(max_height)
        self.setSizePolicy(self.sizePolicy().horizontalPolicy(),
                           self.sizePolicy().verticalPolicy())

    def adjust_height(self):
        doc_height = self.document().size().height()
        new_height = max(self._min_height, min(doc_height + 10, self._max_height))
        self.setFixedHeight(int(new_height))

    def sizeHint(self):
        return QSize(self.width(), self.height())


from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout
import sys


class DemoWindow(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        self.text_edit = MyTextEdit(max_height=-1)
        layout.addWidget(self.text_edit)

        self.setLayout(layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DemoWindow()
    window.show()
    sys.exit(app.exec())

