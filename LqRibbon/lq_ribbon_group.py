"""
LqRibbonGroup - Ribbon group that contains buttons and controls
"""

from PySide6.QtWidgets import (
    QGroupBox, QHBoxLayout, QVBoxLayout, QGridLayout,
    QWidget, QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction, QIcon


class LqRibbonGroup(QGroupBox):
    """Ribbon group that contains buttons and other controls"""

    action_triggered = Signal(str)  # Signal emitted when an action is triggered

    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.title = title
        self.buttons = []
        self.actions = []
        self.init_ui()

    def init_ui(self):
        """Initialize the group UI"""
        # Set size policy
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.setMinimumHeight(92)
        self.setMinimumWidth(80)

        # Create main layout
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(3, 2, 3, 6) # set the margins for the group box 
        self.main_layout.setSpacing(1)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        # Create grid layout for small buttons
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(2)
        self.grid_column = 0
        self.grid_row = 0

    def add_action(self, action_or_icon, text_or_style="icon_text", button_style=None):
        """Add an action button to the group

        Args:
            action_or_icon: QAction object, QIcon, or icon path string
            text_or_style: Text for the button (if icon passed) or button_style (if QAction passed)
            button_style: Style of button - "icon_text", "text_beside" (only when icon passed)

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
            if button_style is None:
                button_style = "icon_text"

            if isinstance(icon, str):
                icon = QIcon(icon)

            action = QAction(icon, text, self)

        action.triggered.connect(lambda: self.on_action_triggered(action.text()))

        # Create button
        button = LqRibbonButton(action, button_style, self)
        self.buttons.append(button)
        self.actions.append(action)

        # Add to layout based on style
        if button_style == "text_beside":
            # Add to grid layout for text_beside buttons - vertical arrangement (3 rows per column)
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
            # Add directly to main layout for large buttons (icon_text style)
            self.main_layout.addWidget(button)

        return button

    def add_separator(self):
        """Add a vertical separator to the group"""
        separator = QWidget()
        separator.setFixedWidth(1)
        separator.setStyleSheet("background-color: #D1D1D1;")
        self.main_layout.addWidget(separator)

    def add_widget(self, widget):
        """Add a custom widget to the group

        Args:
            widget: The widget to add
        """
        self.main_layout.addWidget(widget)

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

    def on_action_triggered(self, action_text):
        """Handle action trigger

        Args:
            action_text: Text of the triggered action
        """
        self.action_triggered.emit(action_text)

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

    def set_title(self, title):
        """Set the group title

        Args:
            title: New title for the group
        """
        self.title = title
        self.setTitle(title)