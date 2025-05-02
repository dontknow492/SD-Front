import pandas as pd
import xxhash
from PIL import Image
from pathlib import Path
from typing import List, Dict, Optional, Union
from loguru import logger
from utils.image.parser import read_sd_webui_gen_info_from_image, parse_generation_parameters
from utils.tools import get_file_size, get_created_date
from utils.helper import hash_file
# Setup logging





def load_existing_dataframe(feather_path: Union[str | Path]= r"data\data.feather") -> tuple[Optional[pd.DataFrame], Dict[str, str]]:
    """
    Load existing DataFrame from Feather file and create a hash lookup.

    Args:
        feather_path: Path to Feather file.

    Returns:
        Tuple of DataFrame (or None if not found) and hash lookup dictionary.
    """
    try:
        df = pd.read_feather(feather_path)
        hash_lookup = dict(zip(df["path"], df["hash"]))
        logger.info(f"Loaded existing DataFrame with {len(df)} records from {feather_path}")
        return df, hash_lookup
    except FileNotFoundError:
        logger.info(f"No existing DataFrame found at {feather_path}")
        return None, {}
    except Exception as e:
        logger.error(f"Error loading DataFrame from {feather_path}: {e}")
        return None, {}

def extract_metadata(image_path: str, hash_value: str) -> Optional[Dict]:
    """
    Extract SD WebUI metadata from an image.

    Args:
        image_path: Path to image file.
        hash_value: Precomputed hash of the image file.

    Returns:
        Dictionary with metadata or None if extraction fails.
    """
    try:
        with Image.open(image_path) as image:
            raw = read_sd_webui_gen_info_from_image(image)  # Assumed function
            if not raw:
                logger.warning(f"No metadata found in {image_path}")
                return None

            nested_data = parse_generation_parameters(raw)  # Assumed function
            return {
                "hash": hash_value,
                "filename": Path(image_path).name,
                "path": image_path,
                "directory":  str(Path(image_path).parent),
                "size": get_file_size(image_path),
                "date": get_created_date(image_path),
                **nested_data.get("meta", {}),
                "lora": [l["name"] for l in nested_data.get("lora", [])],
                "lora_strength": [l["value"] for l in nested_data.get("lora", [])],
                "lyco": nested_data.get("lyco", []),
                "pos_prompt": nested_data.get("pos_prompt", []),
                "neg_prompt": nested_data.get("negative_prompt", [])
            }
    except Exception as e:
        logger.error(f"Error reading {image_path}: {e}")
        return None

def process_images(image_paths: List[str], existing_hashes: Dict[str, str]) -> List[Dict]:
    """
    Process images and extract metadata for new or changed files.

    Args:
        image_paths: List of image file paths.
        existing_hashes: Dictionary of existing paths and their hashes.

    Returns:
        List of metadata dictionaries for new or updated images.
    """
    data = []
    for image_path in image_paths:
        path = str(image_path)
        try:
            hash_value = hash_file(path)
            if existing_hashes.get(path) == hash_value:
                logger.debug(f"Skipping unchanged image: {path}")
                continue

            metadata = extract_metadata(path, hash_value)
            if metadata:
                data.append(metadata)
        except Exception as e:
            logger.error(f"Error processing {path}: {e}")
            continue
    logger.info(f"Processed {len(data)} new or updated images")
    return data

def update_dataframe(
    new_data: List[Dict],
    existing_df: Optional[pd.DataFrame] = None,
    feather_path: str = "data.feather"
) -> pd.DataFrame:
    """
    Merge new data with existing DataFrame and save to Feather file.

    Args:
        new_data: List of new metadata dictionaries.
        existing_df: Existing DataFrame or None.
        feather_path: Path to save Feather file.

    Returns:
        Final DataFrame.
    """
    df_new = pd.DataFrame(new_data)

    if existing_df is not None and not df_new.empty:
        # Remove outdated entries based on path
        existing_df = existing_df[~existing_df["path"].isin(df_new["path"])]
        df_final = pd.concat([existing_df, df_new], ignore_index=True)
    else:
        df_final = df_new if not df_new.empty else existing_df if existing_df is not None else pd.DataFrame()

    if not df_final.empty:
        try:
            df_final.to_feather(feather_path)
            logger.info(f"Saved DataFrame with {len(df_final)} records to {feather_path}")
        except Exception as e:
            logger.error(f"Error saving DataFrame to {feather_path}: {e}")

    return df_final

def scan_and_update_images(image_paths: List[str], feather_path: Union[str | Path] = r"data\data.feather") -> pd.DataFrame:
    """
    Main function to scan images, process metadata, and update DataFrame.

    Args:
        image_paths: List of image file paths.
        feather_path: Path to Feather file.

    Returns:
        Updated DataFrame.
    """
    # Load existing data
    existing_df, existing_hashes = load_existing_dataframe(feather_path)

    # Process new or changed images
    new_data = process_images(image_paths, existing_hashes)

    # Update and save DataFrame
    return update_dataframe(new_data, existing_df, feather_path)

# Example usage
if __name__ == "__main__":
    # Example image paths (replace with your list)

    # Scan and update DataFrame
    # df = scan_and_update_images(images, feather_path="deata.feather")
    print(f"Final DataFrame has  records")