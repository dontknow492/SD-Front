import base64
from idlelib.tree import wheel_event
from pathlib import Path
from typing import Union

from PySide6.QtCore import Qt, QByteArray, QRect, QRectF, Signal
from PySide6.QtGui import QColor, QBrush, QPainter, QPixmap, QImage, QFont, QPen, QPainterPath, QIcon
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QFrame, QFileDialog
from loguru import logger
from qfluentwidgets import isDarkTheme, toggleTheme, qconfig


from utils import recolorPixmap
from config import Placeholder
from utils import base64_pixmap


class ImageViewerBase:
    MIN_ZOOM = 0.1
    MAX_ZOOM = 10.0
    imageChanged = Signal()
    def load_image(self, file_path: Union[str, Path]):
        """Load an image from a file path."""
        try:
            file_path = Path(file_path) if isinstance(file_path, str) else file_path
            logger.info(f"Loading image from: {file_path}")
            self.image_path = file_path
            image = QPixmap(str(self.image_path))
            self.set_pixmap(image)
            if image.isNull():
                raise ValueError("Failed to load image: Image is null")
        except Exception as e:
            logger.exception(f"Error loading image: {e}")

    def wheelEvent(self, event):
        """Handle mouse wheel events for zooming."""
        if self.current_pixmap is None:
            return
        delta = event.angleDelta().y()
        if delta > 0:
            self.zoom_in()
        elif delta < 0:
            self.zoom_out()
        event.accept()


    def zoom_in(self):
        """Increase zoom level."""
        if self.zoom_factor < self.MAX_ZOOM and not self.image_item.pixmap().isNull():
            self.zoom_factor = min(self.MAX_ZOOM, self.zoom_factor * 1.1)
            self.scale(1.1, 1.1)
            # image_size = self.image_item.pixmap().size()
            # logger.info(f"Image size: {image_size * self.zoom_factor}")

    def zoom_out(self):
        """Decrease zoom level."""
        if self.zoom_factor > self.MIN_ZOOM and not self.image_item.pixmap().isNull():
            self.zoom_factor = max(self.MIN_ZOOM, self.zoom_factor * 0.9)
            self.scale(0.9, 0.9)

    def display_base64_image(self, image_data: str):
        pixmap = base64_pixmap(image_data)
        if pixmap:
            self.set_pixmap(pixmap)

    def set_pixmap(self, pixmap: QPixmap):
        if pixmap.isNull():
            return
        # self.image_item.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
        self.image_item.setPixmap(pixmap)
        self.setSceneRect(pixmap.rect())
        #

        self.resetTransform()
        self.zoom_factor = 1.0
        self.current_pixmap = pixmap

        logger.info(f"Image loaded: {pixmap.width()}x{pixmap.height()}")
        print(pixmap.width(), pixmap.height(),  self.viewport().width(), self.viewport().height())
        if pixmap.width() != self.viewport().width() or pixmap.height() != self.viewport().height():
            self.fitInView(self.image_item, Qt.AspectRatioMode.KeepAspectRatio)
        self.imageChanged.emit()
        self.update()

    def resizeEvent(self, event, /):
        self.fitInView(self.image_item, Qt.AspectRatioMode.KeepAspectRatio)

    def setPixmapTransformationMode(self, mode: Qt.TransformationMode):
        self.image_item.setTransformationMode(mode)

class ImageViewer(ImageViewerBase, QGraphicsView):
    MIN_ZOOM = 0.1
    MAX_ZOOM = 10.0
    def __init__(self, parent=None):
        super(ImageViewer, self).__init__(parent)
        self.image_path = None
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.SmoothPixmapTransform)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setAcceptDrops(False)

        self.current_pixmap: QPixmap = None
        self.zoom_factor: float = 1.0
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.image_item = QGraphicsPixmapItem()
        self.scene.addItem(self.image_item)
        self.centerOn(self.image_item)
        # self.scene.setBackgroundBrush(Qt.GlobalColor.transparent)

        self.viewport().setStyleSheet("border: none; background: none;")
        self._create_no_image_pixmap()



    def _create_no_image_pixmap(self):
        size = 512
        icon = QIcon(Placeholder.IMAGE.icon())
        pixmap = icon.pixmap(size, size, QIcon.Mode.Normal, QIcon.State.Off)

        # For dynamic coloring:
        if isDarkTheme():
            colored_pixmap = recolorPixmap(pixmap, QColor(180, 180, 180))
        else:
            colored_pixmap = recolorPixmap(pixmap, QColor(100, 100, 100))

        self.image_item.setPixmap(colored_pixmap)


class InputImageViewer(ImageViewerBase, QGraphicsView):
    MIN_ZOOM = 0.1
    MAX_ZOOM = 10.0
    def __init__(self, parent=None):
        super(InputImageViewer, self).__init__(parent)
        self.image_path = None
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setAcceptDrops(True)

        self.current_pixmap: QPixmap = None
        self.zoom_factor: float = 1.0
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.image_item = QGraphicsPixmapItem()
        self.scene.addItem(self.image_item)
        self.centerOn(self.image_item)
        # self.scene.setBackgroundBrush(Qt.GlobalColor.transparent)

        self.viewport().setStyleSheet("border: none; background: none;")
        self._create_drop_pixmap()


    def _create_drop_pixmap(self):
        size = 512
        radius = 20  # Corner radius

        # Create a transparent pixmap
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)

        # Get theme colors
        if isDarkTheme():
            bg_color = QColor(45, 45, 45)  # Dark background
            text_color = QColor(220, 220, 220)  # Light text
            border_color = QColor(80, 80, 80)  # Border color
        else:
            bg_color = QColor(245, 245, 245)  # Light background
            text_color = QColor(80, 80, 80)  # Dark text
            border_color = QColor(200, 200, 200)  # Border color

        painter = QPainter(pixmap)
        try:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
            # painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

            # Draw rounded rectangle background
            path = QPainterPath()
            path.addRoundedRect(0, 0, size, size, radius, radius)
            painter.setClipPath(path)

            painter.setBrush(bg_color)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(0, 0, size, size, radius, radius)

            # Draw dashed border
            pen = QPen(border_color, 10, Qt.PenStyle.DashLine)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRoundedRect(1, 1, size - 2, size - 2, radius, radius)

            # Draw text
            font = QFont("Arial", 20)
            font.setBold(True)
            painter.setFont(font)
            painter.setPen(text_color)

            text_rect = QRect(20, 20, size - 40, size - 40)
            painter.drawText(
                text_rect,
                Qt.AlignmentFlag.AlignCenter,
                "Drop Image Here\n\nor\n\nClick to Upload Image"
            )

        finally:
            painter.end()

        self.image_item.setPixmap(pixmap)

    def dragEnterEvent(self, event):
        """Handle drag enter events for file drops."""
        logger.debug(f"Drag enter event received: {event.mimeData().formats()}")
        if event.mimeData().hasUrls():
            logger.debug("URLs detected in drag event")
            event.acceptProposedAction()
        else:
            logger.debug("No URLs in drag event, rejecting")
            event.ignore()

    def dragMoveEvent(self, event):
        """Handle drag move events to keep accepting drops."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        """Handle file drop events."""
        logger.debug("Drop event received")
        try:
            if event.mimeData().hasUrls():
                urls = event.mimeData().urls()
                logger.debug(f"Number of URLs dropped: {len(urls)}")
                if urls:
                    file_path = Path(urls[0].toLocalFile())
                    logger.info(f"File dropped: {file_path}")

                    valid_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff'}
                    if file_path.exists() and file_path.suffix.lower() in valid_extensions:
                        self.load_image(file_path)
                        event.acceptProposedAction()
                        logger.info("Drop accepted and image loaded")
                    else:
                        logger.error(f"Invalid file: {file_path}")
                        event.ignore()
                else:
                    logger.error("No valid URLs in drop event")
                    event.ignore()
            else:
                logger.error("Drop event has no URLs")
                event.ignore()
        except Exception as e:
            logger.exception(f"Error handling drop event: {e}")
            event.ignore()

    def mousePressEvent(self, event, /):
        super().mousePressEvent(event)
        if event.button() == Qt.MouseButton.LeftButton and self.acceptDrops():
            if not self.current_pixmap:
                self._open_file_dialog()

    def _open_file_dialog(self):
        """Open a file dialog to select an image file."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp *.tiff)")
        if file_path:
            self.load_image(file_path)

    def get_image(self):
        """Return the current image as a QPixmap."""
        return self.current_pixmap



if  __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    app = QApplication([])
    window = InputImageViewer()
    window.show()
    app.exec()
