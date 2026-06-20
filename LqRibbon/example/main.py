"""
LqRibbon Example Application - Main entry point.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from PySide6.QtCore import QSettings, QTimer, Qt
from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

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
        controls_preview
        or gallery_preview
        or shell_preview
        or width_stress_preview
        or quick_access_hidden_preview
        or quick_access_above_preview
        or quick_access_below_preview
        or quick_access_labels_preview
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
    if preview_path:
        QTimer.singleShot(300, lambda: (window.grab().save(preview_path), app.quit()))

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
