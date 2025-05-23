from gui.common import VerticalScrollWidget, VerticalFrame, ThemedLabel
from gui.elements import SamplerBox, SeedBox, DenoiseBox, MaskBox

class ImgBaseInterface(VerticalScrollWidget):
    def __init__(self, parent = None, *args, **kwargs):
        super().__init__(parent = parent, *args, **kwargs)
        sampler_label = ThemedLabel("Sampler")
        self.sampler_box = SamplerBox()
        seed_label = ThemedLabel("Seed")
        self.seed_box = SeedBox()
        denoise_label = ThemedLabel("Denoise")
        self.denoise_box = DenoiseBox()
        mask_label = ThemedLabel("Mask")
        self.mask_box = MaskBox()


        self.setContentSpacing(0)
        self.setContentsMargins(0, 0, 0, 0)
        self.setLayoutMargins(0, 0, 0, 0)

        self.addWidget(sampler_label)
        self.addWidget(self.sampler_box)

        self.addWidget(seed_label)
        self.addWidget(self.seed_box)

        self.addWidget(denoise_label)
        self.addWidget(self.denoise_box)
        self.addWidget(mask_label)
        self.addWidget(self.mask_box)

    def get_payload(self):
        payload = self.sampler_box.get_payload()
        payload.update(self.seed_box.get_payload())
        payload.update(self.denoise_box.get_payload())
        payload.update(self.mask_box.get_payload())
        return payload

    def set_payload(self, payload: dict):
        self.sampler_box.set_payload(payload)
        self.seed_box.set_payload(payload)
        self.denoise_box.set_payload(payload)
        self.mask_box.set_payload(payload)

if  __name__ == "__main__":
    from PySide6.QtWidgets import QApplication, QWidget
    app = QApplication([])
    window = ImgBaseInterface(None)
    window.show()
    app.exec()