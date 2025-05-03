from gui.common import VerticalScrollWidget, VerticalFrame, ThemedLabel
from gui.elements import RefineBox, DetailerBox

class ControlRefineInterface(VerticalScrollWidget):
    def __init__(self, parent = None, *args, **kwargs):
        super().__init__(parent = parent, *args, **kwargs)
        refine_label = ThemedLabel("Refiner")
        self.refine_box = RefineBox()
        detailer_label = ThemedLabel("Detailer")
        self.detailer_box = DetailerBox()
        self.setContentSpacing(0)
        self.setContentsMargins(0, 0, 0, 0)
        self.setLayoutMargins(0, 0, 0, 0)

        self.addWidget(refine_label)
        self.addWidget(self.refine_box)
        self.addWidget(detailer_label)
        self.addWidget(self.detailer_box)

    def get_payload(self):
        payload = self.refine_box.get_payload()
        payload.update(self.detailer_box.get_payload())
        return payload

    def set_payload(self, payload: dict):
        self.refine_box.set_payload(payload)
        self.detailer_box.set_payload(payload)

if  __name__ == "__main__":
    from PySide6.QtWidgets import QApplication, QWidget
    app = QApplication([])
    window = ControlRefineInterface(None)
    window.show()
    app.exec()