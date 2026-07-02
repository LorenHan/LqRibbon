"""
LqRibbonBar - Ribbon bar container that holds ribbon pages
"""

from PySide6.QtWidgets import QTabWidget, QWidget, QHBoxLayout
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPainter, QBrush, QColor, QIcon

from .lq_styles import LqStyle


class LqRibbonBar(QTabWidget):
    """Ribbon bar that contains multiple ribbon pages"""

    page_changed = Signal(int)  # Signal emitted when page changes
    simplified_mode_changed = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._simplified_mode = False
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

        self._apply_ribbon_height()

    def paintEvent(self, event):
        """Custom paint event to draw blue background for tab bar area"""
        super().paintEvent(event)

        # Paint blue background for tab bar area
        painter = QPainter(self)
        painter.fillRect(0, 0, self.width(), LqStyle.TAB_BAR_HEIGHT, QBrush(QColor(LqStyle.PRIMARY_COLOR)))

    def set_simplified_mode(self, simplified):
        """Switch between classic and simplified ribbon layouts."""
        simplified = bool(simplified)
        if self._simplified_mode == simplified:
            return

        self._simplified_mode = simplified
        self._apply_ribbon_height()
        for page in self.pages:
            page.set_simplified_mode(simplified)
        self.simplified_mode_changed.emit(simplified)

    def toggle_simplified_mode(self):
        """Toggle the simplified ribbon state and return the new state."""
        self.set_simplified_mode(not self._simplified_mode)
        return self._simplified_mode

    def is_simplified_mode(self):
        return self._simplified_mode

    def _apply_ribbon_height(self):
        height = LqStyle.SIMPLIFIED_RIBBON_HEIGHT if self._simplified_mode else LqStyle.RIBBON_HEIGHT
        self.setFixedHeight(height)

    def add_page(self, title):
        """Add a new ribbon page

        Args:
            title: Title of the page

        Returns:
            LqRibbonPage: The created page
        """
        from .lq_ribbon_page import LqRibbonPage

        page = LqRibbonPage(title, self)
        page.set_simplified_mode(self._simplified_mode)
        self.pages.append(page)
        self.addTab(page, title)

        return page

    def page(self, title):
        """Create or return a page by title."""
        existing = self.get_page_by_title(title)
        return existing if existing is not None else self.add_page(title)

    def group(self, page_title, group_title):
        """Create or return a group by page and group title."""
        page = self.page(page_title)
        existing = page.get_group_by_title(group_title)
        return existing if existing is not None else page.add_group(group_title)

    def action(self, page_title, group_title, text, triggered=None, icon=None, tooltip=None, style=None):
        """Create an action with one call.

        Missing pages and groups are created automatically so application code can
        focus on connecting business callbacks.
        """
        group = self.group(page_title, group_title)
        action = group.addAction(icon or QIcon(), text, tooltip, style)
        if triggered is not None:
            action.triggered.connect(triggered)
        return action

    def actions(self, page_title, group_title, actions, icon=None, style=None):
        """Create multiple actions in the same page and group.

        Each item can be a dict or a tuple in this form:
        ``(text, triggered, tooltip=None, style=None, icon=None)``.
        """
        created = []
        for item in actions:
            if isinstance(item, dict):
                created.append(
                    self.action(
                        page_title,
                        group_title,
                        item["text"],
                        item.get("triggered"),
                        item.get("icon", icon),
                        item.get("tooltip"),
                        item.get("style", style),
                    )
                )
                continue

            text = item[0]
            triggered = item[1] if len(item) > 1 else None
            tooltip = item[2] if len(item) > 2 else None
            item_style = item[3] if len(item) > 3 else style
            item_icon = item[4] if len(item) > 4 else icon
            created.append(self.action(page_title, group_title, text, triggered, item_icon, tooltip, item_style))
        return created

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
