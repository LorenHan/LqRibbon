"""
LqRibbonWindow - Main window class with ribbon interface
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QStatusBar
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon
from shiboken6 import isValid as _qt_object_is_valid

from .lq_ribbon_bar import LqRibbonBar
from .lq_styles import LqStyle, _coerce_style


class LqRibbonWindow(QMainWindow):
    """Main window with ribbon interface"""

    action_triggered = Signal(str)  # Signal emitted when an action is triggered

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.apply_styles()

    def init_ui(self):
        """Initialize the UI components"""
        # Set window properties
        self.setWindowTitle("LqRibbon Application")
        self.setGeometry(100, 100, 1200, 700)

        # Use default title bar (remove frameless window)
        # self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        # Create central widget
        central_widget = QWidget()
        self._root_widget = central_widget
        QMainWindow.setCentralWidget(self, central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self._root_layout = main_layout

        # Don't create custom title bar
        # self.title_bar = self.create_title_bar()
        # main_layout.addWidget(self.title_bar)

        # Create ribbon bar
        self.ribbon_bar = LqRibbonBar(self)
        main_layout.addWidget(self.ribbon_bar)

        # Create display area
        self.display_area = QTextEdit()
        self.display_area.setObjectName("display_area")
        self.display_area.setReadOnly(True)
        self.display_area.setPlaceholderText("Click any action button to see its name here...")
        main_layout.addWidget(self.display_area, 1)
        self._content_widget = self.display_area

        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

        # Connect signals
        self.action_triggered.connect(self.on_action_triggered)

    def create_title_bar(self):
        """Create custom title bar"""
        title_bar = QWidget()
        title_bar.setObjectName("title_bar")
        title_bar.setFixedHeight(35)

        layout = QHBoxLayout(title_bar)
        layout.setContentsMargins(5, 0, 5, 0)
        layout.setSpacing(5)

        # Application icon and title
        self.title_label = QLabel("LqRibbon")
        self.title_label.setObjectName("title_label")
        layout.addWidget(self.title_label)

        # Search box
        self.search_box = QLineEdit()
        self.search_box.setObjectName("search_box")
        self.search_box.setPlaceholderText("Search")
        layout.addWidget(self.search_box)

        # Spacer
        layout.addStretch()

        # Window control buttons
        self.min_button = QPushButton("—")
        self.min_button.setObjectName("window_button")
        self.min_button.clicked.connect(self.showMinimized)
        layout.addWidget(self.min_button)

        self.max_button = QPushButton("□")
        self.max_button.setObjectName("window_button")
        self.max_button.clicked.connect(self.toggle_maximize)
        layout.addWidget(self.max_button)

        self.close_button = QPushButton("✕")
        self.close_button.setObjectName("close_button")
        self.close_button.clicked.connect(self.close)
        layout.addWidget(self.close_button)

        return title_bar

    def toggle_maximize(self):
        """Toggle between maximized and normal window state"""
        if self.isMaximized():
            self.showNormal()
            self.max_button.setText("□")
        else:
            self.showMaximized()
            self.max_button.setText("◱")


    def apply_styles(self):
        """Apply the active Ribbon style."""
        self.setStyleSheet(LqStyle.get_full_style(self.ribbon_bar.ribbonStyle()))

    def on_action_triggered(self, action_name):
        """Handle action trigger and display in the main area"""
        message = f"Action triggered: {action_name}"
        display_area = getattr(self, "display_area", None)
        if display_area is not None and _qt_object_is_valid(display_area):
            display_area.append(message)
        status_bar = getattr(self, "status_bar", None)
        if status_bar is not None and _qt_object_is_valid(status_bar):
            status_bar.showMessage(f"Executed: {action_name}", 3000)

    def get_ribbon_bar(self):
        """Get the ribbon bar instance"""
        return self.ribbon_bar

    def ribbonBar(self):
        """Qtitan/C++ compatible ribbon bar getter."""
        return self.ribbon_bar

    def setRibbonBar(self, ribbon_bar):
        """Replace the current ribbon bar."""
        if ribbon_bar is self.ribbon_bar:
            return
        parent_layout = self._root_layout
        parent_layout.removeWidget(self.ribbon_bar)
        self.ribbon_bar.deleteLater()
        self.ribbon_bar = ribbon_bar
        parent_layout.insertWidget(0, self.ribbon_bar)

    def setCentralWidget(self, widget):
        """Set the content widget below the Ribbon, matching C++ RibbonMainWindow."""
        if not hasattr(self, "_root_layout"):
            QMainWindow.setCentralWidget(self, widget)
            return
        if widget is self._content_widget:
            return
        if self._content_widget is not None:
            self._root_layout.removeWidget(self._content_widget)
            self._content_widget.setParent(None)
        self._content_widget = widget
        self._root_layout.addWidget(widget, 1)

    def centralWidget(self):
        """Return the content widget below the Ribbon."""
        return getattr(self, "_content_widget", QMainWindow.centralWidget(self))

    def setFrameThemeEnabled(self, enabled):
        self.ribbon_bar.setFrameThemeEnabled(enabled)

    def isFrameThemeEnabled(self):
        return self.ribbon_bar.isFrameThemeEnabled()

    def setRibbonStyle(self, style):
        style = _coerce_style(style)
        self.ribbon_bar.setRibbonStyle(style)
        self.apply_styles()

    def ribbonStyle(self):
        return self.ribbon_bar.ribbonStyle()

    def setNativeFrameEnabled(self, enabled):
        self._native_frame_enabled = bool(enabled)

    def isNativeFrameEnabled(self):
        return getattr(self, "_native_frame_enabled", False)

    def setNativeCaptionHeight(self, height):
        self._native_caption_height = int(height)

    def nativeCaptionHeight(self):
        return getattr(self, "_native_caption_height", 36)

    def setNativeResizeBorderWidth(self, width):
        self._native_resize_border_width = int(width)

    def nativeResizeBorderWidth(self):
        return getattr(self, "_native_resize_border_width", 5)

    def set_display_text(self, text):
        """Set text in the display area"""
        self.display_area.setPlainText(text)

    def append_display_text(self, text):
        """Append text to the display area"""
        self.display_area.append(text)


RibbonMainWindow = LqRibbonWindow
RibbonWindow = LqRibbonWindow
