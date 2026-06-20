"""
LqRibbonBar - Ribbon bar container that holds ribbon pages
"""

from PySide6.QtWidgets import QTabWidget, QWidget, QHBoxLayout, QMenu
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction, QIcon, QPainter, QBrush, QColor, QPixmap
from .lq_ribbon_extras import (
    CallableList,
    LqRibbonCustomizeDialog,
    LqRibbonCustomizeManager,
    LqRibbonProgressBar,
    LqRibbonQuickAccessBar,
    LqRibbonSearchBar,
    LqRibbonSystemButton,
    QtnRibbonMinimizeActionString,
    QtnRibbonSimplifiedRibbonActionString,
)


class LqRibbonBar(QTabWidget):
    """Ribbon bar that contains multiple ribbon pages"""

    page_changed = Signal(int)  # Signal emitted when page changes
    current_page_index_changed = Signal(int)
    current_page_changed = Signal(QWidget)
    ribbon_minimized_changed = Signal(bool)
    minimization_changed = Signal(bool)
    simplified_mode_changed = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.pages = CallableList()
        self._quick_access_bar = LqRibbonQuickAccessBar(self)
        self._search_bar = LqRibbonSearchBar(self)
        self._progress_bar = LqRibbonProgressBar(self)
        self._system_button = None
        self._customize_manager = None
        self._customize_dialog = None
        self._ribbon_minimized = False
        self._minimization_enabled = True
        self._simplified_mode = False
        self._simplified_mode_enabled = True
        self._frame_theme_enabled = False
        self._acrylic_enabled = False
        self._contextual_tabs_visible = True
        self._title_groups_visible = True
        self._quick_access_position = 1
        self._tab_bar_position = 1
        self._search_bar_appearance = 1
        self._title_background = QPixmap()
        self._logo_pixmap = QPixmap()
        self._logo_alignment = Qt.AlignmentFlag.AlignLeft
        self._simplified_action = QAction(QtnRibbonSimplifiedRibbonActionString, self)
        self._simplified_action.setCheckable(True)
        self._simplified_action.toggled.connect(self.setSimplifiedMode)
        self._search_suggestions = []
        self._search_actions = []
        self._recent_search_actions = []
        self._recent_search_limit = 8
        self._search_action_trigger_enabled = True
        self._key_tips_enabled = False
        self._key_tips_complement = False
        self._key_tips_showing = False
        self._key_tips = {}
        self.init_ui()

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
        self._quick_access_bar.hide()
        self._search_bar.hide()
        self._progress_bar.hide()

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
        self.addPage(page)

        return page

    def addPage(self, page_or_title):
        """Qtitan/C++ compatible page add overload."""
        if isinstance(page_or_title, str):
            return self.add_page(page_or_title)
        page = page_or_title
        if page not in self.pages:
            self.pages.append(page)
            self.addTab(page, str(page.title))
        self.setCurrentWidget(page)
        return page

    def insertPage(self, index, page_or_title):
        from .lq_ribbon_page import LqRibbonPage

        page = LqRibbonPage(page_or_title, self) if isinstance(page_or_title, str) else page_or_title
        if page in self.pages:
            old_index = self.pages.index(page)
            self.pages.remove(page)
            self.removeTab(old_index)
        if index < 0 or index > len(self.pages):
            index = len(self.pages)
        self.pages.insert(index, page)
        self.insertTab(index, page, str(page.title))
        self.setCurrentIndex(index)
        return page

    def movePage(self, page_or_index, new_index):
        old_index = page_or_index if isinstance(page_or_index, int) else self.pageIndex(page_or_index)
        if not (0 <= old_index < len(self.pages)):
            return
        page = self.pages.pop(old_index)
        self.removeTab(old_index)
        if new_index < 0 or new_index > len(self.pages):
            new_index = len(self.pages)
        self.pages.insert(new_index, page)
        self.insertTab(new_index, page, str(page.title))
        self.setCurrentIndex(new_index)

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

    def page(self, index):
        return self.get_page(index)

    def pageCount(self):
        return len(self.pages)

    def currentPageIndex(self):
        return self.currentIndex()

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

    def currentPage(self):
        return self.get_current_page()

    def pageIndex(self, page):
        return self.pages.index(page) if page in self.pages else -1

    def on_page_changed(self, index):
        """Handle page change event

        Args:
            index: Index of the new current page
        """
        self.page_changed.emit(index)
        self.current_page_index_changed.emit(index)
        self.current_page_changed.emit(self.get_page(index))

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
            page = self.pages.pop(index)
            page.deleteLater()

    def removePage(self, page_or_index):
        index = page_or_index if isinstance(page_or_index, int) else self.pageIndex(page_or_index)
        self.remove_page(index)

    def detachPage(self, page_or_index):
        index = page_or_index if isinstance(page_or_index, int) else self.pageIndex(page_or_index)
        if 0 <= index < len(self.pages):
            page = self.pages.pop(index)
            self.removeTab(index)
            page.setParent(None)

    def clear_pages(self):
        """Remove all pages"""
        self.clear()
        self.pages.clear()

    def clearPages(self):
        self.clear_pages()

    def searchBar(self):
        return self._search_bar

    def searchLineEdit(self):
        return self._search_bar

    def searchCompleter(self):
        return None

    def setSearchVisible(self, visible):
        self._search_bar.setVisible(visible)

    def isSearchVisible(self):
        return self._search_bar.isVisible()

    def setSearchPlaceholderText(self, text):
        self._search_bar.setPlaceholderText(text)

    def searchText(self):
        return self._search_bar.text()

    def setSearchText(self, text):
        self._search_bar.setText(text)

    def setSearchSuggestions(self, suggestions):
        self._search_suggestions = list(suggestions)

    def searchSuggestions(self):
        return list(self._search_suggestions)

    def clearSearchSuggestions(self):
        self._search_suggestions.clear()

    def registerSearchAction(self, action, keywords=None):
        if action not in self._search_actions:
            self._search_actions.append(action)
            self._search_bar.addSuggestedAction(action)
        action.setData(keywords or [])

    def unregisterSearchAction(self, action):
        if action in self._search_actions:
            self._search_actions.remove(action)
        self._search_bar.removeSuggestedAction(action)

    def searchActions(self):
        return list(self._search_actions)

    def searchAction(self, text):
        normalized = text.strip().lower()
        for action in self._search_actions:
            keywords = action.data() or []
            haystack = [action.text()] + list(keywords)
            if any(normalized == item.strip().lower() for item in haystack):
                return action
        return None

    def triggerSearchAction(self, text):
        if not self._search_action_trigger_enabled:
            return False
        action = self.searchAction(text)
        if not action:
            return False
        action.trigger()
        self._recent_search_actions.insert(0, action)
        self._recent_search_actions = self._recent_search_actions[: self._recent_search_limit]
        return True

    def setSearchActionTriggerEnabled(self, enabled):
        self._search_action_trigger_enabled = bool(enabled)

    def isSearchActionTriggerEnabled(self):
        return self._search_action_trigger_enabled

    def recentSearchActions(self):
        return list(self._recent_search_actions)

    def clearRecentSearchActions(self):
        self._recent_search_actions.clear()

    def setRecentSearchLimit(self, count):
        self._recent_search_limit = max(0, int(count))
        self._recent_search_actions = self._recent_search_actions[: self._recent_search_limit]

    def recentSearchLimit(self):
        return self._recent_search_limit

    def progressBar(self):
        return self._progress_bar

    def quickAccessBar(self):
        return self._quick_access_bar

    def addQuickAccessAction(self, *args):
        if len(args) == 1 and isinstance(args[0], QAction):
            action = args[0]
        else:
            icon = args[0] if args else QIcon()
            text = args[1] if len(args) > 1 else ""
            action = QAction(icon if isinstance(icon, QIcon) else QIcon(icon), text, self)
        self._quick_access_bar.addAction(action)
        self._quick_access_bar.show()
        return action

    def clearQuickAccessActions(self):
        self._quick_access_bar.clear()
        self._quick_access_bar.addAction(self._quick_access_bar.actionCustomizeButton())

    def addTitleButton(self, icon, text):
        return QAction(icon if isinstance(icon, QIcon) else QIcon(icon), text, self)

    def addAction(self, *args):
        if len(args) == 1 and isinstance(args[0], QAction):
            return self.addQuickAccessAction(args[0])
        if len(args) >= 2:
            icon, text = args[0], args[1]
            return self.addQuickAccessAction(icon, text)
        return None

    def removeTitleButton(self, action):
        action.deleteLater()

    def setCurrentPageIndex(self, index):
        self.setCurrentIndex(index)

    def setRibbonMinimized(self, minimized):
        if minimized and not self._minimization_enabled:
            return
        self._ribbon_minimized = bool(minimized)
        self.setFixedHeight(30 if minimized else 120)
        self.ribbon_minimized_changed.emit(self._ribbon_minimized)
        self.minimization_changed.emit(self._ribbon_minimized)

    def isRibbonMinimized(self):
        return self._ribbon_minimized

    def minimize(self):
        self.setRibbonMinimized(True)

    def isMinimized(self):
        return self.isRibbonMinimized()

    def setMinimized(self, minimized):
        self.setRibbonMinimized(minimized)

    def maximize(self):
        self.setRibbonMinimized(False)

    def isMaximized(self):
        return not self._ribbon_minimized

    def setMaximized(self, maximized):
        self.setRibbonMinimized(not maximized)

    def setMinimizationEnabled(self, enabled):
        self._minimization_enabled = bool(enabled)

    def isMinimizationEnabled(self):
        return self._minimization_enabled

    def simplifiedAction(self):
        return self._simplified_action

    def simplifiedMode(self):
        return self._simplified_mode

    def setSimplifiedMode(self, enabled):
        if enabled and not self._simplified_mode_enabled:
            return
        self._simplified_mode = bool(enabled)
        self._simplified_action.setChecked(self._simplified_mode)
        self.simplified_mode_changed.emit(self._simplified_mode)

    def simplifiedModeEnabled(self):
        return self._simplified_mode_enabled

    def setSimplifiedModeEnabled(self, enabled):
        self._simplified_mode_enabled = bool(enabled)

    def setFrameThemeEnabled(self, enabled=True):
        self._frame_theme_enabled = bool(enabled)
        self._search_bar.setVisible(enabled)

    def isFrameThemeEnabled(self):
        return self._frame_theme_enabled

    def setAcrylicEnabled(self, enabled):
        self._acrylic_enabled = bool(enabled)

    def isAcrylicEnabled(self):
        return self._acrylic_enabled

    def setContextualTabsVisible(self, visible):
        self._contextual_tabs_visible = bool(visible)

    def isContextualTabsVisible(self):
        return self._contextual_tabs_visible

    def setTitleGroupsVisible(self, visible):
        self._title_groups_visible = bool(visible)

    def isTitleGroupsVisible(self):
        return self._title_groups_visible

    def setQuickAccessBarPosition(self, position):
        self._quick_access_position = position

    def quickAccessBarPosition(self):
        return self._quick_access_position

    def setTabBarPosition(self, position):
        self._tab_bar_position = position
        self.setTabPosition(QTabWidget.TabPosition.North if position == 1 else QTabWidget.TabPosition.South)

    def tabBarPosition(self):
        return self._tab_bar_position

    def setSearchBarAppearance(self, appearance):
        self._search_bar_appearance = appearance
        self._search_bar.setVisible(appearance != 3)

    def searchBarAppearance(self):
        return self._search_bar_appearance

    def setTitleBackground(self, pixmap):
        self._title_background = pixmap

    def titleBackground(self):
        return self._title_background

    def setLogoPixmap(self, pixmap, alignment):
        self._logo_pixmap = pixmap
        self._logo_alignment = alignment

    def logoPixmap(self):
        return self._logo_pixmap

    def addSystemButton(self, *args):
        if len(args) == 1:
            icon, text = QIcon(), args[0]
        else:
            icon, text = args[0], args[1]
        if self._system_button is None:
            self._system_button = LqRibbonSystemButton(self)
        action = QAction(icon if isinstance(icon, QIcon) else QIcon(icon), text, self)
        self._system_button.setDefaultAction(action)
        self._system_button.show()
        return action

    def systemButton(self):
        return self._system_button

    def isBackstageVisible(self):
        return bool(self._system_button and self._system_button.backstage() and self._system_button.backstage().isVisible())

    def isKeyTipsShowing(self):
        return self._key_tips_showing

    def keyTipsEnabled(self):
        return self._key_tips_enabled

    def setKeyTipsEnable(self, enable):
        self._key_tips_enabled = bool(enable)

    def isKeyTipsComplement(self):
        return self._key_tips_complement

    def setKeyTipsComplement(self, complement):
        self._key_tips_complement = bool(complement)

    def setKeyTip(self, action, key_tip):
        self._key_tips[action] = key_tip

    def isMovableTabs(self):
        return self.isMovable()

    def setMovableTabs(self, movable):
        self.setMovable(movable)

    def tabsElideMode(self):
        return self.elideMode()

    def setTabsElideMode(self, mode):
        self.setElideMode(mode)

    def addMenu(self, text):
        return QMenu(text, self)

    def customizeManager(self):
        if self._customize_manager is None:
            self._customize_manager = LqRibbonCustomizeManager(self)
        return self._customize_manager

    def customizeDialog(self):
        if self._customize_dialog is None:
            self._customize_dialog = LqRibbonCustomizeDialog(self)
        return self._customize_dialog

    def showCustomizeDialog(self):
        self.customizeDialog().show()

    def rowItemHeight(self):
        return 24

    def rowItemCount(self):
        return 3

    def updateLayout(self):
        self.updateGeometry()

    def beginUpdate(self):
        self.setUpdatesEnabled(False)

    def endUpdate(self):
        self.setUpdatesEnabled(True)

    @staticmethod
    def loadTranslation(country=""):
        return True

    @staticmethod
    def tr_compatible(text, context=None):
        return text


RibbonBar = LqRibbonBar
