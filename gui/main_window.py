import json
import os
import zipfile
from datetime import datetime
from typing import Callable, Optional
from PySide6.QtCore import Qt, QUrl, QTimer
from PySide6.QtGui import QDesktopServices, QPixmap, QColor
from PySide6.QtWidgets import QHBoxLayout, QFrame, QWidget, QFileDialog, QGridLayout, QDialog
from qasync import asyncSlot
from qfluentwidgets import FluentWindow, FluentIcon, NavigationItemPosition, \
    PopUpAniStackedWidget, \
    NavigationPushButton, MessageBox
from config import GenerationTypeFlags, sd_config
from gui.common import HoverSplitter
from gui.interface import GalleryInterface
from gui.interface import TxtOptionWindow, ExtraOptionWindow, ControlOptionWindow, ImgOptionWindow, SettingsInterface
from loguru import logger
from api import sd_api_manager
from manager import info_view_manager, image_manager
from utils import IconManager, save_sdwebui_image_with_info, base64_pixmap, pixmap_base64
from gui.elements import OutputImageBox, ImageInputBox
from gui.common import NaviAvatarWidget, InfoTime
from gui.components import NotificationWidget, BackupOptionsDialog

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
        self.settings_interface = SettingsInterface(self)
        self.settings_interface.setObjectName("Settings Interface")
        #notification
        self.notification_widget = NotificationWidget(self)
        self.notification_widget.setTitle("Notification")
        self.notification_widget.setDescription("This is a notification")
        self.notification_widget.adjustSize()

        self.has_input_box = [self.extras_interface, self.image2image_interface]

        self._init_ui()
        self._init_navigation()
        self._signal_listener()

        QTimer.singleShot(1000, self.load_state)
        sd_config.maxGalleryImages.valueChanged.connect(self.gallery_interface.set_preload_images)

        # sd_api_manager.check_server_status()
        self.info_bar = InfoTime(self)
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

        #settings
        self.settings_interface.clearCacheSignal.connect(self.clear_cache)
        self.settings_interface.backupSignal.connect(self.backup)
        self.settings_interface.restoreSignal.connect(self.restore_backup)

    def switchTo(self, interface: QWidget):
        if interface == self.gallery_interface:
            self.refresh_gallery()
        super().switchTo(interface)

    def option_switch(self, option):
        self.switchTo(self.spliter)
        if option in self.has_input_box:
            self.inputImageView.show()
        else:
            self.inputImageView.hide()
        self.option_stack.setCurrentWidget(option)

    @asyncSlot()
    async def refresh_gallery(self):
        await image_manager.refresh()


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
            init_image = self.inputImageView.get_pixmap()
            if init_image is None:
                self.info_bar.error_msg("Error", "Please insert valid image to input image box")
                QTimer.singleShot(500, lambda : self.outputImageView.enable_generation(True))
                return
            payload = self.image2image_interface.get_payload()
            raw_init_image = pixmap_base64(init_image, "png")
            # logger.critical(f"Init Image: {raw_init_image[100]}")
            pixmap = base64_pixmap(raw_init_image)
            payload['init_images'] = [raw_init_image]
            self._current_image_gen = GenerationTypeFlags.IMAGE2IMAGE
            sd_api_manager.generate_img2img_image(payload)
        elif current_widget == self.controls_interface:
            logger.debug("Controls Generate")
            self._current_image_gen = GenerationTypeFlags.CONTROLS
        elif current_widget == self.extras_interface:
            logger.debug("Extras Generate")
            self._current_image_gen = GenerationTypeFlags.EXTRAS

        # logger.debug(f"Current Image Generation Type: {self._current_image_gen}, Payload: {payload}")

    def on_generation_progress(self, progress: dict):
        live_preview = sd_config.showLivePreview.value
        self.outputImageView.on_progress(progress, live_preview)

    def on_generation_finished(self, image_data: dict):
        # self._previous_gen_data = self._current_image_data
        images = image_data.get('images')
        if not len(images):
            logger.error("No images generated")
            self.show_message("Error", "Error on server side check logs. :|")
            self.outputImageView.on_error("No images generated")
            return

        self._current_image_data = image_data
        self.outputImageView.on_finished(image_data)
        #todo: make it dynamic(based on config).
        match self._current_image_gen:
            case GenerationTypeFlags.TEXT2IMAGE:
                output_dir = sd_config.txt2imgDir.value
            case GenerationTypeFlags.IMAGE2IMAGE:
                output_dir = sd_config.img2imgDir.value
            case GenerationTypeFlags.CONTROLS:
                output_dir = sd_config.controlsDir.value
            case GenerationTypeFlags.EXTRAS:
                output_dir = sd_config.extrasDir.value
            case _:
                output_dir = None
                logger.error("Unknown generation type")

        if save_sdwebui_image_with_info(image_data, output_dir, save_txt=sd_config.saveGenInfoToTxt.value,
                                        image_format=sd_config.defaultImageFormat.value):
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
            self.option_switch(self.text2image_interface)
        if to == GenerationTypeFlags.IMAGE2IMAGE:
            payload = self._current_image_data.get('parameters')
            self.image2image_interface.set_payload(payload)
            self.option_switch(self.image2image_interface)
        if to == GenerationTypeFlags.CONTROLS:
            payload = self._current_image_data.get('parameters')
            self.controls_interface.set_payload(payload)
            self.option_switch(self.controls_interface)
        if to == GenerationTypeFlags.EXTRAS:
            payload = self._current_image_data.get('parameters')
            self.option_switch(self.extras_interface)

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

    def save_state(self):
        """Save the current state of the application."""
        logger.info("Saving application state")

        payload = {
            'txt2img': self.text2image_interface.get_payload(),
            'img2img': self.image2image_interface.get_payload(),
            'controls': self.controls_interface.get_payload(),
            'extras': self.extras_interface.get_payload()
        }
        os.makedirs("config", exist_ok=True)
        file_path = "config/app_state.json"

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=4)
            logger.success(f"Application state saved to: {file_path}")
        except Exception as e:
            logger.error(f"Failed to save application state: {e}")

    def load_state(self):
        """Load the saved state of the application."""
        logger.info("Loading application state")
        try:
            with open('config/app_state.json', "r") as file:
                payload = json.load(file)
                self.text2image_interface.set_payload(payload['txt2img'])
                self.image2image_interface.set_payload(payload['img2img'])
                self.controls_interface.set_payload(payload['controls'])
                self.extras_interface.set_payload(payload['extras'])
        except FileNotFoundError:
            logger.warning("No saved state found")
        except json.JSONDecodeError:
            logger.error("Error decoding saved state")

    def backup(self, is_auto: bool = False):
        """Backup the current state of the application."""
        """Backup the current state of the application."""
        dialog = BackupOptionsDialog(self)
        if dialog.exec() != QDialog.Accepted:
            logger.info("Backup cancelled by user")
            return

        selected = dialog.get_selected()
        logger.info(f"Backup selections: {selected}")

        payload = {}
        if selected["txt2img"]:
            payload["txt2img"] = self.text2image_interface.get_payload()
        if selected["img2img"]:
            payload["img2img"] = self.image2image_interface.get_payload()
        if selected["controls"]:
            payload["controls"] = self.controls_interface.get_payload()
        if selected["extras"]:
            payload["extras"] = self.extras_interface.get_payload()

        os.makedirs("config", exist_ok=True)
        state_path = "config/app_state.json"
        config_path = "config/config.json"
        backup_dir = "backups"

        os.makedirs(backup_dir, exist_ok=True)

        # Save current state to app_state.json
        try:
            with open(state_path, "w", encoding="utf-8") as state_file:
                json.dump(payload, state_file, indent=4)
            logger.success("Application state saved for backup")
        except Exception as e:
            logger.error(f"Failed to save application state: {e}")
            return

        # Read existing config.json or fallback to empty config
        try:
            with open(config_path, "r", encoding="utf-8") as cfg_file:
                config = json.load(cfg_file)
        except FileNotFoundError:
            logger.warning("No config.json file found, using empty config")
            with open(config_path, "w", encoding="utf-8") as cfg_file:
                json.dump({}, cfg_file, indent=4)
        except Exception as e:
            logger.error(f"Failed to read config.json: {e}")
            return

        # Generate timestamped backup filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{backup_dir}/sd_front_backup_{timestamp}.zip"

        # Optionally let user choose location to save
        if is_auto:
            file_path = backup_filename
        else:
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Backup As",
                backup_filename,
                "ZIP Files (*.zip);;All Files (*)"
            )
            if not file_path:
                logger.info("Backup cancelled by user")
                return


        # Create ZIP with app_state.json and config.json
        try:
            with zipfile.ZipFile(file_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(state_path, arcname="app_state.json")
                zipf.write(config_path, arcname="config.json")
            logger.success(f"Backup saved successfully to: {file_path}")
            self.info_bar.success_msg("Backup", f"Backup saved successfully to: {file_path}")
        except Exception as e:
            self.show_message("Backup Error", f"Failed to create backup zip: {e}")
            logger.error(f"Failed to create backup zip: {e}")

    def restore_backup(self):
        """Restore the application state and config from a backup ZIP."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Backup ZIP File",
            "",
            "ZIP Files (*.zip);;All Files (*)"
        )
        if not file_path:
            logger.info("Restore cancelled by user")
            return

        try:
            with zipfile.ZipFile(file_path, "r") as zipf:
                if "app_state.json" not in zipf.namelist() or "config.json" not in zipf.namelist():
                    self.show_message("Invalid Backup", "required files not found in zip")
                    logger.error("Invalid backup: required files not found in zip")
                    return

                os.makedirs("config", exist_ok=True)
                zipf.extract("app_state.json", path="config")
                zipf.extract("config.json", path="config")
                logger.success("Backup files extracted")

                # # Load and apply app state
                # with open("config/app_state.json", "r", encoding="utf-8") as state_file:
                #     state = json.load(state_file)
                #
                # self.text2image_interface.set_payload(state.get("txt2img", {}))
                # self.image2image_interface.set_payload(state.get("img2img", {}))
                # self.controls_interface.set_payload(state.get("controls", {}))
                # self.extras_interface.set_payload(state.get("extras", {}))

                logger.success("Application state restored successfully")
                self.show_message("Restore Complete", "Backup successfully restored restart to apply settings.")

        except zipfile.BadZipFile:
            logger.error("Failed to open backup: Not a valid ZIP file")
            self.show_message("Restore Error", "Selected file is not a valid ZIP.")
        except Exception as e:
            logger.error(f"Failed to restore backup: {e}")
            self.show_message("Restore Error", f"An error occurred:\n{str(e)}")

    def clear_cache(self):
        """Clear the cache of the application."""
        logger.info("Clearing cache")
        #todo: clear cache

    def closeEvent(self, event, /):
        logger.info("Closing application")
        sd_api_manager.close()
        if sd_config.enableAutosave.value:
            self.save_state()
        super().closeEvent(event)
