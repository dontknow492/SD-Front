from gui.common import VerticalScrollWidget, VerticalFrame, ThemedLabel
from gui.elements import PromptBox, SizeAndBatch,  ResizeBox

class ImgPromptInterface(VerticalScrollWidget):
    def __init__(self, parent = None, *args, **kwargs):
        super().__init__(parent = parent, *args, **kwargs)

        prompt_label =  ThemedLabel("Prompt")
        self.prompt_box = PromptBox()
        resize_label = ThemedLabel("Resize")
        self.resize_box = ResizeBox()

        self.addWidget(prompt_label)
        self.addWidget(self.prompt_box)
        self.addWidget(resize_label)
        self.addWidget(self.resize_box)
        self.setContentSpacing(0)
        self.setContentsMargins(0, 0, 0, 0)
        self.setLayoutMargins(0, 0, 0, 0)

    def get_prompt(self):
        return self.prompt_box.get_prompt()

    def get_negative_prompt(self):
        return self.prompt_box.get_negative_prompt()


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication, QWidget
    app = QApplication([])
    window = ImgPromptInterface(None)
    window.show()
    app.exec()
