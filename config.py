from enum import Enum
from pathlib import Path
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QPixmap, QIcon
from qfluentwidgets import (
    QConfig, ConfigItem, OptionsConfigItem, RangeConfigItem, ColorConfigItem,
    BoolValidator, OptionsValidator, RangeValidator, ConfigValidator, EnumSerializer,
    qconfig, setTheme, Theme, setThemeColor
)

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

class GenerationTypeFlags(Enum):
    """Flags for generation status."""
    TEXT2IMAGE = "txt2imgDir"
    IMAGE2IMAGE = "img2imgDir"
    CONTROLS = "controlsDir"
    EXTRAS = "extrasDir"


class StartupPage(Enum):
    """Startup page."""
    TXT2IMG = "txt2img"
    IMG2IMG = "img2img"
    CONTROLS = "controls"
    EXTRAS = "extras"

    @staticmethod
    def values():
        return [q.value for q in StartupPage]


def on_theme_mode_changed(mode):
    """Handle theme mode change."""
    if mode == "Light":
        setTheme(Theme.LIGHT)
    elif mode == "Dark":
        setTheme(Theme.DARK)
    else:
        setTheme(Theme.AUTO)

def on_accent_color_changed(color):
    """Handle accent color change."""
    setThemeColor(color)


class MyConfig(QConfig):
    """Application Configuration."""



    # Main Window
    themeModes = OptionsConfigItem("MainWindow", "ThemeMode", "Dark", OptionsValidator(["Light", "Dark", "Auto"]), restart=True)
    themeModes.valueChanged.connect(lambda mode: on_theme_mode_changed(mode))
    enableAcrylic = ConfigItem("MainWindow", "EnableAcrylic", False, BoolValidator())
    accentColor = ColorConfigItem("MainWindow", "AccentColor", "#009faa")
    accentColor.valueChanged.connect(lambda color: on_accent_color_changed(color))
    enableMica = ConfigItem("MainWindow", "EnableMica", True, BoolValidator())
    startupPage = OptionsConfigItem("Startup", "StartupPage", StartupPage.TXT2IMG, OptionsValidator(StartupPage),
                                    EnumSerializer(StartupPage))

    # Output Directories
    extrasDir = ConfigItem("Output", "ExtrasDir", "outputs/extras", ConfigValidator())
    txt2imgDir = ConfigItem("Output", "Txt2ImgDir", "outputs/txt2img", ConfigValidator())
    img2imgDir = ConfigItem("Output", "Img2ImgDir", "outputs/img2img", ConfigValidator())
    controlsDir = ConfigItem("Output", "ControlsDir", "outputs/controls", ConfigValidator())
    defaultImageFormat = OptionsConfigItem("Output", "DefaultImageFormat", "jpeg", OptionsValidator(["png", "jpg", "webp", "jpeg"]))

    #data directory
    dataDir = ConfigItem("Data", "DataDir", "data", ConfigValidator())

    #cache directory
    cacheDir = ConfigItem("Cache", "CacheDir", ".cache", ConfigValidator())

    # API
    apiUrl = ConfigItem("API", "Url", "http://127.0.0.1:7860", ConfigValidator(), restart=True)
    defaultSteps = RangeConfigItem("API", "DefaultSteps", 20, RangeValidator(1, 150))

    # Cache
    netCacheSize = RangeConfigItem("Cache", "NetworkCacheSize", 104857600, RangeValidator(10485760, 1048576000), restart= True)
    thumbCacheSize = RangeConfigItem("Cache", "ThumbnailCacheSize", 104857600, RangeValidator(10485760, 1048576000), restart= True)


    # Preview
    showLivePreview = ConfigItem("Preview", "ShowLivePreview", True, BoolValidator())
    livePreviewDelayMs = RangeConfigItem("Preview", "LivePreviewDelayMs", 500, RangeValidator(1, 5000))

    # Save State
    saveGenInfoToTxt = ConfigItem("Save", "SaveGenInfoToTxt", True, BoolValidator())
    enableAutosave = ConfigItem("Save", "EnableAutosave", True, BoolValidator())

    # Gallery
    maxGalleryImages = RangeConfigItem("Gallery", "PreLoadImages", 50, RangeValidator(50, 200))

    #update
    enableAutoUpdate = ConfigItem("Update", "EnableAutoUpdate", True, BoolValidator())
    repoUrl = ConfigItem("Update", "RepoUrl", "https://github.com/dontknow492/SD-Front", ConfigValidator())


    def reset_to_default(self):
        """Reset the configuration to default."""
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if isinstance(attr, ConfigItem):
                qconfig.set(attr, attr.defaultValue)





# Create a config instance and initialize it using the configuration file
sd_config = MyConfig()
qconfig.load('config/config.json', sd_config)
sd_config.reset_to_default()
print("theme color", sd_config.themeColor.value.name())
qconfig.save()