from PySide6.QtCore import Qt
from PySide6.QtWidgets import QButtonGroup
from qfluentwidgets import TogglePushButton, HorizontalSeparator, InfoBadge, InfoBadgePosition, StrongBodyLabel
from gui.common import ImageViewer, VerticalCard, VerticalFrame, HorizontalFrame, ThemedToolButton



class ImageInputBox(VerticalFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.image_label = StrongBodyLabel("Image")
        self.image_viewer = ImageViewer()
        self.image_viewer.setPixmapTransformationMode(Qt.TransformationMode.FastTransformation)
        self.mask_label = StrongBodyLabel("Mask")
        self.mask_label.setVisible(False)
        self.mask_viewer = ImageViewer()
        self.mask_viewer.setPixmapTransformationMode(Qt.TransformationMode.FastTransformation)
        self.mask_viewer.setVisible(False)
        self.mask_viewer.set_drop(True)
        self.image_viewer.set_drop(True)

        option_container = HorizontalFrame(self)

        button_group = QButtonGroup(self)
        self.image_button = TogglePushButton("Image", self)
        self.image_button.setCheckable(True)
        self.image_inpaint_button = TogglePushButton("Inpaint", self)
        self.mask_button = TogglePushButton("Mask", self)
        self.mask_button.toggled.connect(self.on_mask_clicked)

        button_group.addButton(self.image_button)
        button_group.addButton(self.image_inpaint_button)
        button_group.addButton(self.mask_button)

        option_container.addWidget(self.image_button)
        option_container.addWidget(self.image_inpaint_button)
        option_container.addWidget(self.mask_button)

        h_separate = HorizontalSeparator(self)
        h_separate.setFixedHeight(10)
        self.addWidget(option_container, stretch=0, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.addWidget(self.image_label, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.addWidget(self.image_viewer, stretch=1)
        self.addWidget(h_separate)
        self.addWidget(self.mask_label, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.addWidget(self.mask_viewer, stretch=1)

    def on_mask_clicked(self, state: bool):
        if state:
            # self.image_viewer.set_drop(False)
            self.mask_viewer.set_drop(True)
            self.mask_viewer.show()
            self.mask_label.show()
        else:
            self.image_viewer.set_drop(True)
            self.mask_viewer.set_drop(False)
            self.mask_viewer.hide()
            self.mask_label.hide()



if  __name__ == '__main__':
    from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QFrame
    from gui.common.myFrame import VerticalFrame
    app = QApplication([])
    window = ImageInputBox()
    window.resize(200, 200)
    window.show()

    app.exec()

