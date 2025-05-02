from typing import Union

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QStackedWidget, QVBoxLayout
from qfluentwidgets import Pivot, SegmentedWidget, FluentIconBase


class SegmentedStackedWidget(QWidget):

    def __init__(self, parent = None):
        super().__init__(parent = parent)
        self.pivot = SegmentedWidget(self)
        self.stackedWidget = QStackedWidget(self)
        self.vBoxLayout = QVBoxLayout(self)


        # Connect signal and initialize the current tab
        self.stackedWidget.currentChanged.connect(self.onCurrentIndexChanged)

        # self.vBoxLayout.setContentsMargins(30, 0, 30, 30)
        self.vBoxLayout.addWidget(self.pivot, 0)
        self.vBoxLayout.addWidget(self.stackedWidget)
        self.resize(400, 400)

    def addSubInterface(self, widget: QWidget, objectName: str, text: str, icon: Union[FluentIconBase, str, None] = None, is_selected: bool = False):
        widget.setObjectName(objectName)
        self.stackedWidget.addWidget(widget)

        # Use the globally unique objectName as the route key
        self.pivot.addItem(
            routeKey=objectName,
            text=text,
            onClick=lambda: self.stackedWidget.setCurrentWidget(widget),
            icon = icon
        )
        if is_selected:
            self.pivot.setCurrentItem(objectName)
            self.stackedWidget.setCurrentWidget(widget)


    def onCurrentIndexChanged(self, index):
        widget = self.stackedWidget.widget(index)
        self.pivot.setCurrentItem(widget.objectName())
