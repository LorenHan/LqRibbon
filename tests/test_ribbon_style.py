"""
Smoke tests for Ribbon style switching.

Run with:
    QT_QPA_PLATFORM=offscreen python tests/test_ribbon_style.py
"""

import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(
    0,
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "LqRibbon", "example"),
)

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication, QFrame

from LqRibbon import LqStyle, RibbonMainWindow, RibbonStyle
from main_window import (
    MainWindow,
    SYSTEM_RIBBON_STYLE_VALUE,
    ribbon_style_settings_value,
    save_ribbon_style_choice,
    saved_ribbon_style_choice,
)


def _app():
    app = QApplication.instance()
    return app or QApplication([])


def test_default_style_is_office_2016_blue():
    window = RibbonMainWindow()
    assert window.ribbonStyle() == RibbonStyle.Office2016Blue
    window.close()


def test_bar_style_switch_updates_stylesheet():
    window = RibbonMainWindow()
    ribbon = window.ribbonBar()
    ribbon.setRibbonStyle(RibbonStyle.Microsoft365Light)
    assert ribbon.ribbonStyle() == RibbonStyle.Microsoft365Light
    assert "#0f6cbd" in ribbon.styleSheet()
    ribbon.setRibbonStyle(RibbonStyle.Microsoft365Dark)
    assert ribbon.ribbonStyle() == RibbonStyle.Microsoft365Dark
    assert "#1f1f1f" in ribbon.styleSheet()
    window.close()


def test_reapplying_same_style_emits_no_duplicate():
    window = RibbonMainWindow()
    ribbon = window.ribbonBar()
    hits = []
    ribbon.ribbonStyleChanged.connect(lambda style: hits.append(style))
    ribbon.setRibbonStyle(RibbonStyle.Microsoft365Light)
    ribbon.setRibbonStyle(RibbonStyle.Microsoft365Light)
    assert hits == [int(RibbonStyle.Microsoft365Light)]
    window.close()


def test_window_style_pass_through_updates_full_stylesheet():
    window = RibbonMainWindow()
    window.setRibbonStyle(RibbonStyle.Microsoft365Dark)
    assert window.ribbonStyle() == RibbonStyle.Microsoft365Dark
    assert "#1f1f1f" in window.styleSheet()
    window.close()


def test_fluent_tab_radius_applies_to_m365_only():
    blue_style = LqStyle.get_ribbon_style(RibbonStyle.Office2016Blue)
    light_style = LqStyle.get_ribbon_style(RibbonStyle.Microsoft365Light)
    dark_style = LqStyle.get_ribbon_style(RibbonStyle.Microsoft365Dark)
    assert "border-radius: 0px;" in blue_style
    assert "border-radius: 6px 6px 0px 0px;" in light_style
    assert "border-radius: 6px 6px 0px 0px;" in dark_style


def test_example_combo_switches_style():
    window = MainWindow()
    combo = window.style_combo_control.widget()
    dark_index = combo.findData(int(RibbonStyle.Microsoft365Dark))
    combo.setCurrentIndex(dark_index)
    assert window.ribbonStyle() == RibbonStyle.Microsoft365Dark
    window.close()


def test_example_system_combo_follows_palette():
    window = MainWindow()
    combo = window.style_combo_control.widget()
    system_index = combo.findData(SYSTEM_RIBBON_STYLE_VALUE)
    assert system_index >= 0
    combo.setCurrentIndex(system_index)
    assert window.ribbonStyle() == window.system_ribbon_style()
    window.set_ribbon_style("system")
    assert combo.currentIndex() == system_index
    assert window.ribbonStyle() == window.system_ribbon_style()
    window.close()


def test_example_style_preview_tracks_combo():
    window = MainWindow()
    combo = window.style_combo_control.widget()
    preview = window.style_preview_widget
    accent = preview.findChild(QFrame, "lqRibbonStylePreviewAccent")
    assert preview.property("previewStyle") == int(RibbonStyle.Office2016Blue)
    assert accent.property("previewColor") == "#2b579a"
    dark_index = combo.findData(int(RibbonStyle.Microsoft365Dark))
    combo.setCurrentIndex(dark_index)
    assert preview.property("previewStyle") == int(RibbonStyle.Microsoft365Dark)
    assert accent.property("previewColor") == "#60cdff"
    system_index = combo.findData(SYSTEM_RIBBON_STYLE_VALUE)
    combo.setCurrentIndex(system_index)
    assert preview.property("previewStyle") == int(window.system_ribbon_style())
    window.close()


def test_example_style_choice_persists_to_settings():
    with tempfile.TemporaryDirectory() as directory:
        path = os.path.join(directory, "style.ini")
        settings = QSettings(path, QSettings.Format.IniFormat)
        assert saved_ribbon_style_choice(settings) == ""
        save_ribbon_style_choice(
            settings,
            ribbon_style_settings_value(RibbonStyle.Microsoft365Dark),
        )

        reloaded = QSettings(path, QSettings.Format.IniFormat)
        assert saved_ribbon_style_choice(reloaded) == "microsoft365dark"

        window = MainWindow()
        window.set_ribbon_style(saved_ribbon_style_choice(reloaded))
        assert window.ribbonStyle() == RibbonStyle.Microsoft365Dark
        combo = window.style_combo_control.widget()
        assert (
            window.style_choice_from_combo_index(combo.currentIndex())
            == "microsoft365dark"
        )
        system_index = combo.findData(SYSTEM_RIBBON_STYLE_VALUE)
        assert window.style_choice_from_combo_index(system_index) == "system"
        window.close()


def main():
    _app()
    tests = [
        test_default_style_is_office_2016_blue,
        test_bar_style_switch_updates_stylesheet,
        test_reapplying_same_style_emits_no_duplicate,
        test_window_style_pass_through_updates_full_stylesheet,
        test_fluent_tab_radius_applies_to_m365_only,
        test_example_combo_switches_style,
        test_example_system_combo_follows_palette,
        test_example_style_preview_tracks_combo,
        test_example_style_choice_persists_to_settings,
    ]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")


if __name__ == "__main__":
    main()
