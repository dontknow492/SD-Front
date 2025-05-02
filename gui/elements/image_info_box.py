import pprint

from PySide6.QtCore import Qt
from qfluentwidgets import RoundMenu, TextBrowser, SubtitleLabel, PushButton, DropDownPushButton, SpinBox, Action, \
    FluentIcon

from gui.common import DictTableWidget
from gui.common import ChipBodyLabel, SegmentedStackedWidget, VerticalFrame, DictTableWidget, FlowFrame, VerticalScrollCard
from PySide6.QtWidgets import QWidget

from utils import human_readable_size, copy_to_clipboard, copy_file_to_clipboard, open_folder, IconManager


class ImageInfoBox(VerticalScrollCard):
    def __init__(self, parent: QWidget | None = None):
        """
        A widget displaying metadata and options for an image, including prompts,
        file info, and generation parameters.
        """
        super().__init__(parent)

        self.info: dict = {}
        self._menu = RoundMenu(parent=self)
        self._create_menu_action()
        # === Option Buttons ===
        self.option_frame = FlowFrame(self)
        self.option_frame.setLayoutMargins(0, 0, 0, 0)

        self.open_context_button = DropDownPushButton("Open Context", self.option_frame)
        self.open_context_button.setMenu(self._menu)
        self.copy_prompt_button = PushButton("Copy Prompt", self.option_frame)
        self.copy_positive_prompt_button = PushButton("Copy Positive Prompt", self.option_frame)
        self.copy_negative_prompt_button = PushButton("Copy Negative Prompt", self.option_frame)

        self.option_frame.addWidget(self.open_context_button)
        self.option_frame.addWidget(self.copy_prompt_button)
        self.option_frame.addWidget(self.copy_positive_prompt_button)
        self.option_frame.addWidget(self.copy_negative_prompt_button)

        # === Width Setting ===
        self.width_label = SubtitleLabel("Width", self)
        self.width_box = SpinBox(self)
        self.width_box.setRange(150, 1000)
        self.width_box.valueChanged.connect(self.setFixedWidth)
        self.width_box.setValue(350)
        self.width_box.wheelEvent = lambda event: event.ignore()

        # === Basic Info Table ===
        self.basic_info_table = DictTableWidget()
        self.basic_info_table.setAlternatingRowColors(True)

        # === Structured Metadata ===
        self.structured_metadata_frame = VerticalFrame()

        self.positive_label = SubtitleLabel("Positive Prompt", self.structured_metadata_frame)
        self.positive_prompt_container = FlowFrame(parent=self.structured_metadata_frame)

        self.negative_label = SubtitleLabel("Negative Prompt", self.structured_metadata_frame)
        self.negative_prompt_container = FlowFrame(parent=self.structured_metadata_frame)

        self.generation_params_table = DictTableWidget({}, parent=self.structured_metadata_frame)
        self.generation_params_table.setColumnCount(2)
        self.generation_params_table.setAlternatingRowColors(True)
        self.generation_params_table.setShowGrid(False)
        self.generation_params_table.setMinimumHeight(self.generation_params_table.get_height())

        self.structured_metadata_frame.addWidget(self.positive_label)
        self.structured_metadata_frame.addWidget(self.positive_prompt_container)
        self.structured_metadata_frame.addWidget(self.negative_label)
        self.structured_metadata_frame.addWidget(self.negative_prompt_container)
        self.structured_metadata_frame.addWidget(self.generation_params_table)

        # === Source Metadata ===
        self.source_metadata_frame = VerticalFrame()
        self.source_text_browser = TextBrowser(self.source_metadata_frame)
        self.source_metadata_frame.addWidget(self.source_text_browser)

        # === Metadata Tabs ===
        self.metadata_tabs = SegmentedStackedWidget(self)
        self.metadata_tabs.layout().setContentsMargins(0, 0, 0, 0)
        self.metadata_tabs.addSubInterface(self.structured_metadata_frame, "Structure_Metadata", "Structured", is_selected=True)
        self.metadata_tabs.addSubInterface(self.source_metadata_frame, "Source_Metadata", "Source")

        # === Assemble UI ===
        self.addWidget(self.option_frame)
        self.addWidget(self.width_label)
        self.addWidget(self.width_box)
        self.addWidget(SubtitleLabel("Basic Info"))
        self.addWidget(self.basic_info_table)
        self.addWidget(SubtitleLabel("Generation Parameters"))
        self.addWidget(self.metadata_tabs, stretch=1)

    def _create_chip_label(self, text: str) -> ChipBodyLabel:
        return ChipBodyLabel(text)

    def set_menu(self, menu: RoundMenu) -> None:
        self._menu = menu
        self.open_context_button.setMenu(menu)

    def set_filename(self, filename: str) -> None:
        self.basic_info_table.set_value("Filename", filename)

    def set_file_size(self, size: int) -> None:
        size_text = f"{size} bytes"
        self.basic_info_table.set_value("File size", size_text)

    def set_path(self, path: str) -> None:
        self.basic_info_table.set_value("Path", path)

    def set_resolution(self, width: int, height: int) -> None:
        self.basic_info_table.set_value("Resolution", f"{width}x{height}")

    def set_info(self, info: dict) -> None:
        """
        Set structured metadata including positive/negative prompts and parameters.
        """
        meta = info.get("meta", {})
        # self.generation_params_table.clear()
        self.generation_params_table.add_rows(meta)
        self.generation_params_table.setMinimumHeight(self.generation_params_table.get_height())

        self.set_positive_prompt(info.get("pos_prompt", []))
        self.set_negative_prompt(info.get("neg_prompt", []))

        width = meta.get("width", 0)
        height = meta.get("height", 0)

        size = info.get("size", 0)
        size = human_readable_size(int(size))

        self.set_resolution(width, height)
        self.set_file_size(size)

    def set_positive_prompt(self, prompts: list[str]) -> None:
        self.positive_prompt_container.clear()
        for prompt in prompts:
            self.positive_prompt_container.addWidget(self._create_chip_label(prompt))

    def set_negative_prompt(self, prompts: list[str]) -> None:
        self.negative_prompt_container.clear()
        for prompt in prompts:
            self.negative_prompt_container.addWidget(self._create_chip_label(prompt))

    def set_source_text(self, text: str) -> None:
        self.source_text_browser.setText(text)


    def _create_menu_action(self):
        action_2 = Action(FluentIcon.SAVE, "Save As", self._menu)
        action_3 = Action(FluentIcon.DELETE, "Delete", self._menu)
        action_4 = Action(FluentIcon.COPY, "Copy", self._menu)

        action_5 = Action(FluentIcon.CERTIFICATE, "Copy Prompt", self._menu)
        action_6 = Action(IconManager.TEXT_SIZE_BUTTON, "Copy Positive Prompt", self._menu)
        action_7 = Action(IconManager.TEXT_SIZE_BUTTON, "Copy Negative Prompt", self._menu)
        action_8 = Action(IconManager.PERSPECTIVE_DICE_RANDOM, "Copy Seed", self._menu)

        action_9 = Action(IconManager.TEXT_SIZE, "Send to txt2img", self._menu)
        action_10 = Action(FluentIcon.ALBUM, "Send to img2img", self._menu)
        action_11 = Action(FluentIcon.BRUSH, "Send to Inpaint", self._menu)
        action_12 = Action(FluentIcon.ROBOT, "Send to Control", self._menu)
        action_13 = Action(IconManager.PROCESS_BOX, "Send to Extras", self._menu)


        action_16 = Action(FluentIcon.COMMAND_PROMPT, "Copy Path", self._menu)
        action_15 = Action(FluentIcon.FONT, "Copy Name", self._menu)
        action_17 = Action(FluentIcon.INFO, "Copy Info", self._menu)

        action_19 = Action(FluentIcon.FOLDER, "Open in Explorer", self._menu)
        action_18 = Action(FluentIcon.APPLICATION, "Open in Default App", self._menu)




        self._menu.addActions([action_2, action_3, action_4])
        self._menu.addSeparator()
        self._menu.addActions([action_5, action_6, action_7, action_8])
        self._menu.addSeparator()
        self._menu.addActions([action_9, action_10, action_11, action_12, action_13])
        self._menu.addSeparator()
        self._menu.addActions([action_16, action_15, action_17])
        self._menu.addSeparator()
        self._menu.addActions([action_19, action_18])


if  __name__ == "__main__":
    from PySide6.QtWidgets import QApplication

    # setTheme(Theme.DARK)
    app = QApplication([])
    window = ImageInfoBox()

    info = {
    'lora': [{'name': 'outline xl kohaku delta spv5x', 'value': 3.0}],
    'lyco': [],
    'meta': {'App': 'SD.Next',
              'CFG rescale': '0.7',
              'CFG scale': '6',
              'LoRA networks': 'outline_xl_kohaku_delta_spv5x',
              'Model': 'hassakuXLIllustrious_v21fix',
              'Model hash': '847403d47a',
              'Operations': 'txt2img',
              'Pipeline': 'StableDiffusionXLPipeline',
              'Seed': '1561296656',
              'Steps': '20',
              'Version': '8b73cb6',
              'height': '1408',
              'width': '1312'},
    'negative_prompt': ['low quality', ' worst quality', ' cropped'],
    'pos_prompt': ['masterpiece',
                    'high quality',
                    'aesthetic',
                    'girl',
                    'ponytail',
                    'hair between eyes',
                    'upper body',
                    'portrait',
                    'genshin impact',
                    'source anime',
                    'monochrome',
                    'gray scale',
                    'line art']
    }
    source_text = """
        masterpiece, high quality, aesthetic, girl, ponytail, hair between eyes,
        upper body, portrait, genshin impact, source_anime, portrait,
        <lora:outline_xl_kohaku_delta_spv5x:3.0>, monochrome, gray_scale, line art
        Negative prompt: low quality, worst quality, cropped
        Steps: 20, Size: 1312x1408, Seed: 1561296656, CFG scale: 6,
        CFG rescale: 0.7, Model: hassakuXLIllustrious_v21fix, Model hash: 847403d47a,
        App: SD.Next, Version: 8b73cb6, Pipeline: StableDiffusionXLPipeline,
        Operations: txt2img, LoRA networks: outline_xl_kohaku_delta_spv5x

    """
    print(info)

    window.setWindowFlag(window.windowFlags() | Qt.WindowStaysOnTopHint)
    window.set_info(info)
    window.set_source_text(source_text)
    window.set_filename("00024-2025-04-10-hassakuXLIllustrious_v21fix.jpg")
    window.set_file_size(1000000)
    window.set_path(r"D:\Program\SD Front\samples")
    window.set_resolution(1000, 1000)
    window.set_path("asdf")
    window.show()
    app.exec()


