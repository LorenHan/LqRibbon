"""
Additional LqRibbon widgets and compatibility helpers.
"""

from PySide6.QtCore import Qt, QObject, QPoint, QRect, QSize, QTimer, Signal
from PySide6.QtGui import QAction, QColor, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import (
    QCheckBox,
    QColorDialog,
    QComboBox,
    QDateEdit,
    QDateTimeEdit,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFontComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMdiArea,
    QMenu,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QSizePolicy,
    QSlider,
    QSpinBox,
    QStackedWidget,
    QStatusBar,
    QStyle,
    QTimeEdit,
    QToolBar,
    QToolButton,
    QVBoxLayout,
    QWidget,
    QWidgetAction,
)


QtnRibbonCustomizeQuickAccessToolBarDotString = "Customize Quick Access Toolbar..."
QtnRibbonCustomizeQuickAccessToolBarString = "Customize Quick Access Toolbar"
QtnRibbonShowQuickAccessToolBarBelowString = "Show Quick Access Toolbar Below the Ribbon"
QtnRibbonShowQuickAccessToolBarAboveString = "Show Quick Access Toolbar Above the Ribbon"
QtnRibbonCustomizeActionString = "Customize the Ribbon..."
QtnRibbonMinimizeActionString = "Minimize the Ribbon"
QtnRibbonSimplifiedRibbonActionString = "Simplified Ribbon"
QtnRibbonSimplifiedRibbonActionToolTipsString = "Turn on/off Ribbon Simplified Mode"
QtnRibbonRecentDocumentsString = "Recent Documents"
QtnRibbonUntitledString = "Untitled"
QtnRibbonSeparatorString = "Separator"
QtnRibbonNewPageString = "New Page"
QtnRibbonNewGroupString = "New Group"
QtnRibbonSearchBarSearchString = "Search"
QtnRibbonSearchBarGetHelpString = "Get Help"
QtnRibbonSearchBarHelpString = "Help"
QtnRibbonSearchBarActionsString = "Actions"
QtnRibbonSearchBarRecentActionsString = "Recently Used"
QtnRibbonSearchBarSuggestedActionsString = "Suggested Actions"
QtnRibbonSearchBarDocumentResultsString = "Document Results"
QtnRibbonSearchBarRelatedFilesString = "Related Files"
QtnRibbonGalleryItemSize = QSize(72, 56)
QtnRibbonGalleryItemString = "Gallery Item"


class CallableString(str):
    """String that also works as a Qtitan-style zero-argument getter."""

    def __call__(self):
        return str(self)


class CallableList(list):
    """List that also works as a Qtitan-style zero-argument getter."""

    def __call__(self):
        return list(self)


class ContextColor:
    ContextColorNone = 0
    ContextColorBlue = 1
    ContextColorYellow = 2
    ContextColorGreen = 3
    ContextColorRed = 4
    ContextColorPurple = 5
    ContextColorCyan = 6
    ContextColorOrange = 7


def getRibbonVersion():
    return "6.8.0-compatible"


class LqRibbonControlSizeDefinition:
    GroupLarge = 0x01
    GroupMedium = 0x02
    GroupSmall = 0x04
    GroupPopup = 0x08
    GroupSimplified = 0x10
    GroupSimplifiedOverflow = 0x20

    ImageNone = 0
    ImageLarge = 1
    ImageSmall = 2

    def __init__(self, parent=None, group_size=GroupLarge):
        self.parent = parent
        self._group_size = group_size
        self._image_size = self.ImageLarge
        self._label_visible = True
        self._popup = False
        self._visible = True
        self._enabled = True
        self._stretchable = False
        self._minimum_item_count = 0
        self._maximum_item_count = 0

    def groupSize(self):
        return self._group_size

    def imageSize(self):
        return self._image_size

    def setImageSize(self, size):
        self._image_size = size

    def isLabelVisible(self):
        return self._label_visible

    def setLabelVisible(self, visible):
        self._label_visible = bool(visible)

    def isPopup(self):
        return self._popup

    def setPopup(self, popup):
        self._popup = bool(popup)

    def isVisible(self):
        return self._visible

    def setVisible(self, visible):
        self._visible = bool(visible)

    def isEnabled(self):
        return self._enabled

    def setEnabled(self, enabled):
        self._enabled = bool(enabled)

    def isStretchable(self):
        return self._stretchable

    def setStretchable(self, stretchable):
        self._stretchable = bool(stretchable)

    def minimumItemCount(self):
        return self._minimum_item_count

    def setMinimumItemCount(self, count):
        self._minimum_item_count = int(count)

    def maximumItemCount(self):
        return self._maximum_item_count

    def setMaximumItemCount(self, count):
        self._maximum_item_count = int(count)


class LqRibbonControl(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._default_action = None
        self._current_size = LqRibbonControlSizeDefinition.GroupLarge
        self._definitions = {}

    def parentGroup(self):
        return self.parent()

    def defaultAction(self):
        return self._default_action

    def setDefaultAction(self, action):
        self._default_action = action
        self.actionChanged()

    def adjustCurrentSize(self, expand):
        self._current_size = (
            LqRibbonControlSizeDefinition.GroupLarge
            if expand
            else LqRibbonControlSizeDefinition.GroupSmall
        )
        self.sizeChanged(self._current_size)
        return True

    def sizeChanged(self, size):
        self._current_size = size

    def actionChanged(self):
        pass

    def updateLayout(self):
        self.updateGeometry()

    def currentSize(self):
        return self._current_size

    def sizeDefinition(self, size):
        if size not in self._definitions:
            self._definitions[size] = LqRibbonControlSizeDefinition(self, size)
        return self._definitions[size]


class LqRibbonWidgetControl(LqRibbonControl):
    def __init__(self, parent=None, widget=None):
        super().__init__(parent)
        self._content_widget = None
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        if widget is not None:
            self.setContentWidget(widget)

    def contentWidget(self):
        return self._content_widget

    def setContentWidget(self, widget):
        if self._content_widget is not None:
            self._layout.removeWidget(self._content_widget)
        self._content_widget = widget
        if widget is not None:
            self._layout.addWidget(widget)

    def widget(self):
        return self._content_widget


class LqRibbonLabelControl(LqRibbonWidgetControl):
    def __init__(self, text="", parent=None):
        super().__init__(parent, QLabel(text))


class LqRibbonToolBarControl(LqRibbonControl):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.toolbar = QToolBar(self)
        self.toolbar.setMovable(False)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.toolbar)

    def clear(self):
        self.toolbar.clear()

    def addAction(self, *args):
        return self.toolbar.addAction(*args)

    def addMenu(self, text_or_icon, text=None):
        if text is None:
            text = text_or_icon
            icon = QIcon()
        else:
            icon = text_or_icon if isinstance(text_or_icon, QIcon) else QIcon(text_or_icon)
        menu = QMenu(text, self)
        action = QAction(icon, text, self)
        action.setMenu(menu)
        self.toolbar.addAction(action)
        return menu

    def addWidget(self, widget):
        return self.toolbar.addWidget(widget)

    def addSeparator(self):
        return self.toolbar.addSeparator()

    def overflowMenu(self):
        return QMenu(self)

    def isOverflowMenuIsEmpty(self):
        return True


class LqRibbonButtonControl(LqRibbonWidgetControl):
    def __init__(self, parent=None):
        from .lq_ribbon_button import LqRibbonButton

        super().__init__(parent)
        self.setContentWidget(LqRibbonButton(parent=self))
        self._large_icon = QIcon()
        self._small_icon = QIcon()
        self._label = ""

    def largeIcon(self):
        return self._large_icon

    def setLargeIcon(self, icon):
        self._large_icon = icon if isinstance(icon, QIcon) else QIcon(icon)
        self.widget().setIcon(self._large_icon)
        self.widget().setLargeIcon(True)

    def smallIcon(self):
        return self._small_icon

    def setSmallIcon(self, icon):
        self._small_icon = icon if isinstance(icon, QIcon) else QIcon(icon)
        self.widget().setIcon(self._small_icon)
        self.widget().setLargeIcon(False)

    def label(self):
        return self._label

    def setLabel(self, label):
        self._label = str(label)
        self.widget().setText(self._label)

    def setMenu(self, menu):
        self.widget().setMenu(menu)

    def menu(self):
        return self.widget().menu()

    def setPopupMode(self, mode):
        self.widget().setPopupMode(mode)

    def popupMode(self):
        return self.widget().popupMode()

    def setToolButtonStyle(self, style):
        self.widget().setToolButtonStyle(style)

    def toolButtonStyle(self):
        return self.widget().toolButtonStyle()


class LqRibbonCheckBoxControl(LqRibbonWidgetControl):
    def __init__(self, text="", parent=None):
        super().__init__(parent, QCheckBox(text))


class LqRibbonRadioButtonControl(LqRibbonWidgetControl):
    def __init__(self, text="", parent=None):
        super().__init__(parent, QRadioButton(text))


class LqRibbonFontComboBoxControl(LqRibbonWidgetControl):
    def __init__(self, parent=None):
        super().__init__(parent, QFontComboBox())


class LqRibbonLineEditControl(LqRibbonWidgetControl):
    def __init__(self, parent=None):
        super().__init__(parent, QLineEdit())


class LqRibbonComboBoxControl(LqRibbonWidgetControl):
    def __init__(self, parent=None):
        super().__init__(parent, QComboBox())


class LqRibbonSpinBoxControl(LqRibbonWidgetControl):
    def __init__(self, parent=None):
        super().__init__(parent, QSpinBox())


class LqRibbonDoubleSpinBoxControl(LqRibbonWidgetControl):
    def __init__(self, parent=None):
        super().__init__(parent, QDoubleSpinBox())


class LqRibbonSliderControl(LqRibbonWidgetControl):
    def __init__(self, orientation=Qt.Orientation.Horizontal, parent=None):
        super().__init__(parent, QSlider(orientation))


class LqRibbonDateTimeEditControl(LqRibbonWidgetControl):
    def __init__(self, parent=None):
        super().__init__(parent, QDateTimeEdit())


class LqRibbonTimeEditControl(LqRibbonWidgetControl):
    def __init__(self, parent=None):
        super().__init__(parent, QTimeEdit())


class LqRibbonDateEditControl(LqRibbonWidgetControl):
    def __init__(self, parent=None):
        super().__init__(parent, QDateEdit())


class LqRibbonGalleryItem:
    def __init__(self, caption=QtnRibbonGalleryItemString, icon=None):
        self._caption = str(caption)
        self._icon = icon if isinstance(icon, QIcon) else QIcon(icon or "")
        self._tool_tip = ""
        self._status_tip = ""
        self._data = {}
        self._index = -1
        self._separator = False
        self._enabled = True
        self._visible = True

    def icon(self):
        return self._icon

    def setIcon(self, icon):
        self._icon = icon if isinstance(icon, QIcon) else QIcon(icon)

    def caption(self):
        return self._caption

    def setCaption(self, caption):
        self._caption = str(caption)

    def toolTip(self):
        return self._tool_tip

    def setToolTip(self, tool_tip):
        self._tool_tip = str(tool_tip)

    def statusTip(self):
        return self._status_tip

    def setStatusTip(self, status_tip):
        self._status_tip = str(status_tip)

    def getIndex(self):
        return self._index

    def isSeparator(self):
        return self._separator

    def setSeparator(self, on):
        self._separator = bool(on)

    def setEnabled(self, enabled):
        self._enabled = bool(enabled)

    def isEnabled(self):
        return self._enabled

    def setVisible(self, visible):
        self._visible = bool(visible)

    def isVisible(self):
        return self._visible

    def data(self, role=Qt.ItemDataRole.UserRole):
        return self._data.get(int(role))

    def setData(self, role, value):
        self._data[int(role)] = value


class LqRibbonGalleryGroup(QObject):
    changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._items = []
        self._size = QSize(QtnRibbonGalleryItemSize)

    def _refresh_indexes(self):
        for index, item in enumerate(self._items):
            item._index = index

    def addItem(self, caption=QtnRibbonGalleryItemString, icon=None, *args):
        if isinstance(caption, LqRibbonGalleryItem):
            item = caption
        else:
            item = LqRibbonGalleryItem(caption, icon)
        self.appendItem(item)
        return item

    def addItemFromMap(self, caption, map_index, pixmap, map_size_image, transparent_color=QColor()):
        del map_index, map_size_image, transparent_color
        return self.addItem(caption, QIcon(pixmap) if isinstance(pixmap, QPixmap) else QIcon())

    def appendItem(self, item):
        if not isinstance(item, LqRibbonGalleryItem):
            return
        self._items.append(item)
        self._refresh_indexes()
        self.changed.emit()

    def insertItem(self, index, item):
        if not isinstance(item, LqRibbonGalleryItem):
            return
        index = max(0, min(int(index), len(self._items)))
        self._items.insert(index, item)
        self._refresh_indexes()
        self.changed.emit()

    def addSeparator(self, caption=QtnRibbonSeparatorString):
        item = LqRibbonGalleryItem(caption)
        item.setSeparator(True)
        self.appendItem(item)
        return item

    def clear(self):
        self._items.clear()
        self.changed.emit()

    def remove(self, index):
        if 0 <= index < len(self._items):
            self._items.pop(index)
            self._refresh_indexes()
            self.changed.emit()

    def itemCount(self):
        return len(self._items)

    def item(self, index):
        return self._items[index] if 0 <= index < len(self._items) else None

    def takeItem(self, index):
        if not (0 <= index < len(self._items)):
            return None
        item = self._items.pop(index)
        item._index = -1
        self._refresh_indexes()
        self.changed.emit()
        return item

    def size(self):
        return QSize(self._size)

    def setSize(self, size):
        self._size = QSize(size)
        self.changed.emit()


class LqRibbonGallery(QWidget):
    itemPressed = Signal(object)
    itemClicked = Signal(object)
    currentItemChanged = Signal(object, object)
    selectionChanged = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("lqRibbonGallery")
        self._group = None
        self._column_count = 4
        self._row_count = 2
        self._selected_index = -1
        self._checked_index = -1
        self._popup_menu = None
        self._buttons = []
        self._layout = QGridLayout(self)
        self._layout.setContentsMargins(2, 2, 2, 2)
        self._layout.setHorizontalSpacing(2)
        self._layout.setVerticalSpacing(2)
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

    def setGalleryGroup(self, group):
        if self._group is not None:
            try:
                self._group.changed.disconnect(self.updateLayout)
            except RuntimeError:
                pass
        self._group = group
        if self._group is not None:
            self._group.changed.connect(self.updateLayout)
        self.updateLayout()

    def galleryGroup(self):
        return self._group

    def itemSize(self):
        return self._group.size() if self._group is not None else QSize(QtnRibbonGalleryItemSize)

    def setItemSize(self, size):
        if self._group is None:
            self.setGalleryGroup(LqRibbonGalleryGroup(self))
        self._group.setSize(size)

    def setPopupMenu(self, popup_menu):
        self._popup_menu = popup_menu
        action = QAction(self)
        action.setMenu(popup_menu)
        return action

    def popupMenu(self):
        return self._popup_menu

    def setColumnCount(self, count):
        self._column_count = max(1, int(count))
        self.updateLayout()

    def columnCount(self):
        return self._column_count

    def setRowCount(self, row):
        self._row_count = max(1, int(row))
        self.updateLayout()

    def rowCount(self):
        return self._row_count

    def itemCount(self):
        return self._group.itemCount() if self._group is not None else 0

    def item(self, index):
        return self._group.item(index) if self._group is not None else None

    def setSelectedItem(self, index):
        previous = self.item(self._selected_index)
        self._selected_index = index if self.item(index) is not None else -1
        self.selectionChanged.emit(self._selected_index)
        self.currentItemChanged.emit(self.item(self._selected_index), previous)

    def selectedItem(self):
        return self._selected_index

    def setCheckedIndex(self, index):
        self._checked_index = index if self.item(index) is not None else -1
        for item_index, button in enumerate(self._buttons):
            button.setChecked(item_index == self._checked_index)

    def checkedIndex(self):
        return self._checked_index

    def setCheckedItem(self, item):
        self.setCheckedIndex(item.getIndex() if item else -1)

    def checkedItem(self):
        return self.item(self._checked_index)

    def isItemSelected(self):
        return self._selected_index >= 0

    def ensureVisible(self, index):
        self.setSelectedItem(index)

    def hideSelection(self):
        self._selected_index = -1
        self.selectionChanged.emit(-1)

    def updateLayout(self):
        while self._layout.count():
            child = self._layout.takeAt(0)
            widget = child.widget()
            if widget:
                widget.deleteLater()
        self._buttons.clear()
        if self._group is None:
            return

        visible_index = 0
        item_size = self.itemSize()
        for item_index in range(self._group.itemCount()):
            item = self._group.item(item_index)
            if item is None or not item.isVisible():
                continue
            row = visible_index // self._column_count
            column = visible_index % self._column_count
            if row >= self._row_count:
                break
            if item.isSeparator():
                separator = QFrame(self)
                separator.setFrameShape(QFrame.Shape.HLine)
                self._layout.addWidget(separator, row, column)
                visible_index += 1
                continue
            button = QToolButton(self)
            button.setText(item.caption())
            button.setIcon(item.icon())
            button.setToolTip(item.toolTip())
            button.setStatusTip(item.statusTip())
            button.setEnabled(item.isEnabled())
            button.setCheckable(True)
            button.setChecked(item_index == self._checked_index)
            button.setToolButtonStyle(
                Qt.ToolButtonStyle.ToolButtonTextUnderIcon
                if item_size.height() >= 40
                else Qt.ToolButtonStyle.ToolButtonTextBesideIcon
            )
            button.setIconSize(QSize(16, 16))
            button.setFixedSize(item_size)
            button.clicked.connect(lambda checked=False, idx=item_index: self._activate_item(idx))
            self._layout.addWidget(button, row, column)
            self._buttons.append(button)
            visible_index += 1
        self.updateGeometry()

    def bestFit(self):
        self.updateLayout()

    def sizeHint(self):
        item_size = self.itemSize()
        width = self._column_count * item_size.width() + 6
        height = self._row_count * item_size.height() + 6
        return QSize(width, height)

    def minimumSizeHint(self):
        return self.sizeHint()

    def _activate_item(self, index):
        item = self.item(index)
        if item is None:
            return
        self.itemPressed.emit(item)
        self.setSelectedItem(index)
        self.setCheckedIndex(index)
        self.itemClicked.emit(item)


class LqRibbonGalleryControl(LqRibbonWidgetControl):
    def __init__(self, parent=None, gallery=None):
        super().__init__(parent)
        self.setContentWidget(gallery or LqRibbonGallery(self))

    def widget(self):
        return super().widget()

    def setContentsMargins(self, top, bottom):
        self.layout().setContentsMargins(0, int(top), 0, int(bottom))


class LqRibbonQuickAccessBar(QToolBar):
    show_customize_menu = Signal(QMenu)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMovable(False)
        self.setFloatable(False)
        self._hidden_actions = set()
        self._customize_action = QAction(QtnRibbonCustomizeQuickAccessToolBarString, self)
        self._customize_action.triggered.connect(self._emit_customize_menu)
        super().addAction(self._customize_action)

    def _emit_customize_menu(self):
        menu = QMenu(self)
        self.show_customize_menu.emit(menu)
        if not menu.isEmpty():
            menu.exec(self.mapToGlobal(QPoint(0, self.height())))

    def actionCustomizeButton(self):
        return self._customize_action

    def isActionVisible(self, action):
        return action is not None and action not in self._hidden_actions and action.isVisible()

    def setActionVisible(self, action, visible):
        if action is None or action == self._customize_action:
            return
        if visible:
            self._hidden_actions.discard(action)
        else:
            self._hidden_actions.add(action)
        action.setVisible(visible)

    def visibleCount(self):
        return sum(
            1
            for action in self.actions()
            if action != self._customize_action and self.isActionVisible(action)
        )

    def addAction(self, action):
        result = super().addAction(action)
        self.removeAction(self._customize_action)
        super().addAction(self._customize_action)
        return result


class LqRibbonSearchBar(QLineEdit):
    show_help = Signal(str)

    def __init__(self, ribbon_bar=None):
        super().__init__(ribbon_bar)
        self.ribbon_bar = ribbon_bar
        self._compact = False
        self._help_enabled = True
        self._suggested_actions = []
        self._max_search_item_count = 8
        self._popup = QMenu(self)
        self._popup.setObjectName("lqRibbonSearchPopupMenu")
        self._popup_query = ""
        self._popup_keyboard_active = False
        self._suppress_next_focus_popup = False
        self._icon = self.style().standardIcon(
            QStyle.StandardPixmap.SP_FileDialogContentsView
        )
        self.setPlaceholderText(QtnRibbonSearchBarSearchString)

    def setCompact(self, compact):
        self._compact = bool(compact)
        self.setTextMargins(48 if self._compact else 0, 0, 0, 0)
        self.updateGeometry()
        self.update()

    def isCompact(self):
        return self._compact

    def icon(self):
        return self._icon

    def isHelpEnabled(self):
        return self._help_enabled

    def setHelpEnabled(self, enabled):
        self._help_enabled = bool(enabled)

    def suggestedActions(self):
        return list(self._suggested_actions)

    def addSuggestedAction(self, action):
        if action not in self._suggested_actions:
            self._suggested_actions.append(action)

    def removeSuggestedAction(self, action):
        if action in self._suggested_actions:
            self._suggested_actions.remove(action)

    def maxSearchItemCount(self):
        return self._max_search_item_count

    def setMaxSearchItemCount(self, count):
        self._max_search_item_count = max(0, int(count))

    def _normalized_action_text(self, text):
        return str(text).replace("&", "").strip().lower()

    def _action_search_terms(self, action):
        keywords = action.data() or []
        if isinstance(keywords, str):
            keywords = [keywords]
        return [action.text()] + [str(keyword) for keyword in keywords]

    def _action_matches_text(self, action, normalized):
        return any(
            normalized in self._normalized_action_text(term)
            for term in self._action_search_terms(action)
        )

    def _ordered_popup_actions(self, normalized):
        actions = [
            action
            for action in self._suggested_actions
            if action and action.isVisible() and action.text().strip()
        ]
        if normalized:
            return [
                action for action in actions
                if self._action_matches_text(action, normalized)
            ]

        ordered = []
        if self.ribbon_bar and hasattr(self.ribbon_bar, "searchSuggestions"):
            for suggestion in self.ribbon_bar.searchSuggestions():
                normalized_suggestion = self._normalized_action_text(suggestion)
                for action in actions:
                    normalized_text = self._normalized_action_text(action.text())
                    if action not in ordered and normalized_text == normalized_suggestion:
                        ordered.append(action)
                        break
        ordered.extend(action for action in actions if action not in ordered)
        return ordered

    def _configured_suggested_actions(self, actions):
        if not self.ribbon_bar or not hasattr(self.ribbon_bar, "searchSuggestions"):
            return []
        ordered = []
        for suggestion in self.ribbon_bar.searchSuggestions():
            normalized_suggestion = self._normalized_action_text(suggestion)
            for action in actions:
                normalized_text = self._normalized_action_text(action.text())
                if action not in ordered and normalized_text == normalized_suggestion:
                    ordered.append(action)
                    break
        return ordered

    def _matched_document_results(self, normalized):
        if (
            not normalized
            or not self.ribbon_bar
            or not hasattr(self.ribbon_bar, "searchDocumentResults")
        ):
            return []
        results = []
        for result in self.ribbon_bar.searchDocumentResults():
            text = str(result).strip()
            if text and normalized in text.replace("&", "").lower():
                results.append(text)
            if self._max_search_item_count and len(results) >= max(
                1, self._max_search_item_count // 2
            ):
                break
        return results

    def _matched_related_files(self, normalized):
        if (
            not normalized
            or not self.ribbon_bar
            or not hasattr(self.ribbon_bar, "searchRelatedFiles")
        ):
            return []
        results = []
        for result in self.ribbon_bar.searchRelatedFiles():
            text = str(result).strip()
            if text and normalized in text.replace("&", "").lower():
                results.append(text)
            if self._max_search_item_count and len(results) >= max(
                1, self._max_search_item_count // 2
            ):
                break
        return results

    def _selectable_popup_actions(self):
        return [
            action
            for action in self._popup.actions()
            if action and action.isVisible() and action.isEnabled()
            and not action.isSeparator()
        ]

    def _set_first_popup_action(self):
        actions = self._selectable_popup_actions()
        if not actions:
            return False
        self._popup.setActiveAction(actions[0])
        return True

    def _set_last_popup_action(self):
        actions = self._selectable_popup_actions()
        if not actions:
            return False
        self._popup.setActiveAction(actions[-1])
        return True

    def _move_popup_selection(self, step):
        actions = self._selectable_popup_actions()
        if not actions:
            return False
        current = self._popup.activeAction()
        if current not in actions:
            self._popup.setActiveAction(actions[0 if step > 0 else -1])
            return True
        next_index = actions.index(current) + step
        next_index = max(0, min(next_index, len(actions) - 1))
        self._popup.setActiveAction(actions[next_index])
        return True

    def _focus_without_popup(self):
        self._suppress_next_focus_popup = True
        self.setFocus()
        QTimer.singleShot(0, lambda: setattr(self, "_suppress_next_focus_popup", False))

    def _activate_popup_action(self, action):
        if not action or action.isSeparator() or not action.isEnabled():
            return False
        role = action.property("lqRibbonSearchPopupRole")
        text = action.text()
        if role == "result":
            if self.ribbon_bar:
                self.ribbon_bar.searchSuggestionActivated.emit(text)
            self._suppress_next_focus_popup = True
            self.closePopup()
            self.clear()
            self._focus_without_popup()
            return True
        if role == "help":
            self.show_help.emit(self.text().strip())
            self._suppress_next_focus_popup = True
            self.closePopup()
            self.clear()
            self._focus_without_popup()
            return True
        if self.ribbon_bar and self.ribbon_bar.triggerSearchAction(text):
            self._suppress_next_focus_popup = True
            self.closePopup()
            self.clear()
            self._focus_without_popup()
            return True
        action.trigger()
        self._suppress_next_focus_popup = True
        self.closePopup()
        self.clear()
        self._focus_without_popup()
        return True

    def showPopup(self, text=""):
        text = str(text)
        self._popup_query = text
        self._popup_keyboard_active = False
        self._popup.clear()
        normalized = text.strip().lower()
        count = 0
        actions = self._ordered_popup_actions(normalized)
        document_results = self._matched_document_results(normalized)
        related_files = self._matched_related_files(normalized)
        if not normalized and self.ribbon_bar and hasattr(self.ribbon_bar, "recentSearchActions"):
            recent_actions = [
                action for action in self.ribbon_bar.recentSearchActions()
                if action in actions
            ]
            suggested_actions = [
                action for action in self._configured_suggested_actions(actions)
                if action not in recent_actions
            ]
            remaining_actions = [
                action for action in actions
                if action not in recent_actions and action not in suggested_actions
            ]
            grouped_actions = []
            if recent_actions:
                self._popup.addSection(QtnRibbonSearchBarRecentActionsString)
                grouped_actions.extend(recent_actions)
            if suggested_actions:
                grouped_actions.append(QtnRibbonSearchBarSuggestedActionsString)
                grouped_actions.extend(suggested_actions)
            if remaining_actions:
                grouped_actions.append(QtnRibbonSearchBarActionsString)
                grouped_actions.extend(remaining_actions)
            if grouped_actions:
                actions = grouped_actions

        if (
            normalized
            and actions
            and not any(isinstance(action, str) for action in actions)
        ):
            actions = [QtnRibbonSearchBarActionsString] + actions

        if document_results:
            self._popup.addSection(QtnRibbonSearchBarDocumentResultsString)
            document_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon)
            for result in document_results:
                if self._max_search_item_count and count >= self._max_search_item_count:
                    break
                result_action = self._popup.addAction(document_icon, result)
                result_action.setProperty("lqRibbonSearchPopupRole", "result")
                result_action.triggered.connect(
                    lambda _checked=False, value=result: (
                        self.ribbon_bar.searchSuggestionActivated.emit(value)
                    )
                )
                count += 1

        if related_files:
            self._popup.addSection(QtnRibbonSearchBarRelatedFilesString)
            file_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon)
            for result in related_files:
                if self._max_search_item_count and count >= self._max_search_item_count:
                    break
                result_action = self._popup.addAction(file_icon, result)
                result_action.setProperty("lqRibbonSearchPopupRole", "result")
                result_action.triggered.connect(
                    lambda _checked=False, value=result: (
                        self.ribbon_bar.searchSuggestionActivated.emit(value)
                    )
                )
                count += 1

        for action in actions:
            if isinstance(action, str):
                self._popup.addSection(action)
                continue
            if self._max_search_item_count and count >= self._max_search_item_count:
                break
            self._popup.addAction(action)
            action.setProperty("lqRibbonSearchPopupRole", "action")
            count += 1
        if self._help_enabled and text:
            self._popup.addSection(QtnRibbonSearchBarHelpString)
            help_action = self._popup.addAction(f'{QtnRibbonSearchBarGetHelpString} "{text}"')
            help_action.setProperty("lqRibbonSearchPopupRole", "help")
            help_action.triggered.connect(lambda: self.show_help.emit(text))
        if not self._popup.isEmpty():
            self._popup.popup(self.mapToGlobal(QPoint(0, self.height())))
            self._set_first_popup_action()

    def closePopup(self):
        self._popup_keyboard_active = False
        self._popup.hide()

    def keyPressEvent(self, event):
        key = event.key()
        if key in (Qt.Key.Key_Down, Qt.Key.Key_Up):
            if not self._popup.isVisible() or self._popup_query != self.text():
                self.showPopup(self.text())
            if key == Qt.Key.Key_Down:
                handled = (
                    self._move_popup_selection(1)
                    if self._popup_keyboard_active
                    else self._set_first_popup_action()
                )
            else:
                handled = (
                    self._move_popup_selection(-1)
                    if self._popup_keyboard_active
                    else self._set_last_popup_action()
                )
            if handled:
                self._popup_keyboard_active = True
                event.accept()
                return
        if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter) and self._popup.isVisible():
            if self._popup_query != self.text():
                self.showPopup(self.text())
            action = self._popup.activeAction()
            if action not in self._selectable_popup_actions():
                self._set_first_popup_action()
                action = self._popup.activeAction()
            if self._activate_popup_action(action):
                event.accept()
                return
        if key == Qt.Key.Key_Escape:
            self._suppress_next_focus_popup = True
            self.closePopup()
            self._focus_without_popup()
            event.accept()
            return
        super().keyPressEvent(event)

    def focusInEvent(self, event):
        super().focusInEvent(event)
        if self._suppress_next_focus_popup:
            self._suppress_next_focus_popup = False
            return
        self.showPopup(self.text())

    def paintEvent(self, event):
        super().paintEvent(event)
        if not self._compact:
            return
        icon_size = min(16, self.width(), self.height() - 6)
        if icon_size <= 0:
            return
        painter = QPainter(self)
        icon_rect = QRect(
            (self.width() - icon_size) // 2,
            (self.height() - icon_size) // 2,
            icon_size,
            icon_size,
        )
        self._icon.paint(painter, icon_rect, Qt.AlignmentFlag.AlignCenter)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._compact:
            self.setTextMargins(self.width() + 12, 0, 0, 0)


class LqRibbonSliderPane(QWidget):
    value_changed = Signal(int)
    slider_moved = Signal(int)
    valueChanged = Signal(int)
    sliderMoved = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.decrement_button = QPushButton("-", self)
        self.increment_button = QPushButton("+", self)
        self.slider = QSlider(Qt.Orientation.Horizontal, self)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.decrement_button)
        layout.addWidget(self.slider)
        layout.addWidget(self.increment_button)
        self.decrement_button.clicked.connect(self.decrement)
        self.increment_button.clicked.connect(self.increment)
        self.slider.valueChanged.connect(self.value_changed)
        self.slider.valueChanged.connect(self.valueChanged)
        self.slider.sliderMoved.connect(self.slider_moved)
        self.slider.sliderMoved.connect(self.sliderMoved)

    def setRange(self, minimum, maximum):
        self.slider.setRange(minimum, maximum)

    def setScrollButtons(self, on):
        self.decrement_button.setVisible(on)
        self.increment_button.setVisible(on)

    def setSliderPosition(self, position):
        self.slider.setSliderPosition(position)

    def sliderPosition(self):
        return self.slider.sliderPosition()

    def setSingleStep(self, step):
        self.slider.setSingleStep(step)

    def singleStep(self):
        return self.slider.singleStep()

    def value(self):
        return self.slider.value()

    def setValue(self, value):
        self.slider.setValue(value)

    def increment(self):
        self.slider.setValue(self.slider.value() + self.slider.singleStep())

    def decrement(self):
        self.slider.setValue(self.slider.value() - self.slider.singleStep())


class LqRibbonSliderPaneControl(LqRibbonWidgetControl):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setContentWidget(LqRibbonSliderPane(parent=self))

    def widget(self):
        return super().widget()


class LqRibbonProgressBar(QProgressBar):
    def setValueSafe(self, value):
        self.setValue(value)


class LqRibbonStatusBarSwitchGroup(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

    def clear(self):
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()


class LqRibbonStatusBar(QStatusBar):
    def addPermanentAction(self, action):
        button = QToolButton(self)
        button.setDefaultAction(action)
        self.addPermanentWidget(button)

    def childrenPermanentRect(self):
        return self.rect()


class LqRibbonBackstageSeparator(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._orientation = Qt.Orientation.Horizontal
        self.setFrameShape(QFrame.Shape.HLine)

    def setOrientation(self, orientation):
        self._orientation = orientation
        self.setFrameShape(QFrame.Shape.HLine if orientation == Qt.Orientation.Horizontal else QFrame.Shape.VLine)

    def orientation(self):
        return self._orientation


class LqRibbonBackstageButton(QToolButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._tab_style = False
        self.setAutoRaise(True)
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)

    def tabStyle(self):
        return self._tab_style

    def setTabStyle(self, style):
        self._tab_style = bool(style)
        self.setCheckable(self._tab_style)


class LqRibbonBackstagePage(QWidget):
    pass


class LqRibbonBackstageView(QWidget):
    about_to_show = Signal()
    about_to_hide = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._close_prevented = False
        self._action_buttons = {}
        self._action_pages = {}
        self.menu_widget = QWidget(self)
        self.menu_layout = QVBoxLayout(self.menu_widget)
        self.stack = QStackedWidget(self)
        self.menu_widget.setFixedWidth(190)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.menu_widget)
        layout.addWidget(self.stack, 1)
        self.hide()

    def isClosePrevented(self):
        return self._close_prevented

    def setClosePrevented(self, prevent):
        self._close_prevented = bool(prevent)

    def addAction(self, *args):
        action = QAction(*args, self) if not (len(args) == 1 and isinstance(args[0], QAction)) else args[0]
        button = LqRibbonBackstageButton(self.menu_widget)
        button.setDefaultAction(action)
        self.menu_layout.addWidget(button)
        self._action_buttons[action] = button
        button.clicked.connect(lambda: None if self._close_prevented else self.hide())
        return action

    def addSeparator(self):
        separator = LqRibbonBackstageSeparator(self.menu_widget)
        self.menu_layout.addWidget(separator)
        action = QAction(self)
        action.setSeparator(True)
        return action

    def addPage(self, widget):
        action = self.addAction(widget.windowIcon(), widget.windowTitle() or widget.objectName())
        action.setCheckable(True)
        self._action_pages[action] = widget
        self.stack.addWidget(widget)
        self._action_buttons[action].setTabStyle(True)
        self._action_buttons[action].clicked.connect(lambda: self.setActivePage(widget))
        if self.stack.count() == 1:
            self.setActivePage(widget)
        return action

    def activePage(self):
        return self.stack.currentWidget()

    def setActivePage(self, widget):
        index = self.stack.indexOf(widget)
        if index >= 0:
            self.stack.setCurrentIndex(index)
            for action, page in self._action_pages.items():
                action.setChecked(page is widget)

    def actionGeometry(self, action):
        button = self._action_buttons.get(action)
        return button.geometry() if button else QRect()

    def menuGeometry(self):
        return self.menu_widget.geometry()

    def open(self):
        parent = self.parentWidget()
        if parent:
            self.setGeometry(parent.rect())
        self.about_to_show.emit()
        self.show()
        self.raise_()

    def hideEvent(self, event):
        self.about_to_hide.emit()
        super().hideEvent(event)


class LqRibbonSystemMenu(QMenu):
    def __init__(self, ribbon_bar=None):
        super().__init__(ribbon_bar)
        self.ribbon_bar = ribbon_bar
        self.popup_bar = QToolBar(self)

    def ribbonBar(self):
        return self.ribbon_bar

    def addPopupBarAction(self, action_or_text, style=Qt.ToolButtonStyle.ToolButtonTextOnly):
        action = action_or_text if isinstance(action_or_text, QAction) else QAction(action_or_text, self)
        self.popup_bar.addAction(action)
        return action

    def addPageRecentFile(self, caption):
        widget = LqRibbonPageSystemRecentFileList(caption)
        item = QWidgetAction(self)
        item.setDefaultWidget(widget)
        self.addAction(item)
        return widget

    def addPageSystemPopup(self, caption, default_action=None, split_action=False):
        popup = LqRibbonPageSystemPopup(caption, self)
        if default_action:
            popup.addAction(default_action)
        self.addMenu(popup)
        return popup

    def updateLayout(self):
        self.updateGeometry()


class LqRibbonSystemButton(QToolButton):
    def __init__(self, ribbon_bar=None):
        super().__init__(ribbon_bar)
        self._ribbon_bar = ribbon_bar
        self._backstage = None
        self._system_menu = None
        self._background_color = QColor("#2b579a")

    def ribbonBar(self):
        return self._ribbon_bar

    def backstage(self):
        return self._backstage

    def setBackstage(self, backstage):
        self._backstage = backstage

    def backgroundColor(self):
        return self._background_color

    def setBackgroundColor(self, color):
        self._background_color = QColor(color)

    def systemMenu(self):
        return self._system_menu

    def setSystemMenu(self, menu):
        self._system_menu = menu
        self.setMenu(menu)
        self.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)

    def mousePressEvent(self, event):
        if self._backstage and event.button() == Qt.MouseButton.LeftButton:
            self._backstage.open()
            return
        super().mousePressEvent(event)


class LqRibbonPageSystemRecentFileList(QWidget):
    open_recent_file = Signal(str)

    def __init__(self, caption):
        super().__init__()
        self.caption = caption
        self.files = []
        self._size = 9
        self._current_action = None

    def setSize(self, size):
        self._size = int(size)

    def getSize(self):
        return self._size

    def getCurrentAction(self):
        return self._current_action

    def updateRecentFileActions(self, files):
        self.files = list(files)[: self._size]


class LqRibbonPageSystemPopup(QMenu):
    pass


class LqOfficePopupMenu(QMenu):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._grip_visible = False

    @staticmethod
    def createPopupMenu(parent=None):
        return LqOfficePopupMenu(parent)

    def addWidget(self, widget):
        action = QWidgetAction(self)
        action.setDefaultWidget(widget)
        self.addAction(action)
        return action

    def setGripVisible(self, visible):
        self._grip_visible = bool(visible)

    def isGripVisible(self):
        return self._grip_visible


class LqPopupColorButton(QToolButton):
    color_changed = Signal(QColor)
    colorChanged = Signal(QColor)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._color = QColor("black")

    def color(self):
        return self._color

    def setColor(self, color):
        self._color = QColor(color)
        self.color_changed.emit(self._color)
        self.colorChanged.emit(self._color)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        color = QColorDialog.getColor(self._color, self)
        if color.isValid():
            self.setColor(color)


class LqOfficePopupWindow(QWidget):
    about_to_show = Signal()
    about_to_hide = Signal()

    PopupLocationNearTaskBar = 0
    PopupLocationBottomRight = 1
    PopupLocationCenter = 2
    PopupAnimationNone = 0
    PopupAnimationFade = 1
    PopupAnimationSlide = 2
    PopupAnimationUnfold = 3

    def __init__(self, parent=None):
        super().__init__(parent, Qt.WindowType.ToolTip | Qt.WindowType.FramelessWindowHint)
        self._central_widget = None
        self._title_icon = QIcon()
        self._title_text = ""
        self._body_text = ""
        self._display_time = 4000
        self._animation_speed = 120
        self._transparency = 1.0
        self._location = self.PopupLocationBottomRight
        self._animation = self.PopupAnimationFade
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.closePopup)
        self.title_label = QLabel(self)
        self.body_label = QLabel(self)
        self.close_button = QToolButton(self)
        self.close_button.setText("x")
        self.close_button.clicked.connect(self.closePopup)
        layout = QVBoxLayout(self)
        title_layout = QHBoxLayout()
        title_layout.addWidget(self.title_label, 1)
        title_layout.addWidget(self.close_button)
        layout.addLayout(title_layout)
        layout.addWidget(self.body_label)

    def showPopup(self, *args):
        if not isinstance(self, LqOfficePopupWindow):
            parent = self
            title_icon = args[0] if len(args) > 0 else QIcon()
            title_text = args[1] if len(args) > 1 else ""
            body_text = args[2] if len(args) > 2 else ""
            close_button_visible = args[3] if len(args) > 3 else True
            popup = LqOfficePopupWindow(parent)
            popup.setTitleIcon(title_icon)
            popup.setTitleText(title_text)
            popup.setBodyText(body_text)
            popup.setTitleCloseButtonVisible(close_button_visible)
            popup.showPopup()
            return popup

        pos = args[0] if args else None
        if pos is not None:
            self.move(pos)
        self.about_to_show.emit()
        self.show()
        if self._display_time > 0:
            self._timer.start(self._display_time)
        return True

    def closePopup(self):
        self.about_to_hide.emit()
        self.hide()

    def setCentralWidget(self, widget):
        self._central_widget = widget
        self.layout().addWidget(widget)

    def centralWidget(self):
        return self._central_widget

    def setBodyText(self, text):
        self._body_text = text
        self.body_label.setText(text)

    def bodyText(self):
        return self._body_text

    def setTitleIcon(self, icon):
        self._title_icon = icon

    def titleIcon(self):
        return self._title_icon

    def setTitleText(self, text):
        self._title_text = text
        self.title_label.setText(text)

    def titleText(self):
        return self._title_text

    def setTitleCloseButtonVisible(self, visible=True):
        self.close_button.setVisible(visible)

    def isTitleCloseButtonVisible(self):
        return self.close_button.isVisible()

    def setDisplayTime(self, time):
        self._display_time = int(time)

    def displayTime(self):
        return self._display_time

    def setAnimationSpeed(self, time):
        self._animation_speed = int(time)

    def animationSpeed(self):
        return self._animation_speed

    def setTransparency(self, transparency):
        self._transparency = float(transparency)
        self.setWindowOpacity(self._transparency)

    def transparency(self):
        return self._transparency


class LqRibbonScrollArea(QScrollArea):
    def viewportSizeHint(self):
        return self.viewport().sizeHint()

    def updateScrollBars(self):
        self.updateGeometry()


class LqRibbonWorkspace(LqRibbonScrollArea):
    pass


class LqRibbonMdiArea(QMdiArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setViewMode(QMdiArea.ViewMode.TabbedView)
        self.setTabsClosable(True)
        self.setTabsMovable(True)


class LqRibbonCustomizeManager:
    def __init__(self, ribbon_bar):
        self.ribbon_bar = ribbon_bar
        self._categories = {}
        self._ids = {}
        self._edit_mode = False

    def categories(self):
        return list(self._categories.keys())

    def actionsAll(self):
        actions = []
        for page in self.ribbon_bar.pages():
            for group in page.groups():
                actions.extend(group.actions())
        return actions

    def addToCategory(self, category, obj):
        self._categories.setdefault(category, []).append(obj)

    def actionsByCategory(self, category):
        return [obj for obj in self._categories.get(category, []) if isinstance(obj, QAction)]

    def setEditMode(self, enabled=True):
        self._edit_mode = bool(enabled)

    def isEditMode(self):
        return self._edit_mode

    def commit(self):
        self._edit_mode = False

    def cancel(self):
        self._edit_mode = False

    def pages(self):
        return self.ribbon_bar.pages()

    def createPage(self, page_name, index=-1):
        return self.ribbon_bar.insertPage(index, page_name)

    def deletePage(self, page):
        self.ribbon_bar.removePage(page)

    def pageIndex(self, page):
        return self.ribbon_bar.pageIndex(page)

    def movePage(self, old_index, new_index):
        self.ribbon_bar.movePage(old_index, new_index)

    def pageGroups(self, page):
        return page.groups()

    def createGroup(self, page, group_name, index=-1):
        return page.insertGroup(index, group_name)

    def deleteGroup(self, page, index):
        page.removeGroupByIndex(index)

    def moveGroup(self, page, old_index, new_index):
        group = page.group(old_index)
        if group:
            page.detachGroup(group)
            page.insertGroup(new_index, group)

    def setPageId(self, page, page_id):
        self._ids[page] = page_id

    def pageId(self, page):
        return self._ids.get(page, "")

    def setGroupId(self, group, group_id):
        self._ids[group] = group_id

    def groupId(self, group):
        return self._ids.get(group, "")

    def saveStateToDevice(self, device):
        page_titles = [str(page.title) for page in self.ribbon_bar.pages()]
        state = ("<ribbon pages=\"" + "|".join(page_titles) + "\"/>").encode("utf-8")
        if hasattr(device, "write"):
            return device.write(state) >= 0
        return False

    def loadStateFromDevice(self, device):
        if hasattr(device, "readAll"):
            device.readAll()
            return True
        if hasattr(device, "read"):
            device.read()
            return True
        return False


class LqRibbonCustomizeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.page_list = QListWidget(self)
        self.stack = QStackedWidget(self)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        self.page_list.currentRowChanged.connect(self.stack.setCurrentIndex)
        content = QHBoxLayout()
        content.addWidget(self.page_list)
        content.addWidget(self.stack, 1)
        layout = QVBoxLayout(self)
        layout.addLayout(content)
        layout.addWidget(buttons)

    def addPage(self, page):
        self.insertPage(self.stack.count(), page)

    def insertPage(self, index, page):
        self.stack.insertWidget(index, page)
        self.page_list.insertItem(index, page.windowTitle() or page.objectName())
        if self.page_list.currentRow() < 0:
            self.page_list.setCurrentRow(0)

    def indexOf(self, page):
        return self.stack.indexOf(page)

    def currentPage(self):
        return self.stack.currentWidget()

    def setCurrentPage(self, page):
        self.setCurrentPageIndex(self.indexOf(page))

    def currentPageIndex(self):
        return self.stack.currentIndex()

    def setCurrentPageIndex(self, index):
        self.page_list.setCurrentRow(index)
        self.stack.setCurrentIndex(index)

    def pageCount(self):
        return self.stack.count()

    def pageByIndex(self, index):
        return self.stack.widget(index)


class LqRibbonQuickAccessBarCustomizePage(QWidget):
    def __init__(self, ribbon_bar):
        super().__init__(ribbon_bar)
        self._ribbon_bar = ribbon_bar

    def ribbonBar(self):
        return self._ribbon_bar

    def addCustomCategory(self, category):
        pass

    def addSeparatorCategory(self, category=""):
        pass

    def accepted(self):
        pass


class LqRibbonBarCustomizePage(LqRibbonQuickAccessBarCustomizePage):
    def rejected(self):
        pass


RibbonControlSizeDefinition = LqRibbonControlSizeDefinition
RibbonControl = LqRibbonControl
RibbonWidgetControl = LqRibbonWidgetControl
RibbonLabelControl = LqRibbonLabelControl
RibbonToolBarControl = LqRibbonToolBarControl
RibbonButtonControl = LqRibbonButtonControl
RibbonCheckBoxControl = LqRibbonCheckBoxControl
RibbonRadioButtonControl = LqRibbonRadioButtonControl
RibbonFontComboBoxControl = LqRibbonFontComboBoxControl
RibbonLineEditControl = LqRibbonLineEditControl
RibbonComboBoxControl = LqRibbonComboBoxControl
RibbonSpinBoxControl = LqRibbonSpinBoxControl
RibbonDoubleSpinBoxControl = LqRibbonDoubleSpinBoxControl
RibbonSliderControl = LqRibbonSliderControl
RibbonDateTimeEditControl = LqRibbonDateTimeEditControl
RibbonTimeEditControl = LqRibbonTimeEditControl
RibbonDateEditControl = LqRibbonDateEditControl
RibbonGalleryItem = LqRibbonGalleryItem
RibbonGalleryGroup = LqRibbonGalleryGroup
RibbonGallery = LqRibbonGallery
RibbonGalleryControl = LqRibbonGalleryControl
RibbonQuickAccessBar = LqRibbonQuickAccessBar
RibbonSearchBar = LqRibbonSearchBar
RibbonSliderPane = LqRibbonSliderPane
RibbonSliderPaneControl = LqRibbonSliderPaneControl
RibbonProgressBar = LqRibbonProgressBar
RibbonStatusBarSwitchGroup = LqRibbonStatusBarSwitchGroup
RibbonStatusBar = LqRibbonStatusBar
RibbonBackstageSeparator = LqRibbonBackstageSeparator
RibbonBackstageButton = LqRibbonBackstageButton
RibbonBackstagePage = LqRibbonBackstagePage
RibbonBackstageView = LqRibbonBackstageView
RibbonSystemButton = LqRibbonSystemButton
RibbonSystemMenu = LqRibbonSystemMenu
RibbonPageSystemRecentFileList = LqRibbonPageSystemRecentFileList
RibbonPageSystemPopup = LqRibbonPageSystemPopup
OfficePopupMenu = LqOfficePopupMenu
PopupColorButton = LqPopupColorButton
OfficePopupWindow = LqOfficePopupWindow
RibbonScrollArea = LqRibbonScrollArea
RibbonWorkspace = LqRibbonWorkspace
RibbonMdiArea = LqRibbonMdiArea
RibbonCustomizeManager = LqRibbonCustomizeManager
RibbonCustomizeDialog = LqRibbonCustomizeDialog
RibbonQuickAccessBarCustomizePage = LqRibbonQuickAccessBarCustomizePage
RibbonBarCustomizePage = LqRibbonBarCustomizePage
