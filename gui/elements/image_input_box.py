from PySide6.QtCore import Qt, QPointF, Signal
from PySide6.QtGui import QPixmap, QColor, QPen
from PySide6.QtWidgets import QButtonGroup, QGraphicsPixmapItem, QGridLayout
from qfluentwidgets import TogglePushButton, HorizontalSeparator, StrongBodyLabel, \
    ToolButton, FluentIcon, ToggleToolButton, FlyoutViewBase, Slider, Flyout
from gui.common import InputImageViewer, VerticalFrame, HorizontalFrame, ThemedToolButton

from PySide6.QtGui import QPainter

class SizeFlyout(FlyoutViewBase):
    brushSizeChanged = Signal(int)
    eraserSizeChanged = Signal(int)
    def __init__(self, parent = None):
        super().__init__(parent = parent)
        self.setFixedWidth(300)
        gridLayout = QGridLayout(self)

        # Brush Size Controls
        brushSizeLabel = StrongBodyLabel("Brush Size:", self)
        brushSizeSlider = Slider(Qt.Orientation.Horizontal, self)
        brushSizeSlider.setRange(1, 100)  # Adjust range as needed
        brushSizeSlider.setValue(20)  # Default value
        valueLabel = StrongBodyLabel(str(brushSizeSlider.value()), self)


        # Eraser Size Controls
        eraserSizeLabel = StrongBodyLabel("Eraser Size:", self)
        eraserSizeSlider = Slider(Qt.Orientation.Horizontal, self)
        eraserSizeSlider.setRange(1, 100)  # Adjust range as needed
        eraserSizeSlider.setValue(20)  # Default value
        eraserValueLabel = StrongBodyLabel(str(eraserSizeSlider.value()), self)


        # Add to grid layout (row, column, rowSpan, columnSpan)
        gridLayout.addWidget(brushSizeLabel, 0, 0)
        gridLayout.addWidget(brushSizeSlider, 0, 1)
        gridLayout.addWidget(valueLabel, 0, 2)
        gridLayout.addWidget(eraserSizeLabel, 1, 0)
        gridLayout.addWidget(eraserSizeSlider, 1, 1)
        gridLayout.addWidget(eraserValueLabel, 1, 2)

        # Set layout margins and spacing
        gridLayout.setContentsMargins(10, 10, 10, 10)
        gridLayout.setHorizontalSpacing(0)
        gridLayout.setVerticalSpacing(10)
        gridLayout.setColumnStretch(0, 0)  # Labels
        gridLayout.setColumnStretch(1, 2)  # Sliders (2x wider)
        gridLayout.setColumnStretch(2, 0)  # Values

        # Connect signals (if needed)
        brushSizeSlider.valueChanged.connect(self.brushSizeChanged)
        brushSizeSlider.valueChanged.connect(lambda value: valueLabel.setText(str(value)))
        eraserSizeSlider.valueChanged.connect(self.eraserSizeChanged)
        eraserSizeSlider.valueChanged.connect(lambda value: eraserValueLabel.setText(str(value)))


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
        self.is_inpainted = False
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

        # inpaint overlay
        self.size_flyout = SizeFlyout()
        self.size_flyout.brushSizeChanged.connect(lambda value: setattr(self, 'pen_width', value))
        self.size_flyout.eraserSizeChanged.connect(lambda value: setattr(self, 'eraser_width', value))

        self.inpaint_overlay = VerticalFrame(self)
        self.brush_button = ToggleToolButton(FluentIcon.BRUSH)
        self.brush_button.toggled.connect(lambda checked: setattr(self, 'drawing', checked))

        self.eraser_button = ToggleToolButton(FluentIcon.ERASE_TOOL)
        self.eraser_button.toggled.connect(lambda checked: setattr(self, 'erasing', checked))

        self.move_button = ToggleToolButton(FluentIcon.MOVE)
        self.move_button.toggled.connect(lambda checked: setattr(self, 'scrolling', checked))

        self.clear_button = ThemedToolButton(FluentIcon.CLOSE)
        self.clear_button.clicked.connect(self.clear_mask)

        self.size_button = ToolButton(FluentIcon.FONT_SIZE)
        self.size_button.clicked.connect(self._show_size_flyout)

        self.inpaint_overlay.addWidgets([self.brush_button, self.eraser_button, self.clear_button, self.move_button, self.size_button])
        # self.inpaint_overlay.resize(260, 40)
        self.inpaint_overlay.adjustSize()

        #group buttons
        self.inpaint_button_group = QButtonGroup(self)  # Manages exclusive toggling
        self.inpaint_button_group.setExclusive(True)  # Ensure only one is selected

        # Add buttons to the group
        self.inpaint_button_group.addButton(self.brush_button)
        self.inpaint_button_group.addButton(self.eraser_button)
        self.inpaint_button_group.addButton(self.move_button)

        self.inpaint_overlay.setVisible(False)

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
        self.is_inpainted = True
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

    def clear_mask(self):
        """Clear the drawing area"""
        self.image_mask.fill(Qt.GlobalColor.transparent)
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
        self.is_scrolling = not value

    @property
    def erasing(self):
        return self.is_erasing

    @erasing.setter
    def erasing(self, value):
        self.is_erasing = value
        self.is_drawing = not value
        self.is_scrolling = not value

    @property
    def inpainting(self):
        return self.is_inpainting

    @inpainting.setter
    def inpainting(self, value):
        self.is_inpainting = value
        self.inpaint_overlay.setVisible(value)

    @property
    def scrolling(self):
        return self.is_scrolling

    @scrolling.setter
    def scrolling(self, value):
        self.is_scrolling = value
        self.is_inpainting = not value
        self.is_drawing = not value
        self.is_erasing = not value

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.inpaint_overlay.move(self.width() - self.inpaint_overlay.width(), 0)
        # self.inpaint_overlay.setFixedSize(self.size())

    def _show_size_flyout(self):
        Flyout.make(self.size_flyout, self.size_button, self, isDeleteOnClose=False)

    @property
    def inpainted(self):
        return self.is_inpainted

    # def mousePressEvent(self, event, /):

class ImageInputBox(VerticalFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.image_label = StrongBodyLabel("Image")
        self.image_viewer = InpaintImage(self)
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
        self.image_inpaint_button.toggled.connect(lambda value: setattr(self.image_viewer, 'inpainting', value))
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
            self.mask_viewer.setAcceptDrops(True)
            self.mask_viewer.show()
            self.mask_label.show()
        else:
            self.image_viewer.setAcceptDrops(True)
            self.mask_viewer.setAcceptDrops(False)
            self.mask_viewer.hide()
            self.mask_label.hide()

    def load_image(self, image_path):
        self.image_viewer.load_image(image_path)
        self.image_viewer.setPixmapTransformationMode(Qt.TransformationMode.SmoothTransformation)

    def load_mask(self, image_path):
        self.mask_viewer.load_image(image_path)
        self.mask_viewer.setPixmapTransformationMode(Qt.TransformationMode.SmoothTransformation)

    def get_mask_pixmap(self):
        return self.mask_viewer.get_image()

    def set_pixmap(self, pixmap):
        self.image_viewer.set_pixmap(pixmap)
        self.image_viewer.setPixmapTransformationMode(Qt.TransformationMode.SmoothTransformation)

    def get_pixmap(self):
        return self.image_viewer.get_image()


if  __name__ == '__main__':
    from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QFrame
    from gui.common.myFrame import VerticalFrame, FlowFrame

    app = QApplication([])
    window = ImageInputBox()
    # window = InpaintImage()
    window.load_image(r"D:\Program\SD Front\cover_demo.jpg")
    # window.s
    window.inpainting = True
    window.drawing = True
    window.scrolling  = False
    window.resize(800, 600)
    window.show()

    app.exec()

