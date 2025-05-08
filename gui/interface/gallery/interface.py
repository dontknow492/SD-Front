from typing import List

from PySide6.QtCore import Signal
from loguru import logger
from qfluentwidgets import PushButton

from gui.common import MyTabWidget, VerticalScrollWidget, VerticalTitleCard
from gui.interface.gallery.gallery_tab import GalleryTab
from manager import image_manager

paths = [
    "outputs/txt2img",
    "outputs/img2img",
    "outputs/control",
    "outputs/extra",
]

class HomeTab(VerticalScrollWidget):
    pathClicked = Signal(str)
    def __init__(self, paths: List[str], parent=None):
        super().__init__(parent = parent)

        for path in paths:
            self.add_path(path)

    def add_path(self, path):
        card = VerticalTitleCard(path)
        card.clicked.connect(lambda: self.pathClicked.emit(path))
        self.addWidget(card)



class GalleryInterface(MyTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pre_load_images = 50
        self._paths = image_manager.get_scan_paths()
        self._add_home()


    def onAddNewTab(self):
        self._add_home()

    def _add_home(self):
        home = HomeTab(self._paths, self)
        home.pathClicked.connect(self.on_path_clicked)

        self.addSubInterface(home, f"home_tab_{self.tabCount()}", "Home")

    def on_path_clicked(self, path):
        logger.info(f"Path clicked: {path}")
        tab = GalleryTab(path, parent = self, pre_load=self.pre_load_images)
        # tab = QWidget()
        self.addSubInterface(tab, f"gallery_tab_{self.tabCount()}", path.rsplit("/", 1)[-1])
        self.switchTo(tab)

    def set_preload_images(self, num: int = 50):
        self.pre_load_images = num




if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    window = GalleryInterface()
    # window = HomeTab()
    window.show()
    app.exec()
