from PySide6.QtWidgets import QStackedWidget
from qfluentwidgets import FluentIcon

from gui.common import SegmentedStackedWidget
from gui.interface.controls.options import ControlAdvanceInterface, ControlRefineInterface, ControlPromptInterface, ControlIPAdapterInterface
from utils import IconManager


class ControlOptionWindow(SegmentedStackedWidget):
    def __init__(self, parent = None):
        super().__init__(parent = parent)

        self.stacked_widget = QStackedWidget()
        self.prompt_interface = ControlPromptInterface()
        self.refine_interface = ControlRefineInterface()
        self.advance_interface = ControlAdvanceInterface()
        self.ip_adapter_interface = ControlIPAdapterInterface()

        self.addSubInterface(self.prompt_interface, "txt_prompt", "Prompt", icon=IconManager.FOLDER_OPEN, is_selected=True)
        self.addSubInterface(self.refine_interface, "Control_refine", "Refine", icon = IconManager.FOLDER_FAVOURITE_BOOKMARK)
        self.addSubInterface(self.advance_interface, "txt_advance", "Advance", icon=IconManager.FOLDER_FAVOURITE_STAR)
        self.addSubInterface(self.ip_adapter_interface, "Control_ip_adapter", "IP Adapter",  icon=FluentIcon.FOLDER)

        self.stacked_widget.setCurrentIndex(0)

    def get_prompt(self):
        return self.prompt_interface.get_prompt()

    def get_negative_prompt(self):
        return self.prompt_interface.get_negative_prompt()


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = ControlOptionWindow()
    window.show()
    sys.exit(app.exec())
