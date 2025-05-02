from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QActionGroup
from PySide6.QtWidgets import QVBoxLayout, QApplication, QHBoxLayout
from qfluentwidgets import SearchLineEdit, SubtitleLabel, DropDownToolButton, \
    IconWidget, FluentIcon, ToolButton, Action, CheckableMenu, MenuIndicatorType
from gui.common import FlowScrollWidget
from gui.components import TagWidget, ModelCard
from qframelesswindow import FramelessDialog



class ModelDialog(FramelessDialog):
    modelClicked = Signal(str)
    modelInfoClicked = Signal(str)
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.title_label = SubtitleLabel("Checkpoint", self)
        self.icon_widget = IconWidget(self)
        self.titleBar.hBoxLayout.insertSpacing(0, 10)
        self.titleBar.hBoxLayout.insertWidget(1, self.icon_widget, 0, Qt.AlignLeft)
        self.titleBar.hBoxLayout.insertWidget(2, self.title_label, 0, Qt.AlignLeft)

        self._sort_order = 1
        self._sort_key = "name"

        #
        self.vboxlayout = QVBoxLayout(self)
        self.vboxlayout.setContentsMargins(0, self.titleBar.height(), 0, 0)

        #filter_bar
        hboxlayout = QHBoxLayout()
        self.search_bar = SearchLineEdit(self)
        self.search_bar.setPlaceholderText("Search")
        self.filter_button = DropDownToolButton(FluentIcon.FILTER, self)
        self.refresh_button = ToolButton(FluentIcon.SYNC, self)
        hboxlayout.addWidget(self.search_bar)
        hboxlayout.addWidget(self.filter_button)
        hboxlayout.addWidget(self.refresh_button)

        self.vboxlayout.addLayout(hboxlayout)

        #tag_widget
        self.tag_widget = TagWidget(self)
        self.vboxlayout.addWidget(self.tag_widget, alignment=Qt.AlignmentFlag.AlignTop)

        #scroll widget
        self.scroll_widget = FlowScrollWidget(None, self, True, True)
        self.scroll_widget.setObjectName("scrollWidget")
        self.scroll_widget.setHorizontalSpacing(30)
        self.scroll_widget.setVerticalSpacing(15)
        # self.scroll_widget.setStyleSheet('background: red;')
        self.vboxlayout.addWidget(self.scroll_widget, stretch=1)
        self.scroll_widget.setLayoutMargins(0, 0, 0, 0)

        #filter_menu
        self.createTimeAction = Action(FluentIcon.CALENDAR, "Create Time", checkable=True)
        # self.createTimeAction.setChecked(True)
        self.createTimeAction.triggered.connect(lambda: self._on_sort_action("date"))
        self.nameAction = Action(FluentIcon.FONT, "Name", checkable=True)
        self.nameAction.setChecked(True)
        self.nameAction.triggered.connect(lambda: self._on_sort_action("path"))
        self.sizeAction = Action(FluentIcon.FONT_SIZE, "Size", checkable=True)
        self.sizeAction.triggered.connect(lambda: self._on_sort_action("size"))

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

        self.actionGroup2 = QActionGroup(self)
        self.actionGroup2.addAction(self.ascendAction)
        self.actionGroup2.addAction(self.descendAction)

        self._setup_menu()

    def _setup_menu(self):
        menu = CheckableMenu(parent=self, indicatorType=MenuIndicatorType.RADIO)
        menu.addActions([
            self.createTimeAction, self.nameAction, self.sizeAction
        ])
        menu.addSeparator()
        menu.addActions([self.ascendAction, self.descendAction])

        self.filter_button.setMenu(menu)

    def add_model(self, model_path: str):
        cover = "D:\Program\SD Front\cover_demo.jpg"
        card = ModelCard(cover, 'An imagine-XL', model_path, self)
        self.scroll_widget.addWidget(card)

    def get_model_info(self, model_path: str):
        #TODO: get model info
        pass

    def _on_sort_action(self, sort_type: str):
        self._sort_type = sort_type

    def _on_order_changed(self, order: bool):
        self._sort_order = order

    def apply_sort(self, sort_type: str = 'name', is_asc: bool = True):
        pass

    def _search(self, text: str):
        pass


if __name__ == "__main__":
    # from gui.common import init_app
    app = QApplication()
    dialog = ModelDialog()
    for _ in range(20):
        dialog.add_model(r"D:\Program\SD Front\cover_demo.jpg")
    dialog.show()
    app.exec()