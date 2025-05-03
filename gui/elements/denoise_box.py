from gui.common import GridFrame
from gui.components import DoubleSliderCard

class DenoiseBox(GridFrame):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.denoise_strength = DoubleSliderCard("Denoise Strength", "Denoise Strength", show_info_on_focus=True, parent = self)
        self.denoise_strength.set_range(0, 1, 2)
        self.denoise_strength.set_value(0.3)

        self.denoise_start = DoubleSliderCard("Denoise Start", "Denoise Start", show_info_on_focus=True, parent = self)
        self.denoise_start.set_range(0, 1, 2)
        self.denoise_start.set_value(0)

        self.addWidget(self.denoise_strength)
        self.addWidget(self.denoise_start)

    def get_payload(self):
        return {
            "denoising_strength": self.denoise_strength.value(),
            "refiner_start": self.denoise_start.value()
        }

    def set_payload(self, payload: dict):
        self.denoise_strength.set_value(payload.get("denoising_strength", self.denoise_strength.value()))
        self.denoise_start.set_value(payload.get("refiner_start", self.denoise_start.value()))


if  __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    window = DenoiseBox()
    window.set_payload({
        "denoise_strength": 0.3,
        "refiner_start": 0.5
    })
    window.show()
    sys.exit(app.exec_())