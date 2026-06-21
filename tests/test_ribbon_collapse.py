"""
Smoke tests for Ribbon collapse and temporary expansion behavior.

Run with:
    QT_QPA_PLATFORM=offscreen python tests/test_ribbon_collapse.py
"""

import os
import sys
import json

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
from PySide6.QtWidgets import QApplication, QLabel, QMenu, QStackedWidget, QToolButton

from LqRibbon import RibbonMainWindow
from main_window import (
    MainWindow,
    QUICK_ACCESS_BOTTOM_POSITION,
    QUICK_ACCESS_TOP_POSITION,
    SEARCH_BAR_COMPACT,
    SEARCH_BAR_CENTRAL,
    SEARCH_BAR_HIDDEN,
)


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
    assert ribbon.rowItemCount() == 3
    assert ribbon.rowItemHeight() > 0

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


def test_example_feedback_title_button_is_available():
    window = MainWindow()
    window.show()
    _app().processEvents()
    ribbon = window.ribbonBar()
    title_bar = ribbon._title_button_bar
    feedback_button = title_bar.widgetForAction(window.feedback_title_action)

    assert window.feedback_title_action.objectName() == "feedbackTitleAction"
    assert not window.feedback_title_action.icon().isNull()
    assert "feedback" in window.feedback_title_action.toolTip()
    assert window.feedback_title_action in title_bar.actions()
    assert isinstance(feedback_button, QToolButton)
    assert feedback_button.toolButtonStyle() == Qt.ToolButtonStyle.ToolButtonIconOnly

    window.feedback_title_action.trigger()
    _app().processEvents()
    assert "Feedback" in window.statusBar().currentMessage()
    window.close()


def test_example_account_title_button_is_available():
    window = MainWindow()
    window.show()
    _app().processEvents()
    ribbon = window.ribbonBar()
    title_bar = ribbon._title_button_bar
    account_button = title_bar.widgetForAction(window.account_title_action)

    assert window.account_title_action.objectName() == "accountTitleAction"
    assert not window.account_title_action.icon().isNull()
    assert "profile" in window.account_title_action.toolTip()
    assert window.account_title_action in title_bar.actions()
    assert isinstance(account_button, QToolButton)
    assert account_button.toolButtonStyle() == Qt.ToolButtonStyle.ToolButtonIconOnly

    window.account_title_action.trigger()
    _app().processEvents()
    assert "Account" in window.statusBar().currentMessage()
    window.close()


def test_example_share_title_button_is_available():
    window = MainWindow()
    window.show()
    _app().processEvents()
    ribbon = window.ribbonBar()
    title_bar = ribbon._title_button_bar
    share_button = title_bar.widgetForAction(window.share_title_action)

    assert window.share_title_action.objectName() == "shareTitleAction"
    assert not window.share_title_action.icon().isNull()
    assert "Share" in window.share_title_action.text()
    assert "document" in window.share_title_action.toolTip()
    assert window.share_title_action in title_bar.actions()
    assert isinstance(share_button, QToolButton)
    assert share_button.toolButtonStyle() == Qt.ToolButtonStyle.ToolButtonIconOnly

    window.share_title_action.trigger()
    _app().processEvents()
    assert "Share" in window.statusBar().currentMessage()
    window.close()


def test_example_auto_save_title_toggle_is_available():
    window = MainWindow()
    window.show()
    _app().processEvents()
    title_bar = window.ribbonBar()._title_button_bar
    auto_save_button = title_bar.widgetForAction(window.auto_save_title_action)

    assert window.auto_save_title_action.objectName() == "autoSaveTitleAction"
    assert window.auto_save_title_action.isCheckable()
    assert window.auto_save_title_action.isChecked()
    assert not window.auto_save_title_action.icon().isNull()
    assert "AutoSave" in window.auto_save_title_action.text()
    assert "on" in window.auto_save_title_action.toolTip()
    assert window.auto_save_title_action in title_bar.actions()
    assert isinstance(auto_save_button, QToolButton)
    assert auto_save_button.toolButtonStyle() == Qt.ToolButtonStyle.ToolButtonIconOnly

    window.auto_save_title_action.trigger()
    _app().processEvents()
    assert not window.auto_save_title_action.isChecked()
    assert "off" in window.auto_save_title_action.toolTip()
    assert "AutoSave: off" in window.statusBar().currentMessage()

    window.auto_save_title_action.trigger()
    _app().processEvents()
    assert window.auto_save_title_action.isChecked()
    assert "AutoSave: on" in window.statusBar().currentMessage()
    window.close()


def test_example_auto_save_disabled_explanation_is_available():
    window = MainWindow()
    window.show()
    _app().processEvents()

    window.auto_save_title_action.trigger()
    _app().processEvents()
    assert not window.auto_save_title_action.isChecked()
    assert "local draft" in window.auto_save_title_action.toolTip()
    assert "cloud location" in window.auto_save_title_action.toolTip()
    assert "save to cloud" in window.auto_save_title_action.statusTip()
    assert "save to cloud" in window.statusBar().currentMessage()
    window.close()


def test_example_comments_title_button_is_available():
    window = MainWindow()
    window.show()
    _app().processEvents()
    ribbon = window.ribbonBar()
    title_bar = ribbon._title_button_bar
    comments_button = title_bar.widgetForAction(window.comments_title_action)

    assert window.comments_title_action.objectName() == "commentsTitleAction"
    assert not window.comments_title_action.icon().isNull()
    assert "Comments" in window.comments_title_action.text()
    assert "comments" in window.comments_title_action.toolTip()
    assert window.comments_title_action in title_bar.actions()
    assert isinstance(comments_button, QToolButton)
    assert comments_button.toolButtonStyle() == Qt.ToolButtonStyle.ToolButtonIconOnly

    window.comments_title_action.trigger()
    _app().processEvents()
    assert "Comments" in window.statusBar().currentMessage()
    window.close()


def test_example_presence_avatar_strip_is_available():
    window = MainWindow()
    window.show()
    _app().processEvents()
    title_bar = window.ribbonBar()._title_button_bar
    action = window.presence_avatar_strip_action
    button = title_bar.widgetForAction(action)

    assert action.objectName() == "presenceAvatarStripAction"
    assert "Presence" in action.text()
    assert "Alice Chen" in action.toolTip()
    assert "Bo Li" in action.toolTip()
    assert "Maya Patel" in action.toolTip()
    assert "editing" in action.toolTip()
    assert not action.icon().isNull()
    assert action in title_bar.actions()
    assert isinstance(button, QToolButton)
    assert button.toolButtonStyle() == Qt.ToolButtonStyle.ToolButtonIconOnly

    action.trigger()
    _app().processEvents()
    assert "Presence" in window.statusBar().currentMessage()
    assert "3 collaborators" in window.statusBar().currentMessage()
    window.close()


def test_example_collaboration_status_text_is_available():
    window = MainWindow()
    window.show()
    _app().processEvents()
    label = window.collaboration_status_label

    assert label.objectName() == "collaborationStatusText"
    assert label.isVisible()
    assert "Saved to cloud" in label.text()
    assert "3 editors" in label.text()
    assert "Collaboration status" in label.toolTip()

    window.statusBar().showMessage("Transient command message", 100)
    _app().processEvents()
    assert label.text() == "Saved to cloud | 3 editors"
    window.close()


def test_example_coauthoring_indicator_is_available():
    window = MainWindow()
    window.show()
    _app().processEvents()
    dot = window.coauthoring_indicator_dot
    label = window.coauthoring_indicator_label

    assert dot.objectName() == "coauthoringIndicatorDot"
    assert dot.isVisible()
    assert dot.width() == 10
    assert dot.height() == 10
    assert "#107c41" in dot.styleSheet()
    assert "coauthoring" in dot.toolTip().lower()
    assert label.objectName() == "coauthoringIndicator"
    assert label.isVisible()
    assert label.text() == "Coauthoring"
    assert "coauthoring" in label.toolTip().lower()
    window.close()


def test_example_version_history_entry_is_available():
    window = MainWindow()
    window.show()
    _app().processEvents()

    assert window.version_history_action.objectName() == "versionHistoryAction"
    assert window.version_history_action.isCheckable()
    assert "Version History" in window.version_history_action.text()
    assert "version history" in window.version_history_action.toolTip()
    assert window.version_history_page.objectName() == "versionHistoryPage"
    assert (
        window.backstage._action_pages[window.version_history_action]
        is window.version_history_page
    )

    window.backstage.setActivePage(window.version_history_page)
    _app().processEvents()
    assert window.backstage.activePage() is window.version_history_page
    assert window.version_history_action.isChecked()
    assert "Saved 2 minutes ago" in window.version_history_current_label.text()

    window.version_history_action.trigger()
    _app().processEvents()
    assert "Version History" in window.statusBar().currentMessage()
    window.close()


def test_example_save_copy_replaces_save_as_backstage_command():
    window = MainWindow()
    window.show()
    _app().processEvents()

    action = window.save_copy_action
    action_texts = [
        child.text()
        for child in window.backstage.findChildren(type(action))
        if not child.isSeparator()
    ]

    assert action.objectName() == "saveCopyAction"
    assert action.text() == "Save a Copy"
    assert "separate copy" in action.toolTip()
    assert "Save a Copy" in action.statusTip()
    assert "Save a Copy" in action_texts
    assert "Save As" not in action_texts

    action.trigger()
    _app().processEvents()
    assert "Save a Copy" in window.statusBar().currentMessage()
    window.close()


def test_example_cloud_location_picker_is_available():
    window = MainWindow()
    window.show()
    _app().processEvents()

    combo = window.cloud_location_combo
    assert combo.objectName() == "cloudLocationPicker"
    assert combo.count() == 3
    assert combo.currentText() == "OneDrive - Contoso"
    assert combo.findText("SharePoint Team Site") >= 0
    assert "cloud location" in combo.toolTip()

    combo.setCurrentText("SharePoint Team Site")
    _app().processEvents()
    assert combo.currentText() == "SharePoint Team Site"
    assert "SharePoint Team Site" in window.statusBar().currentMessage()
    window.close()


def test_example_caption_search_defaults_to_centered_microsoft_box():
    window = MainWindow()
    window.show()
    _app().processEvents()
    ribbon = window.ribbonBar()
    search = ribbon.searchLineEdit()
    search_geometry = search.geometry()

    assert ribbon.searchBarAppearance() == SEARCH_BAR_CENTRAL
    assert search.isVisible()
    assert search.placeholderText() == "Search commands"
    assert search_geometry.width() >= 120
    assert abs(search_geometry.center().x() - ribbon.rect().center().x()) <= 2
    window.close()


def test_example_compact_search_action_switches_caption_search_to_icon_mode():
    window = MainWindow()
    window.show()
    _app().processEvents()
    ribbon = window.ribbonBar()
    search = ribbon.searchLineEdit()
    central_width = search.geometry().width()

    window.compact_search_action.trigger()
    _app().processEvents()
    compact_geometry = search.geometry()
    assert ribbon.searchBarAppearance() == SEARCH_BAR_COMPACT
    assert window.compact_search_action.isChecked()
    assert not window.center_search_action.isChecked()
    assert search.isVisible()
    assert search.isCompact()
    assert compact_geometry.width() <= 44
    assert abs(compact_geometry.center().x() - ribbon.rect().center().x()) <= 2

    window.center_search_action.trigger()
    _app().processEvents()
    assert ribbon.searchBarAppearance() == SEARCH_BAR_CENTRAL
    assert window.center_search_action.isChecked()
    assert not window.compact_search_action.isChecked()
    assert not search.isCompact()
    assert search.geometry().width() > compact_geometry.width()
    assert search.geometry().width() == central_width
    window.close()


def test_example_hidden_search_action_removes_caption_search_box():
    window = MainWindow()
    window.show()
    _app().processEvents()
    ribbon = window.ribbonBar()
    search = ribbon.searchLineEdit()

    window.hidden_search_action.trigger()
    _app().processEvents()
    assert ribbon.searchBarAppearance() == SEARCH_BAR_HIDDEN
    assert window.hidden_search_action.isChecked()
    assert not window.center_search_action.isChecked()
    assert not window.compact_search_action.isChecked()
    assert not search.isVisible()
    assert not search.isCompact()

    window.center_search_action.trigger()
    _app().processEvents()
    assert ribbon.searchBarAppearance() == SEARCH_BAR_CENTRAL
    assert window.center_search_action.isChecked()
    assert search.isVisible()
    assert not search.isCompact()
    window.close()


def test_example_alt_q_restores_and_focuses_caption_search():
    window = MainWindow()
    window.show()
    _app().processEvents()
    ribbon = window.ribbonBar()
    search = ribbon.searchLineEdit()

    window.hidden_search_action.trigger()
    search.clearFocus()
    window.setFocus()
    _app().processEvents()
    assert not search.isVisible()

    QTest.keyClick(
        window,
        Qt.Key.Key_Q,
        Qt.KeyboardModifier.AltModifier,
    )
    _app().processEvents()
    assert ribbon.searchBarAppearance() == SEARCH_BAR_CENTRAL
    assert window.focus_search_action.shortcut().toString() == "Alt+Q"
    assert window.center_search_action.isChecked()
    assert search.isVisible()
    assert search.hasFocus()
    window.close()


def test_example_search_enter_triggers_registered_action():
    window = MainWindow()
    window.show()
    _app().processEvents()
    ribbon = window.ribbonBar()
    search = ribbon.searchLineEdit()

    window.center_search_action.trigger()
    search.setFocus()
    search.setText("Compact Search")
    QTest.keyClick(search, Qt.Key.Key_Return)
    _app().processEvents()

    assert ribbon.searchBarAppearance() == SEARCH_BAR_COMPACT
    assert window.compact_search_action.isChecked()
    assert ribbon.recentSearchActions()[0] is window.compact_search_action
    assert search.text() == ""
    window.close()


def test_example_zero_query_search_shows_default_suggestions():
    window = MainWindow()
    window.show()
    _app().processEvents()
    search = window.ribbonBar().searchLineEdit()

    search.setFocus()
    search.clear()
    search.showPopup("")
    _app().processEvents()
    popup_actions = [action.text() for action in search._popup.actions()]

    assert popup_actions[:7] == [
        "Suggested Actions",
        "Settings",
        "Connect",
        "Control Modes",
        "Center Search",
        "Actions",
        "Full Screen",
    ]
    assert search._popup.isVisible()
    search.closePopup()
    window.close()


def test_example_zero_query_search_groups_recent_actions():
    window = MainWindow()
    window.show()
    _app().processEvents()
    ribbon = window.ribbonBar()
    search = ribbon.searchLineEdit()

    assert ribbon.triggerSearchAction("Control Modes")
    assert ribbon.triggerSearchAction("Center Search")
    search.setFocus()
    search.clear()
    search.showPopup("")
    _app().processEvents()
    popup_rows = [action.text() for action in search._popup.actions()]

    assert [action.text() for action in ribbon.recentSearchActions()[:2]] == [
        "Center Search",
        "Control Modes",
    ]
    assert popup_rows[:7] == [
        "Recently Used",
        "Center Search",
        "Control Modes",
        "Suggested Actions",
        "Settings",
        "Connect",
        "Actions",
    ]
    search.closePopup()
    window.close()


def test_example_search_keyboard_navigation_activates_popup_action():
    window = MainWindow()
    window.show()
    _app().processEvents()
    ribbon = window.ribbonBar()
    search = ribbon.searchLineEdit()

    ribbon.clearRecentSearchActions()
    search.setFocus()
    search.clear()
    search.showPopup("")
    _app().processEvents()

    QTest.keyClick(search, Qt.Key.Key_Down)
    _app().processEvents()
    assert search._popup.activeAction().text() == "Settings"

    QTest.keyClick(search, Qt.Key.Key_Down)
    _app().processEvents()
    assert search._popup.activeAction().text() == "Connect"

    QTest.keyClick(search, Qt.Key.Key_Down)
    _app().processEvents()
    assert search._popup.activeAction().text() == "Control Modes"

    QTest.keyClick(search, Qt.Key.Key_Return)
    _app().processEvents()
    assert ribbon.recentSearchActions()[0] is window.control_modes_action
    assert not search._popup.isVisible()
    assert search.text() == ""
    assert search.hasFocus()

    search.setText("driver")
    search.showPopup("driver")
    _app().processEvents()
    QTest.keyClick(search, Qt.Key.Key_Escape)
    _app().processEvents()
    assert not search._popup.isVisible()
    assert search.text() == "driver"
    assert search.hasFocus()
    window.close()


def test_example_search_command_alias_matches_registered_action():
    window = MainWindow()
    window.show()
    _app().processEvents()
    ribbon = window.ribbonBar()
    search = ribbon.searchLineEdit()

    ribbon.clearRecentSearchActions()
    search.setFocus()
    search.setText("axis")
    search.showPopup("axis")
    _app().processEvents()
    popup_rows = [action.text() for action in search._popup.actions()]

    assert popup_rows[:2] == ["Actions", "Control Modes"]
    assert ribbon.triggerSearchAction("Axis Profile")
    assert ribbon.recentSearchActions()[0] is window.control_modes_action
    search.closePopup()
    window.close()


def test_example_search_fuzzy_phrase_matches_registered_action():
    window = MainWindow()
    window.show()
    _app().processEvents()
    ribbon = window.ribbonBar()
    search = ribbon.searchLineEdit()

    ribbon.clearRecentSearchActions()
    search.setFocus()
    search.setText("ctrl mode")
    search.showPopup("ctrl mode")
    _app().processEvents()
    popup_rows = [action.text() for action in search._popup.actions()]

    assert popup_rows[:2] == ["Actions", "Control Modes"]
    assert ribbon.triggerSearchAction("ctrl mode")
    assert ribbon.recentSearchActions()[0] is window.control_modes_action
    search.closePopup()
    window.close()


def test_example_search_shows_document_result_section():
    window = MainWindow()
    window.show()
    _app().processEvents()
    search = window.ribbonBar().searchLineEdit()

    search.setFocus()
    search.setText("driver")
    search.showPopup("driver")
    _app().processEvents()
    popup_rows = [action.text() for action in search._popup.actions()]

    assert popup_rows[:4] == [
        "Document Results",
        "Driver commissioning checklist",
        "Actions",
        "Driver Configuration",
    ]
    assert popup_rows.index('Get Help "driver"') > popup_rows.index("Actions")
    search.closePopup()
    window.close()


def test_example_search_no_result_affordance_keeps_help_path():
    window = MainWindow()
    window.show()
    _app().processEvents()
    search = window.ribbonBar().searchLineEdit()

    search.setFocus()
    search.setText("zzzz-missing")
    search.showPopup("zzzz-missing")
    _app().processEvents()
    popup_actions = search._popup.actions()
    popup_rows = [action.text() for action in popup_actions]
    no_result_action = next(
        action
        for action in popup_actions
        if action.text() == 'No results found for "zzzz-missing"'
    )

    assert popup_rows[:4] == [
        "No Results",
        'No results found for "zzzz-missing"',
        "Help",
        'Get Help "zzzz-missing"',
    ]
    assert not no_result_action.isEnabled()
    assert search._popup.activeAction().text() == 'Get Help "zzzz-missing"'
    search.closePopup()
    window.close()


def test_example_search_shows_help_result_section():
    window = MainWindow()
    window.show()
    _app().processEvents()
    search = window.ribbonBar().searchLineEdit()

    search.setFocus()
    search.setText("sensor")
    search.showPopup("sensor")
    _app().processEvents()
    popup_rows = [action.text() for action in search._popup.actions()]

    assert popup_rows[:4] == [
        "No Results",
        'No results found for "sensor"',
        "Help",
        'Get Help "sensor"',
    ]
    assert search._popup.isVisible()
    search.closePopup()
    window.close()


def test_example_search_shows_related_file_result_section():
    window = MainWindow()
    window.show()
    _app().processEvents()
    search = window.ribbonBar().searchLineEdit()

    search.setFocus()
    search.setText("project")
    search.showPopup("project")
    _app().processEvents()
    popup_rows = [action.text() for action in search._popup.actions()]

    assert popup_rows[:2] == [
        "Related Files",
        "Servo project notes.one",
    ]
    assert popup_rows.index("Help") > popup_rows.index("Related Files")
    search.closePopup()
    window.close()


def test_example_smart_lookup_command_surface():
    window = MainWindow()
    window.show()
    _app().processEvents()
    ribbon = window.ribbonBar()

    ribbon.setCurrentPageIndex(ribbon.pageIndex(window.review_page))
    _app().processEvents()

    assert ribbon.pageIndex(window.review_page) >= 0
    assert window.smart_lookup_action.objectName() == "smartLookupAction"
    assert not window.smart_lookup_action.icon().isNull()
    assert "contextual insights" in window.smart_lookup_action.toolTip()
    assert window.smart_lookup_preview.text() == "Select text to look up insights"
    assert window.smart_lookup_action in window.search_actions
    assert ribbon.searchAction("Smart Lookup") is window.smart_lookup_action

    window.smart_lookup_action.trigger()
    _app().processEvents()
    assert window.smart_lookup_preview.text() == "Insights ready for selected text"
    assert "Smart Lookup" in window.statusBar().currentMessage()
    window.close()


def test_example_tell_me_lightbulb_entry_is_available():
    window = MainWindow()
    window.show()
    _app().processEvents()
    ribbon = window.ribbonBar()

    ribbon.setCurrentPageIndex(ribbon.pageIndex(window.tell_me_page))
    _app().processEvents()

    assert ribbon.pageIndex(window.tell_me_page) >= 0
    assert window.tell_me_lightbulb_action.objectName() == "tellMeLightbulbAction"
    assert not window.tell_me_lightbulb_action.icon().isNull()
    assert "command discovery" in window.tell_me_lightbulb_action.toolTip()
    assert window.tell_me_entry_preview.text() == "Ask for a command or phrase"
    assert window.tell_me_lightbulb_action in window.search_actions
    assert ribbon.searchAction("Tell Me") is window.tell_me_lightbulb_action

    window.tell_me_lightbulb_action.trigger()
    _app().processEvents()
    assert "Tell Me" in window.statusBar().currentMessage()
    window.close()


def test_example_tell_me_phrase_examples_drive_search_text():
    window = MainWindow()
    window.show()
    _app().processEvents()
    ribbon = window.ribbonBar()
    search = ribbon.searchLineEdit()
    phrases = [
        "Change the ribbon display",
        "Find driver settings",
        "Customize quick access toolbar",
    ]

    assert [action.text() for action in window.tell_me_phrase_actions] == phrases
    assert [
        action.objectName() for action in window.tell_me_phrase_actions
    ] == [
        "tellMePhraseRibbonDisplayAction",
        "tellMePhraseDriverSettingsAction",
        "tellMePhraseCustomizeQatAction",
    ]

    window.hidden_search_action.trigger()
    _app().processEvents()
    assert not search.isVisible()

    window.tell_me_phrase_actions[1].trigger()
    _app().processEvents()
    assert ribbon.searchText() == "Find driver settings"
    assert search.isVisible()
    assert search.hasFocus()
    assert window.center_search_action.isChecked()
    assert "Find driver settings" in window.statusBar().currentMessage()
    window.close()


def test_example_tell_me_help_redirect_opens_help_search_path():
    window = MainWindow()
    window.show()
    _app().processEvents()
    ribbon = window.ribbonBar()
    search = ribbon.searchLineEdit()

    assert (
        window.tell_me_help_redirect_action.objectName()
        == "tellMeHelpRedirectAction"
    )
    assert not window.tell_me_help_redirect_action.icon().isNull()
    assert (
        window.tell_me_help_redirect_preview.text()
        == "Help redirects unmatched phrases"
    )
    assert window.tell_me_help_redirect_action in window.search_actions
    assert (
        ribbon.searchAction("Open Tell Me Help")
        is window.tell_me_help_redirect_action
    )

    window.hidden_search_action.trigger()
    ribbon.setSearchText("")
    _app().processEvents()
    assert not search.isVisible()

    window.tell_me_help_redirect_action.trigger()
    _app().processEvents()
    popup_rows = [action.text() for action in search._popup.actions()]
    assert ribbon.searchText() == "unmatched Tell Me phrase"
    assert search.isVisible()
    assert search.hasFocus()
    assert window.center_search_action.isChecked()
    assert "Tell Me help" in window.statusBar().currentMessage()
    assert "No Results" in popup_rows
    assert "Help" in popup_rows
    assert 'Get Help "unmatched Tell Me phrase"' in popup_rows
    search.closePopup()
    window.close()


def test_example_collapse_state_preview_tracks_modes():
    window = MainWindow()
    window.show()
    _app().processEvents()
    ribbon = window.ribbonBar()
    preview = window.collapse_state_preview
    density_preview = window.density_status_preview

    assert "Expanded" in preview.text()
    assert "Expanded" in density_preview.text()
    assert str(ribbon.rowItemCount()) in density_preview.text()
    assert str(ribbon.rowItemHeight()) in density_preview.text()

    ribbon.setRibbonMinimized(True)
    _app().processEvents()
    assert "Collapsed" in preview.text()

    ribbon.setRibbonMinimized(False)
    ribbon.setSimplifiedMode(True)
    _app().processEvents()
    assert "Simplified" in preview.text()
    assert "Compact" in density_preview.text()
    assert str(ribbon.rowItemHeight()) in density_preview.text()

    ribbon.setSimplifiedMode(False)
    _app().processEvents()
    assert "Expanded" in density_preview.text()
    assert str(ribbon.rowItemCount()) in density_preview.text()
    assert str(ribbon.rowItemHeight()) in density_preview.text()

    window.pin_ribbon_action.trigger()
    _app().processEvents()
    assert "Pinned" in preview.text()

    window.display_auto_hide_action.trigger()
    _app().processEvents()
    assert "Collapsed" in preview.text()

    _click_tab(ribbon, 0)
    assert ribbon.isRibbonTemporaryExpanded()
    assert "Temporary" in preview.text()
    window.close()


def test_example_double_click_preview_tracks_modes():
    window = MainWindow()
    window.show()
    _app().processEvents()
    ribbon = window.ribbonBar()
    preview = window.double_click_state_preview

    assert "Collapse" in preview.text()

    ribbon.setRibbonMinimized(True)
    _app().processEvents()
    assert "Restore" in preview.text()

    _click_tab(ribbon, 0)
    assert ribbon.isRibbonTemporaryExpanded()
    assert "Restore" in preview.text()

    _double_click_tab(ribbon, 0)
    assert not ribbon.isRibbonMinimized()
    assert "Collapse" in preview.text()

    window.pin_ribbon_action.trigger()
    _app().processEvents()
    assert "Locked" in preview.text()
    window.close()


def test_example_quick_access_menu_controls_toolbar_visibility():
    window = MainWindow()
    window.show()
    _app().processEvents()
    quick_access_bar = window.ribbonBar().quickAccessBar()
    status = window.quick_access_status_preview

    menu = QMenu(window)
    window.populate_quick_access_menu(menu)
    assert window.show_quick_access_action in menu.actions()
    assert window.quick_access_above_action in menu.actions()
    assert window.quick_access_below_action in menu.actions()
    assert window.quick_access_labels_action in menu.actions()
    assert window.show_quick_access_action.isChecked()
    assert window.quick_access_above_action.isChecked()
    assert not window.quick_access_labels_action.isChecked()
    assert window.ribbonBar().quickAccessBarPosition() == QUICK_ACCESS_TOP_POSITION
    assert not quick_access_bar.isHidden()
    assert quick_access_bar.visibleCount() == 3
    assert quick_access_bar.toolButtonStyle() == Qt.ToolButtonStyle.ToolButtonIconOnly
    assert "Visible 3/3" in status.text()
    assert "Above" in status.text()
    assert "Icons" in status.text()

    window.show_quick_access_action.trigger()
    _app().processEvents()
    assert quick_access_bar.isHidden()
    assert not window.show_quick_access_action.isChecked()
    assert "Hidden 0/3" in status.text()

    window.show_quick_access_action.trigger()
    _app().processEvents()
    assert not quick_access_bar.isHidden()
    assert window.show_quick_access_action.isChecked()
    assert "Visible 3/3" in status.text()
    window.quick_access_below_action.trigger()
    _app().processEvents()
    assert window.ribbonBar().quickAccessBarPosition() == QUICK_ACCESS_BOTTOM_POSITION
    assert window.quick_access_below_action.isChecked()
    assert not window.quick_access_above_action.isChecked()
    assert "Below" in status.text()
    assert quick_access_bar.y() > window.ribbonBar().tabBar().geometry().bottom()
    window.quick_access_above_action.trigger()
    _app().processEvents()
    assert window.ribbonBar().quickAccessBarPosition() == QUICK_ACCESS_TOP_POSITION
    assert window.quick_access_above_action.isChecked()
    assert "Above" in status.text()

    window.quick_access_labels_action.trigger()
    _app().processEvents()
    assert window.quick_access_labels_action.isChecked()
    assert (
        quick_access_bar.toolButtonStyle()
        == Qt.ToolButtonStyle.ToolButtonTextBesideIcon
    )
    assert "Labels" in status.text()
    assert (
        quick_access_bar.widgetForAction(window.full_screen_action).toolButtonStyle()
        == Qt.ToolButtonStyle.ToolButtonTextBesideIcon
    )

    window.quick_access_labels_action.trigger()
    _app().processEvents()
    assert not window.quick_access_labels_action.isChecked()
    assert quick_access_bar.toolButtonStyle() == Qt.ToolButtonStyle.ToolButtonIconOnly
    assert "Icons" in status.text()
    window.close()


def test_example_action_context_menu_adds_command_to_quick_access():
    window = MainWindow()
    window.show()
    _app().processEvents()
    quick_access_bar = window.ribbonBar().quickAccessBar()

    menu = QMenu(window)
    add_action = window.populate_action_context_menu(menu, window.rename_page_action)
    assert add_action is not None
    assert add_action.objectName() == "addToQuickAccessContextAction"
    assert add_action.isEnabled()
    assert "Add to Quick Access Toolbar" in add_action.text()
    assert window.rename_page_action not in quick_access_bar.actions()

    add_action.trigger()
    _app().processEvents()
    assert window.rename_page_action in quick_access_bar.actions()
    assert window.rename_page_action in window.quick_access_actions
    assert quick_access_bar.visibleCount() == 4
    assert "Visible 4/4" in window.quick_access_status_preview.text()

    duplicate_menu = QMenu(window)
    duplicate_action = window.populate_action_context_menu(
        duplicate_menu, window.rename_page_action
    )
    assert duplicate_action is not None
    assert not duplicate_action.isEnabled()
    assert "Already in Quick Access Toolbar" in duplicate_action.text()
    window.close()


def test_example_quick_access_context_menu_removes_command():
    window = MainWindow()
    window.show()
    _app().processEvents()
    quick_access_bar = window.ribbonBar().quickAccessBar()
    window.add_action_to_quick_access(window.rename_page_action)
    _app().processEvents()
    assert window.rename_page_action in quick_access_bar.actions()
    assert "Visible 4/4" in window.quick_access_status_preview.text()

    menu = QMenu(window)
    remove_action = window.populate_quick_access_action_context_menu(
        menu, window.rename_page_action
    )
    assert remove_action is not None
    assert remove_action.objectName() == "removeFromQuickAccessContextAction"
    assert remove_action.isEnabled()
    assert "Remove from Quick Access Toolbar" in remove_action.text()

    remove_action.trigger()
    _app().processEvents()
    assert window.rename_page_action not in quick_access_bar.actions()
    assert window.rename_page_action not in window.quick_access_actions
    assert quick_access_bar.visibleCount() == 3
    assert "Visible 3/3" in window.quick_access_status_preview.text()

    duplicate_menu = QMenu(window)
    duplicate_remove = window.populate_quick_access_action_context_menu(
        duplicate_menu, window.rename_page_action
    )
    assert duplicate_remove is not None
    assert not duplicate_remove.isEnabled()
    assert "Not in Quick Access Toolbar" in duplicate_remove.text()
    window.close()


def test_example_quick_access_context_menu_reorders_command():
    window = MainWindow()
    window.show()
    _app().processEvents()
    quick_access_bar = window.ribbonBar().quickAccessBar()
    window.add_action_to_quick_access(window.rename_page_action)
    _app().processEvents()

    initial_index = quick_access_bar.actions().index(window.rename_page_action)
    menu = QMenu(window)
    window.populate_quick_access_action_context_menu(
        menu, window.rename_page_action
    )
    move_left = next(
        action
        for action in menu.actions()
        if action.objectName() == "moveQuickAccessLeftContextAction"
    )
    move_right_at_end = next(
        action
        for action in menu.actions()
        if action.objectName() == "moveQuickAccessRightContextAction"
    )
    assert move_left.isEnabled()
    assert not move_right_at_end.isEnabled()

    move_left.trigger()
    _app().processEvents()
    assert quick_access_bar.actions().index(window.rename_page_action) == initial_index - 1
    assert window.quick_access_actions.index(window.rename_page_action) == initial_index - 1
    assert quick_access_bar.visibleCount() == 4
    assert "Visible 4/4" in window.quick_access_status_preview.text()

    restore_menu = QMenu(window)
    window.populate_quick_access_action_context_menu(
        restore_menu, window.rename_page_action
    )
    move_right = next(
        action
        for action in restore_menu.actions()
        if action.objectName() == "moveQuickAccessRightContextAction"
    )
    assert move_right.isEnabled()
    move_right.trigger()
    _app().processEvents()
    assert quick_access_bar.actions().index(window.rename_page_action) == initial_index
    window.close()


def test_example_quick_access_menu_resets_commands():
    window = MainWindow()
    window.show()
    _app().processEvents()
    quick_access_bar = window.ribbonBar().quickAccessBar()

    window.add_action_to_quick_access(window.rename_page_action)
    window.move_quick_access_action(window.rename_page_action, -1)
    _app().processEvents()
    assert window.rename_page_action in quick_access_bar.actions()
    assert quick_access_bar.visibleCount() == 4

    menu = QMenu(window)
    window.populate_quick_access_menu(menu)
    reset_action = next(
        action
        for action in menu.actions()
        if action.objectName() == "resetQuickAccessAction"
    )
    reset_action.trigger()
    _app().processEvents()
    visible_actions = [
        action
        for action in quick_access_bar.actions()
        if action != quick_access_bar.actionCustomizeButton()
    ]
    assert visible_actions == window.default_quick_access_actions
    assert window.quick_access_actions == window.default_quick_access_actions
    assert window.rename_page_action not in quick_access_bar.actions()
    assert quick_access_bar.visibleCount() == 3
    assert "Visible 3/3" in window.quick_access_status_preview.text()
    window.close()


def test_example_quick_access_menu_exports_customization():
    window = MainWindow()
    window.show()
    _app().processEvents()

    window.add_action_to_quick_access(window.rename_page_action)
    window.move_quick_access_action(window.rename_page_action, -1)
    window.quick_access_below_action.trigger()
    window.quick_access_labels_action.setChecked(True)
    _app().processEvents()

    menu = QMenu(window)
    window.populate_quick_access_menu(menu)
    export_action = next(
        action
        for action in menu.actions()
        if action.objectName() == "exportQuickAccessAction"
    )
    export_action.trigger()
    _app().processEvents()
    state = json.loads(window.exported_quick_access_state)
    assert state["version"] == 1
    assert state["actions"] == [
        "fullScreen",
        "connect",
        "renamePage",
        "minimizeRibbon",
    ]
    assert state["position"] == "below"
    assert state["labels"] is True
    window.close()


def test_example_quick_access_menu_imports_customization():
    window = MainWindow()
    window.show()
    _app().processEvents()
    quick_access_bar = window.ribbonBar().quickAccessBar()

    window.add_action_to_quick_access(window.rename_page_action)
    window.move_quick_access_action(window.rename_page_action, -1)
    window.quick_access_below_action.trigger()
    window.quick_access_labels_action.setChecked(True)
    window.export_quick_access_action.trigger()
    window.reset_quick_access_action.trigger()
    _app().processEvents()
    assert window.rename_page_action not in quick_access_bar.actions()
    assert quick_access_bar.visibleCount() == 3

    menu = QMenu(window)
    window.populate_quick_access_menu(menu)
    import_action = next(
        action
        for action in menu.actions()
        if action.objectName() == "importQuickAccessAction"
    )
    import_action.trigger()
    _app().processEvents()
    visible_actions = [
        action
        for action in quick_access_bar.actions()
        if action != quick_access_bar.actionCustomizeButton()
    ]
    assert visible_actions == [
        window.full_screen_action,
        window.connect_action,
        window.rename_page_action,
        window.minimize_ribbon_action,
    ]
    assert window.ribbonBar().quickAccessBarPosition() == QUICK_ACCESS_BOTTOM_POSITION
    assert quick_access_bar.toolButtonStyle() == Qt.ToolButtonStyle.ToolButtonTextBesideIcon
    assert "Visible 4/4" in window.quick_access_status_preview.text()
    assert "Below" in window.quick_access_status_preview.text()
    assert "Labels" in window.quick_access_status_preview.text()
    window.close()


def test_example_responsive_label_preview_hides_labels_under_stress():
    window = MainWindow()
    window.show()
    _app().processEvents()
    ribbon = window.ribbonBar()
    actions = [
        window.rename_page_action,
        window.move_gallery_action,
        window.toggle_group_action,
    ]
    status = window.responsive_labels_status_preview

    assert "0/3" in status.text()
    for action in actions:
        assert (
            _action_button(ribbon, action).toolButtonStyle()
            == Qt.ToolButtonStyle.ToolButtonTextBesideIcon
        )

    window.width_stress_action.trigger()
    _app().processEvents()
    assert "3/3" in status.text()
    for action in actions:
        button = _action_button(ribbon, action)
        assert button.toolButtonStyle() == Qt.ToolButtonStyle.ToolButtonIconOnly
        assert button.property("responsiveLabelHidden") is True

    window.width_stress_action.trigger()
    _app().processEvents()
    assert "0/3" in status.text()
    for action in actions:
        assert (
            _action_button(ribbon, action).toolButtonStyle()
            == Qt.ToolButtonStyle.ToolButtonTextBesideIcon
        )
    window.close()


def test_single_click_collapsed_tab_temporarily_expands():
    window, ribbon, *_ = _window()
    ribbon.setRibbonMinimized(True)
    _click_tab(ribbon, 0)
    assert ribbon.isRibbonMinimized()
    assert ribbon.isRibbonTemporaryExpanded()
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
        test_example_feedback_title_button_is_available,
        test_example_account_title_button_is_available,
        test_example_share_title_button_is_available,
        test_example_auto_save_title_toggle_is_available,
        test_example_auto_save_disabled_explanation_is_available,
        test_example_comments_title_button_is_available,
        test_example_presence_avatar_strip_is_available,
        test_example_collaboration_status_text_is_available,
        test_example_coauthoring_indicator_is_available,
        test_example_version_history_entry_is_available,
        test_example_save_copy_replaces_save_as_backstage_command,
        test_example_cloud_location_picker_is_available,
        test_example_caption_search_defaults_to_centered_microsoft_box,
        test_example_compact_search_action_switches_caption_search_to_icon_mode,
        test_example_hidden_search_action_removes_caption_search_box,
        test_example_alt_q_restores_and_focuses_caption_search,
        test_example_search_enter_triggers_registered_action,
        test_example_zero_query_search_shows_default_suggestions,
        test_example_zero_query_search_groups_recent_actions,
        test_example_search_keyboard_navigation_activates_popup_action,
        test_example_search_command_alias_matches_registered_action,
        test_example_search_fuzzy_phrase_matches_registered_action,
        test_example_search_shows_document_result_section,
        test_example_search_no_result_affordance_keeps_help_path,
        test_example_search_shows_help_result_section,
        test_example_search_shows_related_file_result_section,
        test_example_smart_lookup_command_surface,
        test_example_tell_me_lightbulb_entry_is_available,
        test_example_tell_me_phrase_examples_drive_search_text,
        test_example_tell_me_help_redirect_opens_help_search_path,
        test_example_collapse_state_preview_tracks_modes,
        test_example_double_click_preview_tracks_modes,
        test_example_quick_access_menu_controls_toolbar_visibility,
        test_example_action_context_menu_adds_command_to_quick_access,
        test_example_quick_access_context_menu_removes_command,
        test_example_quick_access_context_menu_reorders_command,
        test_example_quick_access_menu_resets_commands,
        test_example_quick_access_menu_exports_customization,
        test_example_quick_access_menu_imports_customization,
        test_example_responsive_label_preview_hides_labels_under_stress,
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
