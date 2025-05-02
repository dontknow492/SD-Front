import asyncio
import sys
from typing import Optional, Union

from loguru import logger
from qfluentwidgets import FluentIconBase, PushButton, isDarkTheme, RoundMenu, Action, FluentIcon, FlyoutViewBase, \
    BodyLabel, StrongBodyLabel, Slider, SwitchButton, CompactSpinBox, SubtitleLabel, TransparentToggleToolButton, \
    TransparentToolButton, TransparentDropDownToolButton, PrimaryPushButton, IconWidget, ComboBox, SearchLineEdit, \
    ToolButton, CheckableMenu, MenuIndicatorType, Flyout

from gui.common import FlowFrame, VerticalFrame, FlowScrollWidget, HorizontalFrame, ImageViewer
from gui.components.cover_card import CoverCard
from gui.elements.image_info_box import ImageInfoBox

from PySide6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QGridLayout
from PySide6.QtCore import Qt, QTimer, Signal, QSize
from PySide6.QtGui import QColor, QPainter, QBrush, QIcon, QActionGroup
from qframelesswindow import TitleBar
import pandas as pd
from manager import ImageManager, image_manager, card_manager


class AdjustmentView(FlyoutViewBase):
    sliderValueChanged = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        container = HorizontalFrame(self)
        self.main_layout = QVBoxLayout(self)
        slider_label = BodyLabel("Size", container)
        value_label = StrongBodyLabel("175", container)

        self.size_slider = Slider(Qt.Orientation.Horizontal, self)
        self.size_slider.setRange(150, 512)
        self.size_slider.setValue(175)
        self.size_slider.valueChanged.connect(self.sliderValueChanged)
        self.size_slider.valueChanged.connect(lambda value: value_label.setText(str(value)))

        container.addWidget(slider_label)
        container.layout().addStretch(0)
        container.addWidget(value_label)

        self.main_layout.addWidget(container)
        self.main_layout.addWidget(self.size_slider)


class SearchView(FlyoutViewBase):
    excluded = Signal(bool)
    limit = Signal(int)
    caseSensitive = Signal(bool)
    exactMatch = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_layout = QVBoxLayout(self)

        grid_layout = QGridLayout()
        grid_layout.setColumnStretch(1, 1)

        # Exclude Search
        excluded_label = BodyLabel("Exclude Search", self)
        self.excluded_button = SwitchButton(self)
        self.excluded_button.setChecked(False)
        self.excluded_button.checkedChanged.connect(self.excluded.emit)

        # Search Limit
        limit_label = BodyLabel("Search Limit", self)
        self.limit_box = CompactSpinBox(self)
        self.limit_box.setRange(20, 1000)
        self.limit_box.setValue(25)
        self.limit_box.valueChanged.connect(self.limit.emit)

        # Case Sensitive
        case_label = BodyLabel("Case Sensitive", self)
        self.case_button = SwitchButton(self)
        self.case_button.setChecked(False)
        self.case_button.checkedChanged.connect(self.caseSensitive.emit)

        # Exact Match
        exact_label = BodyLabel("Exact Match", self)
        self.exact_button = SwitchButton(self)
        self.exact_button.setChecked(False)
        self.exact_button.checkedChanged.connect(self.exactMatch.emit)

        # Add widgets to grid
        grid_layout.addWidget(limit_label, 0, 0)
        grid_layout.addWidget(self.limit_box, 0, 1)

        grid_layout.addWidget(excluded_label, 1, 0)
        grid_layout.addWidget(self.excluded_button, 1, 1)

        grid_layout.addWidget(case_label, 2, 0)
        grid_layout.addWidget(self.case_button, 2, 1)

        grid_layout.addWidget(exact_label, 3, 0)
        grid_layout.addWidget(self.exact_button, 3, 1)

        # Add to main layout
        self.main_layout.addLayout(grid_layout)


class FilterBar(VerticalFrame):
    refreshSignal = Signal()
    sortSignal = Signal(str, bool)
    searchSignal = Signal(str)
    resetSearch = Signal()

    def __init__(self, icon: Union[QIcon, FluentIconBase, str, None] = FluentIcon.ALBUM, title: str = None,
                 parent=None):
        super().__init__(parent=parent)

        self.search_view = SearchView()
        self._last_search_text = None
        self.is_text_excluded = False
        self.is_case_sensitive = False
        self.is_exact_match = False
        self.search_limit = 25
        self.setLayoutMargins(0, 0, 0, 0)
        self.setContentSpacing(4)
        container = HorizontalFrame(self)
        container.setLayoutMargins(0, 0, 0, 0)

        self._sort_order = 1
        self._sort_type = 'creation date'

        title = title if title else "Filter"
        self.title_label = SubtitleLabel(title, container)
        self.search_button = TransparentToggleToolButton(FluentIcon.SEARCH, container)
        self.filter_button = TransparentDropDownToolButton(FluentIcon.FILTER, container)
        self.adjustment_button = TransparentToolButton(FluentIcon.SETTING, container)
        self.adjustment_view = AdjustmentView()
        self.adjustment_view.sliderValueChanged.connect(self.on_size_changed)
        # self.adjustment_view.hide()

        self.refresh_button = PrimaryPushButton(FluentIcon.SYNC, "Refresh", container)

        if icon:
            self.icon_widget = IconWidget(icon, container)
            self.icon_widget.setFixedSize(30, 30)
            container.addWidget(self.icon_widget)

        container.addWidget(self.title_label)
        container.layout().addStretch(3)
        container.addWidget(self.filter_button)
        container.addWidget(self.adjustment_button)
        container.addWidget(self.search_button)
        container.addWidget(self.refresh_button)

        search_container = HorizontalFrame(self)
        search_container.setVisible(False)
        search_container.setLayoutMargins(0, 0, 0, 0)
        search_container.setContentSpacing(0)
        self.search_scope = ComboBox(search_container)
        self.search_scope.setToolTip("Search Scope")
        self.search_scope.addItems(["Default", "Filename", "Pos Prompt", "Neg Prompt", "Seed"])
        self.search_line_edit = SearchLineEdit(search_container)
        self.search_line_edit.setPlaceholderText("Search")
        self.search_line_edit.setClearButtonEnabled(True)

        self.search_timer = QTimer(self)
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self._emit_search_signal)

        self.search_option_button = ToolButton(FluentIcon.SETTING, search_container)

        search_container.addWidget(self.search_option_button)
        search_container.addWidget(self.search_line_edit)
        search_container.addWidget(self.search_scope)

        self.addWidget(container)
        self.addWidget(search_container)
        self.layout().addStretch(1)

        self.search_button.toggled.connect(search_container.setVisible)

        # initializing filter
        # Initialize sort actions
        self.createTimeAction = Action(FluentIcon.CALENDAR, "Create Time", checkable=True)
        self.createTimeAction.setChecked(True)
        self.createTimeAction.triggered.connect(lambda: self._on_sort_action("date"))
        self.nameAction = Action(FluentIcon.FONT, "Name", checkable=True)
        self.nameAction.triggered.connect(lambda: self._on_sort_action("path"))
        self.sizeAction = Action(FluentIcon.FONT_SIZE, "Size", checkable=True)
        self.sizeAction.triggered.connect(lambda: self._on_sort_action("size"))
        self.widthAction = Action(FluentIcon.SCROLL, "Width", checkable=True)
        self.widthAction.triggered.connect(lambda: self._on_sort_action("width"))
        self.heightAction = Action(FluentIcon.SCROLL, "Height", checkable=True)
        self.heightAction.triggered.connect(lambda: self._on_sort_action("height"))

        self.ascendAction = Action(FluentIcon.UP, "Ascending", checkable=True)
        self.ascendAction.setChecked(True)
        self.ascendAction.triggered.connect(lambda: self._on_order_changed(True))
        self.descendAction = Action(FluentIcon.DOWN, "Descending", checkable=True)
        self.descendAction.triggered.connect(lambda: self._on_order_changed(False))

        # Add actions to action groups
        self.actionGroup1 = QActionGroup(self)
        self.actionGroup1.addAction(self.createTimeAction)
        self.actionGroup1.addAction(self.nameAction)
        self.actionGroup1.addAction(self.sizeAction)
        self.actionGroup1.addAction(self.widthAction)
        self.actionGroup1.addAction(self.heightAction)

        self.actionGroup2 = QActionGroup(self)
        self.actionGroup2.addAction(self.ascendAction)
        self.actionGroup2.addAction(self.descendAction)

        self._setup_menu()

        self._signal_handler()

    def _signal_handler(self):
        self.search_button.toggled.connect(
            lambda x: self.search_line_edit.setFocus() if x else self.search_line_edit.clearFocus())
        self.search_view.excluded.connect(lambda x: setattr(self, "is_text_excluded", x))
        self.search_view.limit.connect(lambda x: setattr(self, "search_limit", x))
        self.search_view.caseSensitive.connect(lambda x: setattr(self, "is_case_sensitive", x))
        self.search_view.exactMatch.connect(lambda x: setattr(self, "is_exact_match", x))

        self.search_line_edit.textChanged.connect(self.on_search_text_changed)
        self.search_line_edit.searchSignal.connect(self.searchSignal.emit)
        self.search_line_edit.clearSignal.connect(self.resetSearch)

        self.search_option_button.clicked.connect(self._show_search_options)

        self.refresh_button.clicked.connect(self.refreshSignal.emit)

        self.adjustment_button.clicked.connect(self._show_adjustment)

    @property
    def excluded(self):
        return self.is_text_excluded

    @excluded.setter
    def excluded(self, value):
        self.is_text_excluded = value
        self.search_view.excluded_button.setChecked(value)

    @property
    def limit(self):
        return self.search_limit

    @limit.setter
    def limit(self, value: int):
        self.search_limit = value
        self.search_view.limit_box.setValue(value)

    @property
    def case_sensitive(self):
        return self.is_case_sensitive

    @case_sensitive.setter
    def case_sensitive(self, value: bool):
        self.is_case_sensitive = value
        self.search_view.case_button.setChecked(value)

    @property
    def exact_match(self):
        return self.is_exact_match

    @exact_match.setter
    def exact_match(self, value: bool):
        self.is_exact_match = value
        self.search_view.exact_button.setChecked(value)

    @property
    def scope_search(self):
        return self.search_scope.currentText().strip().lower().replace(" ", "_")

    @scope_search.setter
    def scope_search(self, value: str):
        self.search_scope.setCurrentText(value)

    def on_search_text_changed(self, text):
        if text == "":
            self.resetSearch.emit()
            return
        self._last_search_text = text
        self.search_timer.start(300)  # Delay in ms

    def _emit_search_signal(self):
        self.searchSignal.emit(self._last_search_text)

    def _setup_menu(self):
        menu = CheckableMenu(parent=self, indicatorType=MenuIndicatorType.RADIO)
        menu.addActions([
            self.createTimeAction, self.nameAction, self.sizeAction, self.widthAction, self.heightAction
        ])
        menu.addSeparator()
        menu.addActions([self.ascendAction, self.descendAction])

        self.filter_button.setMenu(menu)

    def _on_sort_action(self, sort_type: str):
        self._sort_type = sort_type
        self.sortSignal.emit(sort_type, self._sort_order)

    def _on_order_changed(self, order: bool):
        self._sort_order = order
        self.sortSignal.emit(self._sort_type, order)

    def _show_adjustment(self):
        Flyout.make(self.adjustment_view, self.adjustment_button, self, isDeleteOnClose=False)

    def _show_search_options(self):
        Flyout.make(self.search_view, self.search_option_button, self, isDeleteOnClose=False)

    def on_size_changed(self, value):
        size = QSize(value, value)
        card_manager.set_size(size)


class ImageDialog(QDialog):
    nextSignal = Signal()
    prevSignal = Signal()
    def __init__(self, parent = None):
        super().__init__(parent)
        self.file_path = None
        if parent:
            print(parent.size())
            self.setFixedSize(parent.size())
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        # self.setFixedSize(300, 200)

        self.title_bar = TitleBar(self)
        self.title_bar.minBtn.hide()
        self.title_bar.maxBtn.hide()



        container = HorizontalFrame(self)
        self.image_display = ImageViewer(container)
        self.image_display.setPixmapTransformationMode(Qt.TransformationMode.SmoothTransformation)

        # self.image_display.set_drop(False)
        self.image_display.setAcceptDrops(False)
        self.image_info_box = ImageInfoBox(container)
        container.addWidget(self.image_display)
        container.addWidget(self.image_info_box)


        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.title_bar,  alignment=Qt.AlignTop)
        layout.addWidget(container, stretch= 1)
        self.setLayout(layout)

        #overlay
        # --- Overlay Buttons ---
        self.prev_button = PushButton("<", self.image_display)
        self.next_button = PushButton(">", self.image_display)

        self._setup_overlay_button(self.prev_button, "left")
        self._setup_overlay_button(self.next_button, "right")

        self.prev_button.clicked.connect(self.prevSignal.emit)
        self.next_button.clicked.connect(self.nextSignal.emit)

    def _setup_overlay_button(self, button: PushButton, side: str):
        button.setFixedSize(50, 90)
        font = button.font()
        font.setPointSize(30)  # Adjust the size as needed
        font.setBold(True)
        button.setFont(font)
        button.raise_()  # Bring it on top of the image
        if side == "left":
            button.move(10, (self.image_display.height() - button.height()) // 2)
        elif side == "right":
            button.move(self.image_display.width() - button.width() - 10,
                        (self.image_display.height() - button.height()) // 2)
        button.show()

    def set_image(self, path, meta_data: dict):
        logger.info(f"Setting Image: {path}")
        self.file_path = path
        name =  path.rsplit("\\", 1)[-1]
        name = name.rsplit("/", 1)[-1]
        self.image_display.load_image(path)
        self.image_info_box.set_filename(name)
        self.image_info_box.set_path(path)
        self.image_info_box.set_info(meta_data)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        color = QColor(0, 0, 0, 180)  if isDarkTheme() else QColor(255, 255, 255, 180) # RGBA: Black with 180 alpha
        brush = QBrush(color)
        painter.setBrush(brush)
        painter.drawRoundedRect(self.rect(), 15, 15)

        super().paintEvent(event)

    def resizeEvent(self, event):
        """ Reposition overlay buttons beside the image_display when resized """
        super().resizeEvent(event)
        if hasattr(self, 'prev_button') and hasattr(self, 'next_button'):
            img_geo = self.image_display.geometry()
            # Move prev button to the left of the image_display
            self.prev_button.move(
                img_geo.left() - self.prev_button.width() + 60 ,
                img_geo.top() + (img_geo.height() - self.prev_button.height()) // 2
            )

            # Move next button to the right of the image_display
            self.next_button.move(
                img_geo.right() - 80,
                img_geo.top() + (img_geo.height() - self.next_button.height()) // 2
            )

    @property
    def image_path(self)->str:
        return self.file_path



class GalleryTab(VerticalFrame):
    def __init__(self, dir_path: str, icon: Union[FluentIconBase, QIcon, str, None] = None, parent = None):
        super().__init__(parent)
        self.setLayoutMargins(9, 0, 0, 0)
        self._prev_hash = None
        # self.setContentSpacing(20)
        self.card_lookup = {}
        self.dir_path = dir_path
        self.tab_dataframe = image_manager.filter_directory(dir_path)

        self.option_container = FilterBar(icon, dir_path, self)


        self.display_container = FlowScrollWidget(None, self, False, False)
        self.display_container.setLayoutMargins(0, 0, 0, 0)
        self.display_container.setVerticalSpacing(10)
        self.display_container.setHorizontalSpacing(30)
        self.display_container.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)  # Ensure vertical scrollbar exists
        self.display_container.scrollArea.verticalScrollBar().valueChanged.connect(self.on_scroll)

        self.image_viewer = ImageDialog(self)

        self.addWidget(self.option_container)
        self.addWidget(self.display_container, stretch=1)

        self._batch_total = 12
        self._batch_size = 10  # Load 10 images at a time
        self._current_batch_start = len(self.card_lookup) + self._batch_total
        self._current_batch_max_index = min(len(self.tab_dataframe), self._current_batch_start + self._batch_total)

        self._batch_timer = QTimer(self)
        self._batch_timer.setInterval(500)
        self._batch_timer.setSingleShot(True)
        self._batch_timer.timeout.connect(self._load_batch)
        # self._batch_timer.start(50)

        if  self.tab_dataframe is not None:
            self.apply_sort()

        self.signal_listener()






    def on_scroll(self, value):
        scroll_bar = self.display_container.scrollArea.verticalScrollBar()
        if value == scroll_bar.maximum():
            self.load_image()

    def signal_listener(self):
        self.option_container.refreshSignal.connect(self.refresh)
        self.option_container.sortSignal.connect(self.apply_sort)
        self.option_container.searchSignal.connect(self.search_text)
        self.option_container.resetSearch.connect(self.reset_filter)

        self.image_viewer.nextSignal.connect(self.next_image)
        self.image_viewer.prevSignal.connect(self.prev_image)

    def apply_sort(self, by: str='size', ascending = True):
        logger.info(f"Applying Sorting-{by}-order asc {ascending}")
        self.card_lookup.clear()
        self.display_container.clear()
        # self.tab_dataframe.reset_index(drop=True, inplace=True)
        self.tab_dataframe = image_manager.apply_sort(self.tab_dataframe, by, ascending)
        self._prev_hash = None
        self.update_view()

    def refresh(self):
        new_df = image_manager.filter_directory(self.dir_path)
        new_hash = hash(pd.util.hash_pandas_object(new_df[["path", "hash"]]).values.tobytes())
        if hasattr(self, "_prev_hash") and new_hash == self._prev_hash:
            logger.info("No change in dataframe")
            return
        self._prev_hash = new_hash
        self.tab_dataframe = new_df
        self.apply_sort()

    def update_view(self):
        if self.tab_dataframe is None:
            return

        # 1. Get valid paths (existing in the DataFrame)
        valid_paths = set(self.tab_dataframe['path'])

        # 2. Identify paths in card_lookup that are no longer valid
        existing_paths = set(self.card_lookup.keys())
        paths_to_remove = existing_paths - valid_paths  # Paths to remove

        # 3. Remove invalid paths (clean up removed cards)
        for path in paths_to_remove:
            logger.debug(f"Removing card for {path} (no longer in dataframe)")
            card = self.card_lookup[path]['card']
            self.display_container.removeWidget(card)
            card.deleteLater()  # Properly delete the widget
            del self.card_lookup[path]  # Remove from lookup

        self.load_image()

    def load_image(self):
        if self.tab_dataframe is None:
            return
        self._current_batch_start = len(self.card_lookup)
        self._current_batch_max_index = min(len(self.tab_dataframe), self._current_batch_start + self._batch_total)
        logger.info(f"Start: {self._current_batch_start}, Max: {self._current_batch_max_index}, len: {len(self.card_lookup)}")
        # print("done")
        self._batch_timer.start(500)

    def _load_batch(self):
        self._batch_timer.stop()
        start = len(self.card_lookup)
        end = min(start + self._batch_size, len(self.tab_dataframe), self._batch_total)
        for row in self.tab_dataframe.iloc[start:end][['path', 'hash']].itertuples(
                index=False):
            path = row.path
            file_hash = row.hash

            if path in self.card_lookup:
                if self.card_lookup[path]['hash'] == file_hash:
                    logger.debug(f"Skipping {path} as hash is same")
                    continue
                else:
                    logger.debug(f"Updating {path} as hash is different")
                    self.card_lookup[path]['card'].set_image(path)
                    self.card_lookup[path]['hash'] = file_hash
            else:
                card = self.add_card(path)
                self.card_lookup[path] = {'card': card, 'hash': file_hash}

        if len(self.card_lookup) >= min(len(self.tab_dataframe) , self._current_batch_max_index):
            self._batch_timer.stop()
            logger.info(
                f"Completed loading all images: total_loaded: {len(self.card_lookup)}, batch_start: {self._current_batch_start}, max_index: {self._current_batch_max_index}")

        elif len(self.card_lookup) <= self._current_batch_max_index:
            logger.info(
                f"Processed batch: total_loaded: {len(self.card_lookup)}, batch_start: {self._current_batch_start}, remaining: {self._current_batch_max_index} - {len(self.card_lookup)}",
            )
            self._batch_timer.start(500)

    def add_card(self, path: str)->Optional[CoverCard]:
        title = path.rsplit('\\', 1)[1]
        cover_image = path
        card = CoverCard(title, cover_image, parent=self)
        card.clicked.connect(self.showFlyout)
        self.display_container.addWidget(card)
        return card

    def search_text(self, text: str):
        # Convert text to lowercase for case-insensitive search
        paths = image_manager.apply_filter(self.tab_dataframe, text)
        paths.head(10)
        if paths is None:
            return
        self._filter_cards(paths)

    def _filter_cards(self, paths: pd.DataFrame):
        # Convert incoming paths to a set for quick lookup
        visible_paths = set(paths['path'])

        # Loop through all known cards
        for path, data in self.card_lookup.items():
            data['card'].setHidden(path not in visible_paths)

        # Add new cards from paths if they don't exist
        for row in paths.itertuples(index=False):
            if row.path not in self.card_lookup:
                card = self.add_card(row.path)
                self.card_lookup[row.path] = {'card': card, 'hash': row.hash}

    def reset_filter(self):
        # Show all cards
        for data in self.card_lookup.values():
            data['card'].setHidden(False)

    def showFlyout(self, image_path):
        metadata = image_manager.get_image_metadata(image_path)
        self.image_viewer.set_image(image_path, metadata)
        if not self.image_viewer.isVisible():
            self.image_viewer.showMaximized()
        else:
            return

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.image_viewer.setMinimumSize(self.size())
        self.image_viewer.resize(self.size())

    def next_image(self):
        next_path = self.get_adjacent_row('next')['path']
        logger.exception(f"Next image: {next_path}")
        self.showFlyout(next_path)


    def prev_image(self):
        prev_path = self.get_adjacent_row('previous')['path']
        logger.exception(f"Prev image: {prev_path}")
        self.showFlyout(prev_path)
        # paths = self.tab_dataframe['path'].tolist()
        # current_index = paths.index(self.image_viewer.image_path)
        # prev_index = (current_index - 1) % len(paths)
        # self.showFlyout(paths[prev_index])

    def get_adjacent_row(self, direction: str = 'next', loop: bool = True) -> Optional[
        pd.Series]:
        """
        Get the adjacent row (next or previous) in a DataFrame based on a specific 'path' value.

        Args:
            direction: Direction to move ('next' or 'previous').
            loop: If True, loop to the last row for 'previous' (first row) or first row for 'next' (last row).
                  If False, return None when no previous/next row exists.

        Returns:
            The adjacent row as a pandas Series, or None if the path is not found or no adjacent row exists
            (when loop=False).

        Raises:
            KeyError: If 'path' column is missing from the DataFrame.
            ValueError: If direction is not 'next' or 'previous'.
        """
        # Validate inputs
        path = self.image_viewer.image_path
        if 'path' not in self.tab_dataframe.columns:
            raise KeyError("DataFrame is missing 'path' column")

        if direction not in ['next', 'previous']:
            raise ValueError("Direction must be 'next' or 'previous'")

        if self.tab_dataframe.empty:
            return None

        # Find the index of the first row where 'path' matches
        match = self.tab_dataframe[self.tab_dataframe['path'] == path]
        if match.empty:
            return None  # Path not found

        # Get the index of the matching row
        match_index = match.index[0]
        match_pos = self.tab_dataframe.index.get_loc(match_index)

        # Determine the adjacent row position
        if direction == 'next':
            next_pos = match_pos + 1
            if next_pos >= len(self.tab_dataframe):
                return self.tab_dataframe.iloc[0] if loop else None  # Loop to first row or return None
            return self.tab_dataframe.iloc[next_pos]
        else:  # direction == 'previous'
            prev_pos = match_pos - 1
            if prev_pos < 0:
                return self.tab_dataframe.iloc[-1] if loop else None  # Loop to last row or return None
            return self.tab_dataframe.iloc[prev_pos]




if __name__ == "__main__":
    image_manager = ImageManager([r"D:\Program\SD Front\samples\Extras", r"D:\Program\SD Front\samples\Img2Img",
                                  r"D:\Program\SD Front\samples\Text2Img"], r"D:\Program\SD Front\data")

    from PySide6.QtWidgets import QApplication
    from qasync import QEventLoop, asyncSlot

    app = QApplication(sys.argv)

    event_loop = QEventLoop(app)
    asyncio.set_event_loop(event_loop)

    app_close_event = asyncio.Event()
    app.aboutToQuit.connect(app_close_event.set)

    main_window = GalleryTab(r"D:\AI Art\Images")
    main_window.showMaximized()
    # main_window.update_view()

    # image_manager = ImageManager(scan_paths=[r"D:\AI Art\Images\Text2Img"])
    # image_manager.scan_completed.connect(lambda: print("Scan completed!"))
    # image_manager.error_occurred.connect(lambda msg: print(f"Error: {msg}"))

    asyncio.ensure_future(image_manager.refresh())

    with event_loop:
        event_loop.run_until_complete(app_close_event.wait())




