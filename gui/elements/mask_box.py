from gui.common import GridFrame
from gui.components import DoubleSliderCard, SliderCard, RadioCard

class MaskBox(GridFrame):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.blur =  SliderCard("Blur", "Blur", show_info_on_focus=True, parent = self)
        self.blur.set_range(0, 32)
        self.blur.setValue(4)

        self.padding = SliderCard("Padding", "Padding", show_info_on_focus=True, parent = self)
        self.padding.set_range(0, 256)
        self.padding.setValue(32)

        self.alpha = DoubleSliderCard("Alpha", "Alpha", show_info_on_focus=True, parent = self)
        self.alpha.set_range(0, 1, 2)
        self.alpha.setValue(1)

        self.inpaint_mode = RadioCard("Inpaint Mode", show_info_on_focus=True, parent = self)
        self.masked_button = self.inpaint_mode.add_option("masked")
        self.inverted_button = self.inpaint_mode.add_option("inverted", is_selected=False)
        self.inpaint_area = RadioCard("Inpaint Area", show_info_on_focus=True, parent = self)
        self.full_button = self.inpaint_area.add_option("full")
        self.masked_area_button = self.inpaint_area.add_option("masked", is_selected=False)
        self.addWidget(self.blur)
        self.addWidget(self.padding)

        self.addFullWidthWidget(self.alpha)

        self.addWidget(self.inpaint_mode)
        self.addWidget(self.inpaint_area)

    def get_payload(self):
        if self.masked_button.isChecked():
            inverted = 0
        elif self.inverted_button.isChecked():
            inverted = 1
        else:
            inverted = 0  # Default fallback, just in case

        return {
            "mask_blur": self.blur.value(),
            "inpaint_full_res": self.full_button.isChecked(),
            "inpaint_full_res_padding": 32,
            "inpainting_mask_invert": inverted,
        }

    def set_payload(self, payload: dict):
        if not isinstance(payload, dict):
            return

        self.blur.setValue(payload.get("mask_blur", self.blur.value()))

        full = payload.get("inpaint_full_res")
        if full:
            self.full_button.setChecked(full)
            self.masked_area_button.setChecked(not full)

        inverted = payload.get("inpainting_mask_invert")
        if inverted:
            self.masked_button.setChecked(inverted == 0)
            self.inverted_button.setChecked(inverted == 1)

        self.padding.setValue(payload.get("inpaint_full_res_padding", self.padding.value()))

    def get_alpha(self):
        return self.alpha.value()

    def set_alpha(self, value):
        self.alpha.setValue(value)


if  __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    window = MaskBox()
    window.show()
    window.set_payload({"mask_blur": 4, "inpaint_full_res": False, "inpainting_mask_invert": 1})
    print(window.get_payload())
    sys.exit(app.exec())
