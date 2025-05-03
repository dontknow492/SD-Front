from gui.common import VerticalScrollWidget, VerticalFrame, ThemedLabel
from gui.elements import AdvanceBox, CorrectionBox, SamplerBox

class ControlAdvanceInterface(VerticalScrollWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        sampler_label = ThemedLabel("Sampler")
        self.sampler_box = SamplerBox()
        correction_label = ThemedLabel("Correction")
        self.correction_box = CorrectionBox()
        advance_label = ThemedLabel("Advance")
        self.advance_box = AdvanceBox()

        self.addWidget(sampler_label)
        self.addWidget(self.sampler_box)

        self.addWidget(advance_label)
        self.addWidget(self.advance_box)

        self.addWidget(correction_label)
        self.addWidget(self.correction_box)

    def get_payload(self):
        payload = self.sampler_box.get_payload()
        payload.update(self.advance_box.get_payload())
        payload.update(self.correction_box.get_payload())
        return payload

    def set_payload(self, payload: dict):
        self.sampler_box.set_payload(payload)
        self.advance_box.set_payload(payload)
        self.correction_box.set_payload(payload)




if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication, QWidget
    app = QApplication([])
    window = ControlAdvanceInterface(None)
    window.show()
    app.exec()
