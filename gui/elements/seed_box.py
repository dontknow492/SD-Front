from gui.common import GridFrame, ThemedToolButton, HorizontalTitleCard, VerticalCard, VerticalFrame
from gui.components import CheckBoxCard, ComboBoxCard, SliderCard, TextEditCard, DoubleSliderCard, MySpinBox, MyDoubleSpinBox
from qfluentwidgets import SpinBox, DoubleSpinBox


class SeedBox(VerticalFrame):
    def __init__(self, parent = None):
        super().__init__(parent = parent)
        self.setContentsMargins(0, 0, 0, 0)

        self.initial_seed = MySpinBox("Initial Seed",  description="Set the seed for the image generation", show_info_on_focus=True, parent=self)
        # self.initial Seed.spinBox().setRange(-1, 2**32 - 1)
        self.initial_seed.spinBox().setRange(-1, 2**31 - 10)
        self.initial_seed.spinBox().setValue(-1)

        self.variation_seed = MySpinBox("Variation Seed", description="Set the seed for the image generation", show_info_on_focus=True, parent=self)
        self.variation_seed.spinBox().setRange(-1, 2**31 - 1)
        self.variation_seed.spinBox().setValue(-1)

        self.variation_strength = DoubleSliderCard("Variation Strength", description="Set the strength of the variation", show_info_on_focus=True, parent=self)
        self.variation_strength.set_range(0, 1, 2)
        self.variation_strength.setValue(0)

        self.addWidget(self.initial_seed)
        self.addWidget(self.variation_seed)
        self.addWidget(self.variation_strength)

    def  get_payload(self):
        return {
            "seed": self.initial_seed.value(),
            "subseed": self.variation_seed.value(),
            "subseed_strength": self.variation_strength.value()
        }

    def set_payload(self, data: dict):
        if "seed" in data:
            self.initial_seed.setValue(data["seed"])
        if "subseed" in data:
            self.variation_seed.setValue(data["subseed"])
        if "subseed_strength" in data:
            self.variation_strength.setValue(data["subseed_strength"])



if  __name__ == "__main__":
    from PySide6.QtWidgets import QApplication, QWidget
    app = QApplication([])
    window = SeedBox()
    window.set_payload({"seed": 123, "subseed": 456, "subseed_strength": 0.5})
    print(window.get_payload())
    window.show()
    app.exec()