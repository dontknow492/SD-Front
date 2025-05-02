from gui.common import VerticalScrollWidget, VerticalFrame, ThemedLabel
from gui.elements import AdvanceBox, CorrectionBox, DetailerBox, RefineBox



class TxtPostProcessingInterface(VerticalScrollWidget):
    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent=parent, *args, **kwargs)
        detailer_label = ThemedLabel("Detailer")
        self.detailer_box = DetailerBox()

        refiner_label = ThemedLabel("Refiner")
        self.refiner_box = RefineBox()

        self.addWidget(refiner_label)
        self.addWidget(self.refiner_box)

        self.addWidget(detailer_label)
        self.addWidget(self.detailer_box)


    def get_payload(self):
        payload = {}
        payload.update(self.detailer_box.get_payload())
        payload.update(self.refiner_box.get_payload())
        return payload

    def set_payload(self, payload):
        self.detailer_box.set_payload(payload)
        self.refiner_box.set_payload(payload)





if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication, QWidget
    app = QApplication([])
    window = TxtPostProcessingInterface(None)
    window.show()
    print(window.get_payload())
    app.exec()
