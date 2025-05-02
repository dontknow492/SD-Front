import hashlib
import os
import re
from pathlib import Path
import xxhash

import psutil
from PySide6.QtGui import QIcon, QPixmap, QPainter, QFont, QFontMetrics
from PySide6.QtCore import Qt, QMimeData, QUrl
from PySide6.QtWidgets import QApplication


def text_icon(text: str, size: int = 24) -> QIcon:
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    font = QFont("Arial", int(size * 0.6))
    painter.setFont(font)
    painter.setPen(Qt.GlobalColor.black)
    painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, text)
    painter.end()

    return QIcon(pixmap)

def find_sdnext_path():
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['cmdline']:
                # Look for typical SDNext entry points
                for arg in proc.info['cmdline']:
                    if 'launch.py' in arg or 'webui-user.bat' in arg or 'webui.sh' in arg:
                        sdnext_path = os.path.dirname(os.path.abspath(arg))
                        return sdnext_path
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return None
# "D:\AI Art\Packages\automatic\html\art-styles.json"

def get_sdnext_path():
    sdnext_path = find_sdnext_path()
    if sdnext_path:
        return sdnext_path
    else:
        raise Exception("SDNext is not running or not found.")

def get_styles_path():
    style_path = r"html\art-styles.json"
    sdnext_path = get_sdnext_path()
    styles_path = os.path.join(sdnext_path, style_path)
    return styles_path

def recolorPixmap(pixmap, color):
    """Helper to recolor monochrome SVG pixmaps"""
    image = pixmap.toImage()
    for x in range(image.width()):
        for y in range(image.height()):
            pixel = image.pixelColor(x, y)
            if pixel.alpha() > 0:  # Only recolor non-transparent pixels
                image.setPixelColor(x, y, color)
    return QPixmap.fromImage(image)


def get_project_root(marker: str = "config.py")->Path:
        """Returns the project root directory based on a marker file/folder like .git, pyproject.toml, etc."""
        path = Path(__file__).resolve()
        for parent in path.parents:
            if (parent / marker).exists():
                return parent
        raise RuntimeError(f"Could not find project root containing {marker}")
    # app = QApplication.instance()
    # if app is None:
    #     app = QApplication([])
    # return app.applicationDirPath()

def hash_file(file_path: str):
    try:
        with open(file_path, "rb") as f:
            file_hash = xxhash.xxh64()
            while chunk := f.read(8192):  # Read file in chunks (8192 bytes)
                file_hash.update(chunk)
        return file_hash.hexdigest()
    except Exception as e:
        return file_path, str(e)


def copy_to_clipboard(text: str):
    clipboard = QApplication.clipboard()
    clipboard.setText(text)

def copy_file_to_clipboard(file_path: str):
    mime_data = QMimeData()
    url = QUrl.fromLocalFile(file_path)
    mime_data.setUrls([url])

    clipboard = QApplication.clipboard()
    clipboard.setMimeData(mime_data)

def delete_file(path: str):
    if os.path.exists(path):
        try:
            os.remove(path)
            print(f"Deleted: {path}")
        except Exception as e:
            print(f"Error deleting file: {e}")
    else:
        print(f"File not found: {path}")

def compute_sha256(file_path):
    sha256_hash = hashlib.sha256()  # Initialize the sha256 hash object
    with open(file_path, "rb") as f:  # Open the file in binary mode
        # Read the file in chunks to prevent memory overload with large files
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)  # Update the hash with each chunk
    return sha256_hash.hexdigest()




# Example usage
if __name__ == "__main__":
    print('calculating')
    print(hash_file(r"D:\AI Art\Packages\automatic\models\Stable-diffusion\SDXL\animagineXL40_v4Opt.safetensors"))

