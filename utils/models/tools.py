from typing import List
from pathlib import Path


def is_model_file(filename: str) -> bool:
    if not isinstance(filename, str):
        return False

    # List of valid model extensions
    extensions = ['.safetensors', '.pt', '.ckpt']

    # Use pathlib's suffix to get the file extension
    extension = Path(filename).suffix.lower()  # Get the file extension
    return extension in extensions


def get_dir_models(dir_path: str) -> List[str]:
    models = []

    # Convert dir_path to a Path object if it's not already
    dir_path = Path(dir_path)

    # Iterate over all files in the directory
    for file in dir_path.glob("*"):
        if file.is_file() and is_model_file(file.name):
            models.append(str(file))  # Add the full path (str)

    return models

def detect_version(name: str, metadata: dict):
    base = str(metadata.get('ss_base_model_version', "")).lower()
    arch = str(metadata.get('modelspec.architecture', "")).lower()
    if base.startswith("sd_v1"):
        return 'sd1'
    if base.startswith("sdxl"):
        return 'xl'
    if base.startswith("stable_cascade"):
        return 'sc'
    if base.startswith("sd3"):
        return 'sd3'
    if base.startswith("flux"):
        return 'f1'

    if arch.startswith("stable-diffusion-v1"):
        return 'sd1'
    if arch.startswith("stable-diffusion-xl"):
        return 'xl'
    if arch.startswith("stable-cascade"):
        return 'sc'
    if arch.startswith("flux"):
        return 'f1'

    if "v1-5" in str(metadata.get('ss_sd_model_name', "")):
        return 'sd1'
    if str(metadata.get('ss_v2', "")) == "True":
        return 'sd2'
    if 'flux' in name.lower():
        return 'f1'
    if 'xl' in name.lower():
        return 'xl'

    return ''



