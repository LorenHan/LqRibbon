"""
LqRibbonButton - Ribbon button with different display styles
"""

from PySide6.QtWidgets import QToolButton, QSizePolicy
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction

from .lq_styles import LqStyle


def _tool_button_style(style):
    if isinstance(style, Qt.ToolButtonStyle):
        return style
    try:
        return Qt.ToolButtonStyle(style)
    except Exception:
        return Qt.ToolButtonStyle.ToolButtonTextUnderIcon


class LqRibbonButton(QToolButton):
    """Ribbon button that can display icon and text in different styles"""

    def __init__(self, action=None, button_style=Qt.ToolButtonStyle.ToolButtonTextUnderIcon, parent=None):
        super().__init__(parent)
        self.button_style = _tool_button_style(button_style)
        self._word_wrap = False
        self._large_icon = False
        self._simplified_mode = False
        self.init_ui()

        if action:
            self.setDefaultAction(action)

    def init_ui(self):
        """Initialize the button UI"""
        self.setMinimumSize(0, 0)
        self.setMaximumSize(16777215, 16777215)

        # Set button properties based on style
        effective_style = self._effective_button_style()
        self.setToolButtonStyle(effective_style)
        self.setProperty("simplified", "true" if self._simplified_mode else "false")

        if effective_style == Qt.ToolButtonStyle.ToolButtonTextUnderIcon:
            # Large button with icon on top and text below
            self.setProperty("buttonStyle", "0")
            self._large_icon = True
            self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
            self.setMinimumSize(LqStyle.LARGE_BUTTON_MIN_WIDTH, LqStyle.LARGE_BUTTON_MIN_HEIGHT)
            self.setMaximumHeight(LqStyle.LARGE_BUTTON_MIN_HEIGHT + 2)
            self.setIconSize(QSize(LqStyle.LARGE_ICON_SIZE, LqStyle.LARGE_ICON_SIZE))

        elif effective_style == Qt.ToolButtonStyle.ToolButtonTextBesideIcon:
            # Medium button with icon and text side by side
            self.setProperty("buttonStyle", "1")
            self._large_icon = False
            self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
            min_width = LqStyle.SIMPLIFIED_BUTTON_MIN_WIDTH if self._simplified_mode else LqStyle.SMALL_BUTTON_MIN_WIDTH
            height = LqStyle.SIMPLIFIED_BUTTON_HEIGHT if self._simplified_mode else LqStyle.SMALL_BUTTON_HEIGHT
            icon_size = LqStyle.SIMPLIFIED_ICON_SIZE if self._simplified_mode else LqStyle.SMALL_ICON_SIZE
            self.setMinimumSize(min_width, height)
            self.setMaximumHeight(height + 1)
            self.setIconSize(QSize(icon_size, icon_size))

        elif effective_style == Qt.ToolButtonStyle.ToolButtonIconOnly:
            # Icon only button
            self.setProperty("buttonStyle", "2")
            self._large_icon = False
            self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            self.setFixedSize(LqStyle.ICON_ONLY_BUTTON_SIZE, LqStyle.ICON_ONLY_BUTTON_SIZE)
            self.setIconSize(QSize(LqStyle.ICON_ONLY_ICON_SIZE, LqStyle.ICON_ONLY_ICON_SIZE))

        # Set auto raise for flat appearance
        self.setAutoRaise(True)

        # Set popup mode to instant popup if needed
        self.setPopupMode(QToolButton.ToolButtonPopupMode.DelayedPopup)
        self.updateIconSize()

    def set_button_style(self, style):
        """Change the button style

        Args:
            style: New button style (Qt.ToolButtonStyle)
        """
        self.button_style = _tool_button_style(style)
        self.init_ui()

    def set_simplified_mode(self, simplified):
        """Switch between classic and simplified ribbon presentation."""
        simplified = bool(simplified)
        if self._simplified_mode == simplified:
            return
        self._simplified_mode = simplified
        self.init_ui()

    def set_icon_size(self, size):
        """Set custom icon size

        Args:
            size: QSize object or integer for square size
        """
        if isinstance(size, int):
            size = QSize(size, size)
        self.setIconSize(size)

    def add_menu(self, menu):
        """Add a dropdown menu to the button

        Args:
            menu: QMenu to add
        """
        self.setMenu(menu)
        self.setPopupMode(QToolButton.ToolButtonPopupMode.MenuButtonPopup)

    def set_large_style(self):
        """Set button to large style with icon on top"""
        self.set_button_style(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)

    def set_medium_style(self):
        """Set button to medium style with icon beside text"""
        self.set_button_style(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)

    def set_small_style(self):
        """Set button to small style"""
        self.set_button_style(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)

    def wordWrap(self):
        """Return whether button text is allowed to wrap."""
        return self._word_wrap

    def setWordWrap(self, on):
        """Set whether button text may wrap."""
        self._word_wrap = bool(on)
        self.updateGeometry()

    def isLargeIcon(self):
        """Return whether the large icon metric is active."""
        return self._large_icon

    def setLargeIcon(self, large):
        """Use large or small icon metrics."""
        self._large_icon = bool(large)
        self.updateIconSize()

    def simplifiedMode(self):
        """Return whether simplified display is active."""
        return self._simplified_mode

    def setSimplifiedMode(self, enabled):
        """Toggle simplified icon-only display."""
        self._simplified_mode = bool(enabled)
        if enabled:
            self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        else:
            self.setToolButtonStyle(self.button_style)
        self.updateGeometry()

    def updateIconSize(self):
        """Apply icon size for the current large/small state."""
        self.setIconSize(QSize(32, 32) if self._large_icon else QSize(16, 16))

    def changed(self):
        """Refresh visual metrics after action or style changes."""
        self.updateIconSize()
        self.updateGeometry()
        self.update()


RibbonButton = LqRibbonButton
