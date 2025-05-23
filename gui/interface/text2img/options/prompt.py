from gui.common import VerticalScrollWidget, VerticalFrame, ThemedLabel
from gui.elements import PromptBox, SizeAndBatch

class TxtPromptInterface(VerticalScrollWidget):
    def __init__(self, parent = None, *args, **kwargs):
        super().__init__(parent = parent, *args, **kwargs)

        prompt_label =  ThemedLabel("Prompt")
        self.prompt_box = PromptBox()
        size_batch_label = ThemedLabel("Size and Batch")
        self.size_batch = SizeAndBatch()

        self.addWidget(prompt_label)
        self.addWidget(self.prompt_box)
        self.addWidget(size_batch_label)
        self.addWidget(self.size_batch)
        self.setContentSpacing(0)
        self.setContentsMargins(0, 0, 0, 0)
        self.setLayoutMargins(0, 0, 0, 0)

    def get_prompt(self):
        return self.prompt_box.get_prompt()

    def get_negative_prompt(self):
        return self.prompt_box.get_negative_prompt()

    def get_payload(self):
        payload = {}
        payload.update(self.prompt_box.get_payload())
        payload.update(self.size_batch.get_payload())
        return payload

    def set_payload(self, payload):
        self.prompt_box.set_payload(payload)


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication, QWidget
    app = QApplication([])
    window = TxtPromptInterface(None)
    window.show()
    app.exec()
