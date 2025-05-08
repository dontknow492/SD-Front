import asyncio

from PySide6.QtGui import QColor

from gui.main_window import SDFront
from api import sd_api_manager
from PySide6.QtWidgets import QApplication
import sys
from qasync import QEventLoop
# from manager import image_manager
from loguru import logger
from qfluentwidgets import setTheme, Theme
from manager import image_manager
import json
from config import sd_config

def save_data(data):
    print('saving')
    with open("data.json", "w") as f:
        json.dump(data, f)

def main():
    setTheme(Theme.DARK)
    logger.add("logs/app.log", rotation="500 MB", level="DEBUG")
    app = QApplication(sys.argv)
    logger.info("Starting app")
    event_loop = QEventLoop(app)
    logger.info("Event loop created")
    asyncio.set_event_loop(event_loop)
    logger.info("Event loop set")

    app_close_event = asyncio.Event()
    app.aboutToQuit.connect(app_close_event.set)
    asyncio.ensure_future(image_manager.refresh())

    main_window = SDFront()
    main_window.setMicaEffectEnabled(True)
    # main_window
    sd_config.enableMica.valueChanged.connect(main_window.setMicaEffectEnabled)
    sd_config.themeColorChanged.connect(lambda color: set_background_colors(color, main_window))

    logger.info("SDFront initialized")
    main_window.showMaximized()
    logger.info("SDFront shown")

    sd_api_manager.get_samplers()
    sd_api_manager.check_server_status()

    with event_loop:
        event_loop.run_until_complete(app_close_event.wait())
        logger.info("App closed")
        # exit(0)

def set_background_colors(theme_color: QColor, main_window):
    # print('color')
    if main_window.isMicaEffectEnabled():
        return
    light_bg, dark_bg = get_background_colors_from_theme(theme_color)
    main_window.setCustomBackgroundColor(light_bg, dark_bg)


def get_background_colors_from_theme(theme_color: QColor):
    # Convert to HSL for manipulation
    h = theme_color.hslHue()
    s = theme_color.hslSaturation()

    # Light mode: high lightness, low saturation (tint)
    light_bg = QColor()
    light_bg.setHsl(h, int(s * 0.2), int(255 * 0.95))  # lightness near 242/255

    # Dark mode: low lightness, moderate saturation (shade)
    dark_bg = QColor()
    dark_bg.setHsl(h, int(s * 0.4), int(255 * 0.12))  # lightness around 31/255

    return light_bg, dark_bg


# Example usage


if __name__ == "__main__":
    main()
    # theme_color = QColor("#009f2a")  # Blue
    # light_bg, dark_bg = get_background_colors_from_theme(theme_color)
    # # 29f1ff
    # # #009faa
    # print("Light background:", light_bg.name())
    # print("Dark background:", dark_bg.name())

