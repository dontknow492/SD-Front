from gui.common import VerticalScrollWidget, VerticalFrame, ThemedLabel
from gui.elements import IPAdapterBox

class ControlIPAdapterInterface(VerticalScrollWidget):
    def __init__(self, parent = None, *args, **kwargs):
        super().__init__(parent = parent, *args, **kwargs)
        ip_adapter_label = ThemedLabel("IP Adapter")
        self.ip_adapter_box = IPAdapterBox()

        self.addWidget(ip_adapter_label)
        self.addWidget(self.ip_adapter_box)


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication, QWidget
    app = QApplication([])
    window = ControlIPAdapterInterface(None)
    window.show()
    app.exec()