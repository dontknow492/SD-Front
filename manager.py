import asyncio
import mimetypes
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, Dict, Any, List, Union
import re

import numpy as np
import pandas as pd
from PySide6.QtGui import QIcon
from loguru import logger
from PySide6.QtCore import Signal, QObject, QSize, Slot
from pathlib import Path
from pandas import DataFrame
from utils import scan_and_update_images
import json


class InfoNotificationManager(QObject):
    showInfo = Signal(str, str, QIcon)
    hideInfo = Signal()
    def __init__(self, parent = None):
        super().__init__(parent)
        self._is_showing = False

    @Slot()
    def set_info(self, title: str, description: str, icon: QIcon):
        if title == "" or not title:
            return
        self._is_showing = True
        self.showInfo.emit(title, description, icon)

    @Slot()
    def hide_info(self):
        if self._is_showing:
            self.hideInfo.emit()
        self._is_showing  = False



class CoverCardManager(QObject):
    size_changed = Signal(QSize)
    border_radius_changed = Signal(int, int, int, int)
    def __init__(self, parent = None):
        super().__init__(parent)
        self.cover_size = QSize(150, 150)
        self.border_radius = [5, 5, 5, 5]

    def set_width(self, width: int):
        self.cover_size.setWidth(width)
        self.size_changed.emit(self.cover_size)

    def set_height(self, height: int):
        self.cover_size.setHeight(height)
        self.size_changed.emit(self.cover_size)

    def set_size(self, size: QSize):
        self.cover_size = size
        self.size_changed.emit(size)

    # @property
    def get_size(self) -> QSize:
        return self.cover_size

    def set_border_radius(self, top_left, top_right, bottom_left, bottom_right ):
        self.border_radius = [top_left, top_right, bottom_left, bottom_right]
        self.border_radius_changed.emit(top_left, top_right, bottom_left, bottom_right)

    # @property
    def get_border_radius(self) -> tuple[int, int , int, int]:
        return tuple(self.border_radius)


class ImageManager(QObject):
    scan_progress = Signal(int, int)  # current, total
    scan_completed = Signal()
    error_occurred = Signal(str)
    def __init__(self, scan_paths: list[str], data_backup_dir: str = "data", parent = None):
        super().__init__(parent)
        self.scan_paths = [Path(path) for path in scan_paths]
        self.data_backup_dir = Path(data_backup_dir)
        self.data_backup_path = self.data_backup_dir / "data.feather"
        self.images: List[Path] = []
        self.image_dataframe: Optional[DataFrame] = None
        self.executor = ThreadPoolExecutor(max_workers=4)

        self.data_backup_dir.mkdir(parents=True, exist_ok=True)
        self.read_backup()

    def read_backup(self) -> bool:
        """Read DataFrame from feather file."""
        try:
            if not self.data_backup_path.exists():
                logger.warning(f"Backup file does not exist: {self.data_backup_path}")
                return False

            self.image_dataframe = pd.read_feather(self.data_backup_path)
            logger.info(f"DataFrame successfully read from {self.data_backup_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to read DataFrame from backup: {str(e)}")
            return False

    async def refresh(self) -> None:
        """Asynchronously refresh image list and update DataFrame."""
        try:
            await self._scan_for_images()
            await self._update_dataframe()
            self.scan_completed.emit()
            logger.info(f"Refresh completed successfully: {self.image_dataframe.columns}")
        except Exception as e:
            logger.error(f"Refresh failed: {str(e)}")
            self.error_occurred.emit(str(e))

    async def _scan_for_images(self) -> None:
        """Scan directories for image files asynchronously."""
        self.images.clear()
        total_paths = len(self.scan_paths)

        for idx, path in enumerate(self.scan_paths):
            if not path.exists():
                logger.warning(f"Path does not exist: {path}")
                continue

            images = await asyncio.get_event_loop().run_in_executor(
                self.executor, self._get_dir_imgs, path
            )
            self.images.extend(images)
            self.scan_progress.emit(idx + 1, total_paths)

        logger.info(f"Found {len(self.images)} images")

    def _get_dir_imgs(self, path: Path) -> List[Path]:
        """Get list of image files in directory."""
        image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff'}
        images = []

        for file_path in path.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in image_extensions:
                mime_type, _ = mimetypes.guess_type(file_path)
                if mime_type and mime_type.startswith('image/'):
                    images.append(file_path)

        return images

    async def _update_dataframe(self) -> None:
        """Update DataFrame with image metadata."""
        try:
            self.image_dataframe = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                scan_and_update_images,
                self.images,
                self.data_backup_path
            )
            logger.info("DataFrame updated successfully")
        except Exception as e:
            logger.error(f"DataFrame update failed: {str(e)}")
            raise

    def backup(self) -> bool:
        """Backup DataFrame to feather file."""
        try:
            if self.image_dataframe is None:
                logger.warning("No DataFrame to backup")
                return False

            self.data_backup_path.parent.mkdir(parents=True, exist_ok=True)
            self.image_dataframe.to_feather(self.data_backup_path)
            logger.info(f"DataFrame successfully backed up to {self.data_backup_path}")
            return True
        except Exception as e:
            logger.error(f"Backup failed: {str(e)}")
            self.error_occurred.emit(str(e))
            return False

    def get_image_metadata(self, image_path: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a specific image."""
        if self.image_dataframe is None:
            logger.warning("Dataframe is empty create index")
            return None
        if image_path not in self.image_dataframe['path'].values:
            logger.warning(f"Image not found in DataFrame: {image_path}")
            return None

        path = Path(image_path)
        result = self.image_dataframe[self.image_dataframe['path'] == str(path)]
        return self.generate_nested_metadata(result.iloc[0].to_dict())

    @staticmethod
    def generate_nested_metadata(row: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert a flat dictionary row into a nested dictionary structure.

        Args:
            row: Input dictionary containing flat data with lora, lyco, and metadata

        Returns:
            Nested dictionary with structured meta, lora, and lyco data

        Raises:
            ValueError: If required fields are missing or invalid
        """
        # Initialize output structures
        nested: Dict[str, Any] = {}
        meta: Dict[str, Any] = {}

        # Validate input
        if not isinstance(row, dict):
            raise ValueError("Input must be a dictionary")

        # Process simple fields directly
        for key, value in row.items():
            key = key.lower().strip().replace(" ", "_")
            if key in ("pos_prompt", "neg_prompt"):
                nested[key] = value if value is not None else []
            elif key in ("hash", "path", 'size', 'filename'):
                nested[key] = value if value is not None else ""
            elif key not in ("lora", "lyco", "lora_strength", "lyco_strength"):
                meta[key] = value

        # Process lora and lyco data using list comprehensions
        lora_names = row.get("lora", [])
        lora_strengths = row.get("lora_strength", [])
        lyco_names = row.get("lyco", [])
        lyco_strengths = row.get("lyco_strength", [])

        # Validate lengths match
        if len(lora_names) != len(lora_strengths) or len(lyco_names) != len(lyco_strengths):
            raise ValueError("Mismatched lengths for lora/lyco names and strengths")

        # Create nested structures efficiently
        nested["meta"] = meta
        nested["lora"] = [
            {"name": name, "value": strength}
            for name, strength in zip(lora_names, lora_strengths)
        ]
        nested["lyco"] = [
            {"name": name, "value": strength}
            for name, strength in zip(lyco_names, lyco_strengths)
        ]

        return nested

    def add_scan_path(self, path: str) -> None:
        """Add a new scan path."""
        path_obj = Path(path)
        if path_obj not in self.scan_paths:
            self.scan_paths.append(path_obj)
            logger.info(f"Added scan path: {path}")

    def remove_scan_path(self, path: str) -> None:
        """Remove a scan path."""
        path_obj = Path(path)
        if path_obj in self.scan_paths:
            self.scan_paths.remove(path_obj)
            logger.info(f"Removed scan path: {path}")

    def get_scan_paths(self) -> List[str]:
        """Get list of scan paths."""
        return [str(path) for path in self.scan_paths]

    def filter_images(self, criteria: Dict[str, Any]) -> DataFrame:
        """
        Filter images based on metadata criteria.

        Args:
            criteria: Dictionary of column names and values to filter by

        Returns:
            Filtered DataFrame
        """
        if self.image_dataframe is None:
            return DataFrame()

        mask = True
        for column, value in criteria.items():
            if column in self.image_dataframe.columns:
                mask &= self.image_dataframe[column] == value

        return self.image_dataframe[mask]

    def filter_directory(self, directory: str) -> pd.DataFrame:
        """
        Filter images by directory, returning rows where the directory column contains the specified substring.

        Args:
            directory (str): The directory substring to search for (e.g., 'D:\\AI Art\\Images\\').

        Returns:
            pd.DataFrame: Filtered DataFrame containing rows where the directory column matches.
        """
        if self.image_dataframe is None:
            logger.warning("DataFrame is not initialized.")
            # Return empty DataFrame with same structure
        if not isinstance(directory, str) or not directory.strip():
            logger.warning(f"Invalid directory: {directory}")
            return pd.DataFrame(columns=self.image_dataframe.columns)  # Return empty DataFrame with same structure

        # Escape backslashes if necessary (for Windows paths)
        directory = directory.replace('\\', '\\\\')

        # Filter DataFrame using str.contains
        filtered_df = self.image_dataframe[
            self.image_dataframe['directory'].str.contains(directory, case=False, na=False)
        ]

        logger.info(f"Filtered {len(filtered_df)} rows for directory: {directory}")
        return filtered_df

    # def filter_dataframe(dataframe, ):
    @staticmethod
    def apply_sort(dataframe, by: str='size', ascending = True):
        logger.info(f"Applying Sorting-{by}-order asc {ascending}")
        # self.tab_dataframe.reset_index(drop=True, inplace=True)
        return dataframe.sort_values(by=by, ascending=ascending)

    @staticmethod
    def apply_filter(
            df: pd.DataFrame,
            filters: Union[str, List[str]],
            excluded: bool = False,
            scope: str = 'default',
            max_limit: int = 25,
            is_case_sensitive: bool = False,
            is_exact_match: bool = False
    ) -> Optional[pd.DataFrame]:
        """
        Filter image paths based on keyword matches in specified columns.

        Args:
            df: DataFrame containing image data with required columns.
            filters: Keyword(s) to filter by (string or list of strings).
            excluded: If True, exclude matching rows instead of including them.
            scope: Search scope ['default', 'filename', 'neg_prompt', 'pos_prompt', 'seed'].
            max_limit: Maximum number of results to return.
            is_case_sensitive: Perform case-sensitive matching if True.
            is_exact_match: Require exact matches if True.

        Returns:
            Filtered DataFrame with selected columns, or None if invalid input.

        Raises:
            KeyError: If required columns are missing.
        """
        # Validate input
        if not isinstance(filters, (str, list)):
            logger.warning(f"Invalid filter type: {type(filters)}")
            return None

        # Check required columns
        required_columns = {'filename', 'pos_prompt', 'neg_prompt', 'seed', 'path', 'hash'}
        missing = required_columns - set(df.columns)
        if missing:
            raise KeyError(f"Missing required columns: {sorted(missing)}, {df.columns}")

        # Process keywords
        keywords = [k.strip() for k in (filters.split(',') if isinstance(filters, str) else filters) if k.strip()]
        if not keywords:
            logger.warning("No valid keywords provided")
            return None

        # Prepare for case sensitivity
        if not is_case_sensitive:
            keywords = [k.lower() for k in keywords]
        regex_pattern = '|'.join(map(re.escape, keywords))

        # Normalize scope
        scope = scope.strip().lower().replace(" ", "_")
        scopes = {'default', 'filename', 'neg_prompt', 'pos_prompt', 'seed'} if scope == 'default' else {scope}

        # Initialize mask
        mask = pd.Series(False, index=df.index)

        # Helper function for prompt processing
        def process_prompts(prompts):
            if isinstance(prompts, (list, tuple, np.ndarray)):
                return ' '.join(p.lower() if not is_case_sensitive else p for p in prompts)
            elif isinstance(prompts, str):
                return prompts.lower() if not is_case_sensitive else prompts
            return ''

        # Apply filters based on scope
        if 'filename' in scopes:
            if is_exact_match:
                mask |= df['filename'].isin(keywords)
            else:
                mask |= df['filename'].str.contains(regex_pattern, case=is_case_sensitive, na=False)

        if 'seed' in scopes:
            seed_str = df['seed'].astype(str)
            if is_exact_match:
                mask |= seed_str.isin(keywords)
            else:
                mask |= seed_str.str.contains(regex_pattern, case=is_case_sensitive, na=False)

        if 'pos_prompt' in scopes:
            if is_exact_match:
                mask |= df['pos_prompt'].apply(
                    lambda x: any(k in x for k in keywords) if isinstance(x, (list, tuple, np.ndarray)) else False)
            else:
                prompt_str = df['pos_prompt'].apply(process_prompts)
                print("prompt: ", prompt_str)
                mask |= prompt_str.str.contains(regex_pattern, case=is_case_sensitive, na=False)

        if 'neg_prompt' in scopes:
            if is_exact_match:
                mask |= df['neg_prompt'].apply(
                    lambda x: any(k in x for k in keywords) if isinstance(x, (list, tuple, np.ndarray)) else False)
            else:
                prompt_str = df['neg_prompt'].apply(process_prompts)
                mask |= prompt_str.str.contains(regex_pattern, case=is_case_sensitive, na=False)

        # Apply exclusion if needed
        if excluded:
            mask = ~mask

        # Return filtered results
        return df.loc[mask, ['path', 'hash']].head(max_limit)
    # print(type(filter))

    def __len__(self) -> int:
        """Return number of images."""
        return len(self.images)

    def __del__(self):
        """Cleanup resources."""
        self.executor.shutdown(wait=True)


scan_dirs = []
try:
    with open("config.json", "r") as config_file:
        config = json.load(config_file)

        config.get('output_dirs')
        for key, value in config.get('output_dirs', {}).items():
            scan_dirs.append(value)
except FileNotFoundError:
    logger.error("Config file not found")


card_manager = CoverCardManager()
image_manager = ImageManager(scan_dirs)
info_view_manager = InfoNotificationManager()
# asyncio.run(image_manager.refresh())
# print(image_manager.get_image_metadata(r"D:\AI Art\Images\Text2Img\00001-2025-04-06-hassakuXLIllustrious_v21fix.jpg"))

# image_manager.backup()S
