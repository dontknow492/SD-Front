import base64

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QCursor, QPixmap

from PySide6.QtWidgets import (
    QApplication
)
from qfluentwidgets import FluentIcon, ToggleToolButton, TogglePushButton, FluentIconBase, ImageLabel
from utils import IconManager
from gui.common import (
    VerticalFrame, ThemedToolButton, HorizontalFrame, ImageViewer, FlowFrame, HorizontalScrollWidget
)
from api import sd_api_manager
from loguru import logger
from config import Placeholder, GenerationTypeFlags

from gui.components import ProgressWidget
from utils import base64_pixmap

def create_themed_tool_button(icon: FluentIconBase, tooltip: str = None, cursor: QCursor | Qt.CursorShape = Qt.CursorShape.PointingHandCursor):
    button = ThemedToolButton(icon)
    if tooltip:
        button.setToolTip(tooltip)
    button.setCursor(cursor)
    return button


class GenerateButton(TogglePushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setText("Generate")
        self.setIcon(FluentIcon.PLAY_SOLID)
        self.toggled.connect(self._on_toggled)
        self.adjustSize()

    def _on_toggled(self, checked: bool):
        self._update_state(checked)

    def setChecked(self, checked: bool = False):
        if self.isChecked() == checked:
            return  # Avoid redundant updates
        self.blockSignals(True)
        super().setChecked(checked)
        self.blockSignals(False)
        self._update_state(checked)

    def _update_state(self, checked: bool):
        if checked:
            self.setText("Generating")
            self.setIcon(FluentIcon.PAUSE_BOLD)
        else:
            self.setText("Generate")
            self.setIcon(FluentIcon.PLAY_SOLID)


class OutputImageBox(VerticalFrame):
    generate_image = Signal()
    reprocess_image = Signal()
    skip_generation = Signal()
    pause_generation = Signal()
    stop_generation = Signal()

    sendTo_signal = Signal(GenerationTypeFlags, QPixmap)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayoutMargins(0, 0, 0, 0)

        #gen options
        container = HorizontalFrame(self)
        # container.setLayoutMargins(0, 0, 0, 0)
        gen_container = FlowFrame(self, False)
        gen_container.setLayoutMargins(0, 0, 0, 0)
        self.progress_widget = ProgressWidget(self)
        self.progress_widget.setVisible(False)
        self.generate_button = GenerateButton(self)

        self.generate_button.adjustSize()
        self.progress_widget.progress_bar.setFixedHeight(self.generate_button.height())
        # self.generate_button.clicked.connect(lambda: self.progress_widget.setHidden(False))

        reprocess_image = create_themed_tool_button(IconManager.PROCESS, 'Reprocess Image')
        generate_forever = ToggleToolButton(FluentIcon.SYNC, 'Generate Forever')
        skip_generation = create_themed_tool_button(IconManager.SKIP_FORWARD, 'Skip Generation')
        pause_generation = create_themed_tool_button(FluentIcon.PAUSE,  'Pause Generation')
        stop_generation = create_themed_tool_button(IconManager.STOP,  'Stop Generation')

        gen_container.addWidget(self.generate_button)
        gen_container.addWidget(reprocess_image)
        gen_container.addWidget(generate_forever)
        gen_container.addWidget(skip_generation)
        gen_container.addWidget(pause_generation)
        gen_container.addWidget(stop_generation)

        # Set up the graphics view and scene
        self.view = ImageViewer(self)
        self.view.setPixmapTransformationMode(Qt.TransformationMode.SmoothTransformation)

        #extra options
        self.extra_option_container = HorizontalFrame(self)
        self.set_enable_extra_controls(False)
        self.show_button = create_themed_tool_button(FluentIcon.FOLDER,  'Open in Folder')
        self.delete_button = create_themed_tool_button(FluentIcon.DELETE,  'Delete')
        self.send_to_image_button = create_themed_tool_button(IconManager.IMAGE_PEN,  'Send to Img2Img')
        self.send_to_text_button = create_themed_tool_button(IconManager.TEXT_SIZE,  'Send to Txt2Img')
        self.send_to_control_button = create_themed_tool_button(FluentIcon.ROBOT, 'Send to Controls')
        self.send_to_extras_button = create_themed_tool_button(IconManager.PROCESS_BOX, 'Send to Extras')
        # Add buttons to layout
        for btn in [
            self.show_button,
            self.send_to_image_button,
            self.send_to_text_button,
            self.send_to_control_button,
            self.send_to_extras_button,
            self.delete_button,
        ]:
            self.extra_option_container.addWidget(btn)



        # Layout setup
        container.layout().addStretch(1)
        container.addWidget(self.progress_widget, stretch=1,  alignment=Qt.AlignmentFlag.AlignTop)
        container.addWidget(gen_container, stretch=3)

        self.addWidget(container)
        self.addWidget(self.view, stretch=1)
        self.addWidget(self.extra_option_container, alignment=Qt.AlignmentFlag.AlignHCenter)

        #overlay_small_preview:
        self.small_preview = HorizontalScrollWidget(None, self.view)
        self.small_preview.setFixedWidth(self.view.width())
        self.small_preview.setStyleSheet("background-color: rgba(0, 0, 0, 200);")
        self.small_preview.setContentSpacing(10)
        self.small_preview.setFixedHeight(100)
        self.hide_preview()

        self.signal_handler()

    def signal_handler(self):
        self.send_to_extras_button.clicked.connect(lambda :  self.on_send_to_image(GenerationTypeFlags.EXTRAS))
        self.send_to_image_button.clicked.connect(lambda :  self.on_send_to_image(GenerationTypeFlags.IMAGE2IMAGE))
        self.send_to_text_button.clicked.connect(lambda :  self.on_send_to_image(GenerationTypeFlags.EXTRAS))
        self.send_to_control_button.clicked.connect(lambda :  self.on_send_to_image(GenerationTypeFlags.CONTROLS))

        self.generate_button.clicked.connect(self.on_generate_toggled)

    def on_generate_toggled(self, state: bool):
        logger.debug(f"Generation Button Toggled: {state}")
        self.progress_widget.setVisible(state)
        if state:
            self.generate_image.emit()
            self.generate_button.setEnabled(False)

    def on_skip_generation(self):
        self.skip_generation.emit()

    def on_stop_generation(self):
        self.stop_generation.emit()

    def on_reprocess_image(self):
        self.reprocess_image.emit()

    def on_pause_generation(self):
        self.pause_generation.emit()

    def enable_generation(self, enable: bool):
        self.progress_widget.setHidden(enable)
        self.progress_widget.reset_state()
        self.generate_button.setEnabled(enable)
        if enable:
            self.generate_button.setChecked(False)

    def on_progress(self, progress: dict, show_live_progress: bool = True):
        self.extra_option_container.setEnabled(False)
        image = progress["current_image"]
        if show_live_progress:
            if image is None:
                logger.debug("No Progress Image Generated")
                if not self.view.current_pixmap:
                    self.view.set_pixmap(Placeholder.NOISE.pixmap())
                return
            self.view.display_base64_image(image)
        self.progress_widget.set_progress(progress)
        self.progress_widget.setVisible(True)
        progress["current_image"] = None
        logger.debug(f"updating progress image: {progress}")

    def on_finished(self, image_data: dict):
        logger.debug("Image Generated")
        image_data = image_data["images"]
        self.view.setPixmapTransformationMode(Qt.TransformationMode.SmoothTransformation)
        # self.view.display_base64_image(image_data[0])
        for index, image in enumerate(image_data):
            self._add_preview(image, not index)

        self.generate_button.setChecked(False)
        self.enable_generation(True)

        # self.set_image(image_data)

    def on_error(self, error: str):
        self.progress_widget.setError(error)
        self.enable_generation(True)

    # def set_image(self, image_data: str):
    #     self.view.display_base64_image(image_data)


    def _add_preview(self, image_data, is_selected: bool = True):
        pixmap = base64_pixmap(image_data)
        if not pixmap:
            return
        if is_selected:
            self.view.set_pixmap(pixmap)
        card = ImageLabel(pixmap, self.small_preview)
        card.setCursor(Qt.CursorShape.PointingHandCursor)
        card.clicked.connect(lambda: self.view.set_pixmap(pixmap))
        card.setFixedSize(100, 100)
        card.setScaledContents(True)

        self.small_preview.addWidget(card)
        #enabling extra controls
        self.extra_option_container.setEnabled(True)
        self.show_preview()

    def reset_preview(self):
        self.small_preview.clear()

    def hide_preview(self):
        self.small_preview.hide()

    def show_preview(self):
        self.small_preview.show()

    def set_enable_extra_controls(self, state: bool):
        self.extra_option_container.setEnabled(state)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.small_preview.setFixedWidth(self.view.width())
        self.small_preview.move(0, self.view.height() - self.small_preview.height())

    def on_send_to_image(self, to: GenerationTypeFlags):
        self.sendTo_signal.emit(to, self.view.current_pixmap)





if __name__ == "__main__":
    import json
    app = QApplication([])
    window = OutputImageBox()
    with open(r"D:\Program\SD Front\data.json", 'r') as file:
        data = json.load(file)

    window.on_finished(data)
    # window.on_error("Error")
    # window.generate_image.connect(lambda: print("Generate Image"))
    window.show()
    app.exec()
