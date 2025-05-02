from qfluentwidgets import ImageLabel, BodyLabel, TitleLabel, TransparentToolButton, TransparentDropDownToolButton
from qfluentwidgets import FluentIcon, setCustomStyleSheet, setThemeColor, setTheme, Theme, ThemeColor, ScrollArea
from qfluentwidgets import SmoothScrollArea, FlowLayout, PrimaryPushButton, ToolButton

import sys

sys.path.append('src')
# print(sys.path)

from PySide6.QtWidgets import QFrame, QHBoxLayout, QApplication, QVBoxLayout, QSpacerItem, QGridLayout, QWidget, QLayout
from PySide6.QtCore import Qt, QSize, Signal, QPoint, QTimer, QObject
from PySide6.QtGui import QFont, QColor, QPainter, QPixmap, QPalette, QBrush
from PySide6.QtWidgets import QGraphicsDropShadowEffect

from typing import override
class MyFrameBase(QFrame):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setContentsMargins(0, 0, 0, 0)
        self.setFrameShape(QFrame.NoFrame)
        self.setFrameStyle(QFrame.Box)
        # self.setFrameShape(QFrame.StyledPanel)
        self.original_pixmap = None
        self.resize_timer = QTimer()  # Timer to debounce resize events
        self.resize_timer.setSingleShot(True)
        self.resize_timer.timeout.connect(self.handle_resize)
        self.setLineWidth(0)
        self.setObjectName("MyFrameBase")
        self.setGraphicsEffect(None)
        self.initLayout()
        
    def initLayout(self):
        self.mainLayout = QVBoxLayout(self)
        self.setLayout(self.mainLayout)
        
    def addWidget(self, widget, stretch = 0, alignment: Qt.AlignmentFlag | None = None):
        if isinstance(widget, QSpacerItem):
            self.mainLayout.addSpacerItem(widget)
        elif alignment is not None:
            self.mainLayout.addWidget(widget, stretch, alignment)
        else:
            if stretch != 0:
                self.mainLayout.addWidget(widget, stretch)
            else:
                self.mainLayout.addWidget(widget)

    def addLayout(self, layout: QLayout, stretch: int = 0):
        self.mainLayout.addLayout(layout, stretch)
                
                
    def addSpacerItem(self, item: QSpacerItem):
        self.mainLayout.addSpacerItem(item)
    
    def insertWidget(self, index, widget, stretch = 0, alignment: Qt.AlignmentFlag | None = None):
        if isinstance(widget, QSpacerItem):
            self.mainLayout.insertSpacerItem(index, widget)
        elif alignment is not None:
            self.mainLayout.insertWidget(index, widget, stretch, alignment)
        else:
            if stretch != 0:
                self.mainLayout.insertWidget(index, widget, stretch)
            else:
                self.mainLayout.insertWidget(index, widget)
        
    def addWidgets(self, widgets):
        for widget in widgets:
            self.addWidget(widget)
            
    def setAlignment(self, alignment: Qt.AlignmentFlag):
        self.mainLayout.setAlignment(alignment)
            
    def setLayoutMargins(self, left: int, top: int, right: int, bottom: int):
        self.mainLayout.setContentsMargins(left, top, right, bottom)
        
    def setContentSpacing(self, spacing):
        self.mainLayout.setSpacing(spacing)
        
    def setBackgroundImage(self, image_path):
        """Set the background image of the widget."""
        # Load the image
        pixmap = QPixmap(image_path)

        # Set the pixmap as the background of the widget
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setBrush(self.backgroundRole(), pixmap)
        self.setPalette(palette)
        
    def setBackgroundImageCSS(self, url):
        """Set the background image of the widget using CSS."""
        # CSS to set the background image
        css = f"""
            QFrame#MyFrameBase {{
                background-image: url('{url}');
                background-position: center;
                background-attachment: fixed;
            }}
        """

        # Apply the CSS to the widget
        self.setStyleSheet(css)
    
    def setBackgroundImage(self, pixmap: QPixmap):
        """Set the background image of the widget."""
        # Load the image and cache it
        self.original_pixmap = pixmap

        # Apply blur effect to the original image and cache the result

        # Update the background with the blurred image
        self.update_background()
    
    def update_background(self):
        """Update the background image based on the current widget size."""
        if self.original_pixmap is None:
            return

        # Scale the cached blurred pixmap to the size of the widget
        scaled_pixmap = self.original_pixmap.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)

        # Set the scaled pixmap as the background of the widget
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setBrush(QPalette.ColorRole.Window, QBrush(scaled_pixmap))
        self.setPalette(palette)
    
    def resizeEvent(self, event):
        self.resize_timer.start(100)
        return super().resizeEvent(event)
    
    def handle_resize(self):
        """Update the background after the resize event is complete."""
        self.update_background()

    def clear(self, type_: QWidget | None = None):
        print('clear', type_)
        for i in reversed(range(self.mainLayout.count())):
            item = self.mainLayout.itemAt(i)
            if item is None:
                continue

            widget = item.widget()
            if widget is None:
                continue

            if type_ is None or isinstance(widget, type_):
                self.delete_widget(widget)

        self.mainLayout.update()  # Ensure layout updates properly

    def count(self):
        return self.mainLayout.count()

    def itemAt(self, index):
        return self.mainLayout.itemAt(index)
        
    def delete_widget(self, widget: QWidget):
        if not widget or not hasattr(widget, "deleteLater"):
            return  # Safety check

        if widget.parent() is not None:
            widget.setParent(None)  # Detach from parent before deletion

        if self.mainLayout.indexOf(widget) != -1:  # Ensure widget is in layout before removing
            self.mainLayout.removeWidget(widget)

        widget.deleteLater()  # Schedule for deletion

        
class FlowFrame(MyFrameBase):
    def __init__(self, parent = None, needAni: bool = True, isTight: bool = False):
        self.needAni = needAni
        self.isTight = isTight
        super().__init__(parent)
        
        
    def initLayout(self):
        self.mainLayout = FlowLayout(self, self.needAni, self.isTight)
        # self.setLayout(self.mainLayout)
        
    def setHorizantalSpacing(self, spacing):
        self.mainLayout.setHorizontalSpacing(spacing)
        
    def setVerticalSpacing(self, spacing):
        self.mainLayout.setVerticalSpacing(spacing)
    
    @override    
    def addWidget(self, widget):
        self.mainLayout.addWidget(widget)
        
class HorizontalFrame(MyFrameBase):
    def __init__(self, parent = None):
        super().__init__(parent)

    def initLayout(self):
        self.mainLayout = QHBoxLayout(self)
        # self.setLayout(self.mainLayout)
        
class VerticalFrame(MyFrameBase):
    def __init__(self, parent = None):
        super().__init__(parent)

    def initLayout(self):
        # self.mainLayout.deleteLater()
        self.mainLayout = QVBoxLayout(self)
        # self.setLayout(self.mainLayout)


from PySide6.QtWidgets import QFrame, QGridLayout, QWidget
from PySide6.QtCore import Qt


class GridFrame(QFrame):
    def __init__(self, parent=None, spacing=12, margins=(8, 8, 8, 8)):
        super().__init__(parent)

        self._layout = QGridLayout(self)
        self._layout.setSpacing(spacing)
        self._layout.setContentsMargins(*margins)
        self.setLayout(self._layout)

        self._row = 0
        self._col = 0
        self._max_columns = 2  # default: 2 columns

    def setColumnCount(self, count: int):
        """Set how many columns to fill before going to next row."""
        self._max_columns = max(1, count)

    def addWidget(self, widget: QWidget, row=None, col=None, row_span=1, col_span=1, alignment=Qt.AlignmentFlag(0)):
        """Add widget at next available slot or at a specific position."""
        if row is not None and col is not None:
            self._layout.addWidget(widget, row, col, row_span, col_span, alignment)
        else:
            self._layout.addWidget(widget, self._row, self._col, row_span, col_span, alignment)
            self._advance_grid_position()

    def _advance_grid_position(self):
        self._col += 1
        if self._col >= self._max_columns:
            self._col = 0
            self._row += 1

    def addFullWidthWidget(self, widget: QWidget, row_span=1, alignment=Qt.AlignmentFlag(0)):
        """Add a widget that spans all columns (full width)."""
        if self._col != 0:
            self._row += 1
            self._col = 0
        self.addWidget(widget, self._row, 0, row_span, self._max_columns, alignment)
        self._row += 1
        self._col = 0

    def clear(self):
        """Remove all widgets from the layout."""
        while self._layout.count():
            item = self._layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)
        self._row = 0
        self._col = 0

    def layout(self):
        return self._layout
