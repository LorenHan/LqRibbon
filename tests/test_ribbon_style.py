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
    os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "LqRibbonPy",
        "example",
    ),
)

from PySide6.QtCore import QSettings, Qt
from PySide6.QtGui import QColor, QIcon, QPalette
from PySide6.QtTest import QTest
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDateTimeEdit,
    QDoubleSpinBox,
    QFrame,
    QListWidget,
    QMdiArea,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QStackedWidget,
    QTableWidget,
    QTabWidget,
    QTimeEdit,
    QTreeWidget,
    QWidget,
    QVBoxLayout,
)

from LqRibbon import LqStyle, RibbonPlatformLayout, RibbonMainWindow, RibbonStyle
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
    assert "QStatusBar QLabel" in window.styleSheet()
    assert "QStatusBar QSlider::handle:horizontal" in window.styleSheet()
    assert "QStatusBar QProgressBar::chunk" in window.styleSheet()
    window.close()


def test_fluent_tab_radius_applies_to_m365_only():
    blue_style = LqStyle.get_ribbon_style(RibbonStyle.Office2016Blue)
    light_style = LqStyle.get_ribbon_style(RibbonStyle.Microsoft365Light)
    dark_style = LqStyle.get_ribbon_style(RibbonStyle.Microsoft365Dark)
    assert "border-radius: 0px;" in blue_style
    assert "border-radius: 6px 6px 0px 0px;" in light_style
    assert "border-radius: 6px 6px 0px 0px;" in dark_style


def test_fluent_soft_borders_apply_to_m365_only():
    blue_palette = LqStyle.palette(RibbonStyle.Office2016Blue)
    light_palette = LqStyle.palette(RibbonStyle.Microsoft365Light)
    dark_palette = LqStyle.palette(RibbonStyle.Microsoft365Dark)
    assert blue_palette["tab_border"] == blue_palette["border"]
    assert blue_palette["command_hover_border"] == blue_palette["group_hover"]
    assert light_palette["tab_border"] == "#e5e5e5"
    assert light_palette["control_border"] == "#e5e5e5"
    assert light_palette["command_hover_border"] == "#e5e5e5"
    assert dark_palette["tab_border"] == "#3a3a3a"
    assert dark_palette["control_border"] == "#3a3a3a"
    assert dark_palette["command_hover_border"] == "#3a3a3a"

    light_style = LqStyle.get_full_style(RibbonStyle.Microsoft365Light)
    dark_style = LqStyle.get_full_style(RibbonStyle.Microsoft365Dark)
    assert "border-left: 1px solid #e5e5e5;" in light_style
    assert "border: 1px solid #e5e5e5;" in light_style
    assert "border-color: #e5e5e5;" in light_style
    assert "border-left: 1px solid #3a3a3a;" in dark_style
    assert "border: 1px solid #3a3a3a;" in dark_style
    assert "border-color: #3a3a3a;" in dark_style


def test_common_control_style_is_scoped_and_covers_dark_inputs():
    style_sheet = LqStyle.get_common_control_style(
        RibbonStyle.Microsoft365Dark,
        "lqRibbonDemoSurface",
    )
    assert "QWidget#lqRibbonDemoSurface QComboBox" in style_sheet
    assert "QWidget#lqRibbonDemoSurface QComboBox QAbstractItemView" in style_sheet
    assert "QWidget#lqRibbonDemoSurface QComboBox::down-arrow" in style_sheet
    assert "QWidget#lqRibbonDemoSurface QAbstractSpinBox::up-arrow" in style_sheet
    assert "QWidget#lqRibbonDemoSurface QSpinBox" in style_sheet
    assert "QWidget#lqRibbonDemoSurface QTableWidget" in style_sheet
    assert "QWidget#lqRibbonDemoSurface QListWidget" in style_sheet
    assert "QWidget#lqRibbonDemoSurface QTreeWidget" in style_sheet
    assert "QWidget#lqRibbonDemoSurface QProgressBar" in style_sheet
    assert "QWidget#lqRibbonDemoSurface QTabWidget::pane" in style_sheet
    assert "#1f1f1f" in style_sheet
    assert "#2d2d2d" in style_sheet
    assert "lq_arrow_down_m365_cyan.svg" in style_sheet
    assert "lq_arrow_up_m365_cyan.svg" in style_sheet
    assert "QApplication" not in style_sheet


def test_common_control_style_uses_fluent_primary_and_checked_glyphs():
    style_sheet = LqStyle.get_common_control_style(
        RibbonStyle.Office2016Blue,
        "lqRibbonDemoSurface",
    )
    button_block = _style_block(
        style_sheet,
        "QWidget#lqRibbonDemoSurface QPushButton {",
    )
    checkbox_block = _style_block(
        style_sheet,
        "QWidget#lqRibbonDemoSurface QCheckBox::indicator:checked {",
    )
    radio_block = _style_block(
        style_sheet,
        "QWidget#lqRibbonDemoSurface QRadioButton::indicator:checked {",
    )

    assert "background-color: #2b579a;" in button_block
    assert "color: #ffffff;" in button_block
    assert "color: #202020;" not in button_block
    assert "lq_checkbox_checked_white.svg" in checkbox_block
    assert "lq_radio_checked_white.svg" in radio_block


def _close_color(actual, expected, tolerance=3):
    return (
        abs(actual.red() - expected.red()) <= tolerance
        and abs(actual.green() - expected.green()) <= tolerance
        and abs(actual.blue() - expected.blue()) <= tolerance
    )


def _sample_widget_lightness(widget, x_start, x_end):
    image = widget.grab().toImage()
    values = []
    for x in range(max(1, x_start), min(image.width() - 1, x_end)):
        for y in range(5, max(6, image.height() - 5)):
            color = image.pixelColor(x, y)
            values.append(color.lightness())
    return sum(values) / len(values)


def _style_block(style_sheet, selector):
    start = style_sheet.index(selector)
    end = style_sheet.index("}", start)
    return style_sheet[start:end]


def test_ribbon_embedded_controls_follow_active_style():
    dark_style = LqStyle.get_ribbon_style(RibbonStyle.Microsoft365Dark)
    assert "LqRibbonBar QComboBox" in dark_style
    assert "LqRibbonBar QComboBox QAbstractItemView" in dark_style
    assert "LqRibbonBar QComboBox::down-arrow" in dark_style
    assert "LqRibbonBar QAbstractSpinBox" in dark_style
    assert "LqRibbonBar QAbstractSpinBox::up-arrow" in dark_style
    assert "LqRibbonBar QRadioButton" in dark_style
    assert "LqRibbonBar QSlider::groove:horizontal" in dark_style
    assert "background-color: #2d2d2d;" in dark_style
    assert "lq_arrow_down_m365_cyan.svg" in dark_style
    assert "lq_arrow_up_m365_cyan.svg" in dark_style

    window = MainWindow()
    window.resize(1180, 560)
    window.select_preview_page(style=True)
    window.show()
    _app().processEvents()

    combo = window.style_combo_control.widget()
    window.set_ribbon_style(RibbonStyle.Office2016Blue)
    _app().processEvents()
    light_sample = _sample_widget_lightness(
        combo,
        combo.width() - 42,
        combo.width() - 24,
    )

    window.set_ribbon_style(RibbonStyle.Microsoft365Dark)
    _app().processEvents()
    dark_sample = _sample_widget_lightness(
        combo,
        combo.width() - 42,
        combo.width() - 24,
    )

    assert light_sample > 180
    assert dark_sample < 90
    window.close()


def test_selected_tab_lines_match_office_generation():
    blue_block = _style_block(
        LqStyle.get_ribbon_style(RibbonStyle.Office2016Blue),
        "QTabBar#lqRibbonTabBar::tab:selected {",
    )
    office_2019_block = _style_block(
        LqStyle.get_ribbon_style(RibbonStyle.Office2019Colorful),
        "QTabBar#lqRibbonTabBar::tab:selected {",
    )
    light_block = _style_block(
        LqStyle.get_ribbon_style(RibbonStyle.Microsoft365Light),
        "QTabBar#lqRibbonTabBar::tab:selected {",
    )
    dark_block = _style_block(
        LqStyle.get_ribbon_style(RibbonStyle.Microsoft365Dark),
        "QTabBar#lqRibbonTabBar::tab:selected {",
    )

    assert "border-top: 1px solid transparent;" in blue_block
    assert "border-bottom: 2px solid transparent;" in blue_block
    assert "border-top: 1px solid transparent;" in office_2019_block
    assert "border-bottom: 2px solid transparent;" in office_2019_block
    assert "border-top: 1px solid transparent;" in light_block
    assert "border-bottom: 2px solid #0f6cbd;" in light_block
    assert "border-top: 1px solid transparent;" in dark_block
    assert "border-bottom: 2px solid #60cdff;" in dark_block


def test_page_command_area_border_style_tokens_apply_to_all_styles():
    for style in RibbonStyle:
        palette = LqStyle.palette(style)
        full_style = LqStyle.get_full_style(style)
        pane_block = _style_block(
            full_style, "QTabWidget#lqRibbonBar::pane {"
        )
        command_area_block = _style_block(
            full_style, "QStackedWidget#lqRibbonCommandArea {"
        )
        group_block = _style_block(full_style, "QGroupBox#lqRibbonGroup {")
        assert "page_border" in palette
        assert "border-left:" not in pane_block
        assert "border-right:" not in pane_block
        assert "border-bottom:" not in pane_block
        assert "border-top:" not in pane_block
        assert "border-bottom-left-radius: 8px;" in pane_block
        assert "border-bottom-right-radius: 8px;" in pane_block
        assert "border: none;" in command_area_block
        assert "border-left:" not in command_area_block
        assert "border-right:" not in command_area_block
        assert "border-bottom:" not in command_area_block
        assert "border-top:" not in command_area_block
        assert "border-bottom-left-radius: 8px;" in command_area_block
        assert "border-bottom-right-radius: 8px;" in command_area_block
        assert "border: none;" in group_block


def test_page_command_area_three_sided_border_is_rendered():
    window = RibbonMainWindow()
    outer_color = QColor("#8a8a8a")
    central = QWidget()
    central.setAutoFillBackground(True)
    central_palette = central.palette()
    central_palette.setColor(QPalette.ColorRole.Window, QColor("#f3f3f3"))
    central.setPalette(central_palette)
    central_layout = QVBoxLayout(central)
    central_layout.setContentsMargins(0, 0, 0, 0)
    mdi_area = QMdiArea(central)
    mdi_area.setBackground(outer_color)
    central_layout.addWidget(mdi_area)
    window.setCentralWidget(central)
    ribbon = window.ribbonBar()
    ribbon.setPlatformLayout(RibbonPlatformLayout.Classic)
    page = ribbon.addPage("General")
    group = page.addGroup("Actions")
    group.addAction(
        window.style().standardIcon(
            window.style().StandardPixmap.SP_DialogApplyButton
        ),
        "Apply",
        Qt.ToolButtonStyle.ToolButtonTextUnderIcon,
    )
    window.resize(640, 260)
    window.show()
    _app().processEvents()

    stack = ribbon.findChild(QStackedWidget, "lqRibbonCommandArea")
    assert stack is not None
    assert ribbon.tabBar().objectName() == "lqRibbonTabBar"
    expected = QColor(LqStyle.palette(ribbon.ribbonStyle())["page_border"])
    expected_ribbon_bg = QColor(LqStyle.palette(ribbon.ribbonStyle())["ribbon_bg"])
    stack_margins = stack.contentsMargins()
    assert (stack_margins.left(), stack_margins.top()) == (0, 0)
    assert (stack_margins.right(), stack_margins.bottom()) == (0, 2)

    def assert_ribbon_side_mask(expected_inset):
        assert stack.x() == expected_inset
        assert stack.width() == ribbon.width() - (expected_inset * 2)
        if expected_inset == 0:
            return

        command_rect = stack.geometry()
        ribbon_image = ribbon.grab().toImage()
        left_x = max(0, command_rect.left() - 1)
        right_x = min(ribbon_image.width() - 1, command_rect.right() + 1)
        mid_y = command_rect.top() + (command_rect.height() // 2)
        bottom_y = max(command_rect.top(), command_rect.bottom() - 1)

        mid_side_samples = [
            ribbon_image.pixelColor(left_x, mid_y),
            ribbon_image.pixelColor(right_x, mid_y),
        ]
        bottom_corner_samples = [
            ribbon_image.pixelColor(left_x, bottom_y),
            ribbon_image.pixelColor(right_x, bottom_y),
        ]
        assert all(_close_color(sampled, expected_ribbon_bg) for sampled in mid_side_samples)
        assert all(_close_color(sampled, outer_color) for sampled in bottom_corner_samples)

    def assert_stack_outer_frame_is_transparent():
        stack_image = stack.grab().toImage()
        outer_samples = [
            stack_image.pixelColor(stack_image.width() // 2, stack_image.height() - 1),
            stack_image.pixelColor(stack_image.width() // 2, stack_image.height() - 2),
        ]
        assert all(_close_color(sampled, outer_color) for sampled in outer_samples)

    def assert_page_frame_visible(rounded_corners=True):
        page_image = page.grab().toImage()
        page_border_samples = [
            page_image.pixelColor(page_image.width() // 2, page_image.height() - 1),
            page_image.pixelColor(page_image.width() // 2, page_image.height() - 2),
            page_image.pixelColor(0, page_image.height() // 2),
            page_image.pixelColor(1, page_image.height() // 2),
            page_image.pixelColor(page_image.width() - 1, page_image.height() // 2),
            page_image.pixelColor(page_image.width() - 2, page_image.height() // 2),
        ]
        top_sample = page_image.pixelColor(page_image.width() // 2, 0)
        inner_sample = page_image.pixelColor(page_image.width() - 12, page_image.height() // 2)
        bottom_corner_samples = [
            page_image.pixelColor(0, page_image.height() - 1),
            page_image.pixelColor(page_image.width() - 1, page_image.height() - 1),
        ]
        assert not _close_color(top_sample, expected)
        assert _close_color(inner_sample, expected_ribbon_bg)
        assert all(_close_color(sampled, expected) for sampled in page_border_samples)
        expected_corner = outer_color if rounded_corners else expected
        assert all(_close_color(sampled, expected_corner) for sampled in bottom_corner_samples)

    mac_layout = ribbon.platformLayout() == RibbonPlatformLayout.MacOS
    assert_ribbon_side_mask(0 if mac_layout else 2)
    assert_stack_outer_frame_is_transparent()
    assert_page_frame_visible(rounded_corners=not mac_layout)
    window.showMaximized()
    _app().processEvents()
    assert_ribbon_side_mask(0)
    assert_stack_outer_frame_is_transparent()
    assert_page_frame_visible(rounded_corners=False)
    window.close()


def test_python_frame_theme_uses_frameless_window_and_buttons():
    window = MainWindow()
    window.show()
    _app().processEvents()

    assert window.isFrameThemeEnabled()
    mac_layout = window.ribbonBar().platformLayout() == RibbonPlatformLayout.MacOS
    assert window.isNativeFrameEnabled()
    assert bool(window.windowFlags() & Qt.WindowType.FramelessWindowHint)
    ribbon = window.ribbonBar()
    title_button_bar = ribbon._title_button_bar
    minimize_button = ribbon.findChild(
        type(ribbon._close_button), "lqRibbonWindowMinimizeButton"
    )
    assert minimize_button is not None
    if title_button_bar.isVisible():
        if mac_layout:
            assert minimize_button.geometry().left() < title_button_bar.geometry().left()
        else:
            assert title_button_bar.geometry().right() < minimize_button.geometry().left()
    for name in (
        "lqRibbonWindowMinimizeButton",
        "lqRibbonWindowMaximizeButton",
        "lqRibbonWindowCloseButton",
    ):
        button = ribbon.findChild(type(ribbon._close_button), name)
        assert button is not None
        assert button.isVisible()

    window.setFrameThemeEnabled(False)
    _app().processEvents()
    assert not window.isNativeFrameEnabled()
    assert not bool(window.windowFlags() & Qt.WindowType.FramelessWindowHint)
    window.close()


def test_macos_platform_layout_keeps_style_choices_with_custom_frame():
    window = RibbonMainWindow()
    ribbon = window.ribbonBar()
    ribbon.setPlatformLayout(RibbonPlatformLayout.MacOS)
    window.setFrameThemeEnabled(True)
    window.setRibbonStyle(RibbonStyle.Office2016Blue)
    blue_style = ribbon.styleSheet()
    window.setRibbonStyle(RibbonStyle.Microsoft365Dark)
    dark_style = ribbon.styleSheet()

    assert ribbon.platformLayout() == RibbonPlatformLayout.MacOS
    assert window.isNativeFrameEnabled()
    assert bool(window.windowFlags() & Qt.WindowType.FramelessWindowHint)
    assert "border-bottom: 2px solid #2b579a;" in blue_style
    assert "#202020" in dark_style
    window.close()


def test_macos_office_styles_keep_colored_caption_styles():
    blue_style = LqStyle.get_ribbon_style(
        RibbonStyle.Office2016Blue,
        RibbonPlatformLayout.MacOS,
    )
    colorful_style = LqStyle.get_ribbon_style(
        RibbonStyle.Office2019Colorful,
        RibbonPlatformLayout.MacOS,
    )
    light_style = LqStyle.get_ribbon_style(
        RibbonStyle.Microsoft365Light,
        RibbonPlatformLayout.MacOS,
    )

    assert "background: #2b579a;" in blue_style
    assert "color: #ffffff;" in blue_style
    assert "background: #185abd;" in colorful_style
    assert "color: #ffffff;" in colorful_style
    assert "background: #ffffff;" in colorful_style
    assert "background: #f7f7f7;" in light_style


def test_macos_office_caption_paint_uses_theme_color():
    window = RibbonMainWindow()
    ribbon = window.ribbonBar()
    ribbon.setPlatformLayout(RibbonPlatformLayout.MacOS)
    window.resize(760, 260)
    window.show()
    _app().processEvents()

    for style, expected in [
        (RibbonStyle.Office2016Blue, QColor("#2b579a")),
        (RibbonStyle.Office2019Colorful, QColor("#185abd")),
    ]:
        window.setRibbonStyle(style)
        _app().processEvents()
        title_color = ribbon.grab().toImage().pixelColor(100, 10)
        assert _close_color(title_color, expected, tolerance=4)

    window.close()


def test_macos_platform_layout_keeps_group_title_visible():
    window = RibbonMainWindow()
    ribbon = window.ribbonBar()
    ribbon.setPlatformLayout(RibbonPlatformLayout.MacOS)
    window.setFrameThemeEnabled(True)
    window.resize(1180, 560)
    window.show()
    _app().processEvents()
    page = ribbon.addPage("Draw")
    group = page.addGroup("Tools")
    group.addAction(QIcon(), "Ruler")
    _app().processEvents()

    title_bottom = group.title_label.mapTo(
        page, group.title_label.rect().bottomLeft()
    ).y()
    assert ribbon.height() <= 160
    assert title_bottom < page.height()
    window.close()


def test_fluent_state_timing_tokens_apply_to_m365_only():
    blue_palette = LqStyle.palette(RibbonStyle.Office2016Blue)
    light_palette = LqStyle.palette(RibbonStyle.Microsoft365Light)
    dark_palette = LqStyle.palette(RibbonStyle.Microsoft365Dark)
    assert blue_palette["hover_duration_ms"] == 0
    assert blue_palette["pressed_hold_ms"] == 0
    assert light_palette["hover_duration_ms"] == 120
    assert light_palette["pressed_hold_ms"] == 80
    assert dark_palette["hover_duration_ms"] == 120
    assert dark_palette["pressed_hold_ms"] == 80


def test_example_combo_switches_style():
    window = MainWindow()
    combo = window.style_combo_control.widget()
    colorful_index = combo.findData(int(RibbonStyle.Office2019Colorful))
    combo.setCurrentIndex(colorful_index)
    assert window.ribbonStyle() == RibbonStyle.Office2019Colorful
    assert "#185abd" in window.ribbonBar().styleSheet()
    blue_index = combo.findData(int(RibbonStyle.Office2016Blue))
    combo.setCurrentIndex(blue_index)
    assert window.ribbonStyle() == RibbonStyle.Office2016Blue
    assert "#2b579a" in window.ribbonBar().styleSheet()
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
    assert "#3a3a3a" in accent.styleSheet()
    system_index = combo.findData(SYSTEM_RIBBON_STYLE_VALUE)
    combo.setCurrentIndex(system_index)
    assert preview.property("previewStyle") == int(window.system_ribbon_style())
    window.close()


def test_example_state_timing_preview_tracks_style():
    window = MainWindow()
    preview = window.state_timing_preview
    assert preview.property("previewStyle") == int(RibbonStyle.Office2016Blue)
    assert preview.property("hoverDurationMs") == 0
    assert preview.property("pressedHoldMs") == 0

    window.set_ribbon_style(RibbonStyle.Microsoft365Light)
    assert preview.property("previewStyle") == int(RibbonStyle.Microsoft365Light)
    assert preview.property("hoverDurationMs") == 120
    assert preview.property("pressedHoldMs") == 80

    preview.leave_preview()
    preview.begin_hover_preview()
    assert preview.property("statePhase") == "normal"
    QTest.qWait(preview.property("hoverDurationMs") + 30)
    assert preview.property("statePhase") == "hover"

    preview.begin_pressed_preview()
    preview.end_pressed_preview()
    assert preview.property("statePhase") == "pressed"
    QTest.qWait(preview.property("pressedHoldMs") + 30)
    assert preview.property("statePhase") == "hover"
    preview.leave_preview()
    assert preview.property("statePhase") == "normal"
    window.close()


def test_example_high_contrast_style_preview_pass():
    window = MainWindow()
    window.show()
    _app().processEvents()
    preview = window.style_preview_widget
    accent = preview.findChild(QFrame, "lqRibbonStylePreviewAccent")

    assert window.ribbonStyle() == RibbonStyle.Office2016Blue
    assert window.high_contrast_style_action.objectName() == "highContrastStyleAction"
    assert window.high_contrast_style_action.isCheckable()
    assert not window.high_contrast_style_action.isChecked()
    assert preview.property("highContrast") is False

    window.high_contrast_style_action.trigger()
    _app().processEvents()
    assert window.ribbonStyle() == RibbonStyle.Office2016Blue
    assert preview.property("highContrast") is True
    assert accent.property("previewColor") == "#ffff00"
    assert "High Contrast" in preview.toolTip()
    assert "preview on" in window.high_contrast_style_action.statusTip()
    assert "High Contrast" in window.statusBar().currentMessage()

    window.high_contrast_style_action.trigger()
    _app().processEvents()
    assert preview.property("highContrast") is False
    assert accent.property("previewColor") == LqStyle.palette(
        RibbonStyle.Office2016Blue
    )["accent"]
    assert "preview off" in window.high_contrast_style_action.statusTip()
    window.close()


def test_example_touch_mouse_spacing_toggle_tracks_preview():
    window = MainWindow()
    window.show()
    _app().processEvents()
    preview = window.style_preview_widget

    assert window.touch_spacing_action.objectName() == "touchSpacingAction"
    assert window.touch_spacing_action.isCheckable()
    assert not window.touch_spacing_action.isChecked()
    assert not window.touch_spacing_action.icon().isNull()
    assert "larger touch targets" in window.touch_spacing_action.toolTip()
    assert window.touch_spacing_action.statusTip() == "Touch spacing: off"
    assert window.touch_spacing_preview.objectName() == "touchSpacingPreview"
    assert window.touch_spacing_preview.text() == "Mouse spacing"
    assert preview.property("inputSpacingMode") == "mouse"
    assert window.touch_spacing_action in window.search_actions
    assert (
        window.ribbonBar().searchAction("Touch Spacing")
        is window.touch_spacing_action
    )

    window.touch_spacing_action.trigger()
    _app().processEvents()
    assert window.touch_spacing_action.isChecked()
    assert window.touch_spacing_enabled is True
    assert window.touch_spacing_preview.text() == "Touch spacing"
    assert preview.property("inputSpacingMode") == "touch"
    assert "#touchSpacingPreview" in window.touch_spacing_preview.styleSheet()
    assert "Touch spacing" in window.statusBar().currentMessage()

    window.touch_spacing_action.trigger()
    _app().processEvents()
    assert not window.touch_spacing_action.isChecked()
    assert window.touch_spacing_enabled is False
    assert window.touch_spacing_preview.text() == "Mouse spacing"
    assert preview.property("inputSpacingMode") == "mouse"
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


def test_example_default_content_exposes_themed_common_controls():
    window = MainWindow()
    window.set_ribbon_style(RibbonStyle.Microsoft365Dark)
    surface = window.centralWidget()

    assert surface.objectName() == "lqRibbonDemoSurface"
    assert surface.property("lqRibbonStyleManaged") is True
    assert "QWidget#lqRibbonDemoSurface QComboBox" in surface.styleSheet()
    assert "#1f1f1f" in surface.styleSheet()
    assert "#2d2d2d" in surface.styleSheet()
    assert surface.findChild(QComboBox, "demoModeCombo") is not None
    assert surface.findChild(QComboBox, "demoProfileCombo") is not None
    assert surface.findChild(QSpinBox, "demoSpeedSpin") is not None
    assert surface.findChild(QDoubleSpinBox, "demoGainSpin") is not None
    assert surface.findChild(QTimeEdit, "demoTimeEdit") is not None
    assert surface.findChild(QDateTimeEdit, "demoTimestampEdit") is not None
    assert surface.findChild(QTabWidget, "demoTabWidget") is not None
    assert surface.findChild(QListWidget, "demoListWidget") is not None
    assert surface.findChild(QTreeWidget, "demoTreeWidget") is not None
    assert surface.findChild(QProgressBar, "demoProgressBar") is not None
    table = surface.findChild(QTableWidget, "demoParameterTable")
    assert table is not None
    assert table.rowCount() == 6
    assert table.item(1, 1).text() == "Target speed"
    override_panel = surface.findChild(QFrame, "demoOverridePanel")
    assert override_panel is not None
    assert "#107c41" in override_panel.styleSheet()
    assert override_panel.findChild(QComboBox, "demoOverrideCombo") is not None
    assert override_panel.findChild(QCheckBox, "demoOverrideCheck") is not None
    assert override_panel.findChild(QPushButton, "demoOverrideButton") is not None
    assert window.demo_theme_badge.text() == LqStyle.ribbon_style_name(
        RibbonStyle.Microsoft365Dark
    )
    window.close()


def test_example_non_dark_content_styles_stay_light():
    window = MainWindow()
    for style in (
        RibbonStyle.Office2016Blue,
        RibbonStyle.Office2019Colorful,
        RibbonStyle.Microsoft365Light,
    ):
        window.set_ribbon_style(style)
        palette = LqStyle.palette(style)
        style_sheet = window.centralWidget().styleSheet()
        assert f"background-color: {palette['window_bg']};" in style_sheet
        assert palette["accent"] in style_sheet
        assert "#1f1f1f" not in style_sheet
        assert "#2d2d2d" not in style_sheet
    window.close()


def test_example_host_override_panel_wins_over_ribbon_theme():
    window = MainWindow()
    surface = window.centralWidget()
    override_panel = surface.findChild(QFrame, "demoOverridePanel")
    assert override_panel is not None
    original_override = override_panel.styleSheet()

    window.set_ribbon_style(RibbonStyle.Microsoft365Dark)

    assert "#1f1f1f" in surface.styleSheet()
    assert "#107c41" in override_panel.styleSheet()
    assert "lq_arrow_down_business_green.svg" in override_panel.styleSheet()
    assert "lq_arrow_up_business_green.svg" in override_panel.styleSheet()
    assert override_panel.styleSheet() == original_override
    assert "QFrame#demoOverridePanel" in override_panel.styleSheet()
    window.close()


def test_example_content_style_does_not_replace_user_override():
    window = MainWindow()
    surface = window.centralWidget()
    override = (
        "QWidget#lqRibbonDemoSurface { background: #123456; } "
        "QComboBox#demoModeCombo { background: #654321; }"
    )
    surface.setStyleSheet(override)

    window.set_ribbon_style(RibbonStyle.Microsoft365Dark)

    assert surface.styleSheet() == override
    assert surface.property("lqRibbonStyleManaged") is False
    window.close()


def main():
    _app()
    tests = [
        test_default_style_is_office_2016_blue,
        test_bar_style_switch_updates_stylesheet,
        test_reapplying_same_style_emits_no_duplicate,
        test_window_style_pass_through_updates_full_stylesheet,
        test_fluent_tab_radius_applies_to_m365_only,
        test_fluent_soft_borders_apply_to_m365_only,
        test_common_control_style_is_scoped_and_covers_dark_inputs,
        test_common_control_style_uses_fluent_primary_and_checked_glyphs,
        test_ribbon_embedded_controls_follow_active_style,
        test_selected_tab_lines_match_office_generation,
        test_page_command_area_border_style_tokens_apply_to_all_styles,
        test_page_command_area_three_sided_border_is_rendered,
        test_python_frame_theme_uses_frameless_window_and_buttons,
        test_macos_office_styles_keep_colored_caption_styles,
        test_macos_office_caption_paint_uses_theme_color,
        test_fluent_state_timing_tokens_apply_to_m365_only,
        test_example_combo_switches_style,
        test_example_system_combo_follows_palette,
        test_example_style_preview_tracks_combo,
        test_example_state_timing_preview_tracks_style,
        test_example_high_contrast_style_preview_pass,
        test_example_touch_mouse_spacing_toggle_tracks_preview,
        test_example_style_choice_persists_to_settings,
        test_example_default_content_exposes_themed_common_controls,
        test_example_non_dark_content_styles_stay_light,
        test_example_host_override_panel_wins_over_ribbon_theme,
        test_example_content_style_does_not_replace_user_override,
    ]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")


if __name__ == "__main__":
    main()
