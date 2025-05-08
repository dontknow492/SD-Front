import base64
import ctypes
import json
import os
import platform
import re
import subprocess
import sys
import zipfile
from datetime import datetime
from pprint import pprint
from typing import List, Dict, Any, Tuple, Optional
import io

import numpy as np
import piexif
import piexif.helper
import xxhash
from PIL import Image
from pathlib import Path

from PIL.ImageQt import QPixmap
from PySide6.QtCore import QByteArray, QBuffer, QIODevice
from PySide6.QtGui import QImage
from loguru import logger
from utils.tools import to_abs_path, normalize_paths, cwd




def get_valid_img_dirs(
        conf: dict,
        keys: List[str]
):
    paths = [conf.get(key) for key in keys]

    # 判断路径是否有效并转为绝对路径
    abs_paths = []
    for path in paths:
        if not path or len(path.strip()) == 0:
            continue
        if os.path.isabs(path):  # 已经是绝对路径
            abs_path = path
        else:  # 转为绝对路径
            abs_path = to_abs_path(path)
        if os.path.exists(abs_path):  # 判断路径是否存在
            abs_paths.append(os.path.normpath(abs_path))

    return abs_paths

def get_dir_imgs(dir_path):
    if not os.path.exists(dir_path):
        return []
    if os.path.isfile(dir_path) and is_image_file(dir_path):
        return [dir_path]
    return [str(p) for p in Path(dir_path).rglob('*') if is_image_file(p.name)]



def is_image_file(filename: str) -> bool:
    if not isinstance(filename, str):
        return False

    extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.avif', '.jpe']
    extension = filename.split('.')[-1].lower()
    return f".{extension}" in extensions

def is_valid_media_path(path):
    """
    判断给定的路径是否是图像文件
    """
    abs_path = to_abs_path(path)  # 转为绝对路径
    if not os.path.exists(abs_path):  # 判断路径是否存在
        return False
    if not os.path.isfile(abs_path):  # 判断是否是文件
        return False
    return is_image_file(abs_path)



def create_zip_file(file_paths: List[str], zip_file_name: str, compress=False):
    """
    将文件打包成一个压缩包

    Args:
        file_paths: 文件路径的列表
        zip_file_name: 压缩包的文件名

    Returns:
        无返回值
    """
    with zipfile.ZipFile(zip_file_name, 'w', zipfile.ZIP_DEFLATED if compress else zipfile.ZIP_STORED) as zip_file:
        for file_path in file_paths:
            if os.path.isfile(file_path):
                zip_file.write(file_path, os.path.basename(file_path))
            elif os.path.isdir(file_path):
                for root, _, files in os.walk(file_path):
                    for file in files:
                        full_path = os.path.join(root, file)
                        zip_file.write(full_path, os.path.relpath(full_path, file_path))




def unique_by(seq, key_func=lambda x: x):
    seen = set()
    return [x for x in seq if not (key := key_func(x)) in seen and not seen.add(key)]

def unquote(text):
    if len(text) == 0 or text[0] != '"' or text[-1] != '"':
        return text

    try:
        return json.loads(text)
    except Exception:
        return text


tags_translate: Dict[str, str] = {}
try:
    import codecs

    with codecs.open(os.path.join(cwd, "tags-translate.csv"), "r", "utf-8") as tag:
        tags_translate_str = tag.read()
        for line in tags_translate_str.splitlines():
            en, mapping = line.split(",")
            tags_translate[en.strip()] = mapping.strip()
except Exception as e:
    pass

def hash_file(file_path: str) -> str:
    """Generate an xxHash for a file."""
    hasher = xxhash.xxh64()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()



def base64_pixmap(image_data: str) -> Optional[QPixmap]:
    """
    Convert a base64-encoded image string to a QPixmap.

    Args:
        image_data (str): Base64-encoded image string, with or without data URI prefix
                         (e.g., "data:image/png;base64,...").

    Returns:
        Optional[QPixmap]: Loaded QPixmap if successful, None if conversion fails.
    """
    if not image_data:
        print("Error: Empty image data provided.")
        return None

    try:
        # Remove data URI prefix if present (e.g., "data:image/png;base64,")
        base64_string = image_data
        if image_data.startswith("data:image/"):
            # Match prefix like "data:image/png;base64," or "data:image/jpeg;base64,"
            match = re.match(r"data:image/[^;]+;base64,", image_data)
            if match:
                base64_string = image_data[match.end():]
            else:
                print("Error: Invalid data URI prefix format.")
                return None

        # Decode base64 string
        image_bytes = base64.b64decode(base64_string)

        # Load into QPixmap
        pixmap = QPixmap()
        if not pixmap.loadFromData(QByteArray(image_bytes)):
            print("Error: Failed to load image from base64 data.")
            return None

        return pixmap

    except base64.binascii.Error:
        print("Error: Invalid base64 encoding.")
        return None
    except Exception as e:
        print(f"Error: Failed to convert base64 to QPixmap: {str(e)}")
        return None


def pixmap_base64(pixmap: QPixmap, format: str = "JPEG", quality: int = 90, with_prefix: bool = False) -> str:
    """
    Convert QPixmap to a base64-encoded image string.

    Args:
        pixmap (QPixmap): Input QPixmap to convert.
        format (str): Output format ("JPEG" or "PNG"). Default is "JPEG".
        quality (int): JPEG quality (0–100). Ignored for PNG.
        with_prefix (bool): Whether to include the data URI prefix (e.g., "data:image/jpeg;base64,").

    Returns:
        str: Base64-encoded image string.

    Raises:
        ValueError: If QPixmap is null or format is invalid.
        RuntimeError: If conversion fails.
    """
    if pixmap.isNull():
        raise ValueError("Input QPixmap is null or invalid")

    format = format.upper()
    if format not in ("JPEG", "PNG"):
        raise ValueError("Only 'JPEG' and 'PNG' formats are supported")

    try:
        # Convert to appropriate format
        qimage = pixmap.toImage().convertToFormat(
            QImage.Format_RGBA8888 if format == "PNG" else QImage.Format_RGB888
        )

        # Create and configure QBuffer
        buffer = QBuffer()
        if not buffer.open(QIODevice.OpenModeFlag.WriteOnly):
            raise RuntimeError("Failed to open QBuffer for writing")

        # Save image to buffer (format passed as positional argument)
        success = qimage.save(buffer, format.upper(), quality if format.upper() == "JPEG" else -1)
        buffer.close()

        if not success:
            raise RuntimeError("Failed to save QImage to QBuffer")

        # Encode to base64
        base64_bytes = base64.b64encode(buffer.data().data()).decode("utf-8")

        if with_prefix:
            mime = "png" if format == "PNG" else "jpeg"
            return f"data:image/{mime};base64,{base64_bytes}"
        return base64_bytes

    except Exception as e:
        raise RuntimeError(f"Failed to convert QPixmap to base64: {str(e)}")

def save_image_as(old_path: str, new_path: str):
    supported_ext = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.avif', '.jpe')

    ext = os.path.splitext(new_path)[1].lower()
    if ext not in supported_ext:
        logger.exception(f"Unsupported file extension: {ext}")
    try:
        with Image.open(old_path) as img:
            save_params = {}

            if ext in ('.jpg', '.jpeg', '.jpe'):
                save_params["format"] = "JPEG"
                save_params["quality"] = 95  # High quality (max is 100)
                save_params["optimize"] = True
                save_params["progressive"] = True
            elif ext == '.png':
                save_params["format"] = "PNG"
                save_params["optimize"] = True
            elif ext == '.gif':
                save_params["format"] = "GIF"
            elif ext == '.bmp':
                save_params["format"] = "BMP"
            elif ext == '.webp':
                save_params["format"] = "WEBP"
                save_params["quality"] = 95
            elif ext == '.avif':
                save_params["format"] = "AVIF"
                save_params["quality"] = 95

            img.save(new_path, **save_params)
            print(f"Image saved as {new_path}")
            return True

    except Exception as e:
        logger.exception(f"Failed to save image: {e}")
        return None


def get_next_index(directory: str, padding: int = 5, extensions: Tuple[str, ...] = (".jpg", ".png")) -> str:
    """
    Get the next available index for an image file (e.g., '00001').

    Args:
        directory: Directory to scan for existing files.
        padding: Number of digits to pad the index with zeros.
        extensions: Tuple of file extensions to consider (case-insensitive).

    Returns:
        A zero-padded string representing the next index.

    Raises:
        OSError: If the directory cannot be accessed.
    """
    try:
        if not os.path.isdir(directory):
            raise OSError(f"Directory does not exist: {directory}")

        # List files with specified extensions
        existing_files = [
            f for f in os.listdir(directory)
            if any(f.lower().endswith(ext.lower()) for ext in extensions)
        ]
        numbers = []
        for name in existing_files:
            parts = name.split("-")
            if parts and parts[0].isdigit():
                numbers.append(int(parts[0]))

        next_index = max(numbers, default=-1) + 1
        return str(next_index).zfill(padding)
    except OSError as e:
        logger.error(f"Failed to scan directory {directory}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_next_index: {e}")
        raise

def format_date(timestamp: str, input_format: str = "%Y%m%d%H%M%S", output_format: str = "%Y-%m-%d") -> str:
    """
    Format a timestamp string to a specified output format.

    Args:
        timestamp: The input timestamp string.
        input_format: The format of the input timestamp (default: YYYYMMDDHHMMSS).
        output_format: The desired output format (default: YYYY-MM-DD).

    Returns:
        The formatted date string, or 'unknown-date' if parsing fails.
    """
    try:
        dt = datetime.strptime(timestamp, input_format)
        return dt.strftime(output_format)
    except ValueError:
        logger.warning(f"Invalid timestamp format: {timestamp}")
        return "unknown-date"
    except Exception as e:
        logger.error(f"Unexpected error in format_date: {e}")
        return "unknown-date"

def save_sdwebui_image_with_info(
    response: Dict[str, Any],
    output_dir: str,
    save_txt: bool = True,
    image_format: str = "JPEG",
    filename_template: str = "{index}-{date}-{model}"
) -> bool:
    """
    Save images from an SD WebUI API response with metadata and auto-naming.
    Supports batch processing of multiple images in the response.

    Args:
        response: SD WebUI API response containing 'images' and 'info'.
        output_dir: Directory to save images and optional metadata files.
        save_txt: Whether to save the infotext string to a .txt file.
        image_format: Image format to save ('JPEG' or 'PNG').
        filename_template: Template for filename (e.g., '{index}-{date}-{model}', supports '{counter}').

    Returns:
        True if all images were saved successfully, False if any failed.

    Raises:
        ValueError: If the response is invalid or missing required fields.
        OSError: If file operations fail (e.g., no write permission).
    """
    try:
        # Validate inputs
        os.makedirs(output_dir, exist_ok=True)
        if not isinstance(response, dict) or "images" not in response or not response["images"]:
            raise ValueError("Invalid response: 'images' field is missing or empty")
        if not os.access(output_dir, os.W_OK):
            raise OSError(f"No write permission for directory: {output_dir}")
        if image_format.upper() not in ("JPEG", "PNG"):
            raise ValueError(f"Unsupported image format: {image_format}")
        # Validate filename template (optional, warn if placeholders missing)
        if "{index}" not in filename_template:
            logger.warning("Filename template missing '{index}' placeholder")



        # Parse infotext and info
        info_raw = response.get("info", "")
        try:
            info_dict = json.loads(info_raw) if isinstance(info_raw, str) else info_raw
        except json.JSONDecodeError:
            logger.warning("Invalid JSON in response 'info' field")
            info_dict = {}

        infotexts = info_dict.get("infotexts", [])
        # Use first infotext as default, or per-image if available
        default_infotext = infotexts[0] if infotexts else ""
        model_name = fetch_model_name(default_infotext)
        job_timestamp = info_dict.get("job_timestamp", "")
        date_str = format_date(job_timestamp)

        # Sanitize model_name for filename
        model_name = re.sub(r'[^\w\-]', '_', model_name)

        # Get base index for the batch
        base_index = int(get_next_index(output_dir, extensions=(".jpg", ".png")))
        extension = ".jpg" if image_format.upper() == "JPEG" else ".png"
        all_success = True

        # Prepare EXIF metadata (shared across images unless infotexts vary)
        exif_dict = {
            "Exif": {
                piexif.ExifIFD.UserComment: default_infotext.encode("utf-8", errors="ignore"),
                piexif.ExifIFD.DateTimeOriginal: job_timestamp.encode("utf-8") if job_timestamp else b"unknown"
            }
        }
        exif_bytes = piexif.dump(exif_dict)

        # Process each image
        for i, image_base64 in enumerate(response["images"]):
            try:
                # Decode image
                try:
                    image_data = base64.b64decode(image_base64)
                    image = Image.open(io.BytesIO(image_data)).convert("RGB")
                except base64.binascii.Error as e:
                    logger.error(f"Invalid base64 for image {i}: {e}")
                    all_success = False
                    continue
                except Exception as e:
                    logger.error(f"Failed to decode image {i}: {e}")
                    all_success = False
                    continue

                # Use per-image infotext if available
                infotext_str = infotexts[i] if i < len(infotexts) else default_infotext
                if infotext_str != default_infotext:
                    exif_dict["Exif"][piexif.ExifIFD.UserComment] = infotext_str.encode("utf-8", errors="ignore")
                    exif_bytes = piexif.dump(exif_dict)

                # Compose filename
                index_str = str(base_index + i).zfill(5)  # Increment index locally
                filename = filename_template.format(
                    index=index_str,
                    date=date_str,
                    model=model_name,
                    counter=str(i).zfill(2)  # Optional counter for batch
                )
                img_path = os.path.join(output_dir, filename + extension)
                txt_path = os.path.join(output_dir, filename + ".txt")

                # Save image
                try:
                    image.save(img_path, image_format.upper(), exif=exif_bytes, quality=95)
                    logger.info(f"Saved image {i} to: {img_path}")
                except Exception as e:
                    logger.error(f"Failed to save image {i} to {img_path}: {e}")
                    all_success = False
                    continue

                # Save infotext to .txt file
                if save_txt and infotext_str:
                    try:
                        with open(txt_path, "w", encoding="utf-8") as f:
                            f.write(infotext_str)
                        logger.info(f"Saved infotext for image {i} to: {txt_path}")
                    except Exception as e:
                        logger.error(f"Failed to save infotext for image {i} to {txt_path}: {e}")
                        all_success = False

            except Exception as e:
                logger.error(f"Unexpected error processing image {i}: {e}")
                all_success = False

        return all_success

    except ValueError as e:
        logger.error(f"Invalid input or data: {e}")
        return False
    except OSError as e:
        logger.error(f"File operation failed: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error in save_sdwebui_image_with_info: {e}")
        return False

def fetch_model_name(infotext: str) -> str:
    """
    Extract the model name from the infotext string.

    Args:
        infotext: The infotext string from the SD WebUI API response.

    Returns:
        The model name, or 'unknown-model' if not found.
    """
    try:
        match = re.search(r"Model:\s*([^\s,]+)", infotext, re.IGNORECASE)
        return match.group(1) if match else "unknown-model"
    except Exception as e:
        logger.warning(f"Failed to parse model name from infotext: {e}")
        return "unknown-model"


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication, QLabel
    from PIL import ImageQt
    app = QApplication(sys.argv)

    # Load PIL image
    pixmap = QPixmap(r"D:\Program\SD Front\outputs\txt2img\00000-2025-05-02-realvisxlV50_v50Bakedvae.jpg")
    raw = pixmap_base64(pixmap, with_prefix=False)
    raw_pixmap = base64_pixmap(raw)
    label = QLabel()
    label.setPixmap(raw_pixmap)
    label.show()
    label.setFixedSize(512, 512)
    label.setScaledContents(True)
    app.exec()

    sys.exit(0)

    # with open(fr"D:\Program\SD Front\data.json", "r") as f:
    #     data = json.load(f)
    #
    # # os.makedirs(r"D:\Program\SD Front\utils\image\cat", exist_ok=True)
    # save_sdwebui_image_with_info(data, r"D:\Program\SD Front\utils\image\cat")
    # # image = Image.open(r"/samples/00024-2025-04-10-hassakuXLIllustrious_v21fix.jpg")
    # # print(read_sd_webui_gen_info_from_image(image))
    # # print(parse_generation_parameters(read_sd_webui_gen_info_from_image(image)))