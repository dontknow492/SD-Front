from pathlib import Path
from typing import Union

from PySide6.QtCore import Signal, QTimer, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QFileDialog
from qfluentwidgets import SettingCard, LineEdit, qconfig, ExpandSettingCard, ConfigItem, FluentIcon, PushButton, \
    Dialog, FluentIconBase, SpinBox



class LineEditSettingCard(SettingCard):
    """ Setting card with a line edit """
    valueChanged = Signal(int)
    def __init__(self, icon, title, content, config_item: ConfigItem, parent=None):
        super().__init__(icon, title, content, parent)
        self.configItem = config_item
        self.lineedit = LineEdit(self)
        self.lineedit.setText(str(qconfig.get(config_item)))
        self.hBoxLayout.addWidget(self.lineedit, 1)
        self.hBoxLayout.addSpacing(16)

        self.timer = QTimer(self)
        self.timer.setInterval(500)
        self.timer.setSingleShot(True)

        self.configItem.valueChanged.connect(self.set_value)
        self.lineedit.textChanged.connect(self._on_value_changed)


    def _on_value_changed(self, value):
        self.timer.stop()
        self.timer.start()
        self.valueChanged.emit(value)
        self.setValue(value)

    def set_value(self, value):
        self.lineedit.setText(str(value))

    def setValue(self, value):
        qconfig.set(self.configItem, value)
        self.valueChanged.emit(value)

class FolderSettingCard(SettingCard):
    """ Setting card with a line edit """
    valueChanged = Signal(str)
    def __init__(self, title, content, configItem, icon: FluentIconBase = FluentIcon.FOLDER, parent=None):
        super().__init__(icon, title, content, parent)
        self.configItem = configItem
        self.folder =  qconfig.get(self.configItem)
        self.push_button =  PushButton(self.folder, self)
        self.push_button.setToolTip(self.folder)
        self.push_button.clicked.connect(self.__showFolderDialog)
        self.hBoxLayout.addWidget(self.push_button)
        self.hBoxLayout.addSpacing(16)

        self.configItem.valueChanged.connect(self.set_value)

    def set_value(self, value):
        self.folder = value
        self.push_button.setText(value)
        self.push_button.setToolTip(value)
        self.push_button.adjustSize()

    def setValue(self, value):
        qconfig.set(self.configItem, value)
        self.valueChanged.emit(value)

    def __showFolderDialog(self):
        """ show folder dialog """
        folder = QFileDialog.getExistingDirectory(
            self, self.tr("Choose folder"), str(qconfig.get(self.configItem)))

        if not folder or folder  == self.folder:
            return

        self.setValue(folder)
        self.push_button.setText(folder)
        self.push_button.adjustSize()


class SpinBoxSettingCard(SettingCard):
    """ Setting card with a line edit """
    valueChanged = Signal(int)

    def __init__(self, configItem, icon: Union[str, QIcon, FluentIconBase], title, content=None, parent=None):
        """
        Parameters
        ----------
        configItem: RangeConfigItem
            configuration item operated by the card

        icon: str | QIcon | FluentIconBase
            the icon to be drawn

        title: str
            the title of card

        content: str
            the content of card

        parent: QWidget
            parent widget
        """
        super().__init__(icon, title, content, parent)
        self.configItem = configItem
        self.spinbox = SpinBox(self)
        self.spinbox.setMinimumWidth(268)

        self.spinbox.setSingleStep(1)
        self.spinbox.setRange(*configItem.range)
        self.spinbox.setValue(configItem.value)

        self.hBoxLayout.addStretch(1)
        self.hBoxLayout.addWidget(self.spinbox, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)
        configItem.valueChanged.connect(self.setValue)
        self.spinbox.valueChanged.connect(self.__onValueChanged)

    def setSuffix(self, suffix: str):
        self.spinbox.setSuffix(suffix)

    def __onValueChanged(self, value: int):
        """ slider value changed slot """
        self.setValue(value)
        self.valueChanged.emit(value)

    def setValue(self, value):
        qconfig.set(self.configItem, value)
        self.spinbox.setValue(value)

class SizeSettingCard(SettingCard):
    """ Setting card with a line edit """
    valueChanged = Signal(int)

    def __init__(self, configItem, icon: Union[str, QIcon, FluentIconBase], title, content=None, parent=None):
        """
        Parameters
        ----------
        configItem: RangeConfigItem
            configuration item operated by the card

        icon: str | QIcon | FluentIconBase
            the icon to be drawn

        title: str
            the title of card

        content: str
            the content of card

        parent: QWidget
            parent widget
        """
        super().__init__(icon, title, content, parent)
        self.configItem = configItem
        self.spinbox = SpinBox(self)
        self.spinbox.setMinimumWidth(268)

        self.spinbox.setSingleStep(1)
        minimum, maximum = configItem.range
        minimum = self.bytes_to_MB(minimum)
        maximum = self.bytes_to_MB(maximum)
        value = self.bytes_to_MB(configItem.value)
        self.spinbox.setRange(minimum, maximum)
        self.spinbox.setValue(value)

        self.hBoxLayout.addStretch(1)
        self.hBoxLayout.addWidget(self.spinbox, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)
        configItem.valueChanged.connect(self.set_value)
        self.spinbox.valueChanged.connect(self.__onValueChanged)
        self.spinbox.setSuffix("MB")

    def __onValueChanged(self, value: int):
        """ slider value changed slot """
        self.setValue(value)
        self.valueChanged.emit(value)

    def setValue(self, value):
        # mb = value
        value = int(self.mb_to_bytes(value))
        print('value', value)
        qconfig.set(self.configItem, value)

    def set_value(self, value: int):
        print('set_value', value)
        mb = self.bytes_to_MB(value)
        self.spinbox.setValue(mb)
        # self.spinbox.setValue(mb)

    def bytes_to_MB(self, bytes):
        return bytes / (1024 * 1024)

    def mb_to_bytes(self, mb):
        return mb * 1024 * 1024

