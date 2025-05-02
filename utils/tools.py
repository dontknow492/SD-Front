import ctypes
from datetime import datetime
import os
import platform
import re
import subprocess
import sys
from typing import List


is_nuitka = "__compiled__" in globals()
is_pyinstaller_bundle = bool(getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'))
is_exe_ver = is_nuitka or is_pyinstaller_bundle
cwd = os.getcwd() if is_exe_ver else os.path.normpath(os.path.join(__file__, "../../../"))

def get_windows_drives():
    drives = []
    bitmask = ctypes.windll.kernel32.GetLogicalDrives()
    for letter in range(65, 91):
        if bitmask & 1:
            drive_name = chr(letter) + ":/"
            drives.append(drive_name)
        bitmask >>= 1
    return drives


def get_formatted_date(timestamp: float) -> str:
    """Convert a timestamp to a formatted datetime string."""
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")

def get_modified_date(file_path: str) -> str:
    """Get the last modified time of a file as a formatted string."""
    try:
        return get_formatted_date(os.path.getmtime(file_path))
    except (FileNotFoundError, OSError):
        return ""  # Or return None if you prefer

def get_created_date(folder_path: str):
    try:
        return get_formatted_date(os.path.getctime(folder_path))
    except (FileNotFoundError, OSError):
        return ""  # Or return None if you prefer

def get_file_size(filepath)->int:
    """Returns the size of the file in bytes."""
    if os.path.isfile(filepath):
        return os.path.getsize(filepath)
    else:
        return 0


def open_folder(folder_path, file_path=None):
    folder = os.path.realpath(folder_path)
    if file_path:
        file = os.path.join(folder, file_path)
        if os.name == "nt":
            subprocess.run(["explorer", "/select,", file])
        elif sys.platform == "darwin":
            subprocess.run(["open", "-R", file])
        elif os.name == "posix":
            subprocess.run(["xdg-open", file])
    else:
        if os.name == "nt":
            subprocess.run(["explorer", folder])
        elif sys.platform == "darwin":
            subprocess.run(["open", folder])
        elif os.name == "posix":
            subprocess.run(["xdg-open", folder])


def open_file_with_default_app(file_path):
    system = platform.system()
    if system == 'Darwin':  # macOS
        subprocess.call(['open', file_path])
    elif system == 'Windows':  # Windows
        subprocess.call(file_path, shell=True)
    elif system == 'Linux':  # Linux
        subprocess.call(['xdg-open', file_path])
    else:
        raise OSError(f'Unsupported operating system: {system}')


def normalize_paths(paths: List[str], base=cwd):
    """
    Normalize a list of paths, ensuring that each path is an absolute path with no redundant components.

    Args:
        paths (List[str]): A list of paths to be normalized.

    Returns:
        List[str]: A list of normalized paths.
    """
    res: List[str] = []
    for path in paths:
        # Skip empty or blank paths
        if not path or len(path.strip()) == 0:
            continue
        # If the path is already an absolute path, use it as is
        if os.path.isabs(path):
            abs_path = path
        # Otherwise, make the path absolute by joining it with the current working directory
        else:
            abs_path = os.path.join(base, path)
        # If the absolute path exists, add it to the result after normalizing it
        if os.path.exists(abs_path):
            res.append(os.path.normpath(abs_path))
    return res

def to_abs_path(path):
    if not os.path.isabs(path):
        path = os.path.join(os.getcwd(), path)
    return os.path.normpath(path)


def human_readable_size(size_bytes):
    """
    Converts bytes to a human-readable format.
    """
    # define the size units
    units = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    # calculate the logarithm of the input value with base 1024
    size = int(size_bytes)
    if size == 0:
        return "0B"
    i = 0
    while size >= 1024 and i < len(units) - 1:
        size /= 1024
        i += 1
    # round the result to two decimal points and return as a string
    return "{:.2f} {}".format(size, units[i])

pattern = re.compile(r"(\d+\.?\d*)([KMGT]?B)", re.IGNORECASE)

def convert_to_bytes(file_size_str):
    match = re.match(pattern, file_size_str)
    if match:
        size_str, unit_str = match.groups()
        size = float(size_str)
        unit = unit_str.upper()
        if unit == "KB":
            size *= 1024
        elif unit == "MB":
            size *= 1024 ** 2
        elif unit == "GB":
            size *= 1024 ** 3
        elif unit == "TB":
            size *= 1024 ** 4
        return int(size)
    else:
        raise ValueError(f"Invalid file size string '{file_size_str}'")

# def get_file_size(filepath):
#     """Returns the size of the file in bytes."""
#     if os.path.isfile(filepath):
#         return os.path.getsize(filepath)
#     else:
#         raise FileNotFoundError(f"No such file: '{filepath}'")