from typing import Union, List

import numpy as np
import pandas as pd
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QTableWidget, QTableWidgetItem, QWidget, QVBoxLayout, QHeaderView
)
from PySide6.QtGui import QFont
import sys

from loguru import logger
from qfluentwidgets import StrongBodyLabel, BodyLabel, TableWidget
from svgwrite.data.pattern import length


class DictTableWidget(TableWidget):
    STYLE = {
        "key_font": QFont("Segoe UI", 12, QFont.Bold),
        "value_font": QFont("Consolas", 12),
        "margin": 6
    }

    def __init__(self, data: dict = {}, parent=None):
        super().__init__(parent)
        self.row_map = {}  # Maps lowercase keys to row indices
        self.keys = []  # Stores lowercase keys in order
        self.setColumnCount(2)
        self.setShowGrid(False)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setVisible(False)
        self.setEditTriggers(QTableWidget.NoEditTriggers)
        self.setFocusPolicy(Qt.NoFocus)
        self.setSelectionMode(QTableWidget.NoSelection)
        self.setBorderRadius(10)
        self.setBorderVisible(True)
        self.add_rows(data)

    def add_rows(self, data: dict):
        """Add multiple key-value pairs from a dictionary."""
        self.clear()
        for key, value in data.items():
            if pd.api.types.is_scalar(value) and pd.isna(value):
                continue
            self.add_row(key, value)

    def add_row(self, key: str, value: Union[str, List[str]]):
        """Add a single key-value pair as a new row."""
        if not isinstance(key, str) or not key.strip():
            logger.warning(f"Invalid key: {key}")
            return
        key_lower = key.lower()
        if key_lower in self.row_map:
            logger.warning(f"Key '{key}' already exists. Use set_value to update.")
            return
        if pd.api.types.is_scalar(value) and pd.isna(value):
            return

        row = self.rowCount()
        self.setRowCount(row + 1)
        self.keys.append(key_lower)
        self.row_map[key_lower] = row
        self._add_key_row(row, key)
        self._add_value_row(row, value)

    def _add_key_row(self, row: int, key: str):
        """Add the key label to the specified row."""
        key_label = StrongBodyLabel(f"{key.upper()}  ")
        key_label.setMargin(self.STYLE["margin"])
        key_label.setFont(self.STYLE["key_font"])
        key_label.setAlignment(Qt.AlignVCenter)
        key_label.setToolTip(key)
        key_label.setAccessibleName(f"Key {key}")
        self.setCellWidget(row, 0, key_label)

    def _add_value_row(self, row: int, value: Union[str, List[str]]):
        """Add the value label to the specified row."""
        if isinstance(value, list):
            value = '\n'.join(str(v) for v in value)
        else:
            value = str(value)

        value_label = BodyLabel(value)
        value_label.setFont(self.STYLE["value_font"])
        value_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        value_label.setMargin(self.STYLE["margin"])
        value_label.setAccessibleName(f"{self.keys[row]} value")
        self.setCellWidget(row, 1, value_label)
        self.resizeRowToContents(row)

    def set_value(self, key: str, value: Union[str, List[str]]):
        """Update the value for an existing key or add a new row."""
        if not isinstance(key, str) or not key.strip():
            logger.warning(f"Invalid key: {key}")
            return
        key_lower = key.lower()

        if key_lower not in self.row_map:
            logger.info(f"Key '{key}' does not exist. Adding as a new row.")
            self.add_row(key, value)
            return

        row = self.row_map[key_lower]

        # Remove the old value widget and clean up
        old_widget = self.cellWidget(row, 1)
        if old_widget:
            old_widget.setParent(None)
            self.removeCellWidget(row, 1)
            old_widget.deleteLater()  # Ensure the old widget is deleted to prevent overlap

        # Add the new value widget
        self._add_value_row(row, value)

        # Force resize the row to fit the new content
        self.resizeRowToContents(row)

        # Update the table's layou

    def get_height(self):
        """Calculate the total height of all rows."""
        return sum(self.rowHeight(row) for row in range(self.rowCount()))

    def clear(self):
        """Clear all rows, widgets, and internal mappings."""
        for row in range(self.rowCount()):
            for col in range(self.columnCount()):
                widget = self.cellWidget(row, col)
                if widget:
                    self.removeCellWidget(row, col)
                    widget.hide()
                    widget.setParent(None)
                    widget.deleteLater()

        super().clear()
        self.setRowCount(0)
        self.row_map.clear()
        self.keys.clear()


if __name__ == "__main__":
    app = QApplication([])
    widget = QWidget()
    widget.setLayout(QVBoxLayout())
    data = {'App': 'SD.Next',
            'CFG rescale': 0.7,
            'CFG scale': 6.0}

    data2 = {'App': 'SD.ndad',
             "un": 'un'}

    table = DictTableWidget(data)
    # table.add_rows(data)
    # table.set_values(data2)

    # table.add_row("Key", "value")
    table.set_value("kEy", "new value")
    table.set_value("app", "new value")
    widget.layout().addWidget(table)
    widget.show()
    # print(table.get_height())
    app.exec()
