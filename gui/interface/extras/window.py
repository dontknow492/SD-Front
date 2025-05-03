from gui.common import VerticalScrollWidget, ThemedLabel
from gui.elements import UpscaleBox, GFPGANBox, CodeformerBox, RemoveBackgroundBox


class ExtraOptionWindow(VerticalScrollWidget):
    def __init__(self, parent = None):
        super().__init__(parent = parent)

        upscaler_label = ThemedLabel("Upscaler")
        self.upscale_box = UpscaleBox()
        gfgpans_label = ThemedLabel("GFPGAN")
        self.gfpgan_box = GFPGANBox()
        codeformer_label = ThemedLabel("Codeformer")
        self.codeformer_box = CodeformerBox()
        remove_background_label = ThemedLabel("Remove Background")
        self.remove_background_box = RemoveBackgroundBox()

        self.addWidget(upscaler_label)
        self.addWidget(self.upscale_box)
        self.addWidget(gfgpans_label)
        self.addWidget(self.gfpgan_box)
        self.addWidget(codeformer_label)
        self.addWidget(self.codeformer_box)
        self.addWidget(remove_background_label)
        self.addWidget(self.remove_background_box)

    def get_payload(self):
        #todo: implement this
        return {}
    #     payload = self.upscale_box.get_payload()
    #     payload.update(self.gfpgan_box.get_payload())
    #     payload.update(self.codeformer_box.get_payload())
    #     payload.update(self.remove_background_box.get_payload())
    #     return payload

    def set_payload(self, payload: dict):
        #todo: implement this
        pass
    #     self.upscale_box.set_payload(payload)
    #     self.gfpgan_box.set_payload(payload)
    #     self.codeformer_box.set_payload(payload)
    #     self.remove_background_box.set_payload(payload)


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = ExtraOptionWindow()
    window.show()
    sys.exit(app.exec())
