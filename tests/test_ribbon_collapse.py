"""
Smoke tests for Ribbon collapse and temporary expansion behavior.

Run with:
    QT_QPA_PLATFORM=offscreen python tests/test_ribbon_collapse.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(
    0,
    os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "LqRibbon",
        "example",
    ),
)

from PySide6.QtCore import QEvent, Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QLabel, QStackedWidget, QToolButton

from LqRibbon import RibbonMainWindow
from main_window import MainWindow


def _app():
    app = QApplication.instance()
    return app or QApplication([])


def _window():
    window = RibbonMainWindow()
    ribbon = window.ribbonBar()
    first_page = ribbon.addPage("General")
    first_group = first_page.addGroup("Actions")
    action_hits = []
    action = first_group.addAction(
        window.style().standardIcon(window.style().StandardPixmap.SP_DialogApplyButton),
        "Apply",
        Qt.ToolButtonStyle.ToolButtonTextUnderIcon,
    )
    action.triggered.connect(lambda: action_hits.append("apply"))

    second_page = ribbon.addPage("Driver")
    second_group = second_page.addGroup("Driver Actions")
    second_action = second_group.addAction(
        window.style().standardIcon(window.style().StandardPixmap.SP_DialogApplyButton),
        "Connect",
        Qt.ToolButtonStyle.ToolButtonTextUnderIcon,
    )
    second_action.triggered.connect(lambda: action_hits.append("connect"))

    content = QLabel("content")
    window.setCentralWidget(content)
    window.resize(700, 420)
    window.show()
    _app().processEvents()
    return window, ribbon, action, second_action, action_hits


def _tab_bar(ribbon):
    return ribbon.tabBar()


def _tab_center(ribbon, index):
    return _tab_bar(ribbon).tabRect(index).center()


def _stack(ribbon):
    return ribbon.findChild(QStackedWidget)


def _command_area_visible(ribbon):
    stack = _stack(ribbon)
    return stack is not None and stack.isVisible() and stack.height() > 0


def _temporary_expanded(ribbon):
    return bool(getattr(ribbon, "_ribbon_temporary_expanded", False))


def _action_button(ribbon, action):
    for button in ribbon.findChildren(QToolButton):
        if button.defaultAction() is action:
            return button
    raise AssertionError(f"missing button for action {action.text()}")


def _click_tab(ribbon, index=0):
    QTest.mouseClick(
        _tab_bar(ribbon),
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier,
        _tab_center(ribbon, index),
    )
    _app().processEvents()


def _double_click_tab(ribbon, index=0):
    tab_bar = _tab_bar(ribbon)
    pos = _tab_center(ribbon, index)
    _send_tab_mouse(
        tab_bar,
        pos,
        QEvent.Type.MouseButtonPress,
        Qt.MouseButton.LeftButton,
        Qt.MouseButton.LeftButton,
    )
    _send_tab_mouse(
        tab_bar,
        pos,
        QEvent.Type.MouseButtonRelease,
        Qt.MouseButton.LeftButton,
        Qt.MouseButton.NoButton,
    )
    _send_tab_mouse(
        tab_bar,
        pos,
        QEvent.Type.MouseButtonDblClick,
        Qt.MouseButton.LeftButton,
        Qt.MouseButton.LeftButton,
    )
    _send_tab_mouse(
        tab_bar,
        pos,
        QEvent.Type.MouseButtonRelease,
        Qt.MouseButton.LeftButton,
        Qt.MouseButton.NoButton,
    )


def _send_tab_mouse(tab_bar, pos, event_type, button, buttons):
    event = QMouseEvent(
        event_type,
        pos,
        tab_bar.mapToGlobal(pos),
        button,
        buttons,
        Qt.KeyboardModifier.NoModifier,
    )
    QApplication.sendEvent(tab_bar, event)
    _app().processEvents()


def test_double_click_expanded_tab_collapses():
    window, ribbon, *_ = _window()
    _double_click_tab(ribbon, 0)
    assert ribbon.isRibbonMinimized()
    assert not _temporary_expanded(ribbon)
    assert not _command_area_visible(ribbon)
    window.close()


def test_double_click_collapsed_tab_restores():
    window, ribbon, *_ = _window()
    ribbon.setRibbonMinimized(True)
    _double_click_tab(ribbon, 0)
    assert not ribbon.isRibbonMinimized()
    assert _command_area_visible(ribbon)
    window.close()


def test_collapse_button_collapses():
    window, ribbon, *_ = _window()
    collapse_button = getattr(ribbon, "_collapse_button")
    QTest.mouseClick(collapse_button, Qt.MouseButton.LeftButton)
    _app().processEvents()
    assert ribbon.isRibbonMinimized()
    assert not _command_area_visible(ribbon)
    window.close()


def test_simplified_mode_keeps_one_line_command_area():
    window, ribbon, *_ = _window()
    full_height = ribbon.height()
    simplified_action = ribbon.simplifiedAction()
    ribbon.setSimplifiedMode(True)
    _app().processEvents()
    assert ribbon.simplifiedMode()
    assert simplified_action.isChecked()
    assert not ribbon.isRibbonMinimized()
    assert _command_area_visible(ribbon)
    assert ribbon.height() < full_height

    ribbon.setSimplifiedMode(False)
    _app().processEvents()
    assert not ribbon.simplifiedMode()
    assert not simplified_action.isChecked()
    assert ribbon.height() >= full_height
    window.close()


def test_example_classic_action_restores_multi_line_ribbon():
    window = MainWindow()
    window.show()
    _app().processEvents()
    ribbon = window.ribbonBar()
    full_height = ribbon.height()
    ribbon.setSimplifiedMode(True)
    ribbon.setRibbonMinimized(True)
    window.classic_ribbon_action.trigger()
    _app().processEvents()
    assert not ribbon.simplifiedMode()
    assert not ribbon.isRibbonMinimized()
    assert _command_area_visible(ribbon)
    assert ribbon.height() >= full_height
    window.close()


def test_example_pin_unpin_actions_control_display_policy():
    window = MainWindow()
    window.show()
    _app().processEvents()
    ribbon = window.ribbonBar()

    ribbon.setRibbonMinimized(True)
    window.pin_ribbon_action.trigger()
    _app().processEvents()
    assert not ribbon.isMinimizationEnabled()
    assert not ribbon.isRibbonMinimized()
    assert _command_area_visible(ribbon)

    _double_click_tab(ribbon, 0)
    assert not ribbon.isRibbonMinimized()
    assert _command_area_visible(ribbon)

    window.unpin_ribbon_action.trigger()
    _app().processEvents()
    assert ribbon.isMinimizationEnabled()
    assert ribbon.isRibbonMinimized()
    assert not _command_area_visible(ribbon)

    _click_tab(ribbon, 0)
    assert ribbon.isRibbonMinimized()
    assert _command_area_visible(ribbon)
    window.close()


def test_example_display_options_menu_controls_ribbon_modes():
    window = MainWindow()
    window.show()
    _app().processEvents()
    ribbon = window.ribbonBar()
    menu = window.display_options_title_action.menu()
    assert menu is window.display_options_menu
    assert [action.text() for action in menu.actions()] == [
        "Show Tabs and Commands",
        "Show Tabs Only",
        "Always Show Ribbon",
        "Auto-Hide Ribbon",
    ]

    window.display_show_tabs_only_action.trigger()
    _app().processEvents()
    assert ribbon.isMinimizationEnabled()
    assert ribbon.isRibbonMinimized()
    assert not _command_area_visible(ribbon)

    window.display_show_tabs_commands_action.trigger()
    _app().processEvents()
    assert ribbon.isMinimizationEnabled()
    assert not ribbon.simplifiedMode()
    assert not ribbon.isRibbonMinimized()
    assert _command_area_visible(ribbon)

    ribbon.setSimplifiedMode(True)
    window.display_always_show_action.trigger()
    _app().processEvents()
    assert not ribbon.isMinimizationEnabled()
    assert not ribbon.simplifiedMode()
    assert not ribbon.isRibbonMinimized()
    assert _command_area_visible(ribbon)

    window.display_auto_hide_action.trigger()
    _app().processEvents()
    assert ribbon.isMinimizationEnabled()
    assert not ribbon.simplifiedMode()
    assert ribbon.isRibbonMinimized()
    assert not _command_area_visible(ribbon)
    window.close()


def test_single_click_collapsed_tab_temporarily_expands():
    window, ribbon, *_ = _window()
    ribbon.setRibbonMinimized(True)
    _click_tab(ribbon, 0)
    assert ribbon.isRibbonMinimized()
    assert _temporary_expanded(ribbon)
    assert _command_area_visible(ribbon)
    window.close()


def test_action_triggers_while_temporarily_expanded():
    window, ribbon, action, _, action_hits = _window()
    action_saw_command_area = []
    action.triggered.connect(lambda: action_saw_command_area.append(_command_area_visible(ribbon)))
    ribbon.setRibbonMinimized(True)
    _click_tab(ribbon, 0)
    button = _action_button(ribbon, action)
    QTest.mouseClick(button, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier, button.rect().center())
    _app().processEvents()
    assert action_hits == ["apply"]
    assert action_saw_command_area == [True]
    window.close()


def test_action_hides_temporary_expansion():
    window, ribbon, action, _, _ = _window()
    ribbon.setRibbonMinimized(True)
    _click_tab(ribbon, 0)
    button = _action_button(ribbon, action)
    QTest.mouseClick(button, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier, button.rect().center())
    _app().processEvents()
    assert ribbon.isRibbonMinimized()
    assert not _temporary_expanded(ribbon)
    assert not _command_area_visible(ribbon)
    window.close()


def test_outside_click_hides_temporary_expansion():
    window, ribbon, *_ = _window()
    ribbon.setRibbonMinimized(True)
    _click_tab(ribbon, 0)
    QTest.mouseClick(window.centralWidget(), Qt.MouseButton.LeftButton)
    _app().processEvents()
    assert ribbon.isRibbonMinimized()
    assert not _temporary_expanded(ribbon)
    assert not _command_area_visible(ribbon)
    window.close()


def test_double_click_temporary_expanded_tab_restores_permanently():
    window, ribbon, *_ = _window()
    ribbon.setRibbonMinimized(True)
    _click_tab(ribbon, 0)
    _double_click_tab(ribbon, 0)
    assert not ribbon.isRibbonMinimized()
    assert not _temporary_expanded(ribbon)
    assert _command_area_visible(ribbon)
    window.close()


def test_collapsed_click_other_page_temporarily_expands_selected_page():
    window, ribbon, _, second_action, action_hits = _window()
    ribbon.setRibbonMinimized(True)
    _click_tab(ribbon, 1)
    assert ribbon.currentIndex() == 1
    assert ribbon.isRibbonMinimized()
    assert _temporary_expanded(ribbon)
    button = _action_button(ribbon, second_action)
    QTest.mouseClick(button, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier, button.rect().center())
    _app().processEvents()
    assert action_hits == ["connect"]
    window.close()


def test_minimization_disabled_blocks_collapse():
    window, ribbon, *_ = _window()
    ribbon.setMinimizationEnabled(False)
    _double_click_tab(ribbon, 0)
    assert not ribbon.isRibbonMinimized()
    assert _command_area_visible(ribbon)
    window.close()


def main():
    _app()
    tests = [
        test_double_click_expanded_tab_collapses,
        test_double_click_collapsed_tab_restores,
        test_collapse_button_collapses,
        test_simplified_mode_keeps_one_line_command_area,
        test_example_classic_action_restores_multi_line_ribbon,
        test_example_pin_unpin_actions_control_display_policy,
        test_example_display_options_menu_controls_ribbon_modes,
        test_single_click_collapsed_tab_temporarily_expands,
        test_action_triggers_while_temporarily_expanded,
        test_action_hides_temporary_expansion,
        test_outside_click_hides_temporary_expansion,
        test_double_click_temporary_expanded_tab_restores_permanently,
        test_collapsed_click_other_page_temporarily_expands_selected_page,
        test_minimization_disabled_blocks_collapse,
    ]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")


if __name__ == "__main__":
    main()
