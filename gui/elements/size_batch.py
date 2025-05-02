from PySide6.QtCore import QObject
from qfluentwidgets import FluentIcon

from gui.components.slider_card import SliderCard
from gui.common.button import ThemedToolButton
from gui.common.myFrame import VerticalFrame, HorizontalFrame
from gui.common.card import VerticalCard, HorizontalCard
from utils import IconManager


class SizeAndBatch(VerticalFrame):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.width_slider = SliderCard("Width", "Width")
        self.width_slider.set_range(64, 2048)
        self.width_slider.set_value(1024)
        self.height_slider = SliderCard("Height", "Height")
        self.height_slider.set_range(64, 2048)
        self.height_slider.set_value(1024)
        self.batch_count_slider = SliderCard("Batch Count", "Batch Count")
        self.batch_count_slider.set_range(1, 100)
        self.batch_size_slider = SliderCard("Batch Size", "Batch Size")
        self.batch_size_slider.set_range(1, 32)

        self.setup_ui()

    def setup_ui(self):
        container = VerticalCard(self)
        ar_container = VerticalCard(container)
        swap_button = ThemedToolButton(IconManager.SWAP, "Swap")
        swap_button.clicked.connect(self.swap_size)
        ar_button = ThemedToolButton(IconManager.ASPECT_RATIO, "Aspect Ratio")
        container.addWidget(swap_button)
        ar_container.addWidget(ar_button)
        size_container = HorizontalFrame(self)
        size_container.setContentsMargins(0, 0, 0, 0)
        size_container.setLayoutMargins(0, 0, 0, 0)
        size_container.addWidget(self.width_slider)
        size_container.addWidget(container)
        size_container.addWidget(self.height_slider)

        batch_container = HorizontalFrame(self)
        batch_container.setContentsMargins(0, 0, 0, 0)
        batch_container.setLayoutMargins(0, 0, 0, 0)
        batch_container.addWidget(self.batch_count_slider)
        batch_container.addWidget(ar_container)
        batch_container.addWidget(self.batch_size_slider)

        self.addWidget(size_container)
        self.addWidget(batch_container)

    def get_payload(self):
        return {
            "width": self.width_slider.value(),
            "height": self.height_slider.value(),
            "n_iter": self.batch_count_slider.value(),
            "batch_size": self.batch_size_slider.value()
        }

    def set_payload(self, data: dict):
        if "width" in data:
            self.width_slider.setValue(data["width"])
        if "height" in data:
            self.height_slider.setValue(data["height"])
        if "n_iter" in data:
            self.batch_count_slider.setValue(data["batch_count"])
        if "batch_size" in data:
            self.batch_size_slider.setValue(data["batch_size"])

    def get_batch_count(self):
        return self.batch_count_slider.value()

    def swap_size(self):
        width = self.width_slider.value()
        height = self.height_slider.value()
        self.width_slider.setValue(height)
        self.height_slider.setValue(width)


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication, QWidget
    app = QApplication([])
    window = SizeAndBatch()
    window.show()
    app.exec()