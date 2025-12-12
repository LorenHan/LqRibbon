"""
LqRibbonBar - Ribbon bar container that holds ribbon pages
"""

from PySide6.QtWidgets import QTabWidget, QWidget, QHBoxLayout
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPainter, QBrush, QColor


class LqRibbonBar(QTabWidget):
    """Ribbon bar that contains multiple ribbon pages"""

    page_changed = Signal(int)  # Signal emitted when page changes

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.pages = []

    def init_ui(self):
        """Initialize the ribbon bar UI"""
        # Set tab position to North (top)
        self.setTabPosition(QTabWidget.TabPosition.North)

        # Don't use document mode to allow background painting
        self.setDocumentMode(False)

        # Connect signals
        self.currentChanged.connect(self.on_page_changed)

        # Set height for ribbon area
        self.setFixedHeight(120)

    def paintEvent(self, event):
        """Custom paint event to draw blue background for tab bar area"""
        super().paintEvent(event)

        # Paint blue background for tab bar area
        painter = QPainter(self)
        painter.fillRect(0, 0, self.width(), 30, QBrush(QColor("#2B579A")))

    def add_page(self, title):
        """Add a new ribbon page

        Args:
            title: Title of the page

        Returns:
            LqRibbonPage: The created page
        """
        from .lq_ribbon_page import LqRibbonPage

        page = LqRibbonPage(title, self)
        self.pages.append(page)
        self.addTab(page, title)

        return page

    def get_page(self, index):
        """Get a page by index

        Args:
            index: Index of the page

        Returns:
            LqRibbonPage: The page at the given index
        """
        if 0 <= index < len(self.pages):
            return self.pages[index]
        return None

    def get_page_by_title(self, title):
        """Get a page by its title

        Args:
            title: Title of the page

        Returns:
            LqRibbonPage: The page with the given title
        """
        for page in self.pages:
            if page.title == title:
                return page
        return None

    def get_current_page(self):
        """Get the currently active page

        Returns:
            LqRibbonPage: The current page
        """
        index = self.currentIndex()
        return self.get_page(index)

    def on_page_changed(self, index):
        """Handle page change event

        Args:
            index: Index of the new current page
        """
        self.page_changed.emit(index)

    def set_page_enabled(self, index, enabled):
        """Enable or disable a page

        Args:
            index: Index of the page
            enabled: True to enable, False to disable
        """
        self.setTabEnabled(index, enabled)

    def remove_page(self, index):
        """Remove a page

        Args:
            index: Index of the page to remove
        """
        if 0 <= index < len(self.pages):
            self.removeTab(index)
            del self.pages[index]

    def clear_pages(self):
        """Remove all pages"""
        self.clear()
        self.pages.clear()