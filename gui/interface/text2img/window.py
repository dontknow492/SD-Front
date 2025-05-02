from PySide6.QtCore import Qt
from PySide6.QtWidgets import QStackedWidget
from qfluentwidgets import FluentIcon

from gui.common import SegmentedStackedWidget
from gui.interface.text2img.options.advance import TxtAdvanceInterface
from gui.interface.text2img.options.base import TxtBaseInterface
from gui.interface.text2img.options.prompt import TxtPromptInterface
from gui.interface.text2img.options.enhancer import TxtPostProcessingInterface
from utils import IconManager


class TxtOptionWindow(SegmentedStackedWidget):
    def __init__(self, parent = None):
        super().__init__(parent = parent)

        self.stacked_widget = QStackedWidget()
        self.base_interface = TxtBaseInterface()
        self.prompt_interface = TxtPromptInterface()
        self.advance_interface = TxtAdvanceInterface()
        self.post_processing_interface = TxtPostProcessingInterface()

        self.addSubInterface(self.prompt_interface, "txt_prompt", "Prompt", icon = IconManager.FOLDER_OPEN, is_selected=True)
        self.addSubInterface(self.base_interface, "txt_base", "Base",  icon = IconManager.FOLDER_FAVOURITE_BOOKMARK)
        self.addSubInterface(self.advance_interface, "txt_advance", "Advance",  icon = IconManager.FOLDER_FAVOURITE_STAR)
        self.addSubInterface(self.post_processing_interface, "txt_post_processing", "Post Processing", icon = FluentIcon.ZIP_FOLDER)

        self.stacked_widget.setCurrentIndex(0)

    def get_prompt(self):
        return self.prompt_interface.get_prompt()

    def get_negative_prompt(self):
        return self.prompt_interface.get_negative_prompt()

    def get_payload(self):
        payload = {}
        payload.update(self.base_interface.get_payload())
        payload.update(self.prompt_interface.get_payload())
        payload.update(self.advance_interface.get_payload())
        payload.update(self.post_processing_interface.get_payload())
        return payload

    def set_payload(self, payload):
        self.base_interface.set_payload(payload)
        self.prompt_interface.set_payload(payload)
        self.advance_interface.set_payload(payload)
        self.post_processing_interface.set_payload(payload)
        self.stacked_widget.setCurrentIndex(0)


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = TxtOptionWindow()
    window.setWindowFlag(Qt.WindowStaysOnTopHint)
    window.show()
    sys.exit(app.exec())
