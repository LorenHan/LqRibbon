"""
LqRibbonBar - Ribbon bar container that holds ribbon pages
"""

from PySide6.QtWidgets import (
    QApplication,
    QTabWidget,
    QWidget,
    QHBoxLayout,
    QMenu,
    QStackedWidget,
    QToolBar,
    QToolButton,
)
from PySide6.QtCore import Qt, Signal, QEvent, QSize, QTimer
from PySide6.QtGui import QAction, QIcon, QPainter, QColor, QPen, QPixmap
from .lq_styles import LqStyle, RibbonStyle, _coerce_style
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


RIBBON_CAPTION_HEIGHT = 36
RIBBON_TAB_HEIGHT = 24
RIBBON_BAR_HEIGHT = 158
RIBBON_COLLAPSED_HEIGHT = RIBBON_CAPTION_HEIGHT + RIBBON_TAB_HEIGHT
RIBBON_SIMPLIFIED_HEIGHT = RIBBON_COLLAPSED_HEIGHT + 48
RIBBON_COLLAPSE_BUTTON_WIDTH = 32
RIBBON_COLLAPSE_BUTTON_HEIGHT = 24


class _RibbonCollapseButton(QToolButton):
    """Office-style collapse chevron used by LqRibbonBar."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._collapsed = False
        self.setAutoRaise(True)
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.setFixedSize(RIBBON_COLLAPSE_BUTTON_WIDTH, RIBBON_COLLAPSE_BUTTON_HEIGHT)

    def setCollapsed(self, collapsed):
        collapsed = bool(collapsed)
        if self._collapsed == collapsed:
            return
        self._collapsed = collapsed
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        if self.isDown():
            painter.fillRect(self.rect(), QColor("#d0d0d0"))
        elif self.underMouse():
            painter.fillRect(self.rect(), QColor("#e7e7e7"))

        pen = QPen(QColor("#333333"))
        pen.setWidthF(1.5)
        painter.setPen(pen)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        center_x = self.width() // 2
        center_y = self.height() // 2
        if self._collapsed:
            painter.drawLine(center_x - 6, center_y - 3, center_x, center_y + 3)
            painter.drawLine(center_x, center_y + 3, center_x + 6, center_y - 3)
        else:
            painter.drawLine(center_x - 6, center_y + 3, center_x, center_y - 3)
            painter.drawLine(center_x, center_y - 3, center_x + 6, center_y + 3)


class LqRibbonBar(QTabWidget):
    """Ribbon bar that contains multiple ribbon pages"""

    page_changed = Signal(int)  # Signal emitted when page changes
    pageChanged = Signal(int)
    current_page_index_changed = Signal(int)
    currentPageIndexChanged = Signal(int)
    current_page_changed = Signal(QWidget)
    currentPageChanged = Signal(QWidget)
    ribbon_minimized_changed = Signal(bool)
    ribbonMinimizedChanged = Signal(bool)
    ribbon_temporary_expanded_changed = Signal(bool)
    ribbonTemporaryExpandedChanged = Signal(bool)
    minimization_changed = Signal(bool)
    minimizationChanged = Signal(bool)
    simplified_mode_changed = Signal(bool)
    simplifiedModeChanged = Signal(bool)
    frameThemeChanged = Signal(bool)
    ribbonStyleChanged = Signal(int)
    searchTextChanged = Signal(str)
    searchAccepted = Signal(str)
    searchSuggestionActivated = Signal(str)
    searchActionTriggered = Signal(QAction)
    recentSearchActionsChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.pages = CallableList()
        self._quick_access_bar = LqRibbonQuickAccessBar(self)
        self._title_button_bar = QToolBar(self)
        self._search_bar = LqRibbonSearchBar(self)
        self._progress_bar = LqRibbonProgressBar(self)
        self._system_button = None
        self._customize_manager = None
        self._customize_dialog = None
        self._ribbon_minimized = False
        self._ribbon_temporary_expanded = False
        self._ignore_next_tab_release = False
        self._minimization_enabled = True
        self._simplified_mode = False
        self._simplified_mode_enabled = True
        self._frame_theme_enabled = False
        self._acrylic_enabled = False
        self._contextual_tabs_visible = True
        self._title_groups_visible = True
        self._expand_direction = Qt.LayoutDirection.LeftToRight
        self._quick_access_position = 1
        self._tab_bar_position = 1
        self._search_bar_appearance = 1
        self._ribbon_style = RibbonStyle.Office2016Blue
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
        self._collapse_button = _RibbonCollapseButton(self)
        self._collapse_button.clicked.connect(
            lambda: self.setRibbonMinimized(not self._ribbon_minimized)
        )
        self.init_ui()

    def init_ui(self):
        """Initialize the ribbon bar UI"""
        self.setObjectName("lqRibbonBar")

        # Set tab position to North (top)
        self.setTabPosition(QTabWidget.TabPosition.North)

        # Don't use document mode to allow background painting
        self.setDocumentMode(False)

        # Connect signals
        self.currentChanged.connect(self.on_page_changed)
        self._search_bar.textChanged.connect(lambda text: self.searchTextChanged.emit(text))
        self._search_bar.returnPressed.connect(self._accept_search_text)
        self.tabBar().setExpanding(False)
        self.tabBar().setUsesScrollButtons(True)
        app = QApplication.instance()
        if app:
            app.installEventFilter(self)

        # Set height for ribbon area
        self.setFixedHeight(RIBBON_BAR_HEIGHT)
        self.setStyleSheet(self._style_sheet())
        self._search_bar.setObjectName("lqRibbonSearchEdit")
        self._quick_access_bar.hide()
        self._title_button_bar.setObjectName("lqRibbonTitleButtonBar")
        self._title_button_bar.setMovable(False)
        self._title_button_bar.setFloatable(False)
        self._title_button_bar.setIconSize(QSize(16, 16))
        self._title_button_bar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        self._title_button_bar.hide()
        self._search_bar.hide()
        self._progress_bar.hide()
        self._collapse_button.hide()
        self._update_layout()

    def paintEvent(self, event):
        """Paint the themed title and tab background."""
        super().paintEvent(event)

        palette = LqStyle.palette(self._ribbon_style)
        painter = QPainter(self)
        painter.fillRect(
            0,
            0,
            self.width(),
            RIBBON_COLLAPSED_HEIGHT,
            QColor(palette["caption_bg"]),
        )

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_layout()

    def event(self, event):
        handled = super().event(event)
        if event.type() in (
            QEvent.Type.LayoutRequest,
            QEvent.Type.PolishRequest,
            QEvent.Type.Show,
            QEvent.Type.FontChange,
            QEvent.Type.StyleChange,
        ):
            self._update_layout()
        return handled

    def eventFilter(self, obj, event):
        if obj == self.tabBar() and event.type() == QEvent.Type.MouseButtonDblClick:
            tab_index = self.tabBar().tabAt(event.pos())
            if event.button() == Qt.MouseButton.LeftButton and tab_index >= 0:
                self._ignore_next_tab_release = True
                self.setRibbonMinimized(not self._ribbon_minimized)
                return True
        if obj == self.tabBar() and event.type() == QEvent.Type.MouseButtonRelease:
            if self._ignore_next_tab_release:
                self._ignore_next_tab_release = False
            elif (
                event.button() == Qt.MouseButton.LeftButton
                and self._ribbon_minimized
                and self.tabBar().tabAt(event.pos()) >= 0
            ):
                self._show_temporary_ribbon()

        if self._ribbon_temporary_expanded:
            event_type = event.type()
            if event_type == QEvent.Type.MouseButtonRelease:
                widget = obj if isinstance(obj, QWidget) else None
                if widget is None or not self._is_ribbon_related_widget(widget):
                    self._schedule_hide_temporary_ribbon()
            elif event_type == QEvent.Type.FocusIn:
                widget = obj if isinstance(obj, QWidget) else None
                if widget is not None and not self._is_ribbon_related_widget(widget):
                    self._schedule_hide_temporary_ribbon()
            elif event_type in (
                QEvent.Type.WindowDeactivate,
                QEvent.Type.ApplicationDeactivate,
            ):
                self._hide_temporary_ribbon()
        return super().eventFilter(obj, event)

    def _style_sheet(self):
        return LqStyle.get_ribbon_style(self._ribbon_style)

    def _update_layout(self):
        tab_bar = self.tabBar()
        tab_width = min(self.width(), tab_bar.sizeHint().width())
        tab_bar.setGeometry(0, RIBBON_CAPTION_HEIGHT, tab_width, RIBBON_TAB_HEIGHT)
        tab_bar.raise_()
        command_area_visible = self._is_command_area_visible()

        stack = self.findChild(QStackedWidget)
        if stack:
            stack_top = RIBBON_COLLAPSED_HEIGHT
            stack_height = max(0, self.height() - stack_top) if command_area_visible else 0
            stack.setGeometry(0, stack_top, self.width(), stack_height)
            stack.setVisible(command_area_visible)

        self._search_bar.setGeometry(
            max(0, (self.width() - 524) // 2),
            7,
            min(524, max(120, self.width() - 220)),
            22,
        )
        self._search_bar.raise_()

        title_bar_width = min(
            self._title_button_bar.sizeHint().width(),
            max(0, self.width() - self._search_bar.geometry().right() - 48),
        )
        if self._title_button_bar.actions() and title_bar_width > 0:
            title_bar_x = max(
                self._search_bar.geometry().right() + 8,
                self.width() - title_bar_width - 48,
            )
            self._title_button_bar.setGeometry(title_bar_x, 6, title_bar_width, 24)
            self._title_button_bar.show()
            self._title_button_bar.raise_()
        else:
            self._title_button_bar.hide()

        collapse_x = max(0, self.width() - RIBBON_COLLAPSE_BUTTON_WIDTH)
        collapse_y = max(0, self.height() - RIBBON_COLLAPSE_BUTTON_HEIGHT - 2)
        self._collapse_button.setGeometry(
            collapse_x,
            collapse_y,
            RIBBON_COLLAPSE_BUTTON_WIDTH,
            RIBBON_COLLAPSE_BUTTON_HEIGHT,
        )
        self._collapse_button.setCollapsed(self._ribbon_minimized)
        self._collapse_button.setVisible(self._frame_theme_enabled and not self._ribbon_minimized)
        self._collapse_button.raise_()

    def _is_command_area_visible(self):
        return not self._ribbon_minimized or self._ribbon_temporary_expanded

    def _apply_ribbon_height(self):
        if self._is_command_area_visible():
            height = RIBBON_SIMPLIFIED_HEIGHT if self._simplified_mode else RIBBON_BAR_HEIGHT
        else:
            height = RIBBON_COLLAPSED_HEIGHT
        self.setFixedHeight(height)
        self._update_layout()

    def _show_temporary_ribbon(self):
        if (
            not self._ribbon_minimized
            or self._ribbon_temporary_expanded
            or not self._minimization_enabled
        ):
            return
        self._ribbon_temporary_expanded = True
        self._apply_ribbon_height()
        self.ribbon_temporary_expanded_changed.emit(True)
        self.ribbonTemporaryExpandedChanged.emit(True)

    def _hide_temporary_ribbon(self):
        if not self._ribbon_temporary_expanded:
            return
        self._ribbon_temporary_expanded = False
        self._apply_ribbon_height()
        self.ribbon_temporary_expanded_changed.emit(False)
        self.ribbonTemporaryExpandedChanged.emit(False)

    def _schedule_hide_temporary_ribbon(self):
        if self._ribbon_temporary_expanded:
            QTimer.singleShot(0, self._hide_temporary_ribbon)

    def _is_ribbon_related_widget(self, widget):
        current = widget
        while current:
            if current is self:
                return True
            parent_widget = current.parentWidget() if hasattr(current, "parentWidget") else None
            if parent_widget is not None:
                current = parent_widget
                continue
            parent = current.parent()
            current = parent if isinstance(parent, QWidget) else None
        return False

    def _accept_search_text(self):
        text = self._search_bar.text().strip()
        if not text:
            return
        if not self.triggerSearchAction(text):
            self.searchAccepted.emit(text)

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
        self._update_layout()
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
        self._update_layout()
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
        self._update_layout()

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
        self.pageChanged.emit(index)
        self.current_page_index_changed.emit(index)
        self.currentPageIndexChanged.emit(index)
        self.current_page_changed.emit(self.get_page(index))
        self.currentPageChanged.emit(self.get_page(index))

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
        self.searchActionTriggered.emit(action)
        self._recent_search_actions.insert(0, action)
        self._recent_search_actions = self._recent_search_actions[: self._recent_search_limit]
        self.recentSearchActionsChanged.emit()
        return True

    def setSearchActionTriggerEnabled(self, enabled):
        self._search_action_trigger_enabled = bool(enabled)

    def isSearchActionTriggerEnabled(self):
        return self._search_action_trigger_enabled

    def recentSearchActions(self):
        return list(self._recent_search_actions)

    def clearRecentSearchActions(self):
        self._recent_search_actions.clear()
        self.recentSearchActionsChanged.emit()

    def setRecentSearchLimit(self, count):
        self._recent_search_limit = max(0, int(count))
        self._recent_search_actions = self._recent_search_actions[: self._recent_search_limit]
        self.recentSearchActionsChanged.emit()

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
        action = QAction(icon if isinstance(icon, QIcon) else QIcon(icon), text, self)
        action.setToolTip(text)
        self._title_button_bar.addAction(action)
        self._update_layout()
        return action

    def addAction(self, *args):
        if len(args) == 1 and isinstance(args[0], QAction):
            return self.addQuickAccessAction(args[0])
        if len(args) >= 2:
            icon, text = args[0], args[1]
            return self.addQuickAccessAction(icon, text)
        return None

    def removeTitleButton(self, action):
        self._title_button_bar.removeAction(action)
        action.deleteLater()
        self._update_layout()

    def setCurrentPageIndex(self, index):
        self.setCurrentIndex(index)

    def setRibbonMinimized(self, minimized):
        if minimized and not self._minimization_enabled:
            return
        minimized = bool(minimized)
        if self._ribbon_minimized == minimized:
            if minimized:
                self._hide_temporary_ribbon()
            return
        temporary_was_expanded = self._ribbon_temporary_expanded
        self._ribbon_minimized = minimized
        self._ribbon_temporary_expanded = False
        self._apply_ribbon_height()
        self.ribbon_minimized_changed.emit(self._ribbon_minimized)
        self.ribbonMinimizedChanged.emit(self._ribbon_minimized)
        self.minimization_changed.emit(self._ribbon_minimized)
        self.minimizationChanged.emit(self._ribbon_minimized)
        if temporary_was_expanded:
            self.ribbon_temporary_expanded_changed.emit(False)
            self.ribbonTemporaryExpandedChanged.emit(False)

    def isRibbonMinimized(self):
        return self._ribbon_minimized

    def isRibbonTemporaryExpanded(self):
        return self._ribbon_temporary_expanded

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
        enabled = bool(enabled)
        if self._simplified_mode == enabled:
            return
        self._simplified_mode = enabled
        if enabled:
            self.setRibbonMinimized(False)
        self._simplified_action.setChecked(self._simplified_mode)
        self._apply_ribbon_height()
        self.simplified_mode_changed.emit(self._simplified_mode)
        self.simplifiedModeChanged.emit(self._simplified_mode)

    def simplifiedModeEnabled(self):
        return self._simplified_mode_enabled

    def setSimplifiedModeEnabled(self, enabled):
        self._simplified_mode_enabled = bool(enabled)

    def setFrameThemeEnabled(self, enabled=True):
        self._frame_theme_enabled = bool(enabled)
        self._search_bar.setVisible(enabled)
        self._update_layout()
        self.frameThemeChanged.emit(self._frame_theme_enabled)

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

    def setRibbonStyle(self, style):
        style = _coerce_style(style)
        if self._ribbon_style == style:
            return
        self._ribbon_style = style
        self.setStyleSheet(self._style_sheet())
        self._update_layout()
        self.update()
        self.ribbonStyleChanged.emit(int(style))

    def ribbonStyle(self):
        return self._ribbon_style

    @staticmethod
    def ribbonStyleName(style):
        return LqStyle.ribbon_style_name(style)

    def setSearchBarAppearance(self, appearance):
        self._search_bar_appearance = appearance
        self._search_bar.setVisible(appearance != 3)
        self._update_layout()

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

    def expandDirection(self):
        return self._expand_direction

    def setExpandDirection(self, direction):
        self._expand_direction = direction

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
        self._update_layout()

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
