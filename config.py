from enum import Enum
from pathlib import Path

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QPixmap, QIcon


class Placeholder(Enum):
    IMAGE = "assets/placeholder/image.svg"
    VIDEO = "assets/placeholder/video.svg"
    AUDIO = "assets/placeholder/audio.svg"
    EMPTY = "assets/placeholder/empty.svg"
    NOISE = "assets/placeholder/noise.jpg"

    def path(self) -> str:
        """Returns the path as a string (absolute if it's a real file)."""
        if self.value.startswith(":"):
            return self.value  # Qt resource path
        return str(Path(self.value).resolve())

    def pixmap(self, size: QSize=None) -> QPixmap:
        """Returns a QPixmap, optionally scaled."""
        pix = QPixmap(self.path())
        if pix.isNull():
            pix = QPixmap(Placeholder.EMPTY.path())
        if size:
            return pix.scaled(size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        return pix

    def icon(self) -> QIcon:
        """Returns a QIcon."""
        return QIcon(self.path())
