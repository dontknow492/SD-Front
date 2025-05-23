from PySide6.QtWidgets import QStackedWidget
from gui.common import SegmentedStackedWidget
from gui.interface.img2img.options import ImgBaseInterface, ImgPromptInterface, ImgAdvanceInterface
from utils import IconManager


class ImgOptionWindow(SegmentedStackedWidget):
    def __init__(self, parent = None):
        super().__init__(parent = parent)

        self.stacked_widget = QStackedWidget()
        self.base_interface = ImgBaseInterface()
        self.prompt_interface = ImgPromptInterface()
        self.advance_interface = ImgAdvanceInterface()

        self.addSubInterface(self.prompt_interface, "txt_prompt", "Prompt", icon=IconManager.FOLDER_OPEN, is_selected=True)
        self.addSubInterface(self.base_interface, "txt_base", "Base", icon=IconManager.FOLDER_FAVOURITE_BOOKMARK)
        self.addSubInterface(self.advance_interface, "txt_advance", "Advance", icon=IconManager.FOLDER_FAVOURITE_STAR)

        self.stacked_widget.setCurrentIndex(0)

    def get_prompt(self):
        return self.prompt_interface.get_prompt()

    def get_negative_prompt(self):
        return self.prompt_interface.get_negative_prompt()

    def get_payload(self):
        payload = self.base_interface.get_payload()
        payload.update(self.prompt_interface.get_payload())
        payload.update(self.advance_interface.get_payload())
        return payload

    def set_payload(self, payload: dict):
        self.base_interface.set_payload(payload)
        self.prompt_interface.set_payload(payload)
        self.advance_interface.set_payload(payload)


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = ImgOptionWindow()
    window.show()
    sys.exit(app.exec())
