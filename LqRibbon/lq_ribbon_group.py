"""
LqRibbonGroup - Ribbon group that contains buttons and controls
"""

from PySide6.QtWidgets import (
    QGroupBox, QHBoxLayout, QVBoxLayout, QGridLayout,
    QWidget, QSizePolicy, QMenu, QFrame, QWidgetAction,
    QLabel, QToolButton
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction, QColor, QIcon
from .lq_ribbon_extras import CallableString, CallableList


class LqRibbonGroup(QGroupBox):
    """Ribbon group that contains buttons and other controls"""

    action_triggered = Signal(str)  # Signal emitted when an action is triggered
    actionTriggered = Signal(QAction)
    released = Signal()
    hidePopup = Signal()
    titleChanged = Signal(str)
    titleFontChanged = Signal(object)

    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.title = CallableString(title)
        self.buttons = CallableList()
        self.actions = CallableList()
        self._controls = CallableList()
        self._action_widgets = {}
        self._option_button_action = None
        self._option_button_visible = False
        self._content_alignment = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop
        self._controls_alignment = self._content_alignment
        self._title_elide_mode = Qt.TextElideMode.ElideRight
        self._size_definition = 0
        self._icon = QIcon()
        self._title_color = QColor("#202020")
        self._controls_grouping = False
        self.init_ui()

    def init_ui(self):
        """Initialize the group UI"""
        super().setTitle("")
        self.setObjectName("lqRibbonGroup")

        # Set size policy
        self.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)
        self.setMinimumHeight(98)
        self.setMinimumWidth(44)

        # Create main layout
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        self.main_layout = QHBoxLayout()
        self.main_layout.setContentsMargins(4, 5, 5, 5)
        self.main_layout.setSpacing(2)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        outer_layout.addLayout(self.main_layout, 1)

        self.title_label = QLabel(str(self.title), self)
        self.title_label.setObjectName("lqRibbonGroupTitle")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setFixedHeight(17)

        self.option_button = QToolButton(self)
        self.option_button.setObjectName("lqRibbonGroupOptionButton")
        self.option_button.setAutoRaise(True)
        self.option_button.setFixedSize(16, 16)
        self.option_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.option_button.hide()

        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(4, 0, 4, 0)
        title_layout.setSpacing(2)
        title_layout.addWidget(self.title_label, 1)
        title_layout.addWidget(self.option_button)
        outer_layout.addLayout(title_layout)

        # Create grid layout for small buttons
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(2)
        self.grid_column = 0
        self.grid_row = 0

    def addAction(self, icon, text, tooltip=None, style=None):
        """Add an action button to the group (One-liner)

        Args:
            icon: QIcon or icon path string
            text: Text for the action
            tooltip: Tooltip for the action
            style: Qt.ToolButtonStyle style

        Returns:
            QAction: The created action
        """
        if isinstance(icon, QAction):
            action = icon
            button_style = text
            menu = tooltip
            mode = style
            button = self.add_action(action, button_style)
            if menu is not None and hasattr(button, "setMenu"):
                button.setMenu(menu)
                if mode is not None:
                    button.setPopupMode(mode)
            return action

        # Handle backward compatibility: if the third argument is a style
        if isinstance(tooltip, Qt.ToolButtonStyle):
            style = tooltip
            tooltip = None

        if style is None:
            style = Qt.ToolButtonStyle.ToolButtonTextUnderIcon

        if isinstance(icon, str):
            icon = QIcon(icon)

        action = QAction(icon, text, self)
        if tooltip:
            action.setToolTip(tooltip)
            
        self.add_action(action, style)
        return action

    def add_action(self, action_or_icon, text_or_style=Qt.ToolButtonStyle.ToolButtonTextUnderIcon, button_style=None, tooltip=None):
        """Add an action button to the group

        Args:
            action_or_icon: QAction object, QIcon, or icon path string
            text_or_style: Text for the button (if icon passed) or button_style (if QAction passed)
            button_style: Style of button - Qt.ToolButtonStyle
            tooltip: Tooltip for the action (if action created here)

        Returns:
            LqRibbonButton: The created button
        """
        from .lq_ribbon_button import LqRibbonButton

        # Check whether the first argument is a QAction
        if isinstance(action_or_icon, QAction):
            action = action_or_icon
            button_style = text_or_style
        else:
            # Backward-compatible call: add_action(icon, text, button_style)
            icon = action_or_icon
            text = text_or_style

            if isinstance(icon, str):
                icon = QIcon(icon)

            action = QAction(icon, text, self)

        if tooltip:
            action.setToolTip(tooltip)

        if button_style is None:
            button_style = Qt.ToolButtonStyle.ToolButtonTextUnderIcon

        action.triggered.connect(lambda checked=False, act=action: self.on_action_triggered(act))

        # Create button
        button = LqRibbonButton(action, button_style, self)
        self.buttons.append(button)
        self.actions.append(action)
        self._action_widgets[action] = button

        # Add to layout based on style
        if button_style == Qt.ToolButtonStyle.ToolButtonTextBesideIcon:
            # Add to grid layout for ToolButtonTextBesideIcon buttons - vertical arrangement (3 rows per column)
            self.grid_layout.addWidget(button, self.grid_row, self.grid_column)
            self.grid_row += 1

            # After 3 rows, move to next column
            if self.grid_row >= 3:
                self.grid_row = 0
                self.grid_column += 1

            # Ensure grid layout is added to main layout
            if self.main_layout.indexOf(self.grid_layout) == -1:
                self.main_layout.addLayout(self.grid_layout)
        else:
            # Add directly to main layout for large buttons (ToolButtonTextUnderIcon style)
            self.main_layout.addWidget(button)

        return button

    def insertAction(self, before, action, style=Qt.ToolButtonStyle.ToolButtonTextBesideIcon, menu=None, mode=None):
        """Insert an action before another action."""
        button = self.add_action(action, style)
        if menu is not None:
            button.setMenu(menu)
            button.setPopupMode(mode or button.popupMode())
        if before in self.actions:
            old_index = self.actions.index(action)
            new_index = self.actions.index(before)
            self.actions.insert(new_index, self.actions.pop(old_index))
        return action

    def add_separator(self):
        """Add a vertical separator to the group"""
        separator = QWidget()
        separator.setFixedWidth(1)
        separator.setStyleSheet("background-color: #D1D1D1;")
        self.main_layout.addWidget(separator)
        action = QAction(self)
        action.setSeparator(True)
        self.actions.append(action)
        self._action_widgets[action] = separator
        return action

    def addSeparator(self):
        return self.add_separator()

    def add_widget(self, widget):
        """Add a custom widget to the group

        Args:
            widget: The widget to add
        """
        self.main_layout.addWidget(widget)
        action = QWidgetAction(self)
        self.actions.append(action)
        self._action_widgets[action] = widget
        return action

    def addWidget(self, *args):
        """Qtitan-style widget add overload."""
        if len(args) == 1:
            return self.add_widget(args[0])
        if len(args) >= 3:
            icon, text, widget = args[0], args[1], args[-1]
            action = self.add_widget(widget)
            action.setIcon(icon if isinstance(icon, QIcon) else QIcon(icon))
            action.setText(text)
            return action
        return None

    def addMenu(self, icon, text, style=Qt.ToolButtonStyle.ToolButtonFollowStyle):
        menu = QMenu(text, self)
        action = self.addAction(icon, text, style)
        action.setMenu(menu)
        button = self._action_widgets.get(action)
        if button and hasattr(button, "setMenu"):
            button.setMenu(menu)
        return menu

    def add_layout(self, layout):
        """Add a custom layout to the group

        Args:
            layout: The layout to add
        """
        self.main_layout.addLayout(layout)

    def get_action(self, text):
        """Get an action by its text

        Args:
            text: Text of the action

        Returns:
            QAction: The action with the given text
        """
        for action in self.actions:
            if action.text() == text:
                return action
        return None

    def get_button(self, text):
        """Get a button by its text

        Args:
            text: Text of the button

        Returns:
            LqRibbonButton: The button with the given text
        """
        for button in self.buttons:
            if button.text() == text:
                return button
        return None

    def on_action_triggered(self, action):
        """Handle action trigger

        Args:
            action: Triggered action
        """
        action_text = action.text()
        self.action_triggered.emit(action_text)
        self.actionTriggered.emit(action)
        ribbon_bar = self.ribbonBar()
        if ribbon_bar and ribbon_bar.isRibbonMinimized():
            ribbon_bar.setRibbonMinimized(True)

        # Propagate to parent window
        parent = self.parent()
        while parent:
            if hasattr(parent, 'action_triggered'):
                parent.action_triggered.emit(action_text)
                break
            parent = parent.parent()

    def set_action_enabled(self, text, enabled):
        """Enable or disable an action

        Args:
            text: Text of the action
            enabled: True to enable, False to disable
        """
        action = self.get_action(text)
        if action:
            action.setEnabled(enabled)

    def clear_actions(self):
        """Remove all actions from the group"""
        for button in self.buttons:
            self.main_layout.removeWidget(button)
            button.deleteLater()
        self.buttons.clear()
        self.actions.clear()
        self._action_widgets.clear()

    def clear(self):
        self.clear_actions()

    def set_title(self, title):
        """Set the group title

        Args:
            title: New title for the group
        """
        self.title = CallableString(title)
        self.title_label.setText(title)
        self.titleChanged.emit(title)

    def setTitle(self, title):
        self.title = CallableString(title)
        self.title_label.setText(title)
        self.titleChanged.emit(title)

    def titleFont(self):
        return self.title_label.font()

    def setTitleFont(self, font):
        self.title_label.setFont(font)
        self.titleFontChanged.emit(font)

    def titleColor(self):
        return self._title_color

    def setTitleColor(self, color):
        self._title_color = color if isinstance(color, QColor) else QColor(color)
        self.title_label.setStyleSheet(f"color: {self._title_color.name()};")

    def ribbonBar(self):
        parent = self.parent()
        while parent:
            if hasattr(parent, "isRibbonMinimized") and hasattr(parent, "setRibbonMinimized"):
                return parent
            parent = parent.parent()
        return None

    def isReduced(self):
        return False

    def setIcon(self, icon):
        self._icon = icon if isinstance(icon, QIcon) else QIcon(icon)

    def icon(self):
        return self._icon

    def isOptionButtonVisible(self):
        return self._option_button_visible

    def setOptionButtonVisible(self, visible=True):
        self._option_button_visible = bool(visible)
        self.option_button.setVisible(self._option_button_visible)

    def optionButtonAction(self):
        return self._option_button_action

    def setOptionButtonAction(self, action):
        self._option_button_action = action
        if action is not None:
            self.option_button.setDefaultAction(action)
        self.setOptionButtonVisible(action is not None)

    def contentAlignment(self):
        return self._content_alignment

    def setContentAlignment(self, alignment):
        self._content_alignment = alignment
        self.main_layout.setAlignment(alignment)

    def controlsAlignment(self):
        return self._controls_alignment

    def setControlsAlignment(self, alignment):
        self._controls_alignment = alignment

    def spacing(self):
        return self.main_layout.spacing()

    def setSpacing(self, spacing):
        self.main_layout.setSpacing(spacing)

    def controlCount(self):
        return len(self._controls)

    def controlByIndex(self, index):
        return self._controls[index] if 0 <= index < len(self._controls) else None

    def controlByAction(self, action):
        return self._action_widgets.get(action)

    def controlByWidget(self, widget):
        return widget if widget in self._controls else None

    def addControl(self, control):
        if control not in self._controls:
            self._controls.append(control)
            self.add_widget(control)

    def removeControl(self, control):
        if control in self._controls:
            self._controls.remove(control)
            self.remove(control)

    def remove(self, widget):
        self.main_layout.removeWidget(widget)
        if widget in self.buttons:
            self.buttons.remove(widget)
        for action, action_widget in list(self._action_widgets.items()):
            if action_widget is widget:
                self._action_widgets.pop(action, None)
                if action in self.actions:
                    self.actions.remove(action)
        widget.deleteLater()

    def titleElideMode(self):
        return self._title_elide_mode

    def setTitleElideMode(self, mode):
        self._title_elide_mode = mode

    def sizeDefinition(self):
        return self._size_definition

    def setSizeDefinition(self, definition):
        self._size_definition = definition

    def setControlsCentering(self, enabled=True):
        self.setContentAlignment(Qt.AlignmentFlag.AlignCenter if enabled else Qt.AlignmentFlag.AlignLeft)

    def isControlsCentering(self):
        return bool(self._content_alignment & Qt.AlignmentFlag.AlignHCenter)

    def setControlsGrouping(self, enabled=True):
        self._controls_grouping = bool(enabled)

    def isControlsGrouping(self):
        return self._controls_grouping


RibbonGroup = LqRibbonGroup
