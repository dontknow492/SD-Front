from typing import override, Union

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon
from qfluentwidgets import StrongBodyLabel, SpinBox, DoubleSpinBox, setTheme, Theme, CompactSpinBox, \
    CompactDoubleSpinBox, FluentIconBase
from gui.common.slider import ThemedSlider
from gui.common.card import VerticalCard, HorizontalCard
from gui.common.myFrame import HorizontalFrame

class SliderCardBase(VerticalCard):
    value_changed = Signal(object)
    def __init__(self, title: str = "DropBox", description: str = None,
                 info_icon: Union[QIcon, FluentIconBase, str, None] = None, show_info_on_focus: bool = False,
                 parent=None):
        super().__init__(title, description, info_icon, show_info_on_focus, parent=parent)
        # self.setLayoutMargins(0, 0,0, 0)
        # self.setContentSpacing(0)
        if title is None:
            title = "Slider Card"
        self.setup_ui(title)

    def setup_ui(self, title: str = "Slider Card"):
        h_container = HorizontalFrame(self)
        h_container.setLayoutMargins(10, 0,10, 0)
        title_label = StrongBodyLabel(title, h_container)
        title_label.setObjectName("SliderCardTitle")
        title_label.setWordWrap(True)
        self.value_box = self._get_spin_box()
        self.value_box.valueChanged.connect(self.on_spin_box_value_changed)
        h_container.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignLeading)
        h_container.addWidget(self.value_box, alignment=Qt.AlignmentFlag.AlignTrailing)

        self.slider = ThemedSlider(Qt.Orientation.Horizontal, self)
        self.slider.valueChanged.connect(self.on_slider_value_changed)

        self.addWidget(h_container, stretch= 0)
        self.addWidget(self.slider,  alignment=Qt.AlignmentFlag.AlignTop, stretch=1)

    def _get_spin_box(self):
        raise NotImplementedError("This method should be implemented by subclasses. (return a Spin Box instance:")

    def on_slider_value_changed(self):
        raise NotImplementedError("This method should be implemented by subclasses.")

    def get_slider_value(self):
        return self.slider.value()

    def set_range(self, minimum: int, maximum: int):
        self.slider.setMinimum(minimum)
        self.slider.setMaximum(maximum)
        self.value_box.setMinimum(minimum)
        self.value_box.setMaximum(maximum)

    def on_spin_box_value_changed(self):
        self.slider.blockSignals(True)
        self.slider.setValue(self.value_box.value())
        self.slider.blockSignals(False)

    def set_value(self, value):
        self.value_box.setValue(value)

    def value(self):
        return self.value_box.value()

class SliderCard(SliderCardBase):
    def __init__(self, title: str = "DropBox", description: str = None,
                 info_icon: Union[QIcon, FluentIconBase, str, None] = None, show_info_on_focus: bool = False,
                 parent=None):
        super().__init__(title, description, info_icon, show_info_on_focus, parent=parent)
    def _get_spin_box(self):
        box =  CompactSpinBox(self)
        box.clearFocus()
        # box.adjustSize()
        return box
    @override
    def on_slider_value_changed(self):
        self.value_box.blockSignals(True)
        self.value_box.setValue(self.get_slider_value())
        self.value_box.blockSignals(False)
        self.value_changed.emit(self.get_slider_value())

    def setValue(self, value):
        self.set_value(value)


class DoubleSliderCard(SliderCardBase):
    def __init__(self, title: str = "Double Slider Card", description: str = None,
                 info_icon: Union[QIcon, FluentIconBase, str, None] = None, show_info_on_focus: bool = False,
                 parent=None):
        super().__init__(title, description, info_icon, show_info_on_focus, parent=parent)
        self.multiplier = None
        self.set_range(0, 1, 3)

    @override
    def set_range(self, minimum: float, maximum: float, decimal_point: int = 3):
        self.multiplier = pow(10, decimal_point)
        self.value_box.setMinimum(minimum)
        self.value_box.setMaximum(maximum)
        self.value_box.setDecimals(decimal_point)
        self.slider.setMinimum(minimum * self.multiplier)
        self.slider.setMaximum(maximum * self.multiplier)
        self.value_box.setSingleStep(1 / self.multiplier)

    @override
    def get_slider_value(self):
        return self.slider.value() / self.multiplier

    @override
    def _get_spin_box(self):
        box = CompactDoubleSpinBox()
        # box.setMaximumWidth(50)
        # box.setDecimals(3)
        return box

    @override
    def on_slider_value_changed(self):
        self.value_box.blockSignals(True)
        self.value_box.setValue(self.get_slider_value())
        self.value_box.blockSignals(False)
        self.value_changed.emit(self.get_slider_value())

    @override
    def on_spin_box_value_changed(self):
        self.slider.blockSignals(True)
        self.slider.setValue(self.value_box.value() * self.multiplier)
        self.slider.blockSignals(False)

    def setValue(self, value):
        self.set_value(value)


if __name__ == "__main__":
    setTheme(Theme.DARK)
    import sys
    from PySide6.QtWidgets import QApplication, QMainWindow
    app = QApplication(sys.argv)
    window = SliderCard(title = "Size this is")
    window.set_range(0, 2048)
    window.show()
    window.set_value(1024)
    sys.exit(app.exec())