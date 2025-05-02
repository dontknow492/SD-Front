import os.path
from PySide6.QtCore import Qt, QSize, Property
from qfluentwidgets import ImageLabel, BodyLabel, TextBrowser, TitleLabel, ToolButton, \
    PrimaryPushButton, FluentIcon, PushButton, SubtitleLabel, AvatarWidget, setCustomStyleSheet
from gui.common import DictTableWidget, HorizontalScrollWidget, VerticalFrame, VerticalScrollWidget, HorizontalFrame, \
    LoadingOverlay
from gui.components import TagWidget
from utils import get_cached_pixmap
import json
from PySide6.QtWidgets import QSizePolicy, QHBoxLayout
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve


class ModelInfo(VerticalScrollWidget):
    def __init__(self, model_path: str, parent=None):
        super().__init__(parent = parent)
        self.model_path = model_path
        self.setContentSpacing(0)

        # Internal widget to hold all content

        # Add your custom widgets here
        vlayout = QVBoxLayout(self)
        vlayout.setSpacing(0)
        vlayout.setContentsMargins(0, 0, 0, 9)
        self.title_label = TitleLabel("Model Info", parent=self)
        self.version_label = BodyLabel("Version: 1.0", parent=self)
        vlayout.addWidget(self.title_label)
        vlayout.addWidget(self.version_label)

        self.tag_widget = TagWidget(parent=self)
        self.tag_widget.add_tags(["asdf", "asdf", "asdf", 'dfasdf'])



        container = HorizontalFrame(self)
        container.setContentsMargins(0, 0, 0, 0)
        # container.setSpacing(10)
        container.setFixedHeight(500)
        self.preview_container = HorizontalScrollWidget(parent=self)
        self.preview_container.setLayoutMargins(0, 0, 20, 20)
        self.preview_container.setContentSpacing(30)
        # self.preview_container.setStyleSheet("background: green;")
        info_layout =  QVBoxLayout(container)
        hlayout = QHBoxLayout(container)
        self.share_button = PushButton(FluentIcon.SHARE, "Share", self)
        self.create_button = PrimaryPushButton(FluentIcon.PLAY_SOLID, "Create", self)
        self.reload_button = PrimaryPushButton(FluentIcon.SYNC, "Reload", self)

        hlayout.addWidget(self.share_button)
        hlayout.addWidget(self.create_button)
        hlayout.addWidget(self.reload_button)

        self.info_container = DictTableWidget(parent=self)
        # self.info_container.setStyleSheet('background: red;')

        info_layout.addLayout(hlayout)
        info_layout.addWidget(SubtitleLabel("Details"))
        info_layout.addWidget(self.info_container)

        container.addWidget(self.preview_container, stretch=3)
        container.addLayout(info_layout, stretch=1)

        # description browser
        self.description_browser = TextBrowser(parent=self)
        self.description_browser.setOpenExternalLinks(True)

        # ❌ Remove internal scrolling
        self.description_browser.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.description_browser.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # ✅ Make QTextBrowser expand naturally in height
        self.description_browser.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        self.description_browser.setMaximumHeight(200)  # Or use custom height logic
        self.description_browser.setFocusPolicy(Qt.NoFocus)
        # self.description_browser.setStyleSheet("QTextBrowser { border: none; }")

        # Add widgets to layout

        self.addLayout(vlayout)
        self.addWidget(self.tag_widget)
        self.addWidget(container)
        self.addWidget(self.description_browser)

        #overlay
        self.overlay = HorizontalFrame(self.preview_container)
        self.next_button = ToolButton(self.overlay)
        self.previous_button = ToolButton(self.overlay)
        self.next_button.setIconSize(QSize(24, 24))
        self.previous_button.setIconSize(QSize(24, 24))
        self.next_button.setArrowType(Qt.ArrowType.RightArrow)
        self.previous_button.setArrowType(Qt.ArrowType.LeftArrow)
        self.next_button.clicked.connect(self._on_next_clicked)
        self.previous_button.clicked.connect(self._on_previous_clicked)

        self.overlay.addWidget(self.previous_button, alignment=Qt.AlignmentFlag.AlignLeft)
        self.overlay.addWidget(self.next_button,  alignment=Qt.AlignmentFlag.AlignRight)

        self.overlay.setFixedSize(self.preview_container.size())
        print(self.preview_container.size())

        self.animation = QPropertyAnimation(self, b"scrollValue")
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.animation.setDuration(600)

        #animation overlay
        self.loading_overlay = LoadingOverlay(self)
        self.loading_overlay.setFixedSize(self.size())
        self.loading_overlay.show_overlay()

    def set_description(self, description: str):
        self.description_browser.setHtml(description)
        self.description_browser.document().adjustSize()
        size = self.description_browser.document().size()
        self.description_browser.setFixedHeight(size.height())

    def set_info(self, info: dict):
        self.info_container.add_rows(info)

    def resizeEvent(self, event, /):
        super().resizeEvent(event)
        self.overlay.setFixedSize(self.preview_container.size())
        self.loading_overlay.setFixedSize(self.size())

    def add_preview_image(self, image_path: str):
        if not os.path.exists(image_path):
            return
        # target_size =
        width = (1000//2)-30
        target_size = QSize(width, 440)
        pixmap = get_cached_pixmap(image_path, target_size)
        image_label = ImageLabel(self.preview_container)
        image_label.setImage(pixmap)
        # image_label.setBorderRadius(8, 8, 8, 8)
        self.preview_container.addWidget(image_label, alignment=Qt.AlignmentFlag.AlignVCenter)
        # image_label = ImageLabel(image_path, self)

        # self.preview_container.setFixedHeight(1000)

    def _on_next_clicked(self):
        value = self.preview_container.getHorizontalScrollValue()
        value += 440
        self.smooth_scroll_to(value)

    def _on_previous_clicked(self):
        value = self.preview_container.getHorizontalScrollValue()
        value -= 440
        self.smooth_scroll_to(value)

    def smooth_scroll_to(self, target_value):
        self.animation.stop()
        self.animation.setStartValue(self.preview_container.getHorizontalScrollValue())
        self.animation.setEndValue(target_value)
        self.animation.start()

    def getScrollValue(self):
        return self.preview_container.getHorizontalScrollValue()

    def setScrollValue(self, value):
        self.preview_container.setScrollValue(Qt.Orientation.Horizontal, int(value))

    scrollValue = Property(int, getScrollValue, setScrollValue)

    def set_details(self, data: dict):
        self.info_container.add_rows(data)

    def mousePressEvent(self, event):
        self.loading_overlay.hide_overlay()
        super().mousePressEvent(event)

    def toggle_loading_overlay(self, show: bool):
        if show:
            self.loading_overlay.show_overlay()
        else:
            self.loading_overlay.hide_overlay()


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    from qfluentwidgets import setTheme, Theme
    setTheme(Theme.DARK)
    app = QApplication([])
    widget = ModelInfo("model")

    #sample
    with open("827184.json", 'r', encoding="utf-8") as file:
        data = json.load(file)

    images = ["827184.jpg", "827184_1.jpg", "827184_2.jpg", "827184_3.jpg"]
    widget.showMaximized()
    widget.set_description(data["description"])
    for image in images:
        widget.add_preview_image(image)

    model_data = {
            'type': 'Checkpoint',
            'base_model': 'SDXL',
            'format': 'safetensors',
            'size': '1.2 GB',
            'trained_words': '1.2B',
            'hash': 'c4f1f56c-face-40f4-bc86-96780dc86d6b'
    }
    widget.set_details(model_data)

    app.exec()
