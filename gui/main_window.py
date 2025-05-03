from typing import Callable, Optional

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices, QPixmap
from PySide6.QtWidgets import QHBoxLayout, QFrame
from qfluentwidgets import FluentWindow, SubtitleLabel, setFont, FluentIcon, NavigationItemPosition, \
    PopUpAniStackedWidget, \
    NavigationPushButton, MessageBox
from config import GenerationTypeFlags
from gui.common import HoverSplitter
from gui.interface import GalleryInterface
from gui.interface import TxtOptionWindow, ExtraOptionWindow, ControlOptionWindow, ImgOptionWindow
from loguru import logger
from api import sd_api_manager
from manager import info_view_manager
from utils import IconManager,  save_sdwebui_image_with_info
from gui.elements import OutputImageBox, ImageInputBox
from gui.common import NaviAvatarWidget
from gui.components import NotificationWidget

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

        self._current_image_data = dict()
        self.setWindowTitle("SD Front")
        self._current_image_gen = GenerationTypeFlags.TEXT2IMAGE
        self._previous_gen_data = dict()
        # self._init_window()
        # self.sd_api = sd_api_manager


        self.spliter = HoverSplitter(orientation=Qt.Orientation.Horizontal)
        self.spliter.setHandleWidth(2)

        self.outputImageView = OutputImageBox(self.spliter)
        self.inputImageView = ImageInputBox(self.spliter)
        self.option_stack = PopUpAniStackedWidget(self.spliter)

        self.text2image_interface = TxtOptionWindow(self)
        self.text2image_interface.setObjectName("Text Interface")
        self.image2image_interface = ImgOptionWindow()
        self.image2image_interface.setObjectName("Image OptionWindow")
        self.controls_interface = ControlOptionWindow()
        self.controls_interface.setObjectName("Controls OptionWindow")
        self.extras_interface = ExtraOptionWindow()
        self.extras_interface.setObjectName("Extras Interface")


        self.gallery_interface = GalleryInterface(self)
        self.gallery_interface.setObjectName("Gallery Interface")
        self.settings_interface = Widget("Settings Interface", self)

        #notification
        self.notification_widget = NotificationWidget(self)
        self.notification_widget.setTitle("Notification")
        self.notification_widget.setDescription("This is a notification")
        self.notification_widget.adjustSize()

        self.has_input_box = [self.extras_interface, self.image2image_interface]

        self._init_ui()
        self._init_navigation()
        self._signal_listener()
        sd_api_manager.get_samplers()
        sd_api_manager.check_server_status()
#
    def _init_ui(self):
        self.option_stack.addWidget(self.text2image_interface)
        self.option_stack.addWidget(self.image2image_interface)
        self.option_stack.addWidget(self.controls_interface)
        self.option_stack.addWidget(self.extras_interface)

        self.spliter.addWidget(self.option_stack)
        self.spliter.addWidget(self.inputImageView)
        self.spliter.addWidget(self.outputImageView)


        self.spliter.setStretchFactor(0, 0)
        self.spliter.setStretchFactor(1, 1)
        self.spliter.setStretchFactor(2, 1)

        self.inputImageView.hide()

        self.stackedWidget.addWidget(self.spliter)

        # self.stackedWidget.addWidget(self.spliter)
        self.switchTo(self.spliter)

    def _init_navigation(self):
        navigation_bar = self.navigationInterface
        txt_button = NavigationPushButton(IconManager.TEXT_SIZE, "Text", True)
        img_button = NavigationPushButton(FluentIcon.PHOTO, "Image", True)
        controls_button = NavigationPushButton(FluentIcon.ROBOT, "Controls", True)
        extra_button = NavigationPushButton(IconManager.PROCESS_BOX, "Extras", True)

        navigation_bar.addWidget('txt2img', txt_button, lambda : self.option_switch(self.text2image_interface))
        navigation_bar.addWidget('img2img', img_button,  lambda : self.option_switch(self.image2image_interface))
        navigation_bar.addWidget('controls', controls_button,   lambda : self.option_switch(self.controls_interface))
        navigation_bar.addWidget('extras', extra_button , lambda : self.option_switch(self.extras_interface))

        txt_button.setSelected(True)

        self.addSubInterface(self.gallery_interface, FluentIcon.ALBUM, "Gallery")
        #bottom
        self.server_avatar_widget = NaviAvatarWidget()
        self.server_avatar_widget.text = sd_api_manager.url
        navigation_bar.addWidget("server", self.server_avatar_widget, self.open_in_web, NavigationItemPosition.BOTTOM, "Open in Web", None)
        self.addSubInterface(self.settings_interface, FluentIcon.SETTING, "Settings", position=NavigationItemPosition.BOTTOM)

    def _signal_listener(self):
        sd_api_manager.image_progress_updated.connect(self.on_generation_progress)
        sd_api_manager.image_generated.connect(self.on_generation_finished)
        sd_api_manager.image_generation_error.connect(self.on_generation_error)
        sd_api_manager.server_status_changed.connect(self.on_server_status_changed)

        self.outputImageView.generate_image.connect(self._on_image_generate)
        self.outputImageView.sendTo_signal.connect(self.send_to)

        #notification
        info_view_manager.showInfo.connect(self.show_in_app_notification)
        info_view_manager.hideInfo.connect(self.notification_widget.hide)


    def option_switch(self, option):
        self.switchTo(self.spliter)
        if option in self.has_input_box:
            self.inputImageView.show()
        else:
            self.inputImageView.hide()
        self.option_stack.setCurrentWidget(option)


    def _on_image_generate(self):
        current_widget = self.option_stack.currentWidget()
        self.outputImageView.reset_preview()
        self.outputImageView.hide_preview()
        if current_widget == self.text2image_interface:
            logger.debug("Text Generate")
            payload = self.text2image_interface.get_payload()
            self._current_image_gen = GenerationTypeFlags.TEXT2IMAGE
            # print(payload)
            sd_api_manager.generate_txt_image(payload)
        elif current_widget == self.image2image_interface:
            logger.debug("Image Generate")
            self._current_image_gen = GenerationTypeFlags.IMAGE2IMAGE
        elif current_widget == self.controls_interface:
            logger.debug("Controls Generate")
            self._current_image_gen = GenerationTypeFlags.CONTROLS
        elif current_widget == self.extras_interface:
            logger.debug("Extras Generate")
            self._current_image_gen = GenerationTypeFlags.EXTRAS

    def on_generation_progress(self, progress: dict):
        self.outputImageView.on_progress(progress)

    def on_generation_finished(self, image_data: dict):
        # self._previous_gen_data = self._current_image_data
        self._current_image_data = image_data
        self.outputImageView.on_finished(image_data)
        #todo: make it dynamic(based on config).
        if save_sdwebui_image_with_info(image_data, f"outputs/{self._current_image_gen.value()}"):
            logger.info("Image saved successfully")
        else:
            logger.error("Failed to save image")
            self.show_message("Error", "Failed to save image")

    def on_generation_error(self, error: str):
        logger.error(f"Error Generating image: {error}")
        self.outputImageView.on_error(error)
        self.show_message("Error", f"Error Generating image: {error}")

    def send_to(self, to: GenerationTypeFlags, pixmap: QPixmap):
        #todo crete payload setter for all generation types
        if self._current_image_gen == to:
            logger.warning("Same generation type")
            return
        if to == GenerationTypeFlags.TEXT2IMAGE:
            payload = self._current_image_data.get('parameters')
            self.text2image_interface.set_payload(payload)
        if to == GenerationTypeFlags.IMAGE2IMAGE:
            payload = self._current_image_data.get('parameters')
            self.image2image_interface.set_payload(payload)
        if to == GenerationTypeFlags.CONTROLS:
            payload = self._current_image_data.get('parameters')
            self.controls_interface.set_payload(payload)
        if to == GenerationTypeFlags.EXTRAS:
            payload = self._current_image_data.get('parameters')

            # self.extras_interface.set_payload(payload)
        self.inputImageView.set_pixmap(pixmap)


    def open_in_web(self):
        url = sd_api_manager.url
        QDesktopServices.openUrl(QUrl(url))

    def on_server_status_changed(self, status: bool):
        if status == self.server_avatar_widget.get_status():
            return
        self.server_avatar_widget.set_status(status)
        title = "Server Status"
        if status:
            message = "Server back online :)"
        else:
            message = "Server offline :("

        self.show_message(title, message)

    def show_message(self, title: str, message: str,
                     on_confirm: Optional[Callable] = None,
                     on_cancel: Optional[Callable] = None,
                     confirm_args: tuple = (),
                     cancel_args: tuple = ()):
        message_box = MessageBox(title, message, self)
        if message_box.exec():
            if on_confirm:
                on_confirm(*confirm_args)
        else:
            if on_cancel:
                on_cancel(*cancel_args)

    def show_in_app_notification(self, title: str, description: str, icon):
        print("notification")
        self.notification_widget.setIcon(icon)
        self.notification_widget.setTitle(title)
        self.notification_widget.setDescription(description)
        self.notification_widget.adjustSize()
        self.notification_widget.show()
        self.notification_widget.move(self.width() - self.notification_widget.width() - 20, 20)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.notification_widget.move(self.width() - self.notification_widget.width() - 20, 20)
