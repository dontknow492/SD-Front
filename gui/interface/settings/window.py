from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout
from config import sd_config
from qfluentwidgets import ComboBoxSettingCard, RangeSettingCard, SwitchSettingCard, HyperlinkCard, \
    ExpandGroupSettingCard, FluentIcon, OptionsSettingCard, qconfig, ColorSettingCard, FolderListSettingCard, \
    SettingCardGroup, SpinBox, PrimaryPushButton, PushSettingCard, PrimaryPushSettingCard
from gui.common import VerticalScrollWidget, LineEditSettingCard, FolderSettingCard, SizeSettingCard, SpinBoxSettingCard
from utils import IconManager


class SettingsInterface(VerticalScrollWidget):
    """ Setting interface """
    clearCacheSignal = Signal()
    aboutSignal = Signal()
    saveStateSignal = Signal()
    backupSignal = Signal()
    restoreSignal = Signal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("SettingsInterface")
        self.setLayoutMargins(0, 0, 0, 0)

        self.setContentSpacing(0)
        hboxlayout = QHBoxLayout()
        hboxlayout.setSpacing(6)
        refresh_button = PrimaryPushButton(FluentIcon.SYNC, "Refresh Server", self)
        reset_to_default = PrimaryPushButton("Reset to Default", self)
        reset_to_default.clicked.connect(sd_config.reset_to_default)
        self.scrollContainer_layout.addSpacing(10)
        self.addWidget(reset_to_default, alignment=Qt.AlignmentFlag.AlignRight, stretch=0)

        hboxlayout.addStretch(1)
        hboxlayout.addWidget(refresh_button)
        hboxlayout.addWidget(reset_to_default)

        #main window
        main_win_group = SettingCardGroup(
            title="Main Window"
            , parent=self
        )
        image_save_format = ComboBoxSettingCard(
            configItem=sd_config.defaultImageFormat,
            icon=FluentIcon.DOWNLOAD,
            title="Image Format",
            content="Select the default Image Format",
            texts=sd_config.defaultImageFormat.options,
            parent=self
        )

        theme_card = OptionsSettingCard(
                sd_config.themeModes,
                FluentIcon.BRUSH,
                "Application Theme",
                "Adjust the appearance of your application",
                texts=["Light", "Dark", "Follow System Settings"]
            )

        enable_acrylic = SwitchSettingCard(
            icon=FluentIcon.TILES,
            title="Enable Acrylic Effect",
            content="Enable Acrylic Effect",
            configItem=sd_config.enableAcrylic
        )

        accent_color_card = ColorSettingCard(
            sd_config.accentColor,
            FluentIcon.PENCIL_INK,
            "Accent Color",
            "Select the accent color of your application",
            parent=self
        )
        startup_page = OptionsSettingCard(
            configItem=sd_config.startupPage,
            icon=FluentIcon.FIT_PAGE,
            title="Startup Page",
            content="Set the default startup page",
            texts=['Text', "Image", "Extras", "Controls"],
            parent=self
        )
        mica_effect = SwitchSettingCard(
            icon=FluentIcon.DEVELOPER_TOOLS,
            title="Mica Effect",
            content="Enable Mica Effect",
            configItem=sd_config.enableMica
        )

        main_win_group.addSettingCards(
            [
                theme_card,
                enable_acrylic,
                accent_color_card,
                mica_effect,
                image_save_format,
                startup_page
            ]
        )

        #output directories
        output_dir_group = SettingCardGroup(
            title="Output Directories"
            , parent=self
        )
        extras_dir = FolderSettingCard(
            configItem=sd_config.extrasDir,
            title="Extras Directory",
            content="Select the directory where the extras will be saved",
            parent=self
        )
        txt2img_dir = FolderSettingCard(
            configItem=sd_config.txt2imgDir,
            title="Txt2Img Directory",
            content="Select the directory where the txt2img images will be saved",
            parent=self,
            icon = FluentIcon.FONT_SIZE,
        )
        img2img_dir = FolderSettingCard(
            configItem=sd_config.img2imgDir,
            title="Img2Img Directory",
            content="Select the directory where the img2img images will be saved",
            parent=self,
            icon = FluentIcon.PHOTO
        )
        controls_dir = FolderSettingCard(
            configItem=sd_config.controlsDir,
            title="Controls Directory",
            content="Select the directory where the controls will be saved",
            parent=self,
            icon=FluentIcon.ROBOT
        )

        data_dir = FolderSettingCard(
            configItem=sd_config.dataDir,
            title="Data Directory",
            content="Select the directory where the data will be saved",
            parent=self,
            icon=IconManager.DATA
        )
        cache_dir = FolderSettingCard(
            configItem=sd_config.cacheDir,
            title="Cache Directory",
            content="Select the directory where the cache will be saved",
            parent=self,
            icon=FluentIcon.ZIP_FOLDER
        )

        output_dir_group.addSettingCards(
            [
                extras_dir,
                txt2img_dir,
                img2img_dir,
                controls_dir,
                data_dir,
                cache_dir
            ]
        )

        #api
        api_group = SettingCardGroup(
            title="API"
            , parent=self
        )
        api_url = LineEditSettingCard(
            icon=FluentIcon.GLOBE,
            title="API URL",
            content="Set the URL of the API",
            config_item=sd_config.apiUrl,
            parent=self
        )

        default_steps = RangeSettingCard(
            configItem=sd_config.defaultSteps,
            icon=IconManager.SLIDER,
            title="Default Steps",
            content="Set the default number of steps",
            parent=self
        )

        api_group.addSettingCards(
            [
                api_url,
                default_steps
            ]
        )

        #cache
        cache_group = SettingCardGroup(
            title="Cache"
            , parent=self
        )
        net_cache_size = SizeSettingCard(
            configItem=sd_config.netCacheSize,
            icon=IconManager.TEMP_FOLDER,
            title="Network Cache Size",
            content="Set the size of the network cache",
            parent=self
        )
        thumb_cache_size = SizeSettingCard(
            configItem=sd_config.thumbCacheSize,
            icon=IconManager.TEMP_FOLDER,
            title="Thumbnail Cache Size",
            content="Set the size of the thumbnail cache for Gallery(in memory)",
            parent=self
        )
        clear_cache = PushSettingCard(
            text="Clear Cache",
            icon=IconManager.DELETE,
            title="Clear Cache",
            content="Clear the app cache",
            parent=self
        )
        clear_cache.clicked.connect(self.clearCacheSignal.emit)
        cache_group.addSettingCards(
            [
                net_cache_size,
                thumb_cache_size,
                clear_cache
            ]
        )



        #preview
        preview_group = SettingCardGroup(
            title="Preview"
            , parent=self
        )
        show_live_preview = SwitchSettingCard(
            icon=IconManager.LIVE,
            title="Show Live Preview",
            content="Show live preview of the image",
            configItem=sd_config.showLivePreview
        )

        live_preview_delay_ms = SpinBoxSettingCard(
            configItem=sd_config.livePreviewDelayMs,
            icon=FluentIcon.STOP_WATCH,
            title="Live Preview Delay",
            content="Set the delay of the live preview",
            parent=self
        )
        live_preview_delay_ms.setSuffix("ms")
        preview_group.addSettingCards(
            [
                show_live_preview,
                live_preview_delay_ms
            ]
        )

        #save state
        save_group = SettingCardGroup(
            title="Save"
            , parent=self
        )
        save_gen_info_to_txt = SwitchSettingCard(
            icon=FluentIcon.MESSAGE,
            title="Save Generation Info",
            content="Save generation info to txt",
            configItem=sd_config.saveGenInfoToTxt
        )
        enable_autosave = SwitchSettingCard(
            icon=FluentIcon.SAVE_AS,
            title="Enable Autosave",
            content="Enable autosave",
            configItem=sd_config.enableAutosave
        )
        backup = PrimaryPushSettingCard(
            text="Backup",
            icon=FluentIcon.SAVE_AS,
            title="Backup",
            content="Create backup file.",
            parent=self
        )
        restore = PrimaryPushSettingCard(
            text="Restore",
            icon=FluentIcon.SYNC,
            title="Restore",
            content="Restore the saved state",
            parent=self
        )
        save_group.addSettingCards(
            [
                save_gen_info_to_txt,
                enable_autosave,
                backup,
                restore
            ]
        )
        backup.clicked.connect(self.backupSignal.emit)
        restore.clicked.connect(self.restoreSignal.emit)

        #gallery
        gallery_group = SettingCardGroup(
            title="Gallery"
            , parent=self
        )
        max_gallery_images = RangeSettingCard(
            configItem=sd_config.maxGalleryImages,
            icon=FluentIcon.ALBUM,
            title="Max Gallery Images",
            content="Set the maximum number of images in the gallery",
            parent=self
        )
        gallery_group.addSettingCard(max_gallery_images)

        #update
        update_group = SettingCardGroup(
            title="Update"
            , parent=self
        )
        enable_auto_update = SwitchSettingCard(
            icon=IconManager.CLOCK,
            title="Enable Auto Update",
            content="Enable auto update",
            configItem=sd_config.enableAutoUpdate
        )
        repo_url = HyperlinkCard(
            url = sd_config.repoUrl.defaultValue,
            text = "SD Front",
            icon = FluentIcon.GITHUB,
            title = "Github Rep",
            content = "SD-Front official repo",
            parent = self
        )
        about_button = PrimaryPushSettingCard(
            text="About",
            icon=FluentIcon.INFO,
            title="About",
            content="About SD-Front",
            parent=self
        )
        about_button.clicked.connect(self.aboutSignal.emit)

        update_group.addSettingCards(
            [
                enable_auto_update,
                repo_url,
                about_button
            ]
        )
        self.addLayout(hboxlayout)
        self.addWidgets([
            main_win_group,
            output_dir_group,
            api_group,
            cache_group,
            preview_group,
            save_group,
            gallery_group,
            update_group
        ])

if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    w = SettingsInterface()
    w.show()
    app.exec()

