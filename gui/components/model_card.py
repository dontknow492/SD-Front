from pathlib import Path
from typing import Union

from PySide6.QtGui import QPixmap, QImage, QColor, QFontMetrics
from qfluentwidgets import ImageLabel, StrongBodyLabel, TransparentToolButton, FluentIcon, SimpleCardWidget, Slider, \
    CompactDoubleSpinBox, InfoBadge, InfoBadgePosition, SubtitleLabel, BodyLabel, PrimaryPushButton, ToolButton, \
    TransparentPushButton, FlyoutViewBase, SwitchButton, Flyout
from PySide6.QtWidgets import QFrame, QApplication, QLabel, QHBoxLayout
from PySide6.QtCore import Qt, Signal, QSize
import sys

from gui.common import VerticalFrame, HorizontalFrame, HorizontalCard, VerticalCard, LoadingOverlay
from utils import get_cached_pixmap
# Dummy get_model_card_size (replace with your actual function)
from utils.size import get_model_card_size


class SettingFlyout(FlyoutViewBase):
    negative_toggled = Signal(bool)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(300, 400)
        self.setLayout(QHBoxLayout(self))
        self.layout().addWidget(BodyLabel("Negative"))
        self.toggle_button = SwitchButton()
        self.toggle_button.setChecked(False)
        self.toggle_button.checkedChanged.connect(self.negative_toggled)
        self.layout().addWidget(self.toggle_button, 0, Qt.AlignmentFlag.AlignRight)

        self.setFixedHeight(self.toggle_button.height() + 20)




class ModelCard(VerticalCard):
    def __init__(self, cover_path: str, name: str, model_path: str, parent=None):
        super().__init__(parent=parent)

        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)
        self._name = name
        self._model_path = model_path
        self._cover_path = cover_path


        # cover_path = cover_path if
        self.cover_label = ImageLabel(self)
        pixmap = get_cached_pixmap(cover_path, QSize(200, 200), bg_color = QColor(0, 0, 0))
        self.cover_label.setImage(pixmap)
        # self.cover_label.setBorderRadius(10, 10, 0, 0)

        self.name_label = SubtitleLabel(self)
        self.name_label.setContentsMargins(9, 5, 5, 2)
        self.name_label.setWordWrap(True)
        self.name_label.setText(self.elide_text(name))

        container = HorizontalFrame(self)
        container.setLayoutMargins(9, 0, 5, 5)
        version_label = BodyLabel("Version", container)
        self.select_button = PrimaryPushButton(FluentIcon.PLAY_SOLID, "Select", container)
        container.addWidget(version_label)
        container.layout().addStretch(1)
        container.addWidget(self.select_button)

        self.addWidget(self.cover_label)
        self.addWidget(self.name_label)
        self.addWidget(container)

        #overlay
        self.overlay_widget = HorizontalFrame(self.cover_label)
        self.overlay_widget.setLayoutMargins(0, 0, 0, 0)
        self.overlay_widget.move(0, 0)
        self.overlay_widget.raise_()
        self.overlay_widget.show()
        self.overlay_widget.setFixedSize(self.cover_label.size())

        model_type = QLabel("SDXL", self.overlay_widget)
        model_type.setStyleSheet("background-color: rgba(0, 0, 0, 150); color: white; padding: 2px 5px; border-radius: 5px;")
        self.info_button = ToolButton(FluentIcon.INFO, self.overlay_widget)

        self.overlay_widget.addWidget(model_type, alignment=Qt.AlignmentFlag.AlignTop)
        self.overlay_widget.layout().addStretch(1)
        self.overlay_widget.addWidget(self.info_button, alignment=Qt.AlignmentFlag.AlignTop)

        # loading overlay
        self.loading_overlay = LoadingOverlay(self.cover_label)
        self.loading_overlay.setFixedSize(self.cover_label.size())
        self.loading_overlay.hide_overlay()

        self.setBorderRadius(12)


    def elide_text(self, text: str, mode=Qt.TextElideMode.ElideMiddle) -> str:
        metrics = QFontMetrics(self.name_label.font())
        # Use the width of the title label or the widget, whichever is smaller
        available_width = min(self.name_label.width(), self.width())
        if available_width <= 0:  # Fallback if width is not yet set
            available_width = self.width()
        return metrics.elidedText(text, mode, available_width)

    def resizeEvent(self, event, /):
        super().resizeEvent(event)
        self.name_label.setText(self.elide_text(self._name))
        self.overlay_widget.setFixedSize(self.cover_label.size())
        self.loading_overlay.setFixedSize(self.cover_label.size())

    def toggle_loading_overlay(self, show: bool):
        if show:
            self.loading_overlay.show_overlay()
        else:
            self.loading_overlay.hide_overlay()

    def setBorderRadius(self, radius: int):
        self.cover_label.setBorderRadius(radius, radius, 0, 0)
        super().setBorderRadius(radius)
        self.loading_overlay.setBorderRadius(radius, radius, 0, 0)
        self.overlay_widget.setStyleSheet(
            f"""
            border-top-left-radius: {radius}px;
            border-top-right-radius: {radius}px;
            """
        )


class LandscapeModelCard(HorizontalCard):
    deleteSignal = Signal(str)
    def __init__(self, cover_path: str, name: str, model_path: str, parent=None):
        super().__init__(parent=parent)
        self.set_hover_effect_enabled(False)
        self._name = name
        self._model_path = model_path
        self._cover_path = cover_path
        self._is_negative = False
        # cover_path = cover_path if

        self.setting_flyout = SettingFlyout()
        self.setting_flyout.negative_toggled.connect(self.negative)

        self.cover_label = ImageLabel(self)
        pixmap = get_cached_pixmap(cover_path, QSize(150, 150), bg_color = QColor(0, 0, 0))
        self.cover_label.setImage(pixmap)
        self.cover_label.setFixedSize(75, 75)
        self.cover_label.setScaledContents(True)
        self.cover_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cover_label.setBorderRadius(10, 10, 10, 10)
        self.name_label = StrongBodyLabel(self)
        self.name_label.setText(self.elide_text(name))
        self.name_label.setWordWrap(True)
        self.redirect_button = TransparentPushButton(">", self)
        self.redirect_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.info_button = TransparentToolButton(FluentIcon.INFO, self)
        self.info_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.delete_button = TransparentToolButton(FluentIcon.DELETE, self)
        self.delete_button.setToolTip("Delete")
        self.delete_button.clicked.connect(lambda: self.deleteSignal.emit(self._model_path))
        self.delete_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setting_button = TransparentToolButton(FluentIcon.SETTING, self)
        self.setting_button.clicked.connect(self.show_setting_flyout)
        self.weight_slider = Slider(Qt.Orientation.Horizontal, self)
        self.weight_slider.setRange(-50, 50)
        self.weight_slider.setValue(10)
        self.weight_value = CompactDoubleSpinBox(self)
        self.weight_value.setRange(-5, 5)
        self.weight_value.setSingleStep(0.1)
        self.weight_value.setDecimals(1)
        self.weight_value.setValue(1.0)



        InfoBadge.info("SDXL", self, self.cover_label, InfoBadgePosition.TOP_LEFT)

        self._signal_mapping()
        self._init_ui()

        #loading overlay
        self.loading_overlay = LoadingOverlay(self)
        self.loading_overlay.setFixedSize(self.cover_label.size())
        self.loading_overlay.hide_overlay()

    def _init_ui(self):
        container = VerticalFrame(self)
        container.setLayoutMargins(0, 0, 0, 0)

        container_1 = HorizontalFrame(self)
        container_1.setLayoutMargins(0, 0, 0, 0)
        container_1.addWidget(self.name_label, stretch=1)
        container_1.addWidget(self.redirect_button, alignment=Qt.AlignmentFlag.AlignCenter)
        container_1.addWidget(self.info_button, alignment=Qt.AlignmentFlag.AlignRight)
        container_1.addWidget(self.delete_button, alignment=Qt.AlignmentFlag.AlignRight)


        self.weight_container_2 = HorizontalFrame(self)
        self.weight_container_2.setLayoutMargins(0, 0, 0, 0)
        self.weight_container_2.addWidget(self.weight_slider, stretch=1)
        self.weight_container_2.addWidget(self.setting_button, alignment=Qt.AlignmentFlag.AlignRight)
        self.weight_container_2.addWidget(self.weight_value)


        container.addWidget(container_1, alignment=Qt.AlignmentFlag.AlignVCenter)
        container.addWidget(self.weight_container_2, alignment=Qt.AlignmentFlag.AlignVCenter)
        container.setMinimumHeight(self.cover_label.height())

        self.addWidget(self.cover_label, alignment=Qt.AlignmentFlag.AlignTop)
        self.addWidget(container, alignment=Qt.AlignmentFlag.AlignTop)

    def _signal_mapping(self):
        self.info_button.clicked.connect(lambda: print("Info"))
        self.delete_button.clicked.connect(lambda: print("Delete"))
        self.weight_value.valueChanged.connect(self.on_spinbox_value_changed)
        self.weight_slider.valueChanged.connect(self.on_slider_value_changed)

    def on_slider_value_changed(self, value):
        self.weight_value.setValue(value / 10)

    def on_spinbox_value_changed(self, value):
        self.weight_slider.setValue(int(value * 10))

    def elide_text(self, text: str, mode=Qt.TextElideMode.ElideMiddle) -> str:
        metrics = QFontMetrics(self.name_label.font())
        # Use the width of the title label or the widget, whichever is smaller
        available_width = min(self.name_label.width(), self.width())
        if available_width <= 0:  # Fallback if width is not yet set
            available_width = self.width()
        return metrics.elidedText(text, mode, available_width)

    def resizeEvent(self, event, /):
        super().resizeEvent(event)
        self.name_label.setText(self.elide_text(self._name))

    def show_weight(self, state: bool):
        self.weight_slider.setVisible(state)
        self.weight_slider.setEnabled(state)
        self.weight_slider.blockSignals(not state)
        self.weight_value.setVisible(state)
        self.weight_value.setEnabled(state)
        self.weight_value.blockSignals(not state)

        self.setting_button.setVisible(state)
        self.setting_button.setEnabled(state)
        self.setting_button.blockSignals(not state)

        self.weight_container_2.setVisible(state)

    def is_weight_visible(self):
        return self.weight_slider.isVisible()

    def show_setting_flyout(self):
        Flyout.make(self.setting_flyout, self.setting_button, self, isDeleteOnClose=False)

    @property
    def is_negative(self):
        return self._is_negative

    def negative(self, state: bool):
        print("Negative", state)
        self._is_negative = state

    def toggle_loading_overlay(self, show: bool):
        if show:
            self.loading_overlay.show_overlay()
        else:
            self.loading_overlay.hide_overlay()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.loading_overlay.setFixedSize(self.cover_label.size())



if __name__ == "__main__":
    cover_path = Path(r"D:\Program\SD Front\cover_demo.jpg")
    app = QApplication(sys.argv)
    cover_path = r"D:\Program\SD Front\samples\Extras\00000-2025-04-10-hassakuXLIllustrious_v21fix.jpg"
    # card = LandscapeModelCard(cover_path, "Portrait Lora asdf sadf sdf asd sfa fdf asdf")
    card = ModelCard(cover_path, "Animagine XL",  "temp.py")
    # card = LandscapeModelCard(cover_path, "Animagine XL", "temp.py")
    # card.show_weight(True)
    card.toggle_loading_overlay(True)
    # card.set_model_name("Animagine XL")
    # card.set_model_type("SDXL")
    # card.set_model_cover(cover_path)
    card.show()
    sys.exit(app.exec())
