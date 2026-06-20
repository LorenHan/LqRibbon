"""
LqRibbon Example Application - Main entry point.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from PySide6.QtCore import QPoint, QSettings, QTimer, Qt
from PySide6.QtGui import QFont, QFontDatabase, QPainter
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QMenu

from LqRibbon import RibbonStyle
from main_window import (
    MainWindow,
    save_ribbon_style_choice,
    saved_ribbon_style_choice,
)
import picture_rc  # noqa: F401


def _option_value(arguments, option):
    try:
        index = arguments.index(option)
    except ValueError:
        return ""
    return arguments[index + 1] if index + 1 < len(arguments) else ""


def _install_demo_font(app):
    for path in [
        r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\arial.ttf",
    ]:
        if not os.path.exists(path):
            continue
        font_id = QFontDatabase.addApplicationFont(path)
        families = QFontDatabase.applicationFontFamilies(font_id)
        if families:
            app.setFont(QFont(families[0], 9))
            return


def main():
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("LqRibbon Example")
    app.setOrganizationName("LqRibbon")
    _install_demo_font(app)

    arguments = sys.argv[1:]
    preview_path = _option_value(arguments, "--grab-preview")
    search_preview = "--grab-search-preview" in arguments
    compact_search_preview = "--grab-search-compact-preview" in arguments
    hidden_search_preview = "--grab-search-hidden-preview" in arguments
    alt_q_search_preview = "--grab-alt-q-search-preview" in arguments
    zero_query_search_preview = "--grab-zero-query-search-preview" in arguments
    recent_search_preview = "--grab-recent-search-preview" in arguments
    collapsed_preview = "--grab-collapsed-preview" in arguments
    simplified_preview = "--grab-simplified-preview" in arguments
    temporary_preview = "--grab-temporary-preview" in arguments
    double_click_preview = "--grab-double-click-preview" in arguments
    mdi_preview = "--grab-mdi-preview" in arguments
    tab_preview = "--grab-tab-preview" in arguments
    controls_preview = "--grab-controls-preview" in arguments
    gallery_preview = "--grab-gallery-preview" in arguments
    shell_preview = "--grab-shell-preview" in arguments
    width_stress_preview = "--grab-width-stress-preview" in arguments
    quick_access_hidden_preview = "--grab-qat-hidden-preview" in arguments
    quick_access_above_preview = "--grab-qat-above-preview" in arguments
    quick_access_below_preview = "--grab-qat-below-preview" in arguments
    quick_access_labels_preview = "--grab-qat-labels-preview" in arguments
    add_to_quick_access_preview = "--grab-add-to-qat-preview" in arguments
    remove_from_quick_access_preview = "--grab-remove-from-qat-preview" in arguments
    reorder_quick_access_preview = "--grab-qat-reorder-preview" in arguments
    reset_quick_access_preview = "--grab-qat-reset-preview" in arguments
    export_quick_access_preview = "--grab-qat-export-preview" in arguments
    import_quick_access_preview = "--grab-qat-import-preview" in arguments
    style_preview = "--grab-style-preview" in arguments
    style_name = _option_value(arguments, "--style")
    deterministic_style = bool(preview_path)
    settings = QSettings()
    saved_style_name = "" if deterministic_style else saved_ribbon_style_choice(settings)

    window = MainWindow()
    if not deterministic_style:
        style_combo = window.style_combo_control.widget()
        style_combo.currentIndexChanged.connect(
            lambda index: save_ribbon_style_choice(
                settings, window.style_choice_from_combo_index(index)
            )
        )
    if (
        search_preview
        or compact_search_preview
        or hidden_search_preview
        or alt_q_search_preview
        or zero_query_search_preview
        or recent_search_preview
        or controls_preview
        or gallery_preview
        or shell_preview
        or width_stress_preview
        or quick_access_hidden_preview
        or quick_access_above_preview
        or quick_access_below_preview
        or quick_access_labels_preview
        or add_to_quick_access_preview
        or remove_from_quick_access_preview
        or reorder_quick_access_preview
        or reset_quick_access_preview
        or export_quick_access_preview
        or import_quick_access_preview
        or simplified_preview
        or temporary_preview
        or double_click_preview
    ):
        window.resize(1180, 560)
    if style_preview:
        window.resize(1180, 560)
    if (
        width_stress_preview
        or quick_access_hidden_preview
        or quick_access_above_preview
        or quick_access_below_preview
        or quick_access_labels_preview
        or add_to_quick_access_preview
        or remove_from_quick_access_preview
        or reorder_quick_access_preview
        or reset_quick_access_preview
        or export_quick_access_preview
        or import_quick_access_preview
        or compact_search_preview
        or hidden_search_preview
        or alt_q_search_preview
        or zero_query_search_preview
        or recent_search_preview
    ):
        window.resize(1476, 560)
    if style_name:
        window.set_ribbon_style(style_name)
    elif style_preview:
        window.set_ribbon_style(RibbonStyle.Microsoft365Light)
    elif saved_style_name:
        window.set_ribbon_style(saved_style_name)
    if mdi_preview or tab_preview:
        window.show_mdi_content(tabbed=tab_preview)
    window.select_preview_page(
        controls=controls_preview,
        gallery=gallery_preview,
        shell=(
            shell_preview
            or width_stress_preview
            or quick_access_hidden_preview
            or quick_access_above_preview
            or quick_access_below_preview
            or quick_access_labels_preview
            or add_to_quick_access_preview
            or remove_from_quick_access_preview
            or reorder_quick_access_preview
            or reset_quick_access_preview
            or export_quick_access_preview
            or import_quick_access_preview
            or simplified_preview
            or temporary_preview
            or double_click_preview
        ),
        style=style_preview,
    )
    window.show()

    def show_temporary_preview():
        ribbon = window.ribbonBar()
        ribbon.setRibbonMinimized(True)
        app.processEvents()
        tab_bar = ribbon.tabBar()
        QTest.mouseClick(
            tab_bar,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
            tab_bar.tabRect(ribbon.currentIndex()).center(),
        )
        app.processEvents()

    if search_preview:
        QTimer.singleShot(120, window.focus_search_preview)
    if compact_search_preview:
        QTimer.singleShot(120, window.compact_search_action.trigger)
    if hidden_search_preview:
        QTimer.singleShot(120, window.hidden_search_action.trigger)
    if alt_q_search_preview:
        def show_alt_q_search_preview():
            window.hidden_search_action.trigger()
            window.focus_search_action.trigger()
            window.ribbonBar().setSearchText("ba")

        QTimer.singleShot(120, show_alt_q_search_preview)
    if zero_query_search_preview:
        def show_zero_query_search_preview():
            window.focus_search_action.trigger()
            window.ribbonBar().setSearchText("")
            window.ribbonBar().searchLineEdit().showPopup("")

        QTimer.singleShot(120, show_zero_query_search_preview)
    if recent_search_preview:
        def show_recent_search_preview():
            window.ribbonBar().triggerSearchAction("Control Modes")
            window.ribbonBar().triggerSearchAction("Center Search")
            window.focus_search_action.trigger()
            window.ribbonBar().setSearchText("")
            window.ribbonBar().searchLineEdit().showPopup("")

        QTimer.singleShot(120, show_recent_search_preview)
    if collapsed_preview:
        QTimer.singleShot(120, lambda: window.ribbonBar().setRibbonMinimized(True))
    if simplified_preview:
        QTimer.singleShot(120, lambda: window.ribbonBar().setSimplifiedMode(True))
    if temporary_preview:
        QTimer.singleShot(120, show_temporary_preview)
    if width_stress_preview:
        QTimer.singleShot(120, lambda: window.width_stress_action.setChecked(True))
    if quick_access_hidden_preview:
        QTimer.singleShot(
            120,
            lambda: window.show_quick_access_action.setChecked(False),
        )
    if quick_access_above_preview:
        QTimer.singleShot(120, window.quick_access_above_action.trigger)
    if quick_access_below_preview:
        QTimer.singleShot(120, window.quick_access_below_action.trigger)
    if quick_access_labels_preview:
        def show_quick_access_labels_preview():
            window.quick_access_below_action.trigger()
            window.quick_access_labels_action.setChecked(True)

        QTimer.singleShot(120, show_quick_access_labels_preview)
    if add_to_quick_access_preview:
        def show_add_to_quick_access_preview():
            menu = QMenu(window)
            add_action = window.populate_action_context_menu(
                menu, window.rename_page_action
            )
            if add_action is not None:
                add_action.trigger()
            window.quick_access_below_action.trigger()
            window.quick_access_labels_action.setChecked(True)
            window.statusBar().clearMessage()

        QTimer.singleShot(120, show_add_to_quick_access_preview)
    if remove_from_quick_access_preview:
        def show_remove_from_quick_access_preview():
            menu = QMenu(window)
            remove_action = window.populate_quick_access_action_context_menu(
                menu, window.connect_action
            )
            if remove_action is not None:
                remove_action.trigger()
            window.quick_access_below_action.trigger()
            window.quick_access_labels_action.setChecked(True)
            window.statusBar().clearMessage()

        QTimer.singleShot(120, show_remove_from_quick_access_preview)
    if reorder_quick_access_preview:
        def show_reorder_quick_access_preview():
            menu = QMenu(window)
            window.populate_quick_access_action_context_menu(
                menu, window.full_screen_action
            )
            for action in menu.actions():
                if action.objectName() == "moveQuickAccessRightContextAction":
                    action.trigger()
                    break
            window.quick_access_below_action.trigger()
            window.quick_access_labels_action.setChecked(True)
            window.statusBar().clearMessage()

        QTimer.singleShot(120, show_reorder_quick_access_preview)
    if reset_quick_access_preview:
        def show_reset_quick_access_preview():
            menu = QMenu(window)
            add_action = window.populate_action_context_menu(
                menu, window.rename_page_action
            )
            if add_action is not None:
                add_action.trigger()
            window.reset_quick_access_action.trigger()
            window.quick_access_below_action.trigger()
            window.quick_access_labels_action.setChecked(True)
            window.statusBar().clearMessage()

        QTimer.singleShot(120, show_reset_quick_access_preview)
    if export_quick_access_preview:
        def show_export_quick_access_preview():
            add_menu = QMenu(window)
            add_action = window.populate_action_context_menu(
                add_menu, window.rename_page_action
            )
            if add_action is not None:
                add_action.trigger()
            move_menu = QMenu(window)
            window.populate_quick_access_action_context_menu(
                move_menu, window.rename_page_action
            )
            for action in move_menu.actions():
                if action.objectName() == "moveQuickAccessLeftContextAction":
                    action.trigger()
                    break
            window.quick_access_below_action.trigger()
            window.quick_access_labels_action.setChecked(True)
            window.export_quick_access_action.trigger()

        QTimer.singleShot(120, show_export_quick_access_preview)
    if import_quick_access_preview:
        def show_import_quick_access_preview():
            add_menu = QMenu(window)
            add_action = window.populate_action_context_menu(
                add_menu, window.rename_page_action
            )
            if add_action is not None:
                add_action.trigger()
            move_menu = QMenu(window)
            window.populate_quick_access_action_context_menu(
                move_menu, window.rename_page_action
            )
            for action in move_menu.actions():
                if action.objectName() == "moveQuickAccessLeftContextAction":
                    action.trigger()
                    break
            window.quick_access_below_action.trigger()
            window.quick_access_labels_action.setChecked(True)
            window.export_quick_access_action.trigger()
            window.reset_quick_access_action.trigger()
            window.import_quick_access_action.trigger()

        QTimer.singleShot(120, show_import_quick_access_preview)
    if preview_path:
        def save_preview():
            preview = window.grab()
            if zero_query_search_preview or recent_search_preview:
                popup = window.ribbonBar().searchLineEdit()._popup
                if popup.isVisible():
                    painter = QPainter(preview)
                    popup_top_left = window.mapFromGlobal(
                        popup.mapToGlobal(QPoint(0, 0))
                    )
                    painter.drawPixmap(popup_top_left, popup.grab())
                    painter.end()
            preview.save(preview_path)
            app.quit()

        QTimer.singleShot(300, save_preview)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
