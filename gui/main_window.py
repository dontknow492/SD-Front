from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QFrame, QVBoxLayout
from qfluentwidgets import FluentWindow, SubtitleLabel, setFont, FluentIcon, NavigationItemPosition, \
    PopUpAniStackedWidget, \
    NavigationToolButton, FluentIconBase, NavigationPushButton, NavigationBarPushButton

from gui.common import HoverSplitter
from gui.interface import GalleryInterface
from gui.interface import TxtOptionWindow, ExtraOptionWindow, ControlOptionWindow, ImgOptionWindow
from loguru import logger
from api import api_manager
from utils import IconManager

from gui.elements import ImageBox, ImageInputBox

class Widget(QFrame):

    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.label = SubtitleLabel(text, self)
        self.hBoxLayout = QHBoxLayout(self)

        setFont(self.label, 24)
        self.label.setAlignment(Qt.AlignCenter)
        self.hBoxLayout.addWidget(self.label, 1, Qt.AlignCenter)

        # Must set a globally unique object name for the sub-interface
        self.setObjectName(text.replace(' ', '-'))

class SDFront(FluentWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle("SD Front")

        # self._init_window()
        # self.sd_api = api_manager


        self.spliter = HoverSplitter(orientation=Qt.Orientation.Horizontal)
        self.spliter.setHandleWidth(2)

        self.output_image = ImageBox(self.spliter)
        self.input_image = ImageInputBox(self.spliter)
        self.option_stack = PopUpAniStackedWidget(self.spliter)

        self.text_interface = TxtOptionWindow(self)
        self.text_interface.setObjectName("Text Interface")
        self.image_interface = ImgOptionWindow()
        self.image_interface.setObjectName("Image OptionWindow")
        self.controls_interface = ControlOptionWindow()
        self.controls_interface.setObjectName("Controls OptionWindow")
        self.extras_interface = ExtraOptionWindow()
        self.extras_interface.setObjectName("Extras Interface")


        self.gallery_interface = GalleryInterface(self)
        self.gallery_interface.setObjectName("Gallery Interface")
        self.settings_interface = Widget("Settings Interface", self)

        self.has_input_box = [self.extras_interface, self.image_interface]

        self._init_ui()
        self._init_navigation()
        api_manager.fetch_sampler()
        self._signal_listener()
#
    def _init_ui(self):
        self.option_stack.addWidget(self.text_interface)
        self.option_stack.addWidget(self.image_interface)
        self.option_stack.addWidget(self.controls_interface)
        self.option_stack.addWidget(self.extras_interface)

        self.spliter.addWidget(self.option_stack)
        self.spliter.addWidget(self.input_image)
        self.spliter.addWidget(self.output_image)


        self.spliter.setStretchFactor(0, 0)
        self.spliter.setStretchFactor(1, 1)
        self.spliter.setStretchFactor(2, 1)

        self.input_image.hide()

        self.stackedWidget.addWidget(self.spliter)

        # self.stackedWidget.addWidget(self.spliter)
        self.switchTo(self.spliter)

    def _init_navigation(self):
        navigation_bar = self.navigationInterface
        txt_button = NavigationPushButton(IconManager.TEXT_SIZE, "Text", True)
        img_button = NavigationPushButton(FluentIcon.PHOTO, "Image", True)
        controls_button = NavigationPushButton(FluentIcon.ROBOT, "Controls", True)
        extra_button = NavigationPushButton(IconManager.PROCESS_BOX, "Extras", True)

        navigation_bar.addWidget('txt2img', txt_button, lambda : self.option_switch(self.text_interface))
        navigation_bar.addWidget('img2img', img_button,  lambda : self.option_switch(self.image_interface))
        navigation_bar.addWidget('controls', controls_button,   lambda : self.option_switch(self.controls_interface))
        navigation_bar.addWidget('extras', extra_button , lambda : self.option_switch(self.extras_interface))

        txt_button.setSelected(True)

        self.addSubInterface(self.gallery_interface, FluentIcon.ALBUM, "Gallery")
        self.addSubInterface(self.settings_interface, FluentIcon.SETTING, "Settings", position=NavigationItemPosition.BOTTOM)

    def _signal_listener(self):
        api_manager.image_progress_updated.connect(self.on_generation_progress)
        api_manager.image_generated.connect(self.on_generation_finished)
        api_manager.image_generation_error.connect(self.on_generation_error)
        self.output_image.generate_image.connect(self._on_image_generate)

    def option_switch(self, option):
        self.switchTo(self.spliter)
        if option in self.has_input_box:
            self.input_image.show()
        else:
            self.input_image.hide()
        self.option_stack.setCurrentWidget(option)


    def _on_image_generate(self):
        current_widget = self.option_stack.currentWidget()
        if current_widget == self.text_interface:
            logger.debug("Text Generate")
            payload = self.text_interface.get_payload()
            # print(payload)
            api_manager.generate_txt_image(payload)
        elif current_widget == self.image_interface:
            logger.debug("Image Generate")
        elif current_widget == self.controls_interface:
            logger.debug("Controls Generate")
        elif current_widget == self.extras_interface:
            logger.debug("Extras Generate")

    def on_generation_progress(self, progress: dict):
        self.output_image.on_progress(progress)

    def on_generation_finished(self, image_data: dict):
        self.output_image.on_finished(image_data)

    def on_generation_error(self, error: str):
        logger.error(f"Error Generating image: {error}")
        self.output_image.on_error(error)
