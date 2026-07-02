"""
LqRibbonWindow - Main window class with ribbon interface
"""

import ctypes
import os
import sys
import time
from ctypes import wintypes

from PySide6.QtCore import QFile, QObject, QEasingCurve, QEvent, QPoint, QPropertyAnimation, QRect, QSize, Qt, QTimer, Signal
from PySide6.QtGui import QAction, QColor, QCursor, QPainter, QPen
from PySide6.QtWidgets import (
    QApplication,
    QAbstractButton,
    QLabel,
    QHBoxLayout,
    QMainWindow,
    QMenu,
    QSizePolicy,
    QStatusBar,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from .lq_ribbon_bar import LqRibbonBar
from .lq_styles import LqStyle


IS_WINDOWS = sys.platform == "win32"
IS_MACOS = sys.platform == "darwin"

WM_NCHITTEST = 0x0084
WM_NCCALCSIZE = 0x0083
WM_NCLBUTTONDOWN = 0x00A1
WM_NCLBUTTONUP = 0x00A2
WM_NCLBUTTONDBLCLK = 0x00A3
WM_NCRBUTTONUP = 0x00A5
WM_LBUTTONDBLCLK = 0x0203
GWL_STYLE = -16
SWP_NOSIZE = 0x0001
SWP_NOMOVE = 0x0002
SWP_NOZORDER = 0x0004
SWP_FRAMECHANGED = 0x0020
WVR_REDRAW = 0x0300
HTCLIENT = 1
HTCAPTION = 2
HTMINBUTTON = 8
HTMAXBUTTON = 9
HTLEFT = 10
HTRIGHT = 11
HTTOP = 12
HTTOPLEFT = 13
HTTOPRIGHT = 14
HTBOTTOM = 15
HTBOTTOMLEFT = 16
HTBOTTOMRIGHT = 17
HTCLOSE = 20
WS_SYSMENU = 0x00080000
WS_CAPTION = 0x00C00000
WS_THICKFRAME = 0x00040000
WS_MINIMIZEBOX = 0x00020000
WS_MAXIMIZEBOX = 0x00010000
SW_SHOWNORMAL = 1
SW_MAXIMIZE = 3
SW_RESTORE = 9
MONITOR_DEFAULTTONEAREST = 2
SM_CXSIZEFRAME = 32
SM_CYSIZEFRAME = 33
SM_CXPADDEDBORDER = 92
SM_CXDOUBLECLK = 36
SM_CYDOUBLECLK = 37
ABM_GETSTATE = 0x00000004
ABM_GETAUTOHIDEBAREX = 0x0000000B
ABS_AUTOHIDE = 0x00000001
ABE_LEFT = 0
ABE_TOP = 1
ABE_RIGHT = 2
ABE_BOTTOM = 3
AUTO_HIDE_TASKBAR_THICKNESS = 2


class NCCALCSIZE_PARAMS(ctypes.Structure):
    _fields_ = [
        ("rgrc", wintypes.RECT * 3),
        ("lppos", ctypes.c_void_p),
    ]


class WINDOWPLACEMENT(ctypes.Structure):
    _fields_ = [
        ("length", wintypes.UINT),
        ("flags", wintypes.UINT),
        ("showCmd", wintypes.UINT),
        ("ptMinPosition", wintypes.POINT),
        ("ptMaxPosition", wintypes.POINT),
        ("rcNormalPosition", wintypes.RECT),
    ]


class MONITORINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD),
        ("rcMonitor", wintypes.RECT),
        ("rcWork", wintypes.RECT),
        ("dwFlags", wintypes.DWORD),
    ]


class APPBARDATA(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD),
        ("hWnd", wintypes.HWND),
        ("uCallbackMessage", wintypes.UINT),
        ("uEdge", wintypes.UINT),
        ("rc", wintypes.RECT),
        ("lParam", wintypes.LPARAM),
    ]


class LqWindowButton(QAbstractButton):
    """Painted vector window button for frameless title bars."""

    MINIMIZE = "minimize"
    MAXIMIZE = "maximize"
    RESTORE = "restore"
    CLOSE = "close"

    def __init__(self, button_type, parent=None, macos=False):
        super().__init__(parent)
        self.button_type = button_type
        self._macos = macos
        self._active = True
        self.setObjectName("close_button" if button_type == self.CLOSE else "window_button")
        self.setToolTip(self._tooltip_for(button_type))
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setCursor(Qt.CursorShape.ArrowCursor)

        if macos:
            self.setFixedSize(24, 34)
        else:
            self.setFixedSize(46, 34)

    def set_button_type(self, button_type):
        self.button_type = button_type
        self.setToolTip(self._tooltip_for(button_type))
        self.update()

    def set_active(self, active):
        self._active = active
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        if self._macos:
            self._paint_macos_button(painter)
        else:
            self._paint_windows_button(painter)

    def _paint_windows_button(self, painter):
        if self.isDown():
            background = QColor("#234A83")
            if self.button_type == self.CLOSE:
                background = QColor("#A4261A")
            painter.fillRect(self.rect(), background)
        elif self.underMouse():
            background = QColor("#3A6AB1")
            if self.button_type == self.CLOSE:
                background = QColor("#C42B1C")
            painter.fillRect(self.rect(), background)

        color = QColor("#FFFFFF" if self._active else "#E5E7EB")
        pen = QPen(color, 1.6)
        pen.setCapStyle(Qt.PenCapStyle.SquareCap)
        pen.setJoinStyle(Qt.PenJoinStyle.MiterJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        center = self.rect().center()
        if self.button_type == self.MINIMIZE:
            painter.drawLine(center.x() - 5, center.y() + 4, center.x() + 5, center.y() + 4)
        elif self.button_type == self.MAXIMIZE:
            painter.drawRect(QRect(center.x() - 5, center.y() - 5, 10, 10))
        elif self.button_type == self.RESTORE:
            painter.drawRect(QRect(center.x() - 6, center.y() - 2, 8, 8))
            painter.drawLine(center.x() - 3, center.y() - 5, center.x() + 6, center.y() - 5)
            painter.drawLine(center.x() + 6, center.y() - 5, center.x() + 6, center.y() + 4)
            painter.drawLine(center.x() + 2, center.y() - 2, center.x() + 6, center.y() - 2)
        elif self.button_type == self.CLOSE:
            painter.drawLine(center.x() - 5, center.y() - 5, center.x() + 5, center.y() + 5)
            painter.drawLine(center.x() + 5, center.y() - 5, center.x() - 5, center.y() + 5)

    def _paint_macos_button(self, painter):
        colors = {
            self.CLOSE: QColor("#FF5F57"),
            self.MINIMIZE: QColor("#FFBD2E"),
            self.MAXIMIZE: QColor("#28C840"),
            self.RESTORE: QColor("#28C840"),
        }
        center = self.rect().center()
        fill = colors[self.button_type] if self._active else QColor("#9CA3AF")

        painter.setPen(QPen(QColor(0, 0, 0, 45), 1))
        painter.setBrush(fill)
        painter.drawEllipse(center, 6, 6)

        if not self.underMouse() and not self.isDown():
            return

        painter.setPen(QPen(QColor("#4B5563"), 1.3))
        if self.button_type == self.CLOSE:
            painter.drawLine(center.x() - 3, center.y() - 3, center.x() + 3, center.y() + 3)
            painter.drawLine(center.x() + 3, center.y() - 3, center.x() - 3, center.y() + 3)
        elif self.button_type == self.MINIMIZE:
            painter.drawLine(center.x() - 3, center.y(), center.x() + 3, center.y())
        else:
            painter.drawLine(center.x() - 3, center.y() + 2, center.x() + 2, center.y() + 2)
            painter.drawLine(center.x() + 2, center.y() + 2, center.x() + 2, center.y() - 3)

    def _tooltip_for(self, button_type):
        return {
            self.MINIMIZE: "Minimize",
            self.MAXIMIZE: "Maximize",
            self.RESTORE: "Restore",
            self.CLOSE: "Close",
        }[button_type]


class LqTitleBar(QWidget):
    """Cross-platform title bar used by frameless ribbon windows."""

    def __init__(self, window):
        super().__init__(window)
        self._window = window
        self._drag_position = None
        self._drag_start_pos = QPoint()
        self._drag_restore_ratio = 0.5
        self._system_move_started = False
        self._restore_drag_threshold = 6

        self.setObjectName("title_bar")
        self.setProperty("active", True)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setFixedHeight(34)
        self.setMouseTracking(True)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 0, 0)
        layout.setSpacing(0)

        self.title_label = QLabel(window.windowTitle() or "LqRibbon")
        self.title_label.setObjectName("title_label")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.title_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.title_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

        self.min_button = LqWindowButton(LqWindowButton.MINIMIZE, self, macos=IS_MACOS)
        self.min_button.clicked.connect(window._minimize_window)

        self.max_button = LqWindowButton(LqWindowButton.MAXIMIZE, self, macos=IS_MACOS)
        self.max_button.clicked.connect(window.toggle_maximize)

        self.close_button = LqWindowButton(LqWindowButton.CLOSE, self, macos=IS_MACOS)
        self.close_button.clicked.connect(window.close)

        if IS_MACOS:
            layout.setContentsMargins(8, 0, 10, 0)
            layout.addWidget(self.close_button)
            layout.addWidget(self.min_button)
            layout.addWidget(self.max_button)
            layout.addSpacing(8)
            layout.addWidget(self.title_label, 1)
        else:
            layout.addWidget(self.title_label, 1)
            layout.addWidget(self.min_button)
            layout.addWidget(self.max_button)
            layout.addWidget(self.close_button)

        window.windowTitleChanged.connect(self.title_label.setText)

    def set_active(self, active):
        self.setProperty("active", active)
        for button in (self.min_button, self.max_button, self.close_button):
            button.set_active(active)
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_position = event.globalPosition().toPoint() - self._window.frameGeometry().topLeft()
            self._drag_start_pos = event.globalPosition().toPoint()
            self._drag_restore_ratio = event.position().x() / max(1, self.width())
            self._system_move_started = False
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.MouseButton.LeftButton) or self._drag_position is None:
            super().mouseMoveEvent(event)
            return

        if self._system_move_started:
            event.accept()
            return

        global_pos = event.globalPosition().toPoint()
        if not self._window.isMaximized() and not self._window.isFullScreen():
            if (global_pos - self._drag_start_pos).manhattanLength() >= self._restore_drag_threshold:
                self._system_move_started = self._try_start_system_move()
                if self._system_move_started:
                    event.accept()
                    return

        if self._window.isMaximized():
            if (global_pos - self._drag_start_pos).manhattanLength() < self._restore_drag_threshold:
                event.accept()
                return
            self._restore_for_drag(global_pos, int(event.position().y()))
            if self._system_move_started:
                event.accept()
                return

        self._window.move(global_pos - self._drag_position)
        event.accept()

    def mouseReleaseEvent(self, event):
        if (
            event.button() == Qt.MouseButton.LeftButton
            and not self._system_move_started
            and not self._window.isMaximized()
            and not self._window.isFullScreen()
        ):
            self._window.snap_to_screen_edge(event.globalPosition().toPoint())

        self._drag_position = None
        self._system_move_started = False
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._window._debug("titlebar mouseDoubleClickEvent")
            self._window.toggle_maximize()
            event.accept()
            return
        super().mouseDoubleClickEvent(event)

    def contextMenuEvent(self, event):
        self._window.show_window_menu(event.globalPos())

    def update_maximize_icon(self):
        button_type = LqWindowButton.RESTORE if self._window.isMaximized() else LqWindowButton.MAXIMIZE
        self.max_button.set_button_type(button_type)

    def button_global_rect(self, button):
        top_left = button.mapToGlobal(QPoint(0, 0))
        return QRect(top_left, button.size())

    def _try_start_system_move(self):
        window_handle = self._window.windowHandle()
        return bool(window_handle and window_handle.startSystemMove())

    def _restore_for_drag(self, global_pos, local_y):
        normal_geometry = QRect(self._window._last_normal_geometry)
        if normal_geometry.isNull() or not normal_geometry.isValid():
            normal_geometry = self._window.normalGeometry()
        if normal_geometry.isNull() or not normal_geometry.isValid():
            current = self._window.geometry()
            normal_geometry = QRect(
                current.topLeft(),
                QSize(
                    max(self._window.minimumWidth(), min(current.width(), 1200)),
                    max(self._window.minimumHeight(), min(current.height(), 700)),
                ),
            )

        screen_geometry = self._window._available_geometry_for_point(global_pos)
        width = self._window._bounded_width(normal_geometry.width(), screen_geometry)
        height = self._window._bounded_height(normal_geometry.height(), screen_geometry)
        x = global_pos.x() - int(width * self._drag_restore_ratio)
        y = global_pos.y() - max(8, min(local_y, self.height() // 2))
        target_geometry = self._window._fit_geometry_to_screen(QRect(x, y, width, height), screen_geometry)

        self._window._debug(f"drag restore target={target_geometry}")
        if IS_WINDOWS:
            restore_token = self._window._begin_restore_request()
            self._window._restore_windows_window(target_geometry)
            self._window._restore_to_target_later(target_geometry, restore_token)
        else:
            self._window.showNormal()
            self._window.setGeometry(target_geometry)
        self._window._update_maximize_icon()
        self._drag_position = global_pos - self._window.frameGeometry().topLeft()
        self._system_move_started = self._try_start_system_move()


class LqRibbonWindow(QMainWindow):
    """Main window with ribbon interface."""

    action_triggered = Signal(str)  # Signal emitted when an action is triggered

    def __init__(self, parent=None, frameless=True, ui_file=None, default_content=True):
        super().__init__(parent)
        self._frameless = frameless
        self._default_content = default_content
        self._lq_shell_ready = False
        self._lq_root_widget = None
        self._lq_main_layout = None
        self._content_widget = None
        self._resize_margin = 8 if IS_WINDOWS else 6
        self._resizing_edges = Qt.Edge(0)
        self._resize_start_pos = QPoint()
        self._resize_start_geometry = QRect()
        self._native_pressed_button = None
        self._native_pressed_hit = None
        self._window_animation = None
        self._animation_duration = 140
        self._last_normal_geometry = QRect()
        self._windows_styles_applied = False
        self._windows_screen_changed_connected = False
        self._last_caption_click_time = 0.0
        self._last_caption_click_pos = QPoint()
        self._skip_caption_dblclk_until = 0.0
        self._frameless_debug = os.environ.get("LQRIBBON_FRAMELESS_DEBUG", "").lower() in {"1", "true", "yes", "on"}
        self._was_maximized = False
        self._restore_generation = 0
        self.init_ui()
        if ui_file:
            self.load_ui(ui_file)
        self.apply_styles()

    def _debug(self, message):
        if not self._frameless_debug:
            return
        window_state = self.windowState()
        try:
            state_value = int(window_state)
        except TypeError:
            state_value = int(window_state.value)
        print(
            "[LqFrameless] "
            f"{message} | maximized={self.isMaximized()} minimized={self.isMinimized()} "
            f"fullscreen={self.isFullScreen()} state={state_value} "
            f"geo={self.geometry()} frame={self.frameGeometry()} "
            f"normal={self.normalGeometry()} saved={self._last_normal_geometry}",
            flush=True,
        )

    def _begin_restore_request(self):
        self._restore_generation += 1
        return self._restore_generation

    def _cancel_restore_request(self):
        self._restore_generation += 1

    def init_ui(self):
        """Initialize the UI components."""
        self.setWindowTitle("LqRibbon Application")
        self.setGeometry(100, 100, 1200, 700)
        self.setMinimumSize(720, 420)

        if self._frameless:
            self.setWindowFlag(Qt.WindowType.FramelessWindowHint, True)
            self.setMouseTracking(True)

        central_widget = QWidget()
        central_widget.setObjectName("lq_ribbon_root")
        central_widget.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        central_widget.setMouseTracking(True)
        self._lq_root_widget = central_widget
        super().setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self._lq_main_layout = main_layout

        if self._frameless:
            self.title_bar = LqTitleBar(self)
            main_layout.addWidget(self.title_bar)
            app = QApplication.instance()
            if app and not IS_WINDOWS:
                app.installEventFilter(self)
        else:
            self.title_bar = None

        self.ribbon_bar = LqRibbonBar(self)
        main_layout.addWidget(self.ribbon_bar)

        self.display_area = None
        if self._default_content:
            self.display_area = QTextEdit()
            self.display_area.setObjectName("display_area")
            self.display_area.setReadOnly(True)
            self.display_area.setPlaceholderText("Click any action button to see its name here...")
            self.set_content_widget(self.display_area)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

        self.action_triggered.connect(self.on_action_triggered)
        self._lq_shell_ready = True

    def setCentralWidget(self, widget):
        """Route application content into the ribbon shell after initialization.

        This keeps Qt Designer generated ``setupUi(self)`` calls usable: when the
        generated code calls ``setCentralWidget()``, the widget becomes the area
        below the ribbon instead of replacing the title bar and ribbon shell.
        """
        if self._lq_shell_ready and widget is not self._lq_root_widget:
            self.set_content_widget(widget)
            return
        super().setCentralWidget(widget)

    def set_content_widget(self, widget, stretch=1):
        """Set the widget shown below the ribbon bar."""
        if widget is None:
            return None

        previous = self._content_widget
        if previous is widget:
            return widget

        if previous is not None:
            self._lq_main_layout.removeWidget(previous)
            previous.setParent(None)
            if previous.objectName() == "display_area":
                previous.deleteLater()
                if self.display_area is previous:
                    self.display_area = None

        widget.setParent(self._lq_root_widget)
        widget.setMouseTracking(True)
        self._lq_main_layout.addWidget(widget, stretch)
        self._content_widget = widget
        return widget

    def set_display_widget(self, widget):
        """Set the widget used by display helper methods."""
        self.display_area = widget
        return widget

    def load_ui(self, ui_file):
        """Load a Qt Designer ``.ui`` file into the ribbon window.

        The loaded central widget is installed below the ribbon, and named child
        objects are exposed as attributes on the window for concise business code.
        """
        try:
            from PySide6.QtUiTools import QUiLoader
        except ImportError as exc:
            raise RuntimeError("PySide6.QtUiTools is required to load .ui files at runtime") from exc

        file = QFile(str(ui_file))
        if not file.open(QFile.OpenModeFlag.ReadOnly):
            raise OSError(f"Unable to open UI file: {ui_file}")

        loader = QUiLoader()
        try:
            loaded = loader.load(file)
        except RuntimeError as exc:
            error = loader.errorString()
            raise RuntimeError(f"Unable to load UI file: {ui_file}: {error}") from exc
        finally:
            file.close()

        if loaded is None:
            raise RuntimeError(f"Unable to load UI file: {ui_file}: {loader.errorString()}")

        self._apply_loaded_ui(loaded)
        loaded.deleteLater()
        return self._content_widget

    def _apply_loaded_ui(self, loaded):
        if loaded.windowTitle():
            self.setWindowTitle(loaded.windowTitle())
        if loaded.size().isValid():
            self.resize(loaded.size())
        if loaded.minimumSize().isValid():
            self.setMinimumSize(loaded.minimumSize())

        if isinstance(loaded, QMainWindow):
            content = loaded.takeCentralWidget()
            if content is not None:
                self.set_content_widget(content)

            menu_bar = loaded.menuBar()
            if menu_bar is not None and menu_bar.actions():
                menu_bar.setParent(None)
                self.setMenuBar(menu_bar)

            status_bar = loaded.statusBar()
            if status_bar is not None:
                status_bar.setParent(None)
                self.setStatusBar(status_bar)
                self.status_bar = status_bar
        else:
            self.set_content_widget(loaded)

        self._bind_named_ui_objects(self._content_widget)
        if hasattr(self, "outputTextEdit"):
            self.set_display_widget(self.outputTextEdit)

    def _bind_named_ui_objects(self, root):
        if root is None:
            return

        for obj in [root, *root.findChildren(QObject)]:
            name = obj.objectName()
            if name and not hasattr(self, name):
                setattr(self, name, obj)

    def add_ribbon_page(self, title):
        """Create or return a ribbon page by title."""
        return self.ribbon_bar.page(title)

    def add_ribbon_group(self, page_title, group_title):
        """Create or return a ribbon group by page and group title."""
        return self.ribbon_bar.group(page_title, group_title)

    def add_ribbon_action(self, page_title, group_title, text, triggered=None, icon=None, tooltip=None, style=None):
        """Create an action, creating the target page and group if needed."""
        return self.ribbon_bar.action(page_title, group_title, text, triggered, icon, tooltip, style)

    def add_ribbon_actions(self, page_title, group_title, actions, icon=None, style=None):
        """Create multiple actions in the same page and group."""
        return self.ribbon_bar.actions(page_title, group_title, actions, icon, style)

    def showEvent(self, event):
        super().showEvent(event)
        if IS_WINDOWS and self._frameless and not self._windows_styles_applied:
            self._apply_windows_native_window_styles()
            self._connect_windows_screen_changed()
            self._windows_styles_applied = True

    def nativeEvent(self, event_type, message):
        """Use native hit testing on Windows for snap and resize parity."""
        if IS_WINDOWS and self._frameless:
            try:
                msg = wintypes.MSG.from_address(int(message))
            except (TypeError, ValueError):
                return super().nativeEvent(event_type, message)

            hit_code = int(msg.wParam)

            if msg.message == WM_NCCALCSIZE:
                return self._handle_windows_nc_calc_size(msg)

            if msg.message == WM_NCHITTEST:
                hit = self._windows_hit_test(msg.hWnd)
                if hit is not None:
                    return True, hit

            if msg.message == WM_LBUTTONDBLCLK:
                local_pos = self._windows_cursor_pos_to_local(msg.hWnd)
                if self._local_pos_in_title_bar(local_pos) and not self._local_pos_in_title_bar_button(local_pos):
                    self._debug(f"native WM_LBUTTONDBLCLK local={local_pos}")
                    self.toggle_maximize()
                    return True, 0

            if msg.message == WM_NCLBUTTONDOWN and hit_code in (HTMINBUTTON, HTMAXBUTTON, HTCLOSE):
                self._activate_windows_button_hit(hit_code)
                return True, 0

            if msg.message == WM_NCLBUTTONDOWN and self._native_caption_hit(msg, hit_code):
                if self._caption_click_is_double_click(QCursor.pos()):
                    self._debug(f"native WM_NCLBUTTONDOWN detected double click hit={hit_code}")
                    self.toggle_maximize()
                    self._skip_caption_dblclk_until = time.monotonic() + 0.3
                    return True, 0

            if msg.message == WM_NCLBUTTONDBLCLK and self._native_caption_hit(msg, hit_code):
                if time.monotonic() <= self._skip_caption_dblclk_until:
                    self._debug(f"native WM_NCLBUTTONDBLCLK skipped hit={hit_code}")
                    return True, 0
                self._debug(f"native WM_NCLBUTTONDBLCLK hit={hit_code}")
                self.toggle_maximize()
                return True, 0

            if msg.message == WM_NCRBUTTONUP and self._native_caption_hit(msg, hit_code):
                self.show_window_menu(QCursor.pos())
                return True, 0

        return super().nativeEvent(event_type, message)

    def toggle_maximize(self):
        """Toggle between maximized and normal window state."""
        self._debug("toggle_maximize before")
        if self.isMaximized():
            self._restore_window(animated=True)
        else:
            self._maximize_window(animated=True)
        self._debug("toggle_maximize after")

    def _minimize_window(self):
        self._cancel_restore_request()
        self.showMinimized()

    def _maximize_window(self, animated=True):
        if self.isMaximized() or self.isFullScreen():
            return

        self._cancel_restore_request()
        self._remember_normal_geometry(self.geometry())
        self._debug("maximize before")
        if IS_WINDOWS:
            self.showMaximized()
            self._update_maximize_icon()
            self._debug("maximize after showMaximized")
            return

        target = self._available_geometry_for_window()

        def finish():
            self.showMaximized()
            self._update_maximize_icon()

        if animated:
            self._animate_geometry_to(target, finish)
        else:
            finish()

    def _restore_window(self, animated=True):
        if not self.isMaximized():
            return

        target = QRect(self._last_normal_geometry)
        if target.isNull() or not target.isValid():
            target = self.normalGeometry()
        if target.isNull() or not target.isValid():
            target = QRect(100, 100, 1200, 700)
        target = self._fit_geometry_to_screen(target, self._available_geometry_for_geometry(target))
        self._debug(f"restore target={target}")

        if IS_WINDOWS:
            restore_token = self._begin_restore_request()
            self._restore_windows_window(target)
            self._restore_to_target_later(target, restore_token)
            self._update_maximize_icon()
            self._debug("restore after win32 restore request")
            return

        start = QRect(self.geometry())
        self.showNormal()
        self.setGeometry(start)

        def finish():
            self.setGeometry(target)
            self._update_maximize_icon()

        if animated:
            self._animate_geometry_to(target, finish)
        else:
            finish()

    def _restore_to_target_later(self, target, restore_token=None):
        if restore_token is None:
            restore_token = self._begin_restore_request()
        target = QRect(target)

        def apply_restore_geometry():
            if restore_token != self._restore_generation:
                self._debug("restore timer skipped stale request")
                return
            self._debug(f"restore timer target={target}")
            hwnd = int(self.winId()) if IS_WINDOWS else 0
            if IS_WINDOWS and self._is_windows_hwnd_maximized(hwnd):
                self._debug("restore timer retry because Win32 placement is still maximized")
                self._restore_windows_window(target)
                self._update_maximize_icon()
                return
            if self.isMaximized() or self.isFullScreen():
                self._debug("restore timer skipped because still maximized/fullscreen")
                return
            fitted = self._fit_geometry_to_screen(target, self._available_geometry_for_geometry(target))
            current = QRect(self.geometry())
            if self._geometry_matches_available_screen(current) and self._geometry_differs(current, fitted):
                self._debug(f"restore timer setGeometry fitted={fitted}")
                self.setGeometry(fitted)
                self._cancel_restore_request()
            self._update_maximize_icon()

        QTimer.singleShot(80, apply_restore_geometry)
        QTimer.singleShot(220, apply_restore_geometry)

    def _animate_geometry_to(self, target, finished_callback=None):
        if self._window_animation:
            self._window_animation.stop()
            self._window_animation.deleteLater()

        if self._animation_duration <= 0 or self.geometry() == target:
            self.setGeometry(target)
            if finished_callback:
                finished_callback()
            return

        animation = QPropertyAnimation(self, b"geometry", self)
        animation.setDuration(self._animation_duration)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        animation.setStartValue(QRect(self.geometry()))
        animation.setEndValue(QRect(target))

        def on_finished():
            if finished_callback:
                finished_callback()
            animation.deleteLater()
            if self._window_animation is animation:
                self._window_animation = None

        animation.finished.connect(on_finished)
        self._window_animation = animation
        animation.start()

    def show_window_menu(self, global_pos):
        """Show a compact system-like menu for frameless title bars."""
        menu = QMenu(self)

        restore_action = QAction("Restore", self)
        restore_action.setEnabled(self.isMaximized())
        restore_action.triggered.connect(lambda: self._restore_window(animated=False))
        menu.addAction(restore_action)

        minimize_action = QAction("Minimize", self)
        minimize_action.triggered.connect(self.showMinimized)
        menu.addAction(minimize_action)

        maximize_action = QAction("Maximize", self)
        maximize_action.setEnabled(not self.isMaximized())
        maximize_action.triggered.connect(lambda: self._maximize_window(animated=False))
        menu.addAction(maximize_action)

        menu.addSeparator()

        close_action = QAction("Close", self)
        close_action.triggered.connect(self.close)
        menu.addAction(close_action)

        menu.exec(global_pos)
        self._update_maximize_icon()

    def snap_to_screen_edge(self, global_pos):
        """Fallback snap zones when the platform cannot do native system move."""
        geometry = self._available_geometry_for_point(global_pos)
        if geometry.isNull() or not geometry.isValid():
            return False

        threshold = 18
        at_left = abs(global_pos.x() - geometry.left()) <= threshold
        at_right = abs(global_pos.x() - geometry.right()) <= threshold
        at_top = abs(global_pos.y() - geometry.top()) <= threshold
        at_bottom = abs(global_pos.y() - geometry.bottom()) <= threshold

        if at_top and not (at_left or at_right):
            self._maximize_window(animated=False)
            return True

        if not (at_left or at_right):
            return False

        width = geometry.width() // 2
        height = geometry.height()
        x = geometry.left() if at_left else geometry.left() + geometry.width() - width
        y = geometry.top()

        if at_top or at_bottom:
            height = geometry.height() // 2
            y = geometry.top() if at_top else geometry.top() + geometry.height() - height

        self._cancel_restore_request()
        self.showNormal()
        self.setGeometry(self._fit_geometry_to_screen(QRect(x, y, width, height), geometry))
        self._update_maximize_icon()
        return True

    def _available_geometry_for_window(self):
        screen = self._screen_for_geometry(self.frameGeometry())
        if screen:
            return screen.availableGeometry()

        primary = QApplication.primaryScreen()
        return primary.availableGeometry() if primary else self.geometry()

    def _available_geometry_for_geometry(self, geometry):
        screen = self._screen_for_geometry(geometry)
        if screen:
            return screen.availableGeometry()

        primary = QApplication.primaryScreen()
        return primary.availableGeometry() if primary else self.geometry()

    def _available_geometry_for_point(self, global_pos):
        screen = QApplication.screenAt(global_pos)
        if screen:
            return screen.availableGeometry()

        screen = self._nearest_screen_for_point(global_pos)
        if screen:
            return screen.availableGeometry()

        primary = QApplication.primaryScreen()
        return primary.availableGeometry() if primary else self.geometry()

    def _screen_for_geometry(self, geometry):
        screens = QApplication.screens()
        if not screens:
            return QApplication.primaryScreen()

        best_screen = None
        best_area = -1
        for screen in screens:
            area = self._intersection_area(geometry, screen.geometry())
            if area > best_area:
                best_area = area
                best_screen = screen

        if best_area > 0:
            return best_screen

        return self._nearest_screen_for_point(geometry.center())

    def _nearest_screen_for_point(self, global_pos):
        screens = QApplication.screens()
        if not screens:
            return QApplication.primaryScreen()

        return min(screens, key=lambda screen: self._distance_to_rect(global_pos, screen.geometry()))

    def _fit_geometry_to_screen(self, geometry, screen_geometry):
        if screen_geometry.isNull() or not screen_geometry.isValid():
            return geometry

        width = self._bounded_width(geometry.width(), screen_geometry)
        height = self._bounded_height(geometry.height(), screen_geometry)

        max_x = screen_geometry.left() + max(0, screen_geometry.width() - width)
        max_y = screen_geometry.top() + max(0, screen_geometry.height() - height)
        x = min(max(geometry.x(), screen_geometry.left()), max_x)
        y = min(max(geometry.y(), screen_geometry.top()), max_y)

        return QRect(x, y, width, height)

    def _remember_normal_geometry(self, geometry):
        if self.isMaximized() or self.isFullScreen() or self.isMinimized():
            self._debug(f"remember normal skipped window state geometry={geometry}")
            return False
        if geometry.isNull() or not geometry.isValid():
            self._debug(f"remember normal skipped invalid geometry={geometry}")
            return False
        if self._geometry_matches_available_screen(geometry):
            self._debug(f"remember normal skipped available-screen geometry={geometry}")
            return False

        self._last_normal_geometry = QRect(geometry)
        self._debug(f"remember normal saved geometry={geometry}")
        return True

    def _bounded_width(self, width, screen_geometry):
        minimum = max(1, self.minimumWidth())
        if screen_geometry.isNull() or not screen_geometry.isValid():
            return max(width, minimum)
        maximum = max(minimum, screen_geometry.width())
        return min(max(width, minimum), maximum)

    def _bounded_height(self, height, screen_geometry):
        minimum = max(1, self.minimumHeight())
        if screen_geometry.isNull() or not screen_geometry.isValid():
            return max(height, minimum)
        maximum = max(minimum, screen_geometry.height())
        return min(max(height, minimum), maximum)

    @staticmethod
    def _intersection_area(rect, other):
        intersection = rect.intersected(other)
        if intersection.isNull() or not intersection.isValid():
            return 0
        return max(0, intersection.width()) * max(0, intersection.height())

    @staticmethod
    def _distance_to_rect(point, rect):
        if rect.contains(point):
            return 0

        dx = 0
        if point.x() < rect.left():
            dx = rect.left() - point.x()
        elif point.x() > rect.right():
            dx = point.x() - rect.right()

        dy = 0
        if point.y() < rect.top():
            dy = rect.top() - point.y()
        elif point.y() > rect.bottom():
            dy = point.y() - rect.bottom()

        return dx * dx + dy * dy

    def changeEvent(self, event):
        """Keep custom controls in sync with the window state."""
        super().changeEvent(event)
        if event.type() == QEvent.Type.WindowStateChange:
            if self._was_maximized and not self.isMaximized():
                self._restore_saved_geometry_after_native_state_change()
            self._was_maximized = self.isMaximized()
            self._update_maximize_icon()
        elif event.type() == QEvent.Type.ActivationChange and self.title_bar:
            self.title_bar.set_active(self.isActiveWindow())

    def _restore_saved_geometry_after_native_state_change(self):
        target = QRect(self._last_normal_geometry)
        if target.isNull() or not target.isValid():
            return
        if not self._geometry_matches_available_screen(self.geometry()):
            return
        if IS_WINDOWS:
            self._debug("native state restore deferred to avoid duplicate geometry correction")
            self._restore_to_target_later(target)
            return
        fitted = self._fit_geometry_to_screen(target, self._available_geometry_for_geometry(target))
        self._debug(f"native state restore setGeometry fitted={fitted}")
        self.setGeometry(fitted)

    def _geometry_matches_available_screen(self, geometry):
        available = self._available_geometry_for_geometry(geometry)
        if available.isNull() or not available.isValid():
            return False
        width_close = abs(geometry.width() - available.width()) <= 4
        height_close = abs(geometry.height() - available.height()) <= 4
        return width_close and height_close

    @staticmethod
    def _geometry_differs(geometry, target):
        return (
            abs(geometry.x() - target.x()) > 4
            or abs(geometry.y() - target.y()) > 4
            or abs(geometry.width() - target.width()) > 4
            or abs(geometry.height() - target.height()) > 4
        )

    def keyPressEvent(self, event):
        if (
            self._frameless
            and event.key() == Qt.Key.Key_Space
            and event.modifiers() & Qt.KeyboardModifier.AltModifier
        ):
            pos = self.title_bar.mapToGlobal(QPoint(8, self.title_bar.height()))
            self.show_window_menu(pos)
            event.accept()
            return
        super().keyPressEvent(event)

    def eventFilter(self, watched, event):
        """Handle edge resizing for frameless windows across child widgets."""
        if IS_WINDOWS or not self._frameless or not self._event_belongs_to_window(watched):
            return super().eventFilter(watched, event)

        if event.type() == QEvent.Type.MouseButtonPress:
            return self._handle_resize_press(event)

        if event.type() == QEvent.Type.MouseMove:
            return self._handle_resize_move(watched, event)

        if event.type() == QEvent.Type.MouseButtonRelease:
            self._resizing_edges = Qt.Edge(0)
            self._unset_resize_cursor(watched)

        return super().eventFilter(watched, event)

    def _event_belongs_to_window(self, watched):
        if watched is self:
            return True
        if not isinstance(watched, QWidget):
            return False
        return watched.window() is self

    def _handle_resize_press(self, event):
        if event.button() != Qt.MouseButton.LeftButton or self.isMaximized() or self.isFullScreen():
            return False

        if self._is_title_bar_button(watched=QApplication.widgetAt(event.globalPosition().toPoint())):
            return False

        edges = self._resize_edges_at(event.globalPosition().toPoint())
        if not edges:
            return False

        window_handle = self.windowHandle()
        if window_handle and window_handle.startSystemResize(edges):
            return True

        self._resizing_edges = edges
        self._resize_start_pos = event.globalPosition().toPoint()
        self._resize_start_geometry = self.geometry()
        return True

    def _handle_resize_move(self, watched, event):
        if self._resizing_edges:
            self._resize_from_global_pos(event.globalPosition().toPoint())
            return True

        if self.isMaximized() or self.isFullScreen():
            self._unset_resize_cursor(watched)
            return False

        edges = self._resize_edges_at(event.globalPosition().toPoint())
        self._set_resize_cursor(watched, edges)
        return False

    def _windows_hit_test(self, hwnd):
        if self.isFullScreen():
            return HTCLIENT

        local_pos = self._windows_cursor_pos_to_local(hwnd)
        if local_pos is None:
            return None

        if self.title_bar:
            button_hit = self._windows_title_bar_button_hit(local_pos)
            if button_hit:
                return button_hit

        if not self.isMaximized():
            edges = self._resize_edges_at_local(local_pos)
            if edges:
                return self._hit_test_result_for_edges(edges)

        if self.title_bar:
            if self._local_pos_in_title_bar(local_pos):
                return HTCLIENT

        return HTCLIENT

    def _windows_cursor_pos_to_local(self, hwnd):
        qt_local_pos = self.mapFromGlobal(QCursor.pos())
        hit_rect = self.rect().adjusted(-self._resize_margin, -self._resize_margin, self._resize_margin, self._resize_margin)
        if hit_rect.contains(qt_local_pos):
            return qt_local_pos

        if not hwnd:
            return qt_local_pos

        user32 = ctypes.windll.user32
        point = wintypes.POINT()
        rect = wintypes.RECT()

        if not user32.GetCursorPos(ctypes.byref(point)):
            return None
        if not user32.ScreenToClient(hwnd, ctypes.byref(point)):
            return None
        if not user32.GetClientRect(hwnd, ctypes.byref(rect)):
            return None

        client_width = max(1, rect.right - rect.left)
        client_height = max(1, rect.bottom - rect.top)
        scale_x = client_width / max(1, self.width())
        scale_y = client_height / max(1, self.height())

        return QPoint(round(point.x / scale_x), round(point.y / scale_y))

    def _native_caption_hit(self, msg, hit_code):
        if hit_code == HTCAPTION:
            return True
        local_pos = self._windows_cursor_pos_to_local(msg.hWnd)
        return self._local_pos_in_title_bar(local_pos) and not self._local_pos_in_title_bar_button(local_pos)

    def _caption_click_is_double_click(self, global_pos):
        now = time.monotonic()
        user32 = ctypes.windll.user32
        user32.GetDoubleClickTime.restype = wintypes.UINT
        user32.GetSystemMetrics.argtypes = [ctypes.c_int]
        user32.GetSystemMetrics.restype = ctypes.c_int

        double_click_seconds = max(0.1, user32.GetDoubleClickTime() / 1000)
        max_dx = max(4, user32.GetSystemMetrics(SM_CXDOUBLECLK))
        max_dy = max(4, user32.GetSystemMetrics(SM_CYDOUBLECLK))

        is_double_click = (
            now - self._last_caption_click_time <= double_click_seconds
            and abs(global_pos.x() - self._last_caption_click_pos.x()) <= max_dx
            and abs(global_pos.y() - self._last_caption_click_pos.y()) <= max_dy
        )

        self._last_caption_click_time = now
        self._last_caption_click_pos = QPoint(global_pos)
        return is_double_click

    def _apply_windows_native_window_styles(self):
        hwnd = int(self.winId())
        if not hwnd:
            return

        user32 = ctypes.windll.user32
        get_window_long = getattr(user32, "GetWindowLongPtrW", user32.GetWindowLongW)
        set_window_long = getattr(user32, "SetWindowLongPtrW", user32.SetWindowLongW)
        get_window_long.argtypes = [wintypes.HWND, ctypes.c_int]
        get_window_long.restype = ctypes.c_longlong
        set_window_long.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_longlong]
        set_window_long.restype = ctypes.c_longlong
        user32.SetWindowPos.argtypes = [
            wintypes.HWND,
            wintypes.HWND,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_uint,
        ]
        user32.SetWindowPos.restype = wintypes.BOOL

        style = get_window_long(hwnd, GWL_STYLE)
        style |= WS_CAPTION | WS_THICKFRAME | WS_MINIMIZEBOX | WS_MAXIMIZEBOX | WS_SYSMENU
        set_window_long(hwnd, GWL_STYLE, style)

        user32.SetWindowPos(
            hwnd,
            0,
            0,
            0,
            0,
            0,
            SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER | SWP_FRAMECHANGED,
        )

    def _connect_windows_screen_changed(self):
        window_handle = self.windowHandle()
        if not window_handle or self._windows_screen_changed_connected:
            return
        window_handle.screenChanged.connect(self._refresh_windows_frame)
        self._windows_screen_changed_connected = True

    def _refresh_windows_frame(self):
        if not IS_WINDOWS:
            return
        hwnd = int(self.winId())
        if not hwnd:
            return
        ctypes.windll.user32.SetWindowPos(
            hwnd,
            0,
            0,
            0,
            0,
            0,
            SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER | SWP_FRAMECHANGED,
        )

    def _restore_windows_window(self, target):
        hwnd = int(self.winId())
        if not hwnd:
            self.showNormal()
            return False

        user32 = ctypes.windll.user32
        placement = WINDOWPLACEMENT()
        placement.length = ctypes.sizeof(WINDOWPLACEMENT)
        user32.GetWindowPlacement.argtypes = [wintypes.HWND, ctypes.POINTER(WINDOWPLACEMENT)]
        user32.GetWindowPlacement.restype = wintypes.BOOL
        user32.SetWindowPlacement.argtypes = [wintypes.HWND, ctypes.POINTER(WINDOWPLACEMENT)]
        user32.SetWindowPlacement.restype = wintypes.BOOL
        user32.ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]
        user32.ShowWindow.restype = wintypes.BOOL

        if user32.GetWindowPlacement(hwnd, ctypes.byref(placement)):
            native_left, native_top, native_right, native_bottom = self._windows_native_rect_for_qt_geometry(target, hwnd)
            placement.showCmd = SW_SHOWNORMAL
            placement.rcNormalPosition.left = native_left
            placement.rcNormalPosition.top = native_top
            placement.rcNormalPosition.right = native_right
            placement.rcNormalPosition.bottom = native_bottom
            ok = bool(user32.SetWindowPlacement(hwnd, ctypes.byref(placement)))
            self._debug(
                "win32 SetWindowPlacement "
                f"target={target} native=({native_left}, {native_top}, {native_right}, {native_bottom}) ok={ok}"
            )

        restored = bool(user32.ShowWindow(hwnd, SW_RESTORE))
        self._debug(f"win32 ShowWindow(SW_RESTORE) restored={restored}")
        return restored

    def _windows_native_rect_for_qt_geometry(self, target, hwnd):
        dpi = self._windows_dpi_for_window(hwnd)
        scale = dpi / 96.0 if dpi else self.devicePixelRatioF()
        if scale <= 0:
            scale = 1.0

        screen = self._screen_for_geometry(target)
        screen_geometry = screen.geometry() if screen else QRect()
        monitor_rect = self._windows_monitor_rect_for_window(hwnd)

        if monitor_rect and screen_geometry.isValid():
            left = monitor_rect.left + round((target.left() - screen_geometry.left()) * scale)
            top = monitor_rect.top + round((target.top() - screen_geometry.top()) * scale)
        else:
            left = round(target.left() * scale)
            top = round(target.top() * scale)

        right = left + round(target.width() * scale)
        bottom = top + round(target.height() * scale)
        return left, top, right, bottom

    def _handle_windows_nc_calc_size(self, msg):
        rect = None
        if msg.wParam:
            params = NCCALCSIZE_PARAMS.from_address(int(msg.lParam))
            rect = params.rgrc[0]
        elif msg.lParam:
            rect = wintypes.RECT.from_address(int(msg.lParam))

        hwnd = int(msg.hWnd)
        is_maximized = self._is_windows_hwnd_maximized(hwnd)
        is_fullscreen = self._is_windows_hwnd_fullscreen(hwnd)

        if rect and is_maximized and not is_fullscreen:
            thickness_x = self._windows_resize_border_thickness(hwnd, horizontal=True)
            thickness_y = self._windows_resize_border_thickness(hwnd, horizontal=False)
            rect.left += thickness_x
            rect.right -= thickness_x
            rect.top += thickness_y
            rect.bottom -= thickness_y

        if rect and (is_maximized or is_fullscreen) and self._windows_taskbar_auto_hide():
            edge = self._windows_taskbar_position(hwnd)
            if edge == ABE_LEFT:
                rect.left += AUTO_HIDE_TASKBAR_THICKNESS
            elif edge == ABE_TOP:
                rect.top += AUTO_HIDE_TASKBAR_THICKNESS
            elif edge == ABE_RIGHT:
                rect.right -= AUTO_HIDE_TASKBAR_THICKNESS
            elif edge == ABE_BOTTOM:
                rect.bottom -= AUTO_HIDE_TASKBAR_THICKNESS

        return True, WVR_REDRAW if msg.wParam else 0

    def _is_windows_hwnd_maximized(self, hwnd):
        if not hwnd:
            return self.isMaximized()
        placement = WINDOWPLACEMENT()
        placement.length = ctypes.sizeof(WINDOWPLACEMENT)
        user32 = ctypes.windll.user32
        user32.GetWindowPlacement.argtypes = [wintypes.HWND, ctypes.POINTER(WINDOWPLACEMENT)]
        user32.GetWindowPlacement.restype = wintypes.BOOL
        if not user32.GetWindowPlacement(hwnd, ctypes.byref(placement)):
            return self.isMaximized()
        return placement.showCmd == SW_MAXIMIZE

    def _is_windows_hwnd_fullscreen(self, hwnd):
        if not hwnd:
            return self.isFullScreen()
        window_rect = wintypes.RECT()
        user32 = ctypes.windll.user32
        user32.GetWindowRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
        user32.GetWindowRect.restype = wintypes.BOOL
        if not user32.GetWindowRect(hwnd, ctypes.byref(window_rect)):
            return self.isFullScreen()

        monitor_rect = self._windows_monitor_rect_for_window(hwnd)
        if not monitor_rect:
            return self.isFullScreen()

        return (
            window_rect.left == monitor_rect.left
            and window_rect.top == monitor_rect.top
            and window_rect.right == monitor_rect.right
            and window_rect.bottom == monitor_rect.bottom
        )

    def _windows_resize_border_thickness(self, hwnd, horizontal=True):
        index = SM_CXSIZEFRAME if horizontal else SM_CYSIZEFRAME
        user32 = ctypes.windll.user32
        get_for_dpi = getattr(user32, "GetSystemMetricsForDpi", None)
        if get_for_dpi and hwnd:
            get_for_dpi.argtypes = [ctypes.c_int, wintypes.UINT]
            get_for_dpi.restype = ctypes.c_int
            dpi = self._windows_dpi_for_window(hwnd)
            thickness = get_for_dpi(index, dpi) + get_for_dpi(SM_CXPADDEDBORDER, dpi)
        else:
            user32.GetSystemMetrics.argtypes = [ctypes.c_int]
            user32.GetSystemMetrics.restype = ctypes.c_int
            thickness = user32.GetSystemMetrics(index) + user32.GetSystemMetrics(SM_CXPADDEDBORDER)

        if thickness > 0:
            return thickness
        return round((8 if horizontal else 8) * self.devicePixelRatioF())

    def _windows_dpi_for_window(self, hwnd):
        get_dpi = getattr(ctypes.windll.user32, "GetDpiForWindow", None)
        if get_dpi and hwnd:
            get_dpi.argtypes = [wintypes.HWND]
            get_dpi.restype = wintypes.UINT
            dpi = get_dpi(hwnd)
            if dpi:
                return dpi
        return 96

    def _windows_monitor_rect_for_window(self, hwnd):
        user32 = ctypes.windll.user32
        user32.MonitorFromWindow.argtypes = [wintypes.HWND, wintypes.DWORD]
        user32.MonitorFromWindow.restype = wintypes.HANDLE
        monitor = user32.MonitorFromWindow(hwnd, MONITOR_DEFAULTTONEAREST)
        if not monitor:
            return None

        info = MONITORINFO()
        info.cbSize = ctypes.sizeof(MONITORINFO)
        user32.GetMonitorInfoW.argtypes = [wintypes.HANDLE, ctypes.POINTER(MONITORINFO)]
        user32.GetMonitorInfoW.restype = wintypes.BOOL
        if not user32.GetMonitorInfoW(monitor, ctypes.byref(info)):
            return None
        return info.rcMonitor

    def _windows_taskbar_auto_hide(self):
        data = APPBARDATA(ctypes.sizeof(APPBARDATA), 0, 0, 0, wintypes.RECT(), 0)
        state = ctypes.windll.shell32.SHAppBarMessage(ABM_GETSTATE, ctypes.byref(data))
        return bool(state & ABS_AUTOHIDE)

    def _windows_taskbar_position(self, hwnd):
        monitor_rect = self._windows_monitor_rect_for_window(hwnd)
        if not monitor_rect:
            return None

        data = APPBARDATA(ctypes.sizeof(APPBARDATA), 0, 0, 0, monitor_rect, 0)
        shell32 = ctypes.windll.shell32
        shell32.SHAppBarMessage.argtypes = [wintypes.DWORD, ctypes.POINTER(APPBARDATA)]
        shell32.SHAppBarMessage.restype = ctypes.c_ulonglong
        for edge in (ABE_LEFT, ABE_TOP, ABE_RIGHT, ABE_BOTTOM):
            data.uEdge = edge
            if shell32.SHAppBarMessage(ABM_GETAUTOHIDEBAREX, ctypes.byref(data)):
                return edge
        return None

    def _local_pos_in_title_bar(self, local_pos):
        if not self.title_bar or local_pos is None:
            return False
        title_rect = QRect(self.title_bar.mapTo(self, QPoint(0, 0)), self.title_bar.size())
        return title_rect.contains(local_pos)

    def _local_pos_in_title_bar_button(self, local_pos):
        return self._windows_title_bar_button_hit(local_pos) is not None

    def _windows_title_bar_button_hit(self, local_pos):
        if not self.title_bar or local_pos is None:
            return None
        for button, hit in self._windows_button_hits():
            button_rect = QRect(button.mapTo(self, QPoint(0, 0)), button.size())
            if button_rect.contains(local_pos):
                return hit
        return None

    def _title_bar_buttons(self):
        if not self.title_bar:
            return ()
        return (self.title_bar.min_button, self.title_bar.max_button, self.title_bar.close_button)

    def _windows_button_hits(self):
        if not self.title_bar:
            return ()
        return (
            (self.title_bar.min_button, HTMINBUTTON),
            (self.title_bar.max_button, HTMAXBUTTON),
            (self.title_bar.close_button, HTCLOSE),
        )

    def _button_for_windows_hit(self, hit):
        if not self.title_bar:
            return None
        if hit == HTMINBUTTON:
            return self.title_bar.min_button
        if hit == HTMAXBUTTON:
            return self.title_bar.max_button
        if hit == HTCLOSE:
            return self.title_bar.close_button
        return None

    def _activate_windows_button_hit(self, hit):
        if hit == HTMINBUTTON:
            self.showMinimized()
        elif hit == HTMAXBUTTON:
            self.toggle_maximize()
        elif hit == HTCLOSE:
            self.close()

    def _is_title_bar_button(self, watched):
        while isinstance(watched, QWidget):
            if isinstance(watched, LqWindowButton):
                return True
            watched = watched.parentWidget()
        return False

    def _hit_test_result_for_edges(self, edges):
        left = bool(edges & Qt.Edge.LeftEdge)
        right = bool(edges & Qt.Edge.RightEdge)
        top = bool(edges & Qt.Edge.TopEdge)
        bottom = bool(edges & Qt.Edge.BottomEdge)

        if top and left:
            return HTTOPLEFT
        if top and right:
            return HTTOPRIGHT
        if bottom and left:
            return HTBOTTOMLEFT
        if bottom and right:
            return HTBOTTOMRIGHT
        if left:
            return HTLEFT
        if right:
            return HTRIGHT
        if top:
            return HTTOP
        if bottom:
            return HTBOTTOM
        return None

    def _resize_edges_at(self, global_pos):
        return self._resize_edges_at_local(self.mapFromGlobal(global_pos))

    def _resize_edges_at_local(self, pos):
        rect = self.rect()
        margin = self._resize_margin
        edges = Qt.Edge(0)

        if pos.x() <= margin:
            edges |= Qt.Edge.LeftEdge
        elif pos.x() >= rect.width() - margin:
            edges |= Qt.Edge.RightEdge

        if pos.y() <= margin:
            edges |= Qt.Edge.TopEdge
        elif pos.y() >= rect.height() - margin:
            edges |= Qt.Edge.BottomEdge

        return edges

    def _resize_from_global_pos(self, global_pos):
        delta = global_pos - self._resize_start_pos
        geometry = QRect(self._resize_start_geometry)
        minimum = self.minimumSize()

        if self._resizing_edges & Qt.Edge.LeftEdge:
            new_left = min(geometry.left() + delta.x(), geometry.right() - minimum.width() + 1)
            geometry.setLeft(new_left)
        elif self._resizing_edges & Qt.Edge.RightEdge:
            geometry.setRight(max(geometry.right() + delta.x(), geometry.left() + minimum.width() - 1))

        if self._resizing_edges & Qt.Edge.TopEdge:
            new_top = min(geometry.top() + delta.y(), geometry.bottom() - minimum.height() + 1)
            geometry.setTop(new_top)
        elif self._resizing_edges & Qt.Edge.BottomEdge:
            geometry.setBottom(max(geometry.bottom() + delta.y(), geometry.top() + minimum.height() - 1))

        self.setGeometry(geometry)

    def _set_resize_cursor(self, watched, edges):
        if edges in (Qt.Edge.LeftEdge | Qt.Edge.TopEdge, Qt.Edge.RightEdge | Qt.Edge.BottomEdge):
            cursor = Qt.CursorShape.SizeFDiagCursor
        elif edges in (Qt.Edge.RightEdge | Qt.Edge.TopEdge, Qt.Edge.LeftEdge | Qt.Edge.BottomEdge):
            cursor = Qt.CursorShape.SizeBDiagCursor
        elif edges & (Qt.Edge.LeftEdge | Qt.Edge.RightEdge):
            cursor = Qt.CursorShape.SizeHorCursor
        elif edges & (Qt.Edge.TopEdge | Qt.Edge.BottomEdge):
            cursor = Qt.CursorShape.SizeVerCursor
        else:
            self._unset_resize_cursor(watched)
            return
        watched.setCursor(cursor)

    def _unset_resize_cursor(self, watched):
        if isinstance(watched, QWidget):
            watched.unsetCursor()

    def _update_maximize_icon(self):
        if self.title_bar:
            self.title_bar.update_maximize_icon()

    def apply_styles(self):
        """Apply the blue flat style."""
        self.setStyleSheet(LqStyle.get_full_style())

    def on_action_triggered(self, action_name):
        """Handle action trigger and display in the main area."""
        message = f"Action triggered: {action_name}"
        self.append_display_text(message)
        if self.statusBar():
            self.statusBar().showMessage(f"Executed: {action_name}", 3000)

    def get_ribbon_bar(self):
        """Get the ribbon bar instance."""
        return self.ribbon_bar

    def set_display_text(self, text):
        """Set text in the display area."""
        if self.display_area is None:
            if self.statusBar():
                self.statusBar().showMessage(text)
            return
        if hasattr(self.display_area, "setPlainText"):
            self.display_area.setPlainText(text)
        elif hasattr(self.display_area, "setText"):
            self.display_area.setText(text)

    def append_display_text(self, text):
        """Append text to the display area."""
        if self.display_area is None:
            if self.statusBar():
                self.statusBar().showMessage(text)
            return
        if hasattr(self.display_area, "append"):
            self.display_area.append(text)
        elif hasattr(self.display_area, "setPlainText") and hasattr(self.display_area, "toPlainText"):
            current = self.display_area.toPlainText()
            self.display_area.setPlainText(f"{current}\n{text}" if current else text)
        elif hasattr(self.display_area, "setText") and hasattr(self.display_area, "text"):
            current = self.display_area.text()
            self.display_area.setText(f"{current}\n{text}" if current else text)
