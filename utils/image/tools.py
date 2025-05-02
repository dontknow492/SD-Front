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
from typing import List, Dict, Any
import io

import piexif
import piexif.helper
import xxhash
from PIL import Image
from pathlib import Path
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


def save_sdwebui_jpg(image_data: str, generation_info: str, output_path: str):
    """
    Save an image from SD WebUI API with generation info embedded into EXIF UserComment.

    Args:
        image_data (str): Base64-encoded image data (usually from API).
        generation_info (str): Text containing generation parameters (prompt, seed, steps, etc).
        output_path (str): Path to save the JPEG file.
    """
    # Decode base64 image data
    image_bytes = base64.b64decode(image_data)
    image = Image.open(io.BytesIO(image_bytes))

    # Prepare EXIF UserComment
    exif_dict = {"Exif": {piexif.ExifIFD.UserComment: generation_info.encode('utf-8')}}
    exif_bytes = piexif.dump(exif_dict)

    # Save as JPEG with EXIF metadata
    image.convert("RGB").save(output_path, "JPEG", exif=exif_bytes)

    print(f"Saved image with generation info to {output_path}")


if __name__ == "__main__":
    image = Image.open(r"/samples/00024-2025-04-10-hassakuXLIllustrious_v21fix.jpg")
    # print(read_sd_webui_gen_info_from_image(image))
    # print(parse_generation_parameters(read_sd_webui_gen_info_from_image(image)))