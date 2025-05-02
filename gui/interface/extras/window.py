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


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = ExtraInterfaceOptionWindow()
    window.show()
    sys.exit(app.exec())
