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


def test_example_dictate_microphone_command_surface():
    window = MainWindow()
    window.show()
    _app().processEvents()
    ribbon = window.ribbonBar()

    assert window.dictate_microphone_action.objectName() == "dictateMicrophoneAction"
    assert window.dictate_microphone_action.isCheckable()
    assert not window.dictate_microphone_action.isChecked()
    assert not window.dictate_microphone_action.icon().isNull()
    assert "voice dictation" in window.dictate_microphone_action.toolTip()
    assert (
        window.dictate_microphone_preview.objectName()
        == "dictateMicrophonePreview"
    )
    assert window.dictate_microphone_preview.text() == "Dictate: microphone idle"
    assert window.dictate_microphone_action in window.search_actions
    assert ribbon.searchAction("Dictate") is window.dictate_microphone_action

    window.dictate_microphone_action.trigger()
    _app().processEvents()
    assert window.dictate_microphone_action.isChecked()
    assert window.dictate_microphone_preview.text() == "Dictate: listening"
    assert "#dictateMicrophonePreview" in window.dictate_microphone_preview.styleSheet()
    assert "Dictate" in window.statusBar().currentMessage()
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
    assert window.backstage.activePage() is window.backstage_account_page
    assert "Account" in window.statusBar().currentMessage()
    window.close()


def test_example_account_privacy_settings_entry_is_available():
    window = MainWindow()
    window.show()
    _app().processEvents()
    ribbon = window.ribbonBar()

    assert window.backstage_account_action.objectName() == "backstageAccountAction"
    assert window.backstage_account_action.isCheckable()
    assert window.backstage_account_page.objectName() == "backstageAccountPage"
    assert window.account_signed_in_label.objectName() == "accountSignedInLabel"
    assert "Local User" in window.account_signed_in_label.text()
    assert window.account_privacy_summary.objectName() == "accountPrivacySummary"
    assert "optional diagnostics off" in window.account_privacy_summary.text()
    assert (
        window.account_privacy_settings_action.objectName()
        == "accountPrivacySettingsAction"
    )
    assert not window.account_privacy_settings_action.icon().isNull()
    assert "privacy settings" in window.account_privacy_settings_action.toolTip()
    assert isinstance(window.account_privacy_settings_button, QToolButton)
    assert (
        window.account_privacy_settings_button.defaultAction()
        is window.account_privacy_settings_action
    )
    assert window.account_privacy_settings_action in window.search_actions
    assert (
        ribbon.searchAction("Privacy Settings")
        is window.account_privacy_settings_action
    )

    window.backstage.setActivePage(window.backstage_account_page)
    _app().processEvents()
    assert window.backstage.activePage() is window.backstage_account_page
    assert window.backstage_account_action.isChecked()

    window.account_privacy_settings_action.trigger()
    _app().processEvents()
    assert "connected experiences reviewed" in window.account_privacy_summary.text()
    assert "#accountPrivacySummary" in window.account_privacy_summary.styleSheet()
    assert "Account Privacy" in window.statusBar().currentMessage()
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


def test_example_upload_before_share_prompt_is_available():
    window = MainWindow()
    window.show()
    _app().processEvents()

    prompt = window.upload_before_share_prompt
    assert prompt.objectName() == "uploadBeforeSharePrompt"
    assert "Upload required" in prompt.text()
    assert "cloud location" in prompt.toolTip()

    window.share_title_action.trigger()
    _app().processEvents()
    assert "Upload before sharing" in prompt.text()
    assert "OneDrive" in prompt.text()
    assert "SharePoint" in prompt.text()
    assert "#uploadBeforeSharePrompt" in prompt.styleSheet()
    assert window.backstage.activePage() is window.backstage_open_page
    assert "upload before sharing" in window.statusBar().currentMessage()
    window.close()


def test_example_backstage_info_page_is_available():
    _app()
    window = MainWindow()
    window.show()
    _app().processEvents()

    assert window.backstage_info_action.objectName() == "backstageInfoAction"
    assert window.backstage_info_action.isCheckable()
    assert "document information" in window.backstage_info_action.toolTip()
    assert window.backstage_info_page.objectName() == "backstageInfoPage"
    assert window.backstage_info_page.windowTitle() == "Info"
    assert window.backstage_info_product_label.objectName() == "backstageInfoProductLabel"
    assert window.backstage_info_product_label.text() == "LqRibbon Demo"
    assert window.backstage_info_mode_label.objectName() == "backstageInfoModeLabel"
    assert window.backstage_info_mode_label.text() == "Backstage page"

    window.backstage.setActivePage(window.backstage_info_page)
    _app().processEvents()
    assert window.backstage.activePage() is window.backstage_info_page
    assert window.backstage_info_action.isChecked()
    window.backstage_info_action.trigger()
    _app().processEvents()
    assert window.backstage.activePage() is window.backstage_info_page
    assert window.backstage_info_action.isChecked()
    assert "Info:" in window.statusBar().currentMessage()
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


def test_example_icon_only_title_commands_are_available():
    window = MainWindow()
    window.show()
    _app().processEvents()
    title_bar = window.ribbonBar()._title_button_bar

    expected_actions = [
        window.display_options_title_action,
        window.auto_save_title_action,
        window.share_title_action,
        window.comments_title_action,
        window.presence_avatar_strip_action,
        window.feedback_title_action,
        window.help_title_action,
        window.account_title_action,
    ]
    assert window.icon_only_title_actions == expected_actions
    assert title_bar.toolButtonStyle() == Qt.ToolButtonStyle.ToolButtonIconOnly
    for action in expected_actions:
        button = title_bar.widgetForAction(action)
        assert isinstance(button, QToolButton)
        assert button.toolButtonStyle() == Qt.ToolButtonStyle.ToolButtonIconOnly
        assert not action.icon().isNull()
        assert action.text()
        assert button.toolTip()
    window.close()


def test_example_accessible_tooltip_names_are_available():
    window = MainWindow()
    window.show()
    _app().processEvents()
    title_bar = window.ribbonBar()._title_button_bar

    assert window.accessible_tooltip_actions == window.icon_only_title_actions
    for action in window.accessible_tooltip_actions:
        button = title_bar.widgetForAction(action)
        assert isinstance(button, QToolButton)
        command_name = action.text()
        tooltip = action.toolTip()
        assert tooltip.startswith(command_name)
        assert button.toolTip() == tooltip
        assert len(tooltip) > len(command_name)
    window.close()


def test_example_screen_reader_names_are_available():
    window = MainWindow()
    window.show()
    _app().processEvents()
    title_bar = window.ribbonBar()._title_button_bar

    assert window.screen_reader_title_actions == window.icon_only_title_actions
    for action in window.screen_reader_title_actions:
        button = title_bar.widgetForAction(action)
        assert isinstance(button, QToolButton)
        assert button.accessibleName() == action.text()
        assert button.accessibleDescription() == action.toolTip()
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


def test_example_zoom_slider_status_item_is_available():
    window = MainWindow()
    window.show()
    _app().processEvents()

    assert window.zoom_status_label.objectName() == "zoomStatusLabel"
    assert window.zoom_status_label.text() == "100%"
    assert "document zoom" in window.zoom_status_label.toolTip()
    assert window.zoom_slider.objectName() == "zoomStatusSlider"
    assert window.zoom_slider.slider.minimum() == 10
    assert window.zoom_slider.slider.maximum() == 200
    assert window.zoom_slider.singleStep() == 10
    assert window.zoom_slider.value() == 100
    assert "zoom percentage" in window.zoom_slider.toolTip()
    assert window.progress_bar.objectName() == "zoomStatusProgress"
    assert window.progress_bar.minimum() == 10
    assert window.progress_bar.maximum() == 200
    assert window.progress_bar.value() == 100

    window.zoom_slider.setValue(125)
    _app().processEvents()
    assert window.zoom_slider.value() == 125
    assert window.zoom_status_label.text() == "125%"
    assert window.progress_bar.value() == 125
    assert "Zoom: 125%" in window.statusBar().currentMessage()
    window.close()


def test_example_view_switch_status_buttons_are_available():
    window = MainWindow()
    window.show()
    _app().processEvents()

    group = window.status_view_switch_group
    buttons = group.findChildren(QToolButton)

    assert group.objectName() == "statusViewSwitchGroup"
    assert window.normal_status_view_action.objectName() == "normalStatusViewAction"
    assert window.compact_status_view_action.objectName() == "compactStatusViewAction"
    assert "Normal document view" in window.normal_status_view_action.toolTip()
    assert "Compact document view" in window.compact_status_view_action.toolTip()
    assert window.normal_status_view_action.isCheckable()
    assert window.compact_status_view_action.isCheckable()
    assert window.normal_status_view_action.isChecked()
    assert not window.compact_status_view_action.isChecked()
    assert any(
        button.defaultAction() is window.normal_status_view_action
        for button in buttons
    )
    assert any(
        button.defaultAction() is window.compact_status_view_action
        for button in buttons
    )

    window.compact_status_view_action.trigger()
    _app().processEvents()
    assert window.status_view_mode == "Compact View"
    assert window.compact_status_view_action.isChecked()
    assert not window.normal_status_view_action.isChecked()
    assert "View: Compact View" in window.statusBar().currentMessage()

    window.normal_status_view_action.trigger()
    _app().processEvents()
    assert window.status_view_mode == "Normal View"
    assert window.normal_status_view_action.isChecked()
    assert not window.compact_status_view_action.isChecked()
    assert "View: Normal View" in window.statusBar().currentMessage()
    window.close()


def test_example_character_count_status_item_is_available():
    window = MainWindow()
    window.show()
    _app().processEvents()

    label = window.character_count_status_label

    assert label.objectName() == "characterCountStatusItem"
    assert label.text() == "1,248 characters"
    assert "character count" in label.toolTip()
    assert label.minimumWidth() >= 112
    assert label.isVisible()
    window.close()


def test_example_sync_status_action_is_available():
    window = MainWindow()
    window.show()
    _app().processEvents()

    action = window.sync_status_action

    assert action.objectName() == "syncStatusAction"
    assert action.text() == "Sync"
    assert not action.icon().isNull()
    assert "Sync document changes" in action.toolTip()

    action.trigger()
    _app().processEvents()
    assert window.collaboration_status_label.text() == (
        "Saved to cloud | synced just now"
    )
    assert "Sync: Up to date" in window.statusBar().currentMessage()
    window.close()


def test_example_high_dpi_gallery_icon_is_available():
    window = MainWindow()
    window.show()
    _app().processEvents()

    item = window.high_dpi_gallery_item
    pixmap = item.icon().pixmap(64, 64)

    assert window.style_gallery.objectName() == "styleGallery"
    assert window.style_gallery.itemCount() >= 7
    assert window.style_gallery.columnCount() == 4
    assert item.caption() == "High DPI"
    assert item.toolTip() == "Scalable high-DPI icon sample"
    assert item.data(Qt.ItemDataRole.UserRole) == "highDpiScalableIcon"
    assert not item.icon().isNull()
    assert pixmap.width() >= 64
    assert pixmap.height() >= 64
    window.close()


def test_example_app_icon_color_set_is_available():
    window = MainWindow()
    window.show()
    _app().processEvents()

    item = window.app_icon_color_set_item
    pixmap = item.icon().pixmap(64, 64)

    assert window.style_gallery.itemCount() >= 8
    assert item.caption() == "App Colors"
    assert item.toolTip() == "New Office app icon color set"
    assert item.data(Qt.ItemDataRole.UserRole) == "newAppIconColorSet"
    assert not item.icon().isNull()
    assert pixmap.width() >= 64
    assert pixmap.height() >= 64
    window.close()


def test_example_svg_icon_insert_command_surface():
    window = MainWindow()
    window.show()
    _app().processEvents()
    ribbon = window.ribbonBar()

    assert window.insert_page.title() == "Insert"
    assert window.svg_icon_insert_action.objectName() == "svgIconInsertAction"
    assert not window.svg_icon_insert_action.icon().isNull()
    assert "Insert a scalable SVG icon" in window.svg_icon_insert_action.toolTip()
    assert window.svg_icon_insert_action.statusTip() == "SVG Icon: ready to insert"
    assert window.svg_icon_insert_preview.objectName() == "svgIconInsertPreview"
    assert window.svg_icon_insert_preview.text() == "SVG Icons: none inserted"
    assert "Last inserted SVG" in window.svg_icon_insert_preview.toolTip()
    assert window.svg_icon_insert_action in window.search_actions
    assert ribbon.searchAction("SVG Icon") is window.svg_icon_insert_action

    window.svg_icon_insert_action.trigger()
    _app().processEvents()
    assert window.svg_icon_insert_preview.text() == "SVG Icons: 1 inserted"
    assert "#svgIconInsertPreview" in window.svg_icon_insert_preview.styleSheet()
    assert "SVG Icon" in window.statusBar().currentMessage()
    window.close()


def test_example_svg_recolor_command_surface():
    window = MainWindow()
    window.show()
    _app().processEvents()
    ribbon = window.ribbonBar()

    assert window.format_page.title() == "Format"
    assert window.svg_recolor_action.objectName() == "svgRecolorAction"
    assert not window.svg_recolor_action.icon().isNull()
    assert "accent color" in window.svg_recolor_action.toolTip()
    assert window.svg_recolor_action.statusTip() == "Recolor SVG: accent preview ready"
    assert window.svg_recolor_preview.objectName() == "svgRecolorPreview"
    assert window.svg_recolor_preview.text() == "SVG color: original"
    assert "Selected SVG recolor" in window.svg_recolor_preview.toolTip()
    assert window.svg_recolor_action in window.search_actions
    assert ribbon.searchAction("Recolor SVG") is window.svg_recolor_action

    window.svg_recolor_action.trigger()
    _app().processEvents()
    assert window.svg_recolor_preview.text() == "SVG color: blue accent"
    assert "#svgRecolorPreview" in window.svg_recolor_preview.styleSheet()
    assert "Recolor SVG" in window.statusBar().currentMessage()
    window.close()


def test_example_svg_convert_shape_command_surface():
    window = MainWindow()
    window.show()
    _app().processEvents()
    ribbon = window.ribbonBar()

    assert window.format_page.title() == "Format"
    assert window.svg_convert_shape_action.objectName() == "svgConvertShapeAction"
    assert not window.svg_convert_shape_action.icon().isNull()
    assert "editable vector shapes" in window.svg_convert_shape_action.toolTip()
    assert (
        window.svg_convert_shape_action.statusTip()
        == "Convert to Shape: editable vector preview ready"
    )
    assert window.svg_convert_shape_preview.objectName() == "svgConvertShapePreview"
    assert window.svg_convert_shape_preview.text() == "SVG shape: vector icon"
    assert "shape conversion" in window.svg_convert_shape_preview.toolTip()
    assert window.svg_convert_shape_action in window.search_actions
    assert ribbon.searchAction("Convert to Shape") is window.svg_convert_shape_action

    window.svg_convert_shape_action.trigger()
    _app().processEvents()
    assert window.svg_convert_shape_preview.text() == "SVG shape: editable shape"
    assert "#svgConvertShapePreview" in window.svg_convert_shape_preview.styleSheet()
    assert "Convert to Shape" in window.statusBar().currentMessage()
    window.close()


def test_example_reduced_motion_option_is_available():
    window = MainWindow()
    window.show()
    _app().processEvents()
    ribbon = window.ribbonBar()

    assert window.options_page.title() == "Options"
    assert window.reduced_motion_action.objectName() == "reducedMotionAction"
    assert window.reduced_motion_action.isCheckable()
    assert not window.reduced_motion_action.isChecked()
    assert not window.reduced_motion_action.icon().isNull()
    assert "minimize animated transitions" in window.reduced_motion_action.toolTip()
    assert window.reduced_motion_action.statusTip() == "Reduced Motion: off"
    assert window.reduced_motion_preview.objectName() == "reducedMotionPreview"
    assert window.reduced_motion_preview.text() == "Motion: full animation"
    assert window.state_timing_preview.property("reducedMotion") is None
    assert window.reduced_motion_action in window.search_actions
    assert ribbon.searchAction("Reduced Motion") is window.reduced_motion_action

    window.reduced_motion_action.trigger()
    _app().processEvents()
    assert window.reduced_motion_action.isChecked()
    assert window.reduced_motion_preview.text() == "Motion: reduced"
    assert window.state_timing_preview.property("reducedMotion") is True
    assert "#reducedMotionPreview" in window.reduced_motion_preview.styleSheet()
    assert "Reduced Motion" in window.statusBar().currentMessage()

    window.reduced_motion_action.trigger()
    _app().processEvents()
    assert not window.reduced_motion_action.isChecked()
    assert window.reduced_motion_preview.text() == "Motion: full animation"
    assert window.state_timing_preview.property("reducedMotion") is False
    window.close()


def test_example_contextual_tab_group_color_preview_is_available():
    window = MainWindow()
    window.show()
    _app().processEvents()
    ribbon = window.ribbonBar()
    ribbon.setCurrentPageIndex(ribbon.pageIndex(window.contextual_page))
    _app().processEvents()

    assert window.contextual_page.title() == "Contextual"
    assert (
        window.contextual_group_color_action.objectName()
        == "contextualGroupColorAction"
    )
    assert not window.contextual_group_color_action.icon().isNull()
    assert "contextual tab group color" in window.contextual_group_color_action.toolTip()
    assert (
        window.contextual_group_color_action.statusTip()
        == "Contextual group color: purple"
    )
    assert (
        window.contextual_group_color_preview.objectName()
        == "contextualGroupColorPreview"
    )
    assert window.contextual_group_color_preview.text() == "Picture Tools: neutral"
    assert window.contextual_group_color_action in window.search_actions
    assert (
        ribbon.searchAction("Group Color")
        is window.contextual_group_color_action
    )

    window.contextual_group_color_action.trigger()
    _app().processEvents()
    assert window.contextual_group_color_preview.text() == "Picture Tools: purple"
    assert (
        "#contextualGroupColorPreview"
        in window.contextual_group_color_preview.styleSheet()
    )
    assert "Contextual group color" in window.statusBar().currentMessage()
    window.close()


def test_example_contextual_tab_show_hide_toggle_is_available():
    window = MainWindow()
    window.show()
    _app().processEvents()
    ribbon = window.ribbonBar()
    ribbon.setCurrentPageIndex(ribbon.pageIndex(window.contextual_page))
    _app().processEvents()

    assert (
        window.contextual_tab_visibility_action.objectName()
        == "contextualTabVisibilityAction"
    )
    assert window.contextual_tab_visibility_action.isCheckable()
    assert window.contextual_tab_visibility_action.isChecked()
    assert not window.contextual_tab_visibility_action.icon().isNull()
    assert "Show or hide contextual" in window.contextual_tab_visibility_action.toolTip()
    assert ribbon.isContextualTabsVisible()
    assert (
        window.contextual_tab_visibility_preview.objectName()
        == "contextualTabVisibilityPreview"
    )
    assert window.contextual_tab_visibility_preview.text() == "Contextual tabs: visible"
    assert window.contextual_tab_visibility_action in window.search_actions
    assert (
        ribbon.searchAction("Show Contextual")
        is window.contextual_tab_visibility_action
    )

    window.contextual_tab_visibility_action.trigger()
    _app().processEvents()
    assert not window.contextual_tab_visibility_action.isChecked()
    assert not ribbon.isContextualTabsVisible()
    assert window.contextual_tab_visibility_preview.text() == "Contextual tabs: hidden"
    assert (
        "#contextualTabVisibilityPreview"
        in window.contextual_tab_visibility_preview.styleSheet()
    )
    assert "hidden" in window.statusBar().currentMessage()

    window.contextual_tab_visibility_action.trigger()
    _app().processEvents()
    assert window.contextual_tab_visibility_action.isChecked()
    assert ribbon.isContextualTabsVisible()
    assert window.contextual_tab_visibility_preview.text() == "Contextual tabs: visible"
    window.close()


def test_example_title_groups_visibility_toggle_is_available():
    window = MainWindow()
    window.show()
    _app().processEvents()
    ribbon = window.ribbonBar()
    ribbon.setCurrentPageIndex(ribbon.pageIndex(window.contextual_page))
    _app().processEvents()

    assert (
        window.title_groups_visibility_action.objectName()
        == "titleGroupsVisibilityAction"
    )
    assert window.title_groups_visibility_action.isCheckable()
    assert window.title_groups_visibility_action.isChecked()
    assert not window.title_groups_visibility_action.icon().isNull()
    assert "contextual title groups" in window.title_groups_visibility_action.toolTip()
    assert ribbon.isTitleGroupsVisible()
    assert (
        window.title_groups_visibility_preview.objectName()
        == "titleGroupsVisibilityPreview"
    )
    assert window.title_groups_visibility_preview.text() == "Title groups: visible"
    assert window.title_groups_visibility_action in window.search_actions
    assert ribbon.searchAction("Title Groups") is window.title_groups_visibility_action

    window.title_groups_visibility_action.trigger()
    _app().processEvents()
    assert not window.title_groups_visibility_action.isChecked()
    assert not ribbon.isTitleGroupsVisible()
    assert window.title_groups_visibility_preview.text() == "Title groups: hidden"
    assert (
        "#titleGroupsVisibilityPreview"
        in window.title_groups_visibility_preview.styleSheet()
    )
    assert "hidden" in window.statusBar().currentMessage()

    window.title_groups_visibility_action.trigger()
    _app().processEvents()
    assert window.title_groups_visibility_action.isChecked()
    assert ribbon.isTitleGroupsVisible()
    assert window.title_groups_visibility_preview.text() == "Title groups: visible"
    window.close()


def test_example_custom_tab_creation_is_available():
    window = MainWindow()
    window.show()
    _app().processEvents()
    ribbon = window.ribbonBar()
    initial_count = ribbon.pageCount()

    assert window.add_page_action.objectName() == "addPageAction"
    assert not window.add_page_action.icon().isNull()
    assert "custom ribbon tab" in window.add_page_action.toolTip()
    assert window.add_page_action.statusTip() == "Custom tab: not created"
    assert window.custom_tab_preview.objectName() == "customTabPreview"
    assert window.custom_tab_preview.text() == "Custom tab: none"
    assert window.add_page_action in window.search_actions
    assert ribbon.searchAction("Add Page") is window.add_page_action

    window.add_page_action.trigger()
    _app().processEvents()
    new_page = ribbon.currentPage()
    assert ribbon.pageCount() == initial_count + 1
    assert new_page.title() == "Runtime 1"
    assert new_page.group(0).title() == "Generated"
    assert window.customize_manager.pageId(new_page) == "runtime1"
    assert window.custom_tab_preview.text() == "Custom tab: Runtime 1"
    assert "#customTabPreview" in window.custom_tab_preview.styleSheet()
    assert window.add_page_action.statusTip() == "Custom tab: Runtime 1"
    assert "Custom tab" in window.statusBar().currentMessage()
    window.close()


def test_example_custom_group_creation_is_available():
    window = MainWindow()
    window.show()
    _app().processEvents()
    ribbon = window.ribbonBar()

    window.add_page_action.trigger()
    _app().processEvents()
    runtime_page = ribbon.currentPage()
    initial_group_count = runtime_page.groupCount()

    assert window.add_group_action.objectName() == "addGroupAction"
    assert not window.add_group_action.icon().isNull()
    assert "custom group" in window.add_group_action.toolTip()
    assert window.add_group_action.statusTip() == "Custom group: not created"
    assert window.custom_group_preview.objectName() == "customGroupPreview"
    assert window.custom_group_preview.text() == "Custom group: none"
    assert window.add_group_action in window.search_actions
    assert ribbon.searchAction("Add Group") is window.add_group_action

    window.add_group_action.trigger()
    _app().processEvents()
    new_group = runtime_page.group(initial_group_count)
    assert runtime_page.groupCount() == initial_group_count + 1
    assert new_group.title() == "Custom Group 1"
    assert window.customize_manager.groupId(new_group) == "customGroup1"
    assert window.custom_group_preview.text() == "Custom group: Custom Group 1"
    assert "#customGroupPreview" in window.custom_group_preview.styleSheet()
    assert window.add_group_action.statusTip() == "Custom group: Custom Group 1"
    assert "Custom group" in window.statusBar().currentMessage()
    window.close()


def test_example_rename_custom_tab_and_group_is_available():
    window = MainWindow()
    window.show()
    _app().processEvents()
    ribbon = window.ribbonBar()

    window.add_page_action.trigger()
    window.add_group_action.trigger()
    _app().processEvents()
    runtime_page = ribbon.currentPage()
    custom_group = window.last_custom_group

    assert window.rename_custom_action.objectName() == "renameCustomAction"
    assert not window.rename_custom_action.icon().isNull()
    assert "custom tab and group" in window.rename_custom_action.toolTip()
    assert window.rename_custom_action.statusTip() == "Rename custom: pending"
    assert window.rename_custom_preview.objectName() == "renameCustomPreview"
    assert window.rename_custom_preview.text() == "Rename custom: pending"
    assert window.rename_custom_action in window.search_actions
    assert ribbon.searchAction("Rename Custom") is window.rename_custom_action

    window.rename_custom_action.trigger()
    _app().processEvents()
    assert runtime_page.title() == "Renamed Tab 1"
    assert custom_group.title() == "Renamed Group 1"
    assert window.customize_manager.pageName(runtime_page) == "Renamed Tab 1"
    assert window.customize_manager.groupName(custom_group) == "Renamed Group 1"
    assert window.custom_tab_preview.text() == "Custom tab: Renamed Tab 1"
    assert window.custom_group_preview.text() == "Custom group: Renamed Group 1"
    assert window.rename_custom_preview.text() == "Renamed Tab 1 / Renamed Group 1"
    assert "#renameCustomPreview" in window.rename_custom_preview.styleSheet()
    assert window.rename_custom_action.statusTip() == (
        "Renamed custom: Renamed Tab 1 / Renamed Group 1"
    )
    assert "Renamed custom" in window.statusBar().currentMessage()
    window.close()


def test_example_add_command_to_custom_group_is_available():
    window = MainWindow()
    window.show()
    _app().processEvents()
    ribbon = window.ribbonBar()

    window.add_page_action.trigger()
    window.add_group_action.trigger()
    _app().processEvents()
    custom_group = window.last_custom_group
    initial_actions = window.customize_manager.actionsGroup(custom_group)

    assert window.add_command_action.objectName() == "addCustomCommandAction"
    assert not window.add_command_action.icon().isNull()
    assert "last custom group" in window.add_command_action.toolTip()
    assert window.add_command_action.statusTip() == "Custom command: not added"
    assert window.custom_command_preview.objectName() == "customCommandPreview"
    assert window.custom_command_preview.text() == "Custom command: none"
    assert window.add_command_action in window.search_actions
    assert ribbon.searchAction("Add Command") is window.add_command_action

    window.add_command_action.trigger()
    _app().processEvents()
    actions = window.customize_manager.actionsGroup(custom_group)
    added_action = actions[-1]
    assert len(actions) == len(initial_actions) + 1
    assert added_action.objectName() == "customCommand1"
    assert added_action.text() == "Custom Command 1"
    assert window.customize_manager.actionsGroup(custom_group)[-1] is added_action
    assert window.custom_command_preview.text() == "Custom command: Custom Command 1"
    assert "#customCommandPreview" in window.custom_command_preview.styleSheet()
    assert window.add_command_action.statusTip() == "Custom command: Custom Command 1"
    assert "Custom command" in window.statusBar().currentMessage()
    window.close()


def test_example_remove_command_from_custom_group_is_available():
    window = MainWindow()
    window.show()
    _app().processEvents()
    ribbon = window.ribbonBar()

    window.add_page_action.trigger()
    window.add_group_action.trigger()
    window.add_command_action.trigger()
    _app().processEvents()
    custom_group = window.last_custom_group
    actions_before_remove = window.customize_manager.actionsGroup(custom_group)
    command_to_remove = actions_before_remove[-1]

    assert window.remove_command_action.objectName() == "removeCustomCommandAction"
    assert not window.remove_command_action.icon().isNull()
    assert "last command" in window.remove_command_action.toolTip()
    assert window.remove_command_action.statusTip() == "Custom command: not removed"
    assert window.removed_command_preview.objectName() == "removedCommandPreview"
    assert window.removed_command_preview.text() == "Removed command: none"
    assert window.remove_command_action in window.search_actions
    assert ribbon.searchAction("Remove Command") is window.remove_command_action

    window.remove_command_action.trigger()
    _app().processEvents()
    actions_after_remove = window.customize_manager.actionsGroup(custom_group)
    assert len(actions_after_remove) == len(actions_before_remove) - 1
    assert command_to_remove not in actions_after_remove
    assert window.removed_command_preview.text() == "Removed command: Custom Command 1"
    assert "#removedCommandPreview" in window.removed_command_preview.styleSheet()
    assert window.remove_command_action.statusTip() == "Removed command: Custom Command 1"
    assert "Removed command" in window.statusBar().currentMessage()
    window.close()


def test_example_reset_selected_custom_tab_is_available():
    window = MainWindow()
    window.show()
    _app().processEvents()
    ribbon = window.ribbonBar()

    window.add_page_action.trigger()
    window.add_group_action.trigger()
    window.add_command_action.trigger()
    window.rename_custom_action.trigger()
    _app().processEvents()
    runtime_page = ribbon.currentPage()
    assert runtime_page.title() == "Renamed Tab 1"
    assert runtime_page.groupCount() == 2

    assert window.reset_selected_tab_action.objectName() == "resetSelectedTabAction"
    assert not window.reset_selected_tab_action.icon().isNull()
    assert "selected custom tab" in window.reset_selected_tab_action.toolTip()
    assert window.reset_selected_tab_action.statusTip() == "Selected tab: not reset"
    assert window.reset_selected_tab_preview.objectName() == "resetSelectedTabPreview"
    assert window.reset_selected_tab_preview.text() == "Selected tab reset: none"
    assert window.reset_selected_tab_action in window.search_actions
    assert ribbon.searchAction("Reset Tab") is window.reset_selected_tab_action

    window.reset_selected_tab_action.trigger()
    _app().processEvents()
    assert runtime_page.title() == "Runtime 1"
    assert runtime_page.groupCount() == 1
    assert runtime_page.group(0).title() == "Generated"
    assert window.last_custom_group is None
    assert window.custom_tab_preview.text() == "Custom tab: Runtime 1"
    assert window.custom_group_preview.text() == "Custom group: none"
    assert window.custom_command_preview.text() == "Custom command: none"
    assert window.reset_selected_tab_preview.text() == "Selected tab reset: Runtime 1"
    assert "#resetSelectedTabPreview" in window.reset_selected_tab_preview.styleSheet()
    assert window.reset_selected_tab_action.statusTip() == "Selected tab reset: Runtime 1"
    assert "Selected tab reset" in window.statusBar().currentMessage()
    window.close()


def test_example_reset_all_customizations_is_available():
    window = MainWindow()
    window.show()
    _app().processEvents()
    ribbon = window.ribbonBar()
    initial_page_count = ribbon.pageCount()

    window.add_page_action.trigger()
    first_runtime_page = ribbon.currentPage()
    window.add_group_action.trigger()
    window.add_command_action.trigger()
    window.add_page_action.trigger()
    _app().processEvents()
    assert ribbon.pageCount() == initial_page_count + 2

    assert window.reset_all_customizations_action.objectName() == "resetAllCustomizationsAction"
    assert not window.reset_all_customizations_action.icon().isNull()
    assert "all ribbon customizations" in window.reset_all_customizations_action.toolTip()
    assert window.reset_all_customizations_action.statusTip() == "Ribbon customizations: not reset"
    assert window.reset_all_customizations_preview.objectName() == "resetAllCustomizationsPreview"
    assert window.reset_all_customizations_preview.text() == "All customizations: active"
    assert window.reset_all_customizations_action in window.search_actions
    assert ribbon.searchAction("Reset All") is window.reset_all_customizations_action

    window.reset_all_customizations_action.trigger()
    _app().processEvents()
    assert ribbon.pageCount() == initial_page_count
    assert ribbon.pageIndex(first_runtime_page) == -1
    assert window.runtime_page_counter == 1
    assert window.runtime_group_counter == 1
    assert window.last_custom_group is None
    assert window.custom_tab_preview.text() == "Custom tab: none"
    assert window.custom_group_preview.text() == "Custom group: none"
    assert window.custom_command_preview.text() == "Custom command: none"
    assert window.reset_all_customizations_preview.text() == "All customizations: reset"
    assert "#resetAllCustomizationsPreview" in window.reset_all_customizations_preview.styleSheet()
    assert window.reset_all_customizations_action.statusTip() == (
        "Ribbon customizations reset: 2 page(s)"
    )
    assert "Ribbon customizations reset" in window.statusBar().currentMessage()
    window.close()


def test_example_export_ribbon_customization_is_available():
    window = MainWindow()
    window.show()
    _app().processEvents()
    ribbon = window.ribbonBar()

    window.add_page_action.trigger()
    _app().processEvents()
    assert b"Runtime 1" not in window.exported_ribbon_customization_state

    assert window.export_customization_action.objectName() == "exportRibbonCustomizationAction"
    assert not window.export_customization_action.icon().isNull()
    assert "ribbon customization state" in window.export_customization_action.toolTip()
    assert window.export_customization_action.statusTip() == "Ribbon export: not created"
    assert window.export_customization_preview.objectName() == "exportRibbonCustomizationPreview"
    assert window.export_customization_preview.text() == "Ribbon export: none"
    assert window.export_customization_action in window.search_actions
    assert ribbon.searchAction("Export Ribbon") is window.export_customization_action

    window.export_customization_action.trigger()
    _app().processEvents()
    exported = window.exported_ribbon_customization_state
    assert exported
    assert b"Runtime 1" in exported
    assert window.export_customization_preview.text() == f"Ribbon export: {len(exported)} bytes"
    assert "#exportRibbonCustomizationPreview" in window.export_customization_preview.styleSheet()
    assert window.export_customization_action.statusTip() == (
        f"Ribbon export: {len(exported)} bytes"
    )
    assert "Ribbon export" in window.statusBar().currentMessage()
    window.close()


def test_example_import_ribbon_customization_is_available():
    window = MainWindow()
    window.show()
    _app().processEvents()
    ribbon = window.ribbonBar()
    initial_page_count = ribbon.pageCount()

    window.add_page_action.trigger()
    window.export_customization_action.trigger()
    exported = window.exported_ribbon_customization_state
    window.reset_all_customizations_action.trigger()
    _app().processEvents()
    assert ribbon.pageCount() == initial_page_count

    assert window.import_customization_action.objectName() == "importRibbonCustomizationAction"
    assert not window.import_customization_action.icon().isNull()
    assert "ribbon customization state" in window.import_customization_action.toolTip()
    assert window.import_customization_action.statusTip() == "Ribbon import: no export"
    assert window.import_customization_preview.objectName() == "importRibbonCustomizationPreview"
    assert window.import_customization_preview.text() == "Ribbon import: none"
    assert window.import_customization_action in window.search_actions
    assert ribbon.searchAction("Import Ribbon") is window.import_customization_action

    window.import_customization_action.trigger()
    _app().processEvents()
    titles = [page.title() for page in ribbon.pages()]
    assert ribbon.pageCount() == initial_page_count + 1
    assert "Runtime 1" in titles
    assert window.import_customization_preview.text() == f"Ribbon import: {len(exported)} bytes"
    assert "#importRibbonCustomizationPreview" in window.import_customization_preview.styleSheet()
    assert window.import_customization_action.statusTip() == (
        f"Ribbon import: {len(exported)} bytes"
    )
    assert "Ribbon import" in window.statusBar().currentMessage()
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


def test_example_recent_file_pinning_is_available():
    window = MainWindow()
    window.show()
    _app().processEvents()

    action = window.pin_recent_file_action
    recent_files = window.recent_files

    assert action.objectName() == "pinRecentFileAction"
    assert action.isCheckable()
    assert not action.isChecked()
    assert action.text() == "Pin Recent File"
    assert recent_files.files == ["drive-layout.lqr", "axis-profile.lqr"]

    action.trigger()
    _app().processEvents()
    assert action.isChecked()
    assert action.text() == "Unpin Recent File"
    assert recent_files.files == ["axis-profile.lqr", "drive-layout.lqr"]
    assert "Pinned recent file" in window.statusBar().currentMessage()

    action.trigger()
    _app().processEvents()
    assert not action.isChecked()
    assert action.text() == "Pin Recent File"
    assert recent_files.files == ["drive-layout.lqr", "axis-profile.lqr"]
    assert "Unpinned recent file" in window.statusBar().currentMessage()
    window.close()


def test_example_backstage_open_page_shows_frequent_sites_and_groups():
    window = MainWindow()
    window.show()
    _app().processEvents()

    action = window.backstage_open_action
    page = window.backstage_open_page

    assert action.objectName() == "backstageOpenAction"
    assert action.isCheckable()
    assert page.objectName() == "backstageOpenPage"
    assert window.frequent_sites_label.objectName() == "frequentSitesList"
    assert "OneDrive - Contoso" in window.frequent_sites_label.text()
    assert "SharePoint Team Site" in window.frequent_sites_label.text()
    assert window.frequent_groups_label.objectName() == "frequentGroupsList"
    assert "Drive Tuning Team" in window.frequent_groups_label.text()
    assert "Firmware Release Group" in window.frequent_groups_label.text()

    window.backstage.setActivePage(page)
    _app().processEvents()
    assert window.backstage.activePage() is page
    assert action.isChecked()

    action.trigger()
    _app().processEvents()
    assert "frequent sites and groups" in window.statusBar().currentMessage()
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


def test_example_sensitivity_label_command_surface():
    window = MainWindow()
    window.show()
    _app().processEvents()
    ribbon = window.ribbonBar()

    assert window.sensitivity_label_action.objectName() == "sensitivityLabelAction"
    assert not window.sensitivity_label_action.icon().isNull()
    assert "sensitivity label" in window.sensitivity_label_action.toolTip()
    assert window.sensitivity_label_preview.objectName() == "sensitivityLabelPreview"
    assert window.sensitivity_label_preview.text() == "Sensitivity: Public"
    assert window.sensitivity_label_action in window.search_actions
    assert ribbon.searchAction("Sensitivity") is window.sensitivity_label_action

    window.sensitivity_label_action.trigger()
    _app().processEvents()
    assert window.sensitivity_label_preview.text() == "Sensitivity: Confidential"
    assert "#sensitivityLabelPreview" in window.sensitivity_label_preview.styleSheet()
    assert "Sensitivity" in window.statusBar().currentMessage()
    window.close()


def test_example_accessibility_checker_command_surface():
    window = MainWindow()
    window.show()
    _app().processEvents()
    ribbon = window.ribbonBar()

    assert window.accessibility_checker_action.objectName() == "accessibilityCheckerAction"
    assert not window.accessibility_checker_action.icon().isNull()
    assert "accessibility issues" in window.accessibility_checker_action.toolTip()
    assert (
        window.accessibility_checker_preview.objectName()
        == "accessibilityCheckerPreview"
    )
    assert window.accessibility_checker_preview.text() == "Accessibility: not checked"
    assert window.accessibility_checker_action in window.search_actions
    assert (
        ribbon.searchAction("Check Accessibility")
        is window.accessibility_checker_action
    )

    window.accessibility_checker_action.trigger()
    _app().processEvents()
    assert window.accessibility_checker_preview.text() == "Accessibility: 2 issues found"
    assert (
        "#accessibilityCheckerPreview"
        in window.accessibility_checker_preview.styleSheet()
    )
    assert "Accessibility" in window.statusBar().currentMessage()
    window.close()


def test_example_editor_pane_command_surface():
    window = MainWindow()
    window.show()
    _app().processEvents()
    ribbon = window.ribbonBar()

    assert window.editor_pane_action.objectName() == "editorPaneAction"
    assert not window.editor_pane_action.icon().isNull()
    assert "Editor pane" in window.editor_pane_action.toolTip()
    assert window.editor_pane_preview.objectName() == "editorPanePreview"
    assert window.editor_pane_preview.text() == "Editor: suggestions hidden"
    assert window.editor_pane_action in window.search_actions
    assert ribbon.searchAction("Editor") is window.editor_pane_action

    window.editor_pane_action.trigger()
    _app().processEvents()
    assert window.editor_pane_preview.text() == "Editor: 5 suggestions ready"
    assert "#editorPanePreview" in window.editor_pane_preview.styleSheet()
    assert "Editor" in window.statusBar().currentMessage()
    window.close()


def test_example_spelling_grammar_card_surface():
    window = MainWindow()
    window.show()
    _app().processEvents()
    ribbon = window.ribbonBar()

    assert window.spelling_grammar_action.objectName() == "spellingGrammarAction"
    assert not window.spelling_grammar_action.icon().isNull()
    assert "spelling and grammar" in window.spelling_grammar_action.toolTip()
    assert window.spelling_grammar_card.objectName() == "spellingGrammarCard"
    assert window.spelling_grammar_card.text() == "Spelling & Grammar: no scan yet"
    assert window.spelling_grammar_action in window.search_actions
    assert (
        ribbon.searchAction("Spelling & Grammar")
        is window.spelling_grammar_action
    )

    window.spelling_grammar_action.trigger()
    _app().processEvents()
    assert (
        window.spelling_grammar_card.text()
        == "Spelling & Grammar: 1 spelling, 2 grammar"
    )
    assert "#spellingGrammarCard" in window.spelling_grammar_card.styleSheet()
    assert "Spelling & Grammar" in window.statusBar().currentMessage()
    window.close()


def test_example_translator_command_surface():
    window = MainWindow()
    window.show()
    _app().processEvents()
    ribbon = window.ribbonBar()

    assert window.translator_action.objectName() == "translatorAction"
    assert not window.translator_action.icon().isNull()
    assert "Translate selected text" in window.translator_action.toolTip()
    assert window.translator_preview.objectName() == "translatorPreview"
    assert window.translator_preview.text() == "Translator: no selection"
    assert window.translator_action in window.search_actions
    assert ribbon.searchAction("Translator") is window.translator_action

    window.translator_action.trigger()
    _app().processEvents()
    assert window.translator_preview.text() == "Translator: English to Chinese"
    assert "#translatorPreview" in window.translator_preview.styleSheet()
    assert "Translator" in window.statusBar().currentMessage()
    window.close()


def test_example_read_aloud_command_surface():
    window = MainWindow()
    window.show()
    _app().processEvents()
    ribbon = window.ribbonBar()

    assert window.read_aloud_action.objectName() == "readAloudAction"
    assert window.read_aloud_action.isCheckable()
    assert not window.read_aloud_action.isChecked()
    assert not window.read_aloud_action.icon().isNull()
    assert "Read selected text aloud" in window.read_aloud_action.toolTip()
    assert window.read_aloud_preview.objectName() == "readAloudPreview"
    assert window.read_aloud_preview.text() == "Read Aloud: stopped"
    assert window.read_aloud_action in window.search_actions
    assert ribbon.searchAction("Read Aloud") is window.read_aloud_action

    window.read_aloud_action.trigger()
    _app().processEvents()
    assert window.read_aloud_action.isChecked()
    assert window.read_aloud_preview.text() == "Read Aloud: playing paragraph"
    assert "#readAloudPreview" in window.read_aloud_preview.styleSheet()
    assert "Read Aloud" in window.statusBar().currentMessage()
    window.close()


def test_example_immersive_reader_command_surface():
    window = MainWindow()
    window.show()
    _app().processEvents()
    ribbon = window.ribbonBar()

    ribbon.setCurrentPageIndex(ribbon.pageIndex(window.view_page))
    _app().processEvents()

    assert ribbon.pageIndex(window.view_page) >= 0
    assert window.immersive_reader_action.objectName() == "immersiveReaderAction"
    assert window.immersive_reader_action.isCheckable()
    assert not window.immersive_reader_action.isChecked()
    assert not window.immersive_reader_action.icon().isNull()
    assert "focused reading" in window.immersive_reader_action.toolTip()
    assert window.immersive_reader_preview.objectName() == "immersiveReaderPreview"
    assert window.immersive_reader_preview.text() == "Immersive Reader: off"
    assert window.immersive_reader_action in window.search_actions
    assert (
        ribbon.searchAction("Immersive Reader")
        is window.immersive_reader_action
    )

    window.immersive_reader_action.trigger()
    _app().processEvents()
    assert window.immersive_reader_action.isChecked()
    assert (
        window.immersive_reader_preview.text()
        == "Immersive Reader: line focus on"
    )
    assert "#immersiveReaderPreview" in window.immersive_reader_preview.styleSheet()
    assert "Immersive Reader" in window.statusBar().currentMessage()
    window.close()


def test_example_focus_mode_command_surface():
    window = MainWindow()
    window.show()
    _app().processEvents()
    ribbon = window.ribbonBar()

    ribbon.setCurrentPageIndex(ribbon.pageIndex(window.view_page))
    _app().processEvents()

    assert window.focus_mode_action.objectName() == "focusModeAction"
    assert window.focus_mode_action.isCheckable()
    assert not window.focus_mode_action.isChecked()
    assert not window.focus_mode_action.icon().isNull()
    assert "focused editing" in window.focus_mode_action.toolTip()
    assert window.focus_mode_preview.objectName() == "focusModePreview"
    assert window.focus_mode_preview.text() == "Focus Mode: ribbon visible"
    assert window.focus_mode_action in window.search_actions
    assert ribbon.searchAction("Focus Mode") is window.focus_mode_action
    assert not ribbon.isRibbonMinimized()

    window.focus_mode_action.trigger()
    _app().processEvents()
    assert window.focus_mode_action.isChecked()
    assert ribbon.isRibbonMinimized()
    assert window.focus_mode_preview.text() == "Focus Mode: distractions hidden"
    assert "#focusModePreview" in window.focus_mode_preview.styleSheet()
    assert "Focus Mode" in window.statusBar().currentMessage()

    window.focus_mode_action.trigger()
    _app().processEvents()
    assert not window.focus_mode_action.isChecked()
    assert not ribbon.isRibbonMinimized()
    assert window.focus_mode_preview.text() == "Focus Mode: ribbon visible"
    window.close()


def test_example_dark_canvas_toggle_surface():
    window = MainWindow()
    window.show()
    _app().processEvents()
    ribbon = window.ribbonBar()

    ribbon.setCurrentPageIndex(ribbon.pageIndex(window.view_page))
    _app().processEvents()

    assert window.dark_canvas_action.objectName() == "darkCanvasAction"
    assert window.dark_canvas_action.isCheckable()
    assert not window.dark_canvas_action.isChecked()
    assert not window.dark_canvas_action.icon().isNull()
    assert "dark background" in window.dark_canvas_action.toolTip()
    assert window.dark_canvas_preview.objectName() == "darkCanvasPreview"
    assert window.dark_canvas_preview.text() == "Canvas: light"
    assert window.dark_canvas_action in window.search_actions
    assert ribbon.searchAction("Dark Canvas") is window.dark_canvas_action
    assert window.centralWidget().styleSheet() == ""

    window.dark_canvas_action.trigger()
    _app().processEvents()
    assert window.dark_canvas_action.isChecked()
    assert window.dark_canvas_preview.text() == "Canvas: dark"
    assert "#darkCanvasPreview" in window.dark_canvas_preview.styleSheet()
    assert "#1b1b1b" in window.centralWidget().styleSheet()
    assert "Dark Canvas" in window.statusBar().currentMessage()

    window.dark_canvas_action.trigger()
    _app().processEvents()
    assert not window.dark_canvas_action.isChecked()
    assert window.dark_canvas_preview.text() == "Canvas: light"
    assert window.centralWidget().styleSheet() == ""
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


def test_example_key_tips_overlay_toggle_is_available():
    window = MainWindow()
    window.show()
    _app().processEvents()
    ribbon = window.ribbonBar()
    ribbon.setCurrentPageIndex(ribbon.pageIndex(window.tell_me_page))
    _app().processEvents()

    assert window.key_tips_overlay_action.objectName() == "keyTipsOverlayAction"
    assert window.key_tips_overlay_action.isCheckable()
    assert not window.key_tips_overlay_action.isChecked()
    assert not window.key_tips_overlay_action.icon().isNull()
    assert "keyboard navigation" in window.key_tips_overlay_action.toolTip()
    assert window.key_tips_overlay_action.statusTip() == "KeyTips overlay: hidden"
    assert window.key_tips_overlay_preview.objectName() == "keyTipsOverlayPreview"
    assert window.key_tips_overlay_preview.text() == "KeyTips: hidden"
    assert window.key_tips_overlay_action in window.search_actions
    assert ribbon.searchAction("KeyTips") is window.key_tips_overlay_action

    window.key_tips_overlay_action.trigger()
    _app().processEvents()
    assert window.key_tips_overlay_action.isChecked()
    assert window.key_tips_overlay_preview.text() == "KeyTips: F H N P"
    assert "#keyTipsOverlayPreview" in window.key_tips_overlay_preview.styleSheet()
    assert "visible" in window.key_tips_overlay_action.statusTip()
    assert "KeyTips overlay" in window.statusBar().currentMessage()

    window.key_tips_overlay_action.trigger()
    _app().processEvents()
    assert not window.key_tips_overlay_action.isChecked()
    assert window.key_tips_overlay_preview.text() == "KeyTips: hidden"
    assert "hidden" in window.key_tips_overlay_action.statusTip()
    window.close()


def test_example_alt_key_tab_activation_is_available():
    window = MainWindow()
    window.show()
    _app().processEvents()
    ribbon = window.ribbonBar()
    ribbon.setCurrentPageIndex(ribbon.pageIndex(window.tell_me_page))
    _app().processEvents()

    assert window.alt_key_tabs_action.objectName() == "altKeyTabsAction"
    assert not window.alt_key_tabs_action.icon().isNull()
    assert "Activate ribbon tabs" in window.alt_key_tabs_action.toolTip()
    assert window.alt_key_tabs_action.property("shortcutHint") == "Alt"
    assert window.alt_key_tabs_action.statusTip() == "Alt key tabs: inactive"
    assert window.alt_key_tabs_preview.objectName() == "altKeyTabsPreview"
    assert window.alt_key_tabs_preview.text() == "Alt tabs: inactive"
    assert window.alt_key_tabs_action in window.search_actions
    assert ribbon.searchAction("Alt Tabs") is window.alt_key_tabs_action

    window.alt_key_tabs_action.trigger()
    _app().processEvents()
    assert ribbon.currentPage() is window.general_page
    assert window.key_tips_overlay_action.isChecked()
    assert window.key_tips_overlay_preview.text() == "KeyTips: F H N P"
    assert window.alt_key_tabs_preview.text() == "Alt tabs: General F"
    assert "#altKeyTabsPreview" in window.alt_key_tabs_preview.styleSheet()
    assert window.alt_key_tabs_action.statusTip() == "Alt key tabs: active"
    assert "Alt key tabs" in window.statusBar().currentMessage()
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
        test_example_dictate_microphone_command_surface,
        test_example_feedback_title_button_is_available,
        test_example_account_title_button_is_available,
        test_example_account_privacy_settings_entry_is_available,
        test_example_backstage_info_page_is_available,
        test_example_share_title_button_is_available,
        test_example_upload_before_share_prompt_is_available,
        test_example_auto_save_title_toggle_is_available,
        test_example_auto_save_disabled_explanation_is_available,
        test_example_comments_title_button_is_available,
        test_example_presence_avatar_strip_is_available,
        test_example_icon_only_title_commands_are_available,
        test_example_accessible_tooltip_names_are_available,
        test_example_screen_reader_names_are_available,
        test_example_collaboration_status_text_is_available,
        test_example_coauthoring_indicator_is_available,
        test_example_zoom_slider_status_item_is_available,
        test_example_view_switch_status_buttons_are_available,
        test_example_character_count_status_item_is_available,
        test_example_sync_status_action_is_available,
        test_example_high_dpi_gallery_icon_is_available,
        test_example_app_icon_color_set_is_available,
        test_example_svg_icon_insert_command_surface,
        test_example_svg_recolor_command_surface,
        test_example_svg_convert_shape_command_surface,
        test_example_reduced_motion_option_is_available,
        test_example_contextual_tab_group_color_preview_is_available,
        test_example_contextual_tab_show_hide_toggle_is_available,
        test_example_title_groups_visibility_toggle_is_available,
        test_example_custom_tab_creation_is_available,
        test_example_custom_group_creation_is_available,
        test_example_rename_custom_tab_and_group_is_available,
        test_example_add_command_to_custom_group_is_available,
        test_example_remove_command_from_custom_group_is_available,
        test_example_reset_selected_custom_tab_is_available,
        test_example_reset_all_customizations_is_available,
        test_example_export_ribbon_customization_is_available,
        test_example_import_ribbon_customization_is_available,
        test_example_version_history_entry_is_available,
        test_example_save_copy_replaces_save_as_backstage_command,
        test_example_cloud_location_picker_is_available,
        test_example_recent_file_pinning_is_available,
        test_example_backstage_open_page_shows_frequent_sites_and_groups,
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
        test_example_sensitivity_label_command_surface,
        test_example_accessibility_checker_command_surface,
        test_example_editor_pane_command_surface,
        test_example_spelling_grammar_card_surface,
        test_example_translator_command_surface,
        test_example_read_aloud_command_surface,
        test_example_immersive_reader_command_surface,
        test_example_focus_mode_command_surface,
        test_example_dark_canvas_toggle_surface,
        test_example_tell_me_lightbulb_entry_is_available,
        test_example_tell_me_phrase_examples_drive_search_text,
        test_example_tell_me_help_redirect_opens_help_search_path,
        test_example_key_tips_overlay_toggle_is_available,
        test_example_alt_key_tab_activation_is_available,
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
