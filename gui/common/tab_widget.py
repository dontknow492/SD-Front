from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt, QObject
from PySide6.QtWidgets import QLabel, QWidget, QStackedWidget, QVBoxLayout
from qfluentwidgets import TabBar
from qfluentwidgets import OpacityAniStackedWidget, PopUpAniStackedWidget
from typing import Optional


class MyTabWidget(QWidget):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.tabBar = TabBar(self)
        self.stackedWidget = PopUpAniStackedWidget(self)
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.counter = 0

        # Connect signals to slots
        self.stackedWidget.currentChanged.connect(self.onCurrentIndexChanged)
        self.tabBar.tabAddRequested.connect(self.onAddNewTab)
        self.tabBar.tabCloseRequested.connect(self.onCloseTab)

        # Layout setup
        # self.vBoxLayout.setContentsMargins(30, 0, 30, 30)
        self.vBoxLayout.addWidget(self.tabBar, 0, Qt.AlignmentFlag.AlignTop)
        self.vBoxLayout.addWidget(self.stackedWidget)
        self.resize(400, 400)

    def addSubInterface(self, widget: QWidget, objectName: str, text: str) -> None:
        """
        Add a new widget to the stacked widget and a corresponding tab in the tab bar.
        """
        if self.findChild(QWidget, objectName):
            QMessageBox.warning(self, "Tab Exists", f"A tab with objectName '{objectName}' already exists.")
            return

        widget.setObjectName(objectName)
        self.stackedWidget.addWidget(widget)

        self.tabBar.addTab(
            routeKey=objectName,
            text=text,
            onClick=lambda: self.stackedWidget.setCurrentWidget(widget)
        )

    def switchTo(self, widget: QWidget) -> None:
        """
        Switch to the specified widget in the stacked widget.
        """
        self.stackedWidget.setCurrentWidget(widget)

    def onCurrentIndexChanged(self, index: int) -> None:
        """
        Update tab bar selection when the current stacked widget index changes.
        """
        widget = self.stackedWidget.widget(index)
        if widget:
            self.tabBar.setCurrentTab(widget.objectName())

    def onAddNewTab(self) -> None:
        """
        Handler to dynamically create a new tab with a QLabel.
        """
        label_text = f"Tab {self.counter}"
        w = QLabel(label_text)
        self.addSubInterface(w, label_text, label_text)
        self.counter += 1

    def onCloseTab(self, index: int) -> None:
        """
        Handler to close and delete a tab by index.
        """
        try:
            item = self.tabBar.tabItem(index)
            widget = self.findChild(QWidget, item.routeKey())
            if widget:
                self.stackedWidget.removeWidget(widget)
                widget.deleteLater()
            self.tabBar.removeTab(index)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to close tab: {e}")

    def tabCount(self) -> int:
        return self.tabBar.count()

    def hasTab(self, objectName: str) -> bool:
        """
        Check if a tab with a specific objectName exists.
        """
        return self.findChild(QWidget, objectName) is not None

    def switchToTab(self, objectName: str) -> bool:
        """
        Try to switch to a tab by its objectName.
        Returns True if successful, False otherwise.
        """
        widget = self.findChild(QWidget, objectName)
        if widget:
            self.stackedWidget.setCurrentWidget(widget)
            return True
        return False

    def currentTabWidget(self) -> Optional[QWidget]:
        """
        Returns the currently visible widget.
        """
        return self.stackedWidget.currentWidget()

    def allTabs(self) -> list[str]:
        """
        Returns a list of objectNames of all tabs.
        """
        return [self.stackedWidget.widget(i).objectName() for i in range(self.stackedWidget.count())]



if __name__ == "__main__":
    app = QApplication([])
    demo = MyTabWidget()
    demo.show()
    app.exec()
