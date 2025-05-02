from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPixmap, QColor, QPen
from PySide6.QtWidgets import QButtonGroup, QGraphicsPixmapItem
from qfluentwidgets import TogglePushButton, HorizontalSeparator, InfoBadge, InfoBadgePosition, StrongBodyLabel
from gui.common import InputImageViewer, VerticalCard, VerticalFrame, HorizontalFrame, ThemedToolButton

from PySide6.QtGui import QPainter


class InpaintImage(InputImageViewer):
    def __init__(self, parent = None):
        super().__init__(parent = parent)

        self.pen_color = QColor(0, 0, 0)
        self.pen_width = 30
        self.eraser_width = 30

        self.is_drawing = False
        self.is_erasing = False
        self.last_point = QPointF()

        self.is_inpainting = False
        self.allow_drawing = False
        self.is_scrolling = True

        self.image_mask = QPixmap(1024, 1024)
        self.image_mask.fill(Qt.GlobalColor.transparent)
        self.image_mask_item = QGraphicsPixmapItem()
        self.image_mask_item.setPixmap(self.image_mask)
        self.image_mask_item.setZValue(1)
        self.image_mask_item.setOpacity(0.5)
        self.scene.addItem(self.image_mask_item)

        self._last_pos = None

        self.imageChanged.connect(self._on_image_changed)

    def _on_image_changed(self):
        self.image_mask = QPixmap(self.image_item.pixmap().size())
        self.image_mask.fill(Qt.GlobalColor.transparent)
        self.image_mask_item.setPixmap(self.image_mask)


    def mousePressEvent(self, event):
        scene_pos = self.mapToScene(event.position().toPoint())
        if self.is_scrolling:
            super().mouseMoveEvent(event)
        if event.button() == Qt.MouseButton.LeftButton and self.is_inpainting:
            self.allow_drawing = True
            self.last_point = scene_pos
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        scene_pos = self.mapToScene(event.position().toPoint())
        if self.is_scrolling:
            super().mouseMoveEvent(event)
        elif (event.buttons() & Qt.MouseButton.LeftButton) and self.is_inpainting and self.allow_drawing:
            if self.drawing:
                self.drawLine(scene_pos)
            elif self.erasing:
                self.eraseLine(scene_pos)
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.is_scrolling:
            super().mouseMoveEvent(event)
        if event.button() == Qt.LeftButton and self.allow_drawing:
            self.allow_drawing = False
        else:
            super().mouseReleaseEvent(event)

    def drawLine(self, end_point):
        """Draw a line from last_point to end_point"""
        painter = QPainter(self.image_mask)
        painter.setRenderHint(QPainter.Antialiasing)

        pen = QPen(self.pen_color, self.pen_width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        painter.setPen(pen)
        painter.drawLine(self.last_point, end_point)
        painter.end()

        self.image_mask_item.setPixmap(self.image_mask)
        self.last_point = end_point

    def eraseLine(self, end_point):
        """Erase along a line from last_point to end_point"""
        painter = QPainter(self.image_mask)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setCompositionMode(QPainter.CompositionMode_Clear)

        pen = QPen(Qt.transparent, self.eraser_width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        painter.setPen(pen)
        painter.drawLine(self.last_point, end_point)
        painter.end()

        self.image_mask_item.setPixmap(self.image_mask)
        self.last_point = end_point

    def setPenColor(self, color):
        """Set the pen color for drawing"""
        self.pen_color = color

    def setPenWidth(self, width):
        """Set the pen width for drawing"""
        self.pen_width = width

    def setEraserWidth(self, width):
        """Set the eraser size"""
        self.eraser_width = width

    def clear(self):
        """Clear the drawing area"""
        self.image_mask.fill(Qt.white)
        self.image_mask_item.setPixmap(self.image_mask)

    def create_mask(self):
        mask = QPixmap(self.image_mask.size())
        mask.fill(Qt.GlobalColor.white)
        painter = QPainter(mask)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.drawPixmap(0, 0, self.image_mask)
        painter.end()
        return mask

    @property
    def drawing(self):
        return self.is_drawing

    @drawing.setter
    def drawing(self, value):
        self.is_drawing = value
        self.is_erasing = not value

    @property
    def erasing(self):
        return self.is_erasing

    @erasing.setter
    def erasing(self, value):
        self.is_erasing = value
        self.is_drawing = not value

    @property
    def inpainting(self):
        return self.is_inpainting

    @inpainting.setter
    def inpainting(self, value):
        self.is_inpainting = value

    @property
    def scrolling(self):
        return self.is_scrolling

    @scrolling.setter
    def scrolling(self, value):
        self.is_scrolling = value


    # def mousePressEvent(self, event, /):

class ImageInputBox(VerticalFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.image_label = StrongBodyLabel("Image")
        self.image_viewer = InputImageViewer()
        self.image_viewer.setPixmapTransformationMode(Qt.TransformationMode.FastTransformation)
        self.mask_label = StrongBodyLabel("Mask")
        self.mask_label.setVisible(False)
        self.mask_viewer = InputImageViewer()
        self.mask_viewer.setPixmapTransformationMode(Qt.TransformationMode.FastTransformation)
        self.mask_viewer.setVisible(False)

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
            self.mask_viewer.setAcceptDrops(True)
            self.mask_viewer.show()
            self.mask_label.show()
        else:
            self.image_viewer.setAcceptDrops(True)
            self.mask_viewer.setAcceptDrops(False)
            self.mask_viewer.hide()
            self.mask_label.hide()



if  __name__ == '__main__':
    from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QFrame
    from gui.common.myFrame import VerticalFrame
    app = QApplication([])
    # window = ImageInputBox()
    window = InpaintImage()
    window.load_image(r"D:\Program\SD Front\cover_demo.jpg")
    # window.s
    # window.inpainting = True
    # window.drawing = True
    window.resize(800, 600)
    window.show()

    app.exec()

