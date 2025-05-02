import asyncio


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
    # app.aboutToQuit.connect(event_loop.stop)

    # image_manager.scan_paths([r"D:\Program\SD Front\samples\Extras", r"D:\Program\SD Front\samples\Img2Img", r"D:\Program\SD Front\samples\Text2Img"])

    asyncio.ensure_future(image_manager.refresh())

    main_window = SDFront()
    logger.info("SDFront initialized")
    main_window.showMaximized()
    logger.info("SDFront shown")

    with event_loop:
        event_loop.run_until_complete(app_close_event.wait())
        logger.info("App closed")
        # exit(0)


if __name__ == "__main__":
    main()

