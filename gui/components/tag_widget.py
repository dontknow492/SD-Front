from typing import List

from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QMouseEvent

from gui.common import HorizontalScrollWidget, ChipBodyLabel


class TagWidget(HorizontalScrollWidget):
    tagClicked = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent = parent)
        self._tags = []
        self.setLayoutMargins(0, 0, 0, 0)
        self.setMaximumHeight(30)
        # self.scrollContainer_layout.setContentsMargins(0, 0, 0, 0)

    def add_tags(self, tags: List[str]):
        for tag in tags:
            self.add_tag(tag)

    def add_tag(self, tag):
        if tag not in self._tags:
            self._tags.append(tag)
            chip_label = ChipBodyLabel(tag)
            chip_label.adjustSize()
            chip_label.setFixedSize(chip_label.size())


            chip_label.clicked.connect(self.tagClicked.emit)

            self.addWidget(chip_label)


    def remove_tag(self, tag):
        for i in range(self.layout().count()):
            widget = self.layout().itemAt(i).widget()
            if isinstance(widget, ChipBodyLabel) and widget.text() == tag:
                self.layout().removeWidget(widget)
                widget.deleteLater()
                self._tags.remove(tag)
                break

if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget

    app = QApplication(sys.argv)
    widget = TagWidget()
    widget.add_tags(['1', '2', '2', '3', '5'])
    widget.show()
    sys.exit(app.exec())
