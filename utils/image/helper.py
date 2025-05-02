from pathlib import Path

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QPainter, QPixmap, QColor, QPixmapCache

from config import Placeholder





def add_padding_to_pixmap(pixmap: QPixmap, target_size: QSize, bg_color: QColor = QColor(0, 0, 0, 0)) -> QPixmap:
    # Scale original pixmap with aspect ratio
    if pixmap.isNull():
        return QPixmap(target_size)

    if pixmap.size() == target_size:
        return pixmap

    scaled_pixmap = pixmap.scaled(
        target_size, Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation
    )

    # Create a new pixmap with desired size and fill with background
    padded_pixmap = QPixmap(target_size)
    padded_pixmap.fill(bg_color)

    # Draw scaled pixmap centered
    painter = QPainter(padded_pixmap)
    x = (target_size.width() - scaled_pixmap.width()) // 2
    y = (target_size.height() - scaled_pixmap.height()) // 2
    painter.drawPixmap(x, y, scaled_pixmap)
    painter.end()

    return padded_pixmap

def get_cached_pixmap(path: str, size: QSize = QSize(512, 512), bg_color: QColor = QColor(0, 0, 0, 0)) -> QPixmap:

    if path is None or not Path(path).exists():
        path = Placeholder.IMAGE.path()  # Fallback placeholder image


    key = f"thumb:{path}"
    cached = QPixmap()

    if QPixmapCache.find(key, cached):
        print("Cached:", path)
        return cached

    pixmap = QPixmap(path)
    if path == Placeholder.IMAGE.path():
        scaled_pixmap = pixmap.scaled(size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
    else:
        scaled_pixmap = add_padding_to_pixmap(pixmap, size, bg_color)  # this centers/fits the image
    QPixmapCache.insert(key, scaled_pixmap)
    return scaled_pixmap  # <- Corrected return