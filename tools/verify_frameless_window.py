"""
Visible frameless-window regression checks for the example app.

This script intentionally opens a real window on Windows so native hit testing,
system buttons, maximize/restore, and snap prerequisites can be verified.
"""

import ctypes
import os
import sys
import time
from pathlib import Path

from PySide6.QtCore import QEvent, QPoint, QRect, Qt
from PySide6.QtGui import QContextMenuEvent, QCursor, QKeyEvent
from PySide6.QtWidgets import QApplication


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "LqRibbon" / "example"))

from LqRibbon.lq_ribbon_window import (  # noqa: E402
    GWL_STYLE,
    HTBOTTOM,
    HTBOTTOMLEFT,
    HTBOTTOMRIGHT,
    HTCAPTION,
    HTCLIENT,
    HTCLOSE,
    HTLEFT,
    HTMAXBUTTON,
    HTMINBUTTON,
    HTRIGHT,
    HTTOP,
    HTTOPLEFT,
    HTTOPRIGHT,
    WM_NCLBUTTONDBLCLK,
    WS_CAPTION,
    WS_MAXIMIZEBOX,
    WS_MINIMIZEBOX,
    WS_SYSMENU,
    WS_THICKFRAME,
)
from main_window import MainWindow  # noqa: E402


IS_WINDOWS = sys.platform == "win32"
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004


class FramelessVerifier:
    def __init__(self):
        self.app = QApplication.instance() or QApplication([])
        self.app.setQuitOnLastWindowClosed(False)
        self.window = MainWindow()
        self.window.resize(1200, 700)
        self.failures = []
        self.passes = 0

    def run(self):
        self.trace("START frameless verifier")
        self.window.show()
        self.trace("SHOWN window")
        self.window.raise_()
        self.window.activateWindow()
        self.trace("ACTIVATED window")
        self.wait(900)
        self.trace("BEGIN checks")

        self.check("example window is frameless", self.window._frameless)
        self.check("custom title bar exists", self.window.title_bar is not None)
        self.check("title text is transparent for mouse events", self.window.title_bar.title_label.testAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents))

        if IS_WINDOWS:
            self.trace("STAGE check_windows_style_bits")
            self.check_windows_style_bits()
            self.trace("STAGE check_windows_hit_tests_normal")
            self.check_windows_hit_tests_normal()
            self.trace("STAGE check_titlebar_menu_shortcuts")
            self.check_titlebar_menu_shortcuts()
            self.trace("STAGE check_maximize_button")
            self.check_maximize_button()
            self.trace("STAGE check_double_click_restore")
            self.check_double_click_restore()
            self.trace("STAGE check_maximize_button_restore")
            self.check_maximize_button_restore()
            self.trace("STAGE check_drag_down_restore")
            self.check_drag_down_restore()
            self.trace("STAGE check_minimize_button")
            self.check_minimize_button()

        self.trace("STAGE check_snap_fallback_zones")
        self.check_snap_fallback_zones()
        self.trace("STAGE check_multi_screen_geometry_helpers")
        self.check_multi_screen_geometry_helpers()
        self.trace("STAGE check_stress_repeated_operations")
        self.check_stress_repeated_operations(iterations=30)
        self.trace("STAGE check_close_button")
        self.check_close_button()
        self.finish()

    def finish(self):
        total = self.passes + len(self.failures)
        self.trace(f"\nframeless verification: {self.passes}/{total} passed")
        if self.failures:
            self.trace("failures:")
            for failure in self.failures:
                self.trace(f" - {failure}")
            raise SystemExit(1)
        raise SystemExit(0)

    def check(self, name, condition, details=""):
        if condition:
            self.passes += 1
            self.trace(f"PASS {name}")
        else:
            suffix = f" ({details})" if details else ""
            self.failures.append(f"{name}{suffix}")
            self.trace(f"FAIL {name}{suffix}")

    def trace(self, message):
        print(message, flush=True)

    def wait(self, milliseconds):
        end = time.monotonic() + milliseconds / 1000
        while time.monotonic() < end:
            self.app.processEvents()
            time.sleep(0.01)
        self.app.processEvents()

    def wait_until(self, predicate, timeout_ms=1200):
        end = time.monotonic() + timeout_ms / 1000
        while time.monotonic() < end:
            self.app.processEvents()
            if predicate():
                return True
            time.sleep(0.01)
        self.app.processEvents()
        return predicate()

    def click_at(self, global_pos):
        QCursor.setPos(global_pos)
        self.wait(70)
        ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        self.wait(40)
        ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        self.wait(70)

    def double_click_at(self, global_pos):
        self.click_at(global_pos)
        self.wait(60)
        self.click_at(global_pos)

    def drag_at(self, start, end, steps=18):
        QCursor.setPos(start)
        self.wait(80)
        ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        for index in range(1, steps + 1):
            x = start.x() + round((end.x() - start.x()) * index / steps)
            y = start.y() + round((end.y() - start.y()) * index / steps)
            QCursor.setPos(QPoint(x, y))
            self.wait(20)
        ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        self.wait(500)

    def hwnd(self):
        return int(self.window.winId())

    def hit_at(self, global_pos):
        QCursor.setPos(global_pos)
        self.wait(50)
        return self.window._windows_hit_test(self.hwnd())

    def title_center(self):
        title_bar = self.window.title_bar
        return title_bar.mapToGlobal(QPoint(title_bar.width() // 2, 12))

    def check_windows_style_bits(self):
        user32 = ctypes.windll.user32
        get_window_long = getattr(user32, "GetWindowLongPtrW", user32.GetWindowLongW)
        get_window_long.argtypes = [ctypes.wintypes.HWND, ctypes.c_int]
        get_window_long.restype = ctypes.c_longlong
        style = get_window_long(self.hwnd(), GWL_STYLE)
        self.check("Windows style has caption", bool(style & WS_CAPTION))
        self.check("Windows style has thick frame", bool(style & WS_THICKFRAME))
        self.check("Windows style has minimize box", bool(style & WS_MINIMIZEBOX))
        self.check("Windows style has maximize box", bool(style & WS_MAXIMIZEBOX))
        self.check("Windows style has system menu", bool(style & WS_SYSMENU))

    def check_windows_hit_tests_normal(self):
        self.ensure_normal_geometry()
        width = self.window.width()
        height = self.window.height()
        points = [
            ("title hit is HTCLIENT so Qt can handle double-click", self.title_center(), HTCLIENT),
            ("minimize button hit is HTMINBUTTON", self.window.title_bar.min_button.mapToGlobal(self.window.title_bar.min_button.rect().center()), HTMINBUTTON),
            ("maximize button hit is HTMAXBUTTON", self.window.title_bar.max_button.mapToGlobal(self.window.title_bar.max_button.rect().center()), HTMAXBUTTON),
            ("close button hit is HTCLOSE", self.window.title_bar.close_button.mapToGlobal(self.window.title_bar.close_button.rect().center()), HTCLOSE),
            ("left resize hit", self.window.mapToGlobal(QPoint(1, height // 2)), HTLEFT),
            ("right resize hit", self.window.mapToGlobal(QPoint(width - 2, height // 2)), HTRIGHT),
            ("top resize hit", self.window.mapToGlobal(QPoint(width // 2, 1)), HTTOP),
            ("bottom resize hit", self.window.mapToGlobal(QPoint(width // 2, height - 2)), HTBOTTOM),
            ("top-left resize hit", self.window.mapToGlobal(QPoint(-3, -3)), HTTOPLEFT),
            ("top-right resize hit", self.window.mapToGlobal(QPoint(width + 3, -3)), HTTOPRIGHT),
            ("bottom-left resize hit", self.window.mapToGlobal(QPoint(1, height - 2)), HTBOTTOMLEFT),
            ("bottom-right resize hit", self.window.mapToGlobal(QPoint(width - 2, height - 2)), HTBOTTOMRIGHT),
        ]
        for name, point, expected in points:
            actual = self.hit_at(point)
            self.check(name, actual == expected, f"actual={actual}, expected={expected}")

    def check_titlebar_menu_shortcuts(self):
        calls = []
        original = self.window.show_window_menu
        self.window.show_window_menu = lambda pos: calls.append(pos)
        try:
            key_event = QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_Space, Qt.KeyboardModifier.AltModifier)
            QApplication.sendEvent(self.window, key_event)
            self.check("Alt+Space opens system-like menu handler", len(calls) == 1)

            context_event = QContextMenuEvent(
                QContextMenuEvent.Reason.Mouse,
                QPoint(20, 15),
                self.window.title_bar.mapToGlobal(QPoint(20, 15)),
            )
            QApplication.sendEvent(self.window.title_bar, context_event)
            self.check("title bar right-click opens system-like menu handler", len(calls) == 2)
        finally:
            self.window.show_window_menu = original

    def check_maximize_button(self):
        self.ensure_normal_geometry()
        self.click_at(self.window.title_bar.max_button.mapToGlobal(self.window.title_bar.max_button.rect().center()))
        self.wait(700)
        self.check("maximize button maximizes window", self.window.isMaximized(), str(self.window.geometry()))
        self.check("maximized title hit becomes HTCLIENT for Qt double-click restore", self.hit_at(self.title_center()) == HTCLIENT)
        max_button_hit = self.hit_at(self.window.title_bar.max_button.mapToGlobal(self.window.title_bar.max_button.rect().center()))
        self.check("maximized maximize button hit remains HTMAXBUTTON", max_button_hit == HTMAXBUTTON, f"actual={max_button_hit}")

    def check_double_click_restore(self):
        self.ensure_normal_geometry()
        self.double_click_at(self.title_center())
        self.wait(700)
        self.check("real title double-click maximizes normal window", self.window.isMaximized(), str(self.window.geometry()))
        self.double_click_at(self.title_center())
        self.wait(700)
        self.check("real title double-click restores from maximized", not self.window.isMaximized(), str(self.window.geometry()))
        self.check("real double-click restore returns to saved normal size", self.geometry_close(self.window.geometry(), QRect(100, 100, 1200, 700)), str(self.window.geometry()))

    def check_maximize_button_restore(self):
        self.ensure_normal_geometry()
        self.click_at(self.window.title_bar.max_button.mapToGlobal(self.window.title_bar.max_button.rect().center()))
        self.wait(700)
        self.click_at(self.window.title_bar.max_button.mapToGlobal(self.window.title_bar.max_button.rect().center()))
        self.wait(700)
        self.check("maximize button restores from maximized", not self.window.isMaximized(), str(self.window.geometry()))
        self.check("button restore returns to saved normal size", self.geometry_close(self.window.geometry(), QRect(100, 100, 1200, 700)), str(self.window.geometry()))

    def check_drag_down_restore(self):
        self.ensure_normal_geometry()
        self.window._maximize_window(animated=False)
        self.wait(700)
        available = self.window._available_geometry_for_window()
        title_bar = self.window.title_bar
        start = self.title_center()
        end = QPoint(start.x(), available.top() + max(220, title_bar.height() * 4))
        original_start_system_move = title_bar._try_start_system_move
        title_bar._drag_restore_ratio = 0.5
        title_bar._drag_start_pos = start
        title_bar._drag_position = QPoint()
        title_bar._try_start_system_move = lambda: False
        try:
            title_bar._restore_for_drag(end, 12)
            self.wait(500)
        finally:
            title_bar._try_start_system_move = original_start_system_move
            title_bar._drag_position = None
            title_bar._system_move_started = False
        self.check("drag-down restore logic restores maximized window", not self.window.isMaximized(), str(self.window.geometry()))
        self.ensure_normal_geometry()

    def check_minimize_button(self):
        self.ensure_normal_geometry()
        self.click_at(self.window.title_bar.min_button.mapToGlobal(self.window.title_bar.min_button.rect().center()))
        self.wait(700)
        self.check("minimize button minimizes window", self.window.isMinimized())
        self.window.showNormal()
        self.window.raise_()
        self.window.activateWindow()
        self.wait(500)
        self.ensure_normal_geometry()

    def check_snap_fallback_zones(self):
        available = self.window._available_geometry_for_window()
        half_width = available.width() // 2
        half_height = available.height() // 2
        cases = [
            ("fallback snap top maximizes", QPoint(available.center().x(), available.top()), None),
            ("fallback snap left half", QPoint(available.left(), available.center().y()), QRect(available.left(), available.top(), half_width, available.height())),
            ("fallback snap right half", QPoint(available.right(), available.center().y()), QRect(available.left() + available.width() - half_width, available.top(), half_width, available.height())),
            ("fallback snap top-left quarter", QPoint(available.left(), available.top()), QRect(available.left(), available.top(), half_width, half_height)),
            ("fallback snap top-right quarter", QPoint(available.right(), available.top()), QRect(available.left() + available.width() - half_width, available.top(), half_width, half_height)),
            ("fallback snap bottom-left quarter", QPoint(available.left(), available.bottom()), QRect(available.left(), available.top() + available.height() - half_height, half_width, half_height)),
            ("fallback snap bottom-right quarter", QPoint(available.right(), available.bottom()), QRect(available.left() + available.width() - half_width, available.top() + available.height() - half_height, half_width, half_height)),
        ]
        for name, point, expected in cases:
            self.ensure_normal_geometry()
            did_snap = self.window.snap_to_screen_edge(point)
            self.wait(250)
            if expected is None:
                self.check(name, did_snap and self.window.isMaximized(), str(self.window.geometry()))
            else:
                self.check(name, did_snap and self.geometry_close(self.window.geometry(), expected), f"actual={self.window.geometry()}, expected={expected}")
        self.ensure_normal_geometry()

    def check_multi_screen_geometry_helpers(self):
        available = self.window._available_geometry_for_window()
        oversized = QRect(available.left() - 500, available.top() - 500, available.width() * 2, available.height() * 2)
        fitted = self.window._fit_geometry_to_screen(oversized, available)
        self.check("fit geometry clamps oversized width", fitted.width() <= available.width(), str(fitted))
        self.check("fit geometry clamps oversized height", fitted.height() <= available.height(), str(fitted))
        self.check("available geometry for offscreen point falls back to nearest screen", self.window._available_geometry_for_point(QPoint(available.right() + 10000, available.bottom() + 10000)).isValid())

    def check_stress_repeated_operations(self, iterations=30):
        base_geometry = QRect(100, 100, 1200, 700)
        self.ensure_normal_geometry()

        for index in range(1, iterations + 1):
            self.trace(f"STRESS iteration {index}/{iterations}")

            self.double_click_at(self.title_center())
            maximized = self.wait_until(self.window.isMaximized)
            self.check(f"stress {index}: double-click maximizes", maximized, str(self.window.geometry()))

            self.double_click_at(self.title_center())
            restored = self.wait_until(lambda: not self.window.isMaximized())
            self.wait(120)
            self.check(f"stress {index}: double-click restores", restored, str(self.window.geometry()))
            self.check(
                f"stress {index}: restored geometry is not polluted",
                self.geometry_close(self.window.geometry(), base_geometry),
                str(self.window.geometry()),
            )

            if index % 5 == 0:
                self.click_at(self.window.title_bar.max_button.mapToGlobal(self.window.title_bar.max_button.rect().center()))
                self.check(f"stress {index}: maximize button maximizes", self.wait_until(self.window.isMaximized), str(self.window.geometry()))
                self.click_at(self.window.title_bar.max_button.mapToGlobal(self.window.title_bar.max_button.rect().center()))
                self.check(f"stress {index}: maximize button restores", self.wait_until(lambda: not self.window.isMaximized()), str(self.window.geometry()))
                self.wait(120)
                self.check(
                    f"stress {index}: button restore geometry is stable",
                    self.geometry_close(self.window.geometry(), base_geometry),
                    str(self.window.geometry()),
                )

            if index % 10 == 0:
                available = self.window._available_geometry_for_window()
                top_center = QPoint(available.center().x(), available.top())
                self.window.snap_to_screen_edge(top_center)
                self.check(f"stress {index}: top snap maximizes", self.wait_until(self.window.isMaximized), str(self.window.geometry()))
                self.double_click_at(self.title_center())
                self.check(f"stress {index}: top snap then double-click restores", self.wait_until(lambda: not self.window.isMaximized()), str(self.window.geometry()))
                self.ensure_normal_geometry()
                self.check(
                    f"stress {index}: ensure normal geometry after top snap",
                    self.geometry_close(self.window.geometry(), base_geometry),
                    str(self.window.geometry()),
                )

    def check_close_button(self):
        self.ensure_normal_geometry()
        self.window._maximize_window(animated=False)
        self.wait(700)
        self.click_at(self.window.title_bar.close_button.mapToGlobal(self.window.title_bar.close_button.rect().center()))
        self.wait(500)
        self.check("close button closes maximized window", not self.window.isVisible())

    def send_caption_double_click(self, hit_code):
        point = self.title_center()
        QCursor.setPos(point)
        self.wait(50)
        lparam = ((point.y() & 0xFFFF) << 16) | (point.x() & 0xFFFF)
        user32 = ctypes.windll.user32
        user32.SendMessageW.argtypes = [ctypes.wintypes.HWND, ctypes.wintypes.UINT, ctypes.wintypes.WPARAM, ctypes.wintypes.LPARAM]
        user32.SendMessageW.restype = ctypes.wintypes.LPARAM
        user32.SendMessageW(self.hwnd(), WM_NCLBUTTONDBLCLK, hit_code, lparam)

    def ensure_normal_geometry(self):
        if self.window.isMinimized():
            self.window.showNormal()
            self.wait(300)
        if self.window.isMaximized():
            self.window._restore_window(animated=False)
            self.wait(700)
        self.window.setGeometry(100, 100, 1200, 700)
        self.window._remember_normal_geometry(self.window.geometry())
        self.window.raise_()
        self.window.activateWindow()
        self.wait(200)

    @staticmethod
    def geometry_close(actual, expected, tolerance=8):
        return (
            abs(actual.x() - expected.x()) <= tolerance
            and abs(actual.y() - expected.y()) <= tolerance
            and abs(actual.width() - expected.width()) <= tolerance
            and abs(actual.height() - expected.height()) <= tolerance
        )


if __name__ == "__main__":
    if os.environ.get("QT_QPA_PLATFORM") == "offscreen":
        print("This verifier needs a visible platform plugin.")
        raise SystemExit(2)
    FramelessVerifier().run()
