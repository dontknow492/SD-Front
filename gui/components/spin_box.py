from typing import Any

from qfluentwidgets import SpinBox, DoubleSpinBox, FluentIconBase

from gui.common import HorizontalTitleCard


class QIcon:
    pass


class SpinBoxBase(HorizontalTitleCard):
    def __init__(self,
        title: str = "Horizontal Card",
        description: str | None = None,
    info_icon: FluentIconBase | QIcon | str | None = None,
    show_info_on_focus: bool = False,
    parent: Any = None):
        super().__init__(title, description, info_icon, show_info_on_focus, parent)
        self.setContentsMargins(0, 0, 0, 0)

        self.spin_box = self._spin_box()

        self.addWidget(self.spin_box)

    def get_value(self):
        return self.spin_box.value()

    def _spin_box(self):
        raise NotImplementedError("Subclasses must implement the _spin_box method.")

    def spinBox(self):
        return self.spin_box

class MySpinBox(SpinBoxBase):
    def __init__(self,
                 title: str = "Horizontal Card",
                 description: str | None = None,
                 info_icon: FluentIconBase | QIcon | str | None = None,
                 show_info_on_focus: bool = False,
                 parent: Any = None):
        super().__init__(title, description, info_icon, show_info_on_focus, parent)

    def _spin_box(self):
        return SpinBox(self)

    def value(self):
        return self.spinBox().value()

    def setValue(self, value):
        return self.spinBox().setValue(value)


class MyDoubleSpinBox(SpinBoxBase):
    def __init__(self,
                 title: str = "Horizontal Card",
                 description: str | None = None,
                 info_icon: FluentIconBase | QIcon | str | None = None,
                 show_info_on_focus: bool = False,
                 parent: Any = None):
        super().__init__(title, description, info_icon, show_info_on_focus, parent)

    def _spin_box(self):
        return DoubleSpinBox(self)


if  __name__ == "__main__":
    from PySide6.QtWidgets import QApplication, QWidget
    app = QApplication([])
    window = MySpinBox()
    window.show()
    app.exec()