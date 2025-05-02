from PySide6.QtCore import QPoint, Qt
from qfluentwidgets import FluentIcon, RoundMenu, Action
from loguru import logger

from gui.components.slider_card import SliderCard
from gui.common.button import ThemedToolButton
from gui.common.myFrame import VerticalFrame, HorizontalFrame
from gui.common.card import VerticalCard, HorizontalCard
from utils import IconManager


class SizeAndBatch(VerticalFrame):

    def __init__(self, parent=None):
        super().__init__(parent)

        self._aspect_ratio = 'free'
        self.width_slider = SliderCard("Width", "Width")
        self.width_slider.set_range(64, 2048)
        self.width_slider.set_value(1024)
        self.width_slider.slider.valueChanged.connect(self._on_width_changed)

        self.height_slider = SliderCard("Height", "Height")
        self.height_slider.set_range(64, 2048)
        self.height_slider.set_value(1024)
        self.height_slider.slider.valueChanged.connect(self._on_height_changed)

        self.batch_count_slider = SliderCard("Batch Count", "Batch Count")
        self.batch_count_slider.set_range(1, 100)

        self.batch_size_slider = SliderCard("Batch Size", "Batch Size")
        self.batch_size_slider.set_range(1, 32)

        self.ar_button = ThemedToolButton(None, "Aspect Ratio")
        self.ar_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
        self.ar_button.setText("Free")
        self.ar_button.adjustSize()
        self.ar_button.setFixedWidth(self.ar_button.width())
        # self.ar_button.

        self.aspect_ratios: list[str] = [
            "Free", "1:1", "3:2", "4:3", "5:4", "7:5", "16:9",
            "21:9", "18:9", "9:16", "4:5", "16:10", "32:9"
        ]

        self.ar_menu = RoundMenu(parent=self)
        for ratio in self.aspect_ratios:
            self.ar_menu.addAction(Action(ratio))
        self.ar_menu.triggered.connect(self._on_ar_selected)

        self.setup_ui()
        self.ar_button.clicked.connect(self.show_ar_menu)

    def setup_ui(self):
        container = VerticalCard(self)
        ar_container = VerticalCard(container)

        swap_button = ThemedToolButton(IconManager.SWAP, "Swap")
        swap_button.clicked.connect(self.swap_size)
        swap_button.setFixedWidth(self.ar_button.width())

        container.addWidget(swap_button)
        ar_container.addWidget(self.ar_button)

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
        self.width_slider.setValue(data.get("width", self.width_slider.value()))
        self.height_slider.setValue(data.get("height", self.height_slider.value()))
        self.batch_count_slider.setValue(data.get("n_iter", self.batch_count_slider.value()))
        self.batch_size_slider.setValue(data.get("batch_size", self.batch_size_slider.value()))

    def get_batch_count(self):
        return self.batch_count_slider.value()

    def swap_size(self):
        width, height = self.width_slider.value(), self.height_slider.value()
        self.width_slider.setValue(height)
        self.height_slider.setValue(width)

    def add_aspect_ratio(self, ratio: str):
        if ratio not in self.aspect_ratios:
            self.aspect_ratios.append(ratio)
            self.ar_menu.addAction(Action(ratio))

    def show_ar_menu(self):
        button_pos = self.ar_button.mapToGlobal(self.ar_button.rect().bottomLeft())
        self.ar_menu.exec(button_pos)

    def _on_ar_selected(self, action):
        ratio = action.text()
        self.adjust_size_ar(ratio)

    def adjust_size_ar(self, ratio: str):
        self.ar_button.setText(ratio)
        self._aspect_ratio = ratio
        if ratio.lower() == "free":
            return

        try:
            w_ratio, h_ratio = map(float, ratio.split(":"))
            width = self.width_slider.value()
            height = self.height_slider.value()
            if w_ratio>h_ratio:
                height = self.calculate_corresponding_dimension(width, ratio)
                self.height_slider.setValue(height)
            elif h_ratio>w_ratio:
                width = self.calculate_corresponding_dimension(height, ratio, False)
                self.width_slider.setValue(width)
            elif h_ratio == w_ratio:
                self.width_slider.setValue(height)

        except Exception as e:
            logger.error(f"Failed to apply aspect ratio '{ratio}': {e}")

    def _on_width_changed(self, value: int):
        """
        Handle width change and adjust height based on aspect ratio.

        Args:
            value (int): The new width value.
        """
        if self._aspect_ratio.lower() != "free":
            self.height_slider.setValue(self.calculate_corresponding_dimension(value, self._aspect_ratio, False))

    def _on_height_changed(self, value: int):
        """
        Handle height change and adjust width based on aspect ratio.

        Args:
            value (int): The new height value.
        """
        if self._aspect_ratio.lower() != "free":
            self.width_slider.setValue(self.calculate_corresponding_dimension(value, self._aspect_ratio))

    def calculate_corresponding_dimension(self, value: int, ratio: str, is_width: bool = True) -> int:
        """
        Calculate the corresponding dimension (height or width) based on aspect ratio.

        Args:
            value (int): The width or height value to adjust.
            ratio (str): The aspect ratio in the form of 'width:height'.
            is_width (bool): If True, the value is for width and we calculate height.
                             If False, the value is for height and we calculate width.

        Returns:
            int: The corresponding height or width based on the aspect ratio.
        """
        try:
            w_ratio, h_ratio = map(int, ratio.split(":"))

            if is_width:
                # Calculate height based on width and aspect ratio
                return int(value * h_ratio / w_ratio)
            else:
                # Calculate width based on height and aspect ratio
                return int(value * w_ratio / h_ratio)

        except Exception as e:
            logger.error(f"Error calculating corresponding dimension for ratio '{ratio}': {e}")
            return value  # Return original value if there's an error


if __name__  == "__main__":
    from PySide6.QtWidgets import QApplication
    app = QApplication([])
    widget = SizeAndBatch()
    widget.show()
    app.exec()