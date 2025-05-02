from gui.components import ComboBoxCard, DoubleSliderCard

from gui.common import GridFrame, DropDownCard
from gui.components import SliderCard, CheckBoxCard
from PySide6.QtWidgets import QWidget

class AdapterBox(GridFrame):
    def __init__(self, parent=None):
        super().__init__(spacing= 6, parent=parent)

        self.adapters = ComboBoxCard(
            "Adapter Type",
            description="""Choose the type of adapter to apply:
            - Text: Enhance text prompts
            - Image: Enhance image prompts
            - Both: Enhance both text and image prompts
            Tip: Text adapters work best for text-to-image workflows""",
            parent=self
        )

        self.adapter_strength = DoubleSliderCard(
            "Adapter Strength",
            description="""Adjust the influence of the adapter:
            0.0: No influence
            0.5: Moderate influence
            1.0: Strong influence
            Adjust based on desired effect""",
            parent=self
        )

        self.crop_to_portrait = CheckBoxCard("Crop to Portrait", description="Crop images to portrait aspect ratio", parent=self)

        self.start = DoubleSliderCard(
            "Early-Stage Adjustment",
            description="""When initial adjustments begin:
            0.0-0.3: Immediate refinement
            0.3-0.6: Balanced approach
            0.6-1.0: Late-stage tweaks
            Lower values help with major composition changes""",
            parent=self
        )

        self.end = DoubleSliderCard(
            "Late-Stage Adjustment",
            description="""When final refinements occur:
            0.0-0.3: Early completion
            0.3-0.7: Standard workflow
            0.7-1.0: Last-moment tweaks
            Higher values preserve early creativity""",
            parent=self
        )

        self.addFullWidthWidget(self.adapters)
        self.addWidget(self.adapter_strength)
        self.addWidget(self.crop_to_portrait)
        self.addWidget(self.start)
        self.addWidget(self.end)


class IPAdapterBox(GridFrame):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent=parent)

        self._adapters: list[QWidget] = []
        self._previous_adapter_count: int = 0

        # Slider to control number of adapters
        self.active_ip_adapters = SliderCard(
            "IP Adapter Weight",
            description="Adjust the influence of the IP Adapter:",
            parent=self
        )
        self.active_ip_adapters.set_range(1, 5)
        self.active_ip_adapters.set_value(1)
        self.active_ip_adapters.value_changed.connect(self._on_adapter_count_changed)

        # Checkbox to unload adapter(s)
        self.unload_ip_adapter = CheckBoxCard(
            "Unload IP Adapter",
            description="Remove the IP Adapter from memory",
            parent=self
        )

        # Initial layout
        self.addWidget(self.active_ip_adapters)
        self.addWidget(self.unload_ip_adapter)

        # Create initial adapter(s)
        self._on_adapter_count_changed(1)

    def _create_adapter(self) -> QWidget:
        card = DropDownCard(AdapterBox(parent=self),"IP Adapter", parent=self)
        return card

    def _on_adapter_count_changed(self, count: int):
        """Add or remove adapter widgets to match the desired count."""
        if count < self._previous_adapter_count:
            # Remove extra adapters
            for adapter in self._adapters[count:]:
                adapter.setParent(None)
                adapter.deleteLater()
            self._adapters = self._adapters[:count]

        elif count > self._previous_adapter_count:
            # Add new adapters
            for _ in range(self._previous_adapter_count, count):
                adapter = self._create_adapter()
                self._adapters.append(adapter)
                self.addFullWidthWidget(adapter)

        # Update previous count and layout
        self.adjustSize()
        self._previous_adapter_count = count
        self.updateGeometry()
        self.update()




if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication, QWidget
    app = QApplication([])
    window = IPAdapterBox()
    window.show()
    app.exec()