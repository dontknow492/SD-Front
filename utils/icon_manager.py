from qfluentwidgets import FluentIconBase, Theme, getIconColor, ToolButton
from PySide6.QtWidgets import QApplication
from pathlib import Path
from enum import Enum

class IconManager(FluentIconBase, Enum):
    BOT = "bot"
    BRUSH = "brush"
    CONTROL_MULTIMEDIA_PLAYER = "control-multimedia-player"
    DELETE = "delete"
    DOWNLOAD = "download"
    FOLDER_FAVOURITE_BOOKMARK = "folder-favourite-bookmark"
    FOLDER_FAVOURITE_STAR = "folder-favourite-star"
    FOLDER_OPEN = "folder-open"
    IMAGE_PEN = "image-pen"
    LOOP = "loop"
    MODEL_ALT = "model-alt"
    NO_IMAGE = "no-image"
    PAINT_BRUSH = "paint-brush"
    PASTE = "paste"
    PERSPECTIVE_DICE_RANDOM = "perspective-dice-random"
    PROCESS_BOX = "process-box"
    PROCESS = "process"
    PROMPT_EDIT = "prompt-edit"
    RECYCLE = "recycle"
    SCRIPT = "script"
    SKIP_FORWARD = "skip-forward"
    STAR_FALL = "star-fall"
    STOP = "stop"
    SWAP = "swap"
    TERMINAL = "terminal"
    TEXT_SIZE_BUTTON = "text-size-button"
    TEXT_SIZE = "text-size"
    UP_ARROW = "up-arrow"
    ASPECT_RATIO = "ar-zone"
    DATA = "data"
    TEMP_FOLDER = "temp-opened"
    SLIDER = "slider-01"
    CLOCK = "clock-three"
    LIVE = "live"

    def path(self, theme=Theme.AUTO):
        # getIconColor() return "white" or "black" according to current theme
        return f'assets/icons/{getIconColor(theme)}/{self.value}-svgrepo-com.svg'