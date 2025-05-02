from collections import namedtuple
from pathlib import Path
from typing import Union

from PySide6.QtCore import Qt, QTimer, Signal, QSize
from PySide6.QtWidgets import QWidget, QFrame, QVBoxLayout, QPushButton, QFileDialog
from PySide6.QtGui import QPixmap, QImage, QPainter, QColor, QFontMetrics
from qfluentwidgets import ImageLabel, FluentIcon, BodyLabel, TransparentToolButton, Theme, RoundMenu, \
    SimpleCardWidget, setTheme, TransparentDropDownToolButton, Action
from gui.common import VerticalFrame
from utils import open_folder, open_file_with_default_app, copy_to_clipboard, copy_file_to_clipboard, save_image_as

from manager import card_manager
from utils import get_cached_pixmap
from loguru import logger



class ImageContainer(SimpleCardWidget):
    def __init__(self, cover_path: str = None, parent=None):
        super().__init__(parent)

        self.overlay_enabled = True
        self.cover_path = cover_path
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(1, 1, 1, 1)
        self.setMinimumSize(card_manager.get_size())

        # Create image label
        self.image_label = ImageLabel(self)
        self.layout().addWidget(self.image_label)

        self.set_cover(self.cover_path)
        self.set_border_radius((5, 5, 5, 5))

    def resizeEvent(self, event):
        super().resizeEvent(event)

    def set_border_radius(self, radius: tuple[int]):
        self.image_label.setBorderRadius(*radius)

    def set_size(self, size):
        self.image_label.setFixedSize(size)
        self.setMinimumSize(size)
        self.setMaximumSize(size)
        # self.set_cover(self.cover_path)

    def set_cover(self, cover_image: str = None):
        target_size = QSize(512, 512)
        scaled_pixmap = get_cached_pixmap(cover_image, target_size)
        self.image_label.setImage(scaled_pixmap)
        self.image_label.setFixedSize(card_manager.get_size())
        self.image_label.setScaledContents(True)


class CoverCard(VerticalFrame):
    clicked = Signal(str)
    deleteSignal = Signal(str)
    def __init__(self, title: str, cover_image: str = None, metadata=None, parent=None):
        super().__init__(parent)
        self.setLayoutMargins(0, 0, 0, 0)
        self.cover_path = cover_image
        self.metadata = metadata
        self.title = title
        self.image_container = ImageContainer(cover_image, self)

        # Initialize title label with elided text
        self.title_label = BodyLabel(self)
        self.title_label.setText(self.elide_text(title))
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Create overlay widget
        self.overlay_widget = QWidget(self.image_container)
        self.overlay_widget.setObjectName("overlay")
        self.overlay_widget.setStyleSheet("""
            QWidget#overlay {
                background-color: rgba(0, 0, 0, 0);
            }
            QWidget#overlay:hover {
                background-color: rgba(0, 0, 0, 0.5);
                border-radius: 5px;
            }
        """)

        # Create More button
        self.more_button = TransparentDropDownToolButton(FluentIcon.MORE, self)
        self.more_button.raise_()
        self.more_button.adjustSize()
        self.more_button.setVisible(False)

        # Overlay layout
        overlay_layout = QVBoxLayout(self.overlay_widget)
        overlay_layout.addWidget(self.more_button, 0, Qt.AlignTop | Qt.AlignRight)
        overlay_layout.setContentsMargins(0, 0, 0, 0)

        # Make overlay cover the entire widget
        self.overlay_widget.setFixedSize(self.image_container.size())


        # Show button on hover
        self.overlay_widget.enterEvent = lambda event: self.more_button.setVisible(True)
        self.overlay_widget.leaveEvent = lambda event: self.more_button.setVisible(False)

        card_manager.size_changed.connect(self._update_size)

        self.addWidget(self.image_container)
        self.addWidget(self.title_label, alignment=Qt.AlignmentFlag.AlignTop)

        self._create_menu()

    def _create_menu(self):
        menu = RoundMenu()
        path_obj = Path(self.cover_path)
        dir_path = str(path_obj.parent)
        name = path_obj.name
        action_1 = Action(FluentIcon.FIT_PAGE, "Open", menu, triggered = lambda: self.clicked.emit(self.cover_path))
        action_2 = Action(FluentIcon.SAVE, "Save As", menu,  triggered = self._save_as_action)
        action_3 = Action(FluentIcon.DELETE,"Delete", menu,  triggered = lambda: self.deleteSignal.emit(self.cover_path))
        action_4 = Action(FluentIcon.COPY, "Copy", menu,  triggered = lambda: copy_file_to_clipboard(self.cover_path))
        action_6 = Action(FluentIcon.COMMAND_PROMPT,"Copy Path", menu,  triggered = lambda: copy_to_clipboard(self.cover_path))
        action_5 = Action(FluentIcon.FONT,"Copy Name", menu, triggered = lambda: copy_to_clipboard(name))
        action_7 = Action(FluentIcon.FOLDER, "Open in Explorer", menu, triggered=lambda: open_folder(dir_path))
        action_8 = Action(FluentIcon.APPLICATION, "Open in Default App", menu, triggered=lambda: open_file_with_default_app(self.cover_path))

        menu.addActions([action_1, action_2, action_3, action_4, action_5, action_6, action_7, action_8])

        self.menu = menu

    def _save_as_action(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save As",
            "",
            "Images (*.jpg *'.jpeg *'.png *'.gif *'.bmp *'.webp *'.avif *'.jpe');;All Files (*)"
        )
        if file_path:
            logger.info(f"Saving to: {file_path}")
            if save_image_as(self.cover_path, file_path):
                logger.info(f"Saved to: {file_path}")
            else:
                logger.error(f"Failed to save to: {file_path}")

    def _update_size(self, size):
        self.image_container.set_size(size)
        self.set_size(size)
        # Re-elide text after size update
        self.title_label.setText(self.elide_text(self.title))
        self.title_label.setMaximumSize(size)

    def set_size(self, size: QSize):
        self.image_container.set_size(size)
        self.setMinimumWidth(size.width())
        self.setMinimumHeight(size.height() + self.title_label.height())
        self.update()

    def set_title(self, title: str):
        self.title = title
        self.title_label.setText(self.elide_text(title))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.overlay_widget.setFixedSize(self.image_container.size())
        # Re-elide text on resize
        elided = self.elide_text(self.title)
        self.title_label.setText(self.elide_text(self.title))

    @property
    def menu(self):
        return self.more_button.menu()

    @menu.setter
    def menu(self, menu: RoundMenu):
        self.more_button.setMenu(menu)

    def mousePressEvent(self, event, /):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.cover_path)
        elif event.button() == Qt.MouseButton.RightButton:
            menu = self.more_button.menu()
            if menu:
                menu.exec(event.globalPosition().toPoint())
        super().mousePressEvent(event)

    def elide_text(self, text: str, mode=Qt.TextElideMode.ElideMiddle) -> str:
        metrics = QFontMetrics(self.title_label.font())
        # Use the width of the title label or the widget, whichever is smaller
        available_width = min(self.title_label.width(), self.width())
        if available_width <= 0:  # Fallback if width is not yet set
            available_width = self.image_container.width()
        return metrics.elidedText(text, mode, available_width)



if __name__  == "__main__":
    from PySide6.QtWidgets import QApplication
    setTheme(Theme.DARK)
    app = QApplication([])
    card_manager.set_size(QSize(180, 180))
    window = CoverCard("this is elided text an it si elided ok brok sa f asfj asldjf asdkfj asldjf", r"D:\Program\SD Front\samples\00013-2025-04-07-hassakuXLIllustrious_v21fix.jpg")
    window.show()


    app.exec()
