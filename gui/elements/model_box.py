from gui.common import CollapsibleBase, GridFrame
from gui.components import LandscapeModelCard, ComboBoxCard
from qfluentwidgets import PushButton, ComboBox
from PySide6.QtWidgets import QVBoxLayout, QGroupBox, QWidget, QHBoxLayout

class ModelBox(CollapsibleBase):
    def __init__(self, parent=None, expanded=False):
        super().__init__("Model", expanded, parent)

        self._card_mappings = {
            'model': {},
            'lora': {},
            'lycoris': {},
            'hyper': {},
            'embed': {}
        }

        self._group_boxes = {}
        self.content_layout = QVBoxLayout(self.content_area)

        # Create each groupbox
        for key, title in {
            'model': "Model",
            'lora': "Lora",
            'lycoris': "Lycoris",
            'hyper': "Hypernetwork",
            'embed': "Embedding"
        }.items():
            box = QGroupBox(title)
            box.setLayout(QVBoxLayout())
            box.setVisible(False)
            self._group_boxes[key] = box
            self.content_layout.addWidget(box)

        # Buttons to add items
        button_container = GridFrame(self.content_area)
        button_container.layout().setContentsMargins(0, 0, 0, 0)

        buttons = {
            "Add Lora": self.add_lora,
            "Add Lycoris": self.add_lycoris,
            "Add Hyper": self.add_hyper,
            "Add Embedding": self.add_embedding
        }

        for label, slot in buttons.items():
            btn = PushButton(label)
            btn.clicked.connect(slot)
            button_container.addWidget(btn)

        btn = PushButton("Add Model")
        btn.clicked.connect(lambda: self.add_model())
        button_container.addFullWidthWidget(btn)

        self.content_layout.addWidget(button_container)


        self.vae_box = ComboBoxCard("VAE", "Choose Vae")
        self.content_layout.addWidget(self.vae_box)


    def _add_card(self, group_name: str, path: str, show_weight: bool = True):
        print(path)
        if path in self._card_mappings[group_name]:
            print(f"[{group_name}] already added:", path)
            return

        cover_path = r"D:\Program\SD Front\samples\Extras\00000-2025-04-10-hassakuXLIllustrious_v21fix.jpg"
        card = LandscapeModelCard(cover_path, "Animagine XL", path)
        card.show_weight(show_weight)

        group_box: QGroupBox = self._group_boxes[group_name]
        group_box.layout().addWidget(card)
        group_box.setVisible(True)

        self._card_mappings[group_name][path] = card
        # card.deleteSignal.connect(lambda: self._remove_card(group_name, path))
        height = group_box.sizeHint().height() + self.content_area.height()
        self.set_content_height(height)
        self.adjustSize()

    def _remove_card(self, group_name: str, path: str):
        if path not in self._card_mappings[group_name]:
            return

        card = self._card_mappings[group_name].pop(path)
        print(f"Removed [{group_name}]:", path)

        layout = self._group_boxes[group_name].layout()
        layout.removeWidget(card)
        card.deleteLater()

        if layout.count() == 0:
            self._group_boxes[group_name].setVisible(False)

    def add_model(self, path: str = "temp_model.ckpt"):
        self._add_card('model', path, show_weight=False)

    def add_lora(self, path: str = "temp_lora.safetensors"):
        self._add_card('lora', path)

    def add_lycoris(self, path: str = "temp_lyco.safetensors"):
        self._add_card('lycoris', path)

    def add_hyper(self, path: str = "temp_hyper.safetensors"):
        self._add_card('hyper', path)

    def add_embedding(self, path: str = "temp_embed.pt"):
        self._add_card('embed', path)


    # def get_


if __name__ == "__main__":

    from PySide6.QtWidgets import QApplication
    app = QApplication([])

    widget = ModelBox()
    widget.show()

    app.exec()
