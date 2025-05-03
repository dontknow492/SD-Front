from gui.common import VerticalScrollWidget, VerticalFrame, ThemedLabel
from gui.elements import AdvanceBox, CorrectionBox, DetailerBox

class ImgAdvanceInterface(VerticalScrollWidget):
    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent=parent, *args, **kwargs)
        detailer_label = ThemedLabel("Detailer")
        self.detailer_box = DetailerBox()
        correction_label = ThemedLabel("Correction")
        self.correction_box = CorrectionBox()
        advance_label = ThemedLabel("Advance")
        self.advance_box = AdvanceBox()

        self.addWidget(detailer_label)
        self.addWidget(self.detailer_box)

        self.addWidget(advance_label)
        self.addWidget(self.advance_box)

        self.addWidget(correction_label)
        self.addWidget(self.correction_box)

    def get_payload(self):
        payload = self.detailer_box.get_payload()
        payload.update(self.correction_box.get_payload())
        payload.update(self.advance_box.get_payload())
        return payload

    def set_payload(self, payload: dict):
        self.detailer_box.set_payload(payload)
        self.correction_box.set_payload(payload)
        self.advance_box.set_payload(payload)


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication, QWidget
    app = QApplication([])
    window = ImgAdvanceInterface(None)
    window.show()
    app.exec()
