"""
MainWindow - feature parity demo for the C++ example.
"""

import io
import json

from PySide6.QtCore import QDate, QPoint, QRect, QSize, Qt, QTimer
from PySide6.QtGui import (
    QAction,
    QActionGroup,
    QColor,
    QIcon,
    QKeySequence,
    QPainter,
    QPen,
    QPixmap,
)
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMdiArea,
    QMenu,
    QMessageBox,
    QPlainTextEdit,
    QStyle,
    QTableWidget,
    QToolButton,
    QWidget,
)

from LqRibbon import (
    LqStyle,
    OfficePopupMenu,
    OfficePopupWindow,
    PopupColorButton,
    RibbonBackstageView,
    RibbonButtonControl,
    RibbonCheckBoxControl,
    RibbonComboBoxControl,
    RibbonDateEditControl,
    RibbonDoubleSpinBoxControl,
    RibbonFontComboBoxControl,
    RibbonGallery,
    RibbonGalleryControl,
    RibbonGalleryGroup,
    RibbonLineEditControl,
    RibbonMainWindow,
    RibbonMdiArea,
    RibbonProgressBar,
    RibbonRadioButtonControl,
    RibbonSliderControl,
    RibbonSliderPane,
    RibbonSliderPaneControl,
    RibbonSpinBoxControl,
    RibbonStatusBar,
    RibbonStatusBarSwitchGroup,
    RibbonStyle,
    RibbonSystemMenu,
    RibbonToolBarControl,
)

SYSTEM_RIBBON_STYLE_VALUE = -1
QUICK_ACCESS_TOP_POSITION = 1
QUICK_ACCESS_BOTTOM_POSITION = 2
SEARCH_BAR_CENTRAL = 1
SEARCH_BAR_COMPACT = 2
SEARCH_BAR_HIDDEN = 3
RIBBON_STYLE_SETTINGS_KEY = "Ribbon/Style"


def ribbon_style_settings_value(style):
    style = LqStyle.coerce_style(style)
    names = {
        RibbonStyle.Office2016Blue: "office2016blue",
        RibbonStyle.Office2019Colorful: "office2019colorful",
        RibbonStyle.Microsoft365Light: "microsoft365light",
        RibbonStyle.Microsoft365Dark: "microsoft365dark",
    }
    return names[style]


def saved_ribbon_style_choice(settings):
    return str(settings.value(RIBBON_STYLE_SETTINGS_KEY, "")).strip()


def save_ribbon_style_choice(settings, choice):
    settings.setValue(RIBBON_STYLE_SETTINGS_KEY, choice)
    settings.sync()


class FluentStateTimingPreview(QToolButton):
    """Interactive style swatch for Fluent hover and pressed timing."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("lqRibbonStateTimingPreview")
        self.setFixedSize(30, 24)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setIconSize(QSize(14, 14))
        self.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_DialogApplyButton)
        )
        self.setToolTip("Hover and press timing preview")
        self._style = RibbonStyle.Office2016Blue
        self._phase = "normal"
        self._hovered = False
        self._hover_timer = QTimer(self)
        self._hover_timer.setSingleShot(True)
        self._hover_timer.timeout.connect(lambda: self._set_phase("hover"))
        self._pressed_reset_timer = QTimer(self)
        self._pressed_reset_timer.setSingleShot(True)
        self._pressed_reset_timer.timeout.connect(self._restore_after_pressed)
        self.apply_ribbon_style(RibbonStyle.Office2016Blue)

    def apply_ribbon_style(self, style):
        self._style = LqStyle.coerce_style(style)
        palette = LqStyle.palette(self._style)
        self.setProperty("previewStyle", int(self._style))
        self.setProperty("hoverDurationMs", palette["hover_duration_ms"])
        self.setProperty("pressedHoldMs", palette["pressed_hold_ms"])
        self._update_style_sheet()

    def begin_hover_preview(self):
        self._hovered = True
        self._pressed_reset_timer.stop()
        if self._phase == "pressed":
            return
        hover_ms = int(self.property("hoverDurationMs"))
        if hover_ms > 0:
            self._hover_timer.start(hover_ms)
        else:
            self._set_phase("hover")

    def leave_preview(self):
        self._hovered = False
        self._hover_timer.stop()
        self._pressed_reset_timer.stop()
        self._set_phase("normal")

    def begin_pressed_preview(self):
        self._hover_timer.stop()
        self._pressed_reset_timer.stop()
        self._set_phase("pressed")

    def end_pressed_preview(self):
        if self._phase != "pressed":
            return
        pressed_ms = int(self.property("pressedHoldMs"))
        if pressed_ms > 0:
            self._pressed_reset_timer.start(pressed_ms)
        else:
            self._restore_after_pressed()

    def enterEvent(self, event):
        self.begin_hover_preview()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.leave_preview()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        self.begin_pressed_preview()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        self.end_pressed_preview()

    def _restore_after_pressed(self):
        self._set_phase("hover" if self._hovered else "normal")

    def _set_phase(self, phase):
        if self._phase == phase:
            return
        self._phase = phase
        self.setProperty("statePhase", phase)
        self._update_style_sheet()

    def _update_style_sheet(self):
        palette = LqStyle.palette(self._style)
        backgrounds = {
            "normal": palette["field_bg"],
            "hover": palette["group_hover"],
            "pressed": palette["group_pressed"],
        }
        self.setProperty("statePhase", self._phase)
        self.setStyleSheet(
            "QToolButton#lqRibbonStateTimingPreview "
            f"{{ background: {backgrounds[self._phase]}; "
            f"border: 1px solid {palette['control_border']}; "
            "border-radius: 3px; padding: 0px; "
            f"color: {palette['text']}; }}"
        )


class MainWindow(RibbonMainWindow):
    """Ribbon demo window with the same feature surface as the C++ demo."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("LqRibbon Example")
        self.resize(920, 560)
        self.runtime_page_counter = 1
        self.runtime_group_counter = 1
        self.rename_custom_counter = 1
        self.custom_command_counter = 1
        self.last_custom_group = None
        self.saved_ribbon_state = b""
        self.exported_ribbon_customization_state = b""
        self.search_actions = []
        self.high_contrast_style_pass = False
        self.touch_spacing_enabled = False
        self.create_ribbon()
        self.install_default_content()

    def create_ribbon(self):
        ribbon = self.ribbonBar()

        self.general_page = ribbon.addPage("General")
        view_group = self.general_page.addGroup("View")
        self.full_screen_action = self._add_group_action(
            view_group, QStyle.StandardPixmap.SP_TitleBarMaxButton, "Full Screen"
        )
        self.mdi_action = self._add_group_action(
            view_group,
            QStyle.StandardPixmap.SP_FileDialogDetailedView,
            "Mdi Mode",
            Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )
        self.tab_action = self._add_group_action(
            view_group,
            QStyle.StandardPixmap.SP_FileDialogListView,
            "Tab Mode",
            Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )
        self._create_style_switch_group()
        voice_group = self.general_page.addGroup("Voice")
        self.dictate_microphone_action = voice_group.addAction(
            self._icon(QStyle.StandardPixmap.SP_MediaVolume),
            "Dictate",
            Qt.ToolButtonStyle.ToolButtonTextUnderIcon,
        )
        self.dictate_microphone_action.setObjectName("dictateMicrophoneAction")
        self.dictate_microphone_action.setCheckable(True)
        self.dictate_microphone_action.setToolTip(
            "Start voice dictation from the microphone"
        )
        self.dictate_microphone_action.setStatusTip(
            "Dictate: microphone ready"
        )
        self.dictate_microphone_preview = QLabel(
            "Dictate: microphone idle", voice_group
        )
        self.dictate_microphone_preview.setObjectName("dictateMicrophonePreview")
        self.dictate_microphone_preview.setMinimumWidth(190)
        self.dictate_microphone_preview.setFixedHeight(30)
        self.dictate_microphone_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.dictate_microphone_preview.setFrameShape(QFrame.Shape.StyledPanel)
        self.dictate_microphone_preview.setToolTip(
            "Current dictation microphone state"
        )
        voice_group.addWidget(self.dictate_microphone_preview)

        self.driver_page = ribbon.addPage("Driver")
        communication_group = self.driver_page.addGroup("Communication")
        self.settings_action = self._add_group_action(
            communication_group, QStyle.StandardPixmap.SP_ComputerIcon, "Settings"
        )
        self.connect_action = self._add_group_action(
            communication_group, QStyle.StandardPixmap.SP_DialogApplyButton, "Connect"
        )

        self.specialist_group = self.driver_page.addGroup("Specialist")
        self.basic_action = self._add_group_action(
            self.specialist_group,
            QStyle.StandardPixmap.SP_FileDialogContentsView,
            "Basic Operation",
            Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )
        self.driver_action = self._add_group_action(
            self.specialist_group,
            QStyle.StandardPixmap.SP_DriveHDIcon,
            "Driver Configuration",
            Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )
        self._add_control_modes_button(self.specialist_group)

        self.controls_page = ribbon.addPage("Controls")
        self._create_controls_page()

        self.gallery_page = ribbon.addPage("Gallery")
        self._create_gallery_page()

        self.insert_page = ribbon.addPage("Insert")
        self._create_insert_page()

        self.format_page = ribbon.addPage("Format")
        self._create_format_page()

        self.contextual_page = ribbon.addPage("Contextual")
        self._create_contextual_page()

        self.options_page = ribbon.addPage("Options")
        self._create_options_page()

        self.review_page = ribbon.addPage("Review")
        self._create_review_page()

        self.view_page = ribbon.addPage("View")
        self._create_view_page()

        self.draw_page = ribbon.addPage("Draw")
        self._create_draw_page()

        self.animation_page = ribbon.addPage("Animation")
        self._create_animation_page()

        self.design_page = ribbon.addPage("Design")
        self._create_design_page()

        self.data_page = ribbon.addPage("Data")
        self._create_data_page()

        self.tell_me_page = ribbon.addPage("Tell Me")
        self._create_command_discovery_page()

        self.shell_page = ribbon.addPage("Shell")
        self._create_shell_page()
        self._create_system_surfaces()
        self._create_status_bar()
        self._create_customize_state()
        self._connect_actions()
        self._configure_search_and_quick_access()
        self._configure_quick_access_context_menus()
        self._configure_action_context_menus()

        ribbon.setCurrentPageIndex(ribbon.pageIndex(self.driver_page))
        self.setFrameThemeEnabled(True)
        self.set_search_bar_appearance(SEARCH_BAR_CENTRAL)
        ribbon.setSearchPlaceholderText("Search commands")
        ribbon.setRecentSearchLimit(5)
        ribbon.setSearchSuggestions(
            ["Settings", "Connect", "Control Modes", "Center Search"]
        )
        ribbon.setSearchDocumentResults(
            [
                "Driver commissioning checklist",
                "Servo tuning guide: velocity loop",
                "Find result: alarm reset procedure",
            ]
        )
        ribbon.setSearchRelatedFiles(
            [
                "Servo project notes.one",
                "Alarm history export.csv",
                "Control loop sample.lqribbon",
            ]
        )

    def _create_style_switch_group(self):
        style_group = self.general_page.addGroup("Style")
        self.style_combo_control = RibbonComboBoxControl(style_group)
        style_combo = self.style_combo_control.widget()
        style_combo.setObjectName("lqRibbonStyleCombo")
        style_combo.setMinimumWidth(220)
        for style in RibbonStyle:
            combo_text = (
                "M365 Light"
                if style == RibbonStyle.Microsoft365Light
                else "M365 Dark"
                if style == RibbonStyle.Microsoft365Dark
                else LqStyle.ribbon_style_name(style)
            )
            style_combo.addItem(combo_text, int(style))
            style_combo.setItemData(
                style_combo.count() - 1,
                LqStyle.ribbon_style_name(style),
                Qt.ItemDataRole.ToolTipRole,
            )
        style_combo.addItem("System", SYSTEM_RIBBON_STYLE_VALUE)
        style_combo.setItemData(
            style_combo.count() - 1,
            "Follow current system light/dark palette",
            Qt.ItemDataRole.ToolTipRole,
        )
        style_group.addWidget(self.style_combo_control)
        self.style_preview_widget = self._create_style_preview_widget(style_group)
        self.state_timing_preview = FluentStateTimingPreview(style_group)
        self._update_style_preview(RibbonStyle.Office2016Blue)
        self.style_preview_widget.setProperty("inputSpacingMode", "mouse")
        style_group.addWidget(self.style_preview_widget)
        style_group.addWidget(self.state_timing_preview)
        self.high_contrast_style_action = style_group.addAction(
            self._icon(QStyle.StandardPixmap.SP_MessageBoxWarning),
            "High Contrast",
            Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )
        self.high_contrast_style_action.setObjectName("highContrastStyleAction")
        self.high_contrast_style_action.setCheckable(True)
        self.high_contrast_style_action.setToolTip(
            "High Contrast: preview maximum contrast colors"
        )
        self.high_contrast_style_action.setStatusTip(
            "High Contrast: preview off"
        )
        self.touch_spacing_preview = QLabel("Mouse spacing", style_group)
        self.touch_spacing_preview.setObjectName("touchSpacingPreview")
        self.touch_spacing_preview.setMinimumWidth(130)
        self.touch_spacing_preview.setFixedHeight(24)
        self.touch_spacing_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.touch_spacing_preview.setFrameShape(QFrame.Shape.StyledPanel)
        self.touch_spacing_preview.setToolTip("Current touch or mouse spacing mode")
        style_group.addWidget(self.touch_spacing_preview)
        self.touch_spacing_action = style_group.addAction(
            self._icon(QStyle.StandardPixmap.SP_ComputerIcon),
            "Touch Spacing",
            Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )
        self.touch_spacing_action.setObjectName("touchSpacingAction")
        self.touch_spacing_action.setCheckable(True)
        self.touch_spacing_action.setToolTip(
            "Touch/Mouse spacing: use larger touch targets"
        )
        self.touch_spacing_action.setStatusTip("Touch spacing: off")
        style_combo.highlighted.connect(self._preview_selected_ribbon_style)
        style_combo.currentIndexChanged.connect(self._apply_selected_ribbon_style)

    def _create_style_preview_widget(self, parent):
        preview = QWidget(parent)
        preview.setObjectName("lqRibbonStylePreview")
        preview.setFixedSize(128, 24)
        layout = QHBoxLayout(preview)
        layout.setContentsMargins(0, 2, 0, 2)
        layout.setSpacing(4)
        for name in [
            "lqRibbonStylePreviewAccent",
            "lqRibbonStylePreviewRibbon",
            "lqRibbonStylePreviewField",
            "lqRibbonStylePreviewText",
        ]:
            swatch = QFrame(preview)
            swatch.setObjectName(name)
            swatch.setFixedSize(24, 18)
            layout.addWidget(swatch)
        return preview

    def _style_from_combo_index(self, index):
        style_combo = self.style_combo_control.widget()
        value = style_combo.itemData(index)
        return (
            self.system_ribbon_style()
            if value == SYSTEM_RIBBON_STYLE_VALUE
            else LqStyle.coerce_style(value)
        )

    def style_choice_from_combo_index(self, index):
        style_combo = self.style_combo_control.widget()
        value = style_combo.itemData(index)
        if value == SYSTEM_RIBBON_STYLE_VALUE:
            return "system"
        return ribbon_style_settings_value(value)

    def _update_style_preview(self, style):
        style = LqStyle.coerce_style(style)
        palette = LqStyle.palette(style)
        self.style_preview_widget.setProperty("previewStyle", int(style))
        high_contrast = bool(self.high_contrast_style_pass)
        self.style_preview_widget.setProperty("highContrast", high_contrast)
        tooltip = LqStyle.ribbon_style_name(style)
        if high_contrast:
            tooltip = f"{tooltip} - High Contrast preview"
        self.style_preview_widget.setToolTip(tooltip)
        colors = {
            "accent": "#ffff00",
            "ribbon_bg": "#000000",
            "field_bg": "#000000",
            "text": "#ffffff",
            "control_border": "#ffffff",
        } if high_contrast else palette
        for object_name, palette_key in [
            ("lqRibbonStylePreviewAccent", "accent"),
            ("lqRibbonStylePreviewRibbon", "ribbon_bg"),
            ("lqRibbonStylePreviewField", "field_bg"),
            ("lqRibbonStylePreviewText", "text"),
        ]:
            swatch = self.style_preview_widget.findChild(QFrame, object_name)
            if swatch is None:
                continue
            color = colors[palette_key]
            swatch.setProperty("previewColor", color)
            border = colors["control_border"]
            swatch.setStyleSheet(
                f"QFrame {{ background: {color}; border: 1px solid {border}; }}"
            )
        self.state_timing_preview.apply_ribbon_style(style)

    def _preview_selected_ribbon_style(self, index):
        self._update_style_preview(self._style_from_combo_index(index))

    def _apply_selected_ribbon_style(self, index):
        style = self._style_from_combo_index(index)
        self._update_style_preview(style)
        self.setRibbonStyle(style)

    def system_ribbon_style(self):
        window_color = self.palette().color(self.backgroundRole())
        return (
            RibbonStyle.Microsoft365Dark
            if window_color.lightness() < 128
            else RibbonStyle.Microsoft365Light
        )

    def _create_controls_page(self):
        selector_group = self.controls_page.addGroup("Selectors")
        mode_combo = RibbonComboBoxControl(selector_group)
        mode_combo.widget().addItems(["Position", "Velocity", "Torque"])
        selector_group.addWidget(mode_combo)

        font_combo = RibbonFontComboBoxControl(selector_group)
        selector_group.addWidget(font_combo)

        enabled_check = RibbonCheckBoxControl("Enabled", selector_group)
        enabled_check.widget().setChecked(True)
        selector_group.addWidget(enabled_check)

        auto_radio = RibbonRadioButtonControl("Auto", selector_group)
        auto_radio.widget().setChecked(True)
        selector_group.addWidget(auto_radio)

        value_group = self.controls_page.addGroup("Values")
        name_edit = RibbonLineEditControl(value_group)
        name_edit.widget().setPlaceholderText("Axis name")
        value_group.addWidget(name_edit)

        speed_spin = RibbonSpinBoxControl(value_group)
        speed_spin.widget().setRange(0, 6000)
        speed_spin.widget().setValue(1500)
        value_group.addWidget(speed_spin)

        gain_spin = RibbonDoubleSpinBoxControl(value_group)
        gain_spin.widget().setRange(0.0, 10.0)
        gain_spin.widget().setSingleStep(0.1)
        gain_spin.widget().setValue(1.5)
        value_group.addWidget(gain_spin)

        date_edit = RibbonDateEditControl(value_group)
        date_edit.widget().setCalendarPopup(True)
        date_edit.widget().setDate(QDate.currentDate())
        value_group.addWidget(date_edit)

        range_group = self.controls_page.addGroup("Range")
        limit_slider = RibbonSliderControl(Qt.Orientation.Horizontal, range_group)
        limit_slider.widget().setRange(0, 100)
        limit_slider.widget().setValue(35)
        range_group.addWidget(limit_slider)

        fine_slider = RibbonSliderPaneControl(range_group)
        fine_slider.widget().setRange(0, 100)
        fine_slider.widget().setValue(65)
        range_group.addWidget(fine_slider)

        apply_button = RibbonButtonControl(range_group)
        apply_button.setSmallIcon(self._icon(QStyle.StandardPixmap.SP_DialogApplyButton))
        apply_button.setLargeIcon(self._icon(QStyle.StandardPixmap.SP_DialogApplyButton))
        apply_button.setLabel("Apply")
        apply_button.widget().clicked.connect(lambda: self._message("Apply"))
        range_group.addWidget(apply_button)

    def _create_gallery_page(self):
        style_group = self.gallery_page.addGroup("Styles")
        gallery_group = RibbonGalleryGroup(self)
        gallery_group.setSize(QSize(88, 31))
        gallery_items = [
            ("Normal", QStyle.StandardPixmap.SP_FileDialogDetailedView),
            ("Compact", QStyle.StandardPixmap.SP_FileDialogListView),
            ("Drive", QStyle.StandardPixmap.SP_DriveHDIcon),
            ("Network", QStyle.StandardPixmap.SP_ComputerIcon),
            ("Apply", QStyle.StandardPixmap.SP_DialogApplyButton),
            ("Help", QStyle.StandardPixmap.SP_MessageBoxQuestion),
        ]
        for caption, icon in gallery_items:
            gallery_group.addItem(caption, self._icon(icon))
        self.high_dpi_gallery_item = gallery_group.addItem(
            "High DPI",
            self._high_dpi_gallery_icon(),
        )
        self.high_dpi_gallery_item.setToolTip("Scalable high-DPI icon sample")
        self.high_dpi_gallery_item.setData(
            Qt.ItemDataRole.UserRole,
            "highDpiScalableIcon",
        )
        self.app_icon_color_set_item = gallery_group.addItem(
            "App Colors",
            self._app_icon_color_set_icon(),
        )
        self.app_icon_color_set_item.setToolTip("New Office app icon color set")
        self.app_icon_color_set_item.setData(
            Qt.ItemDataRole.UserRole,
            "newAppIconColorSet",
        )

        self.style_gallery = RibbonGallery(style_group)
        self.style_gallery.setObjectName("styleGallery")
        self.style_gallery.setToolTip("In-ribbon gallery for style presets")
        self.style_gallery.setGalleryGroup(gallery_group)
        self.style_gallery.setColumnCount(4)
        self.style_gallery.setRowCount(2)
        self.style_gallery.setCheckedIndex(1)

        self.gallery_menu = QMenu(self.style_gallery)
        self.gallery_menu.setObjectName("styleGalleryPopupMenu")
        self.gallery_menu.setToolTip("Popup gallery menu for additional style commands")
        self.more_styles_action = self.gallery_menu.addAction("More styles")
        self.more_styles_action.setObjectName("moreStylesGalleryAction")
        self.reset_style_action = self.gallery_menu.addAction("Reset style")
        self.reset_style_action.setObjectName("resetStyleGalleryAction")
        self.style_gallery.setPopupMenu(self.gallery_menu)
        self.style_gallery.itemClicked.connect(
            lambda item: self._message(f"Gallery style: {item.caption()}")
        )

        style_group.addWidget(RibbonGalleryControl(style_group, self.style_gallery))

        gallery_action_group = self.gallery_page.addGroup("Actions")
        gallery_toolbar = RibbonToolBarControl(gallery_action_group)
        gallery_toolbar.addAction(self._icon(QStyle.StandardPixmap.SP_DialogOpenButton), "Open")
        gallery_toolbar.addAction(self._icon(QStyle.StandardPixmap.SP_DialogSaveButton), "Save")
        gallery_toolbar.addSeparator()
        more_menu = gallery_toolbar.addMenu(self._icon(QStyle.StandardPixmap.SP_ArrowDown), "More")
        more_menu.addActions(self.gallery_menu.actions())
        gallery_action_group.addWidget(gallery_toolbar)

    def _create_insert_page(self):
        illustrations_group = self.insert_page.addGroup("Illustrations")
        self.svg_icon_insert_action = illustrations_group.addAction(
            self._svg_insert_icon(),
            "SVG Icon",
            Qt.ToolButtonStyle.ToolButtonTextUnderIcon,
        )
        self.svg_icon_insert_action.setObjectName("svgIconInsertAction")
        self.svg_icon_insert_action.setToolTip(
            "Insert a scalable SVG icon into the document"
        )
        self.svg_icon_insert_action.setStatusTip("SVG Icon: ready to insert")

        self.svg_icon_insert_preview = QLabel("SVG Icons: none inserted", illustrations_group)
        self.svg_icon_insert_preview.setObjectName("svgIconInsertPreview")
        self.svg_icon_insert_preview.setMinimumWidth(190)
        self.svg_icon_insert_preview.setFixedHeight(30)
        self.svg_icon_insert_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.svg_icon_insert_preview.setFrameShape(QFrame.Shape.StyledPanel)
        self.svg_icon_insert_preview.setToolTip("Last inserted SVG icon state")
        illustrations_group.addWidget(self.svg_icon_insert_preview)

        self.model_3d_insert_action = illustrations_group.addAction(
            self._icon(QStyle.StandardPixmap.SP_ComputerIcon),
            "3D Model",
            Qt.ToolButtonStyle.ToolButtonTextUnderIcon,
        )
        self.model_3d_insert_action.setObjectName("model3DInsertAction")
        self.model_3d_insert_action.setToolTip(
            "Insert a rotatable 3D model into the document"
        )
        self.model_3d_insert_action.setStatusTip("3D Model: ready to insert")

        self.model_3d_preview = QLabel("3D Models: none inserted", illustrations_group)
        self.model_3d_preview.setObjectName("model3DPreview")
        self.model_3d_preview.setMinimumWidth(190)
        self.model_3d_preview.setFixedHeight(30)
        self.model_3d_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.model_3d_preview.setFrameShape(QFrame.Shape.StyledPanel)
        self.model_3d_preview.setToolTip("Last inserted 3D model state")
        illustrations_group.addWidget(self.model_3d_preview)

        charts_group = self.insert_page.addGroup("Charts")
        self.recommended_chart_action = charts_group.addAction(
            self._icon(QStyle.StandardPixmap.SP_FileDialogDetailedView),
            "Recommended Chart",
            Qt.ToolButtonStyle.ToolButtonTextUnderIcon,
        )
        self.recommended_chart_action.setObjectName("recommendedChartAction")
        self.recommended_chart_action.setToolTip(
            "Suggest the best chart type for selected data"
        )
        self.recommended_chart_action.setStatusTip(
            "Recommended Chart: suggestions ready"
        )
        self.recommended_chart_preview = QLabel("Charts: no recommendation", charts_group)
        self.recommended_chart_preview.setObjectName("recommendedChartPreview")
        self.recommended_chart_preview.setMinimumWidth(220)
        self.recommended_chart_preview.setFixedHeight(30)
        self.recommended_chart_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.recommended_chart_preview.setFrameShape(QFrame.Shape.StyledPanel)
        self.recommended_chart_preview.setToolTip("Recommended chart selection state")
        charts_group.addWidget(self.recommended_chart_preview)

    def _create_format_page(self):
        svg_format_group = self.format_page.addGroup("SVG Format")
        self.svg_recolor_action = svg_format_group.addAction(
            self._svg_recolor_icon(),
            "Recolor SVG",
            Qt.ToolButtonStyle.ToolButtonTextUnderIcon,
        )
        self.svg_recolor_action.setObjectName("svgRecolorAction")
        self.svg_recolor_action.setToolTip(
            "Apply an accent color to the selected SVG icon"
        )
        self.svg_recolor_action.setStatusTip("Recolor SVG: accent preview ready")

        self.svg_recolor_preview = QLabel("SVG color: original", svg_format_group)
        self.svg_recolor_preview.setObjectName("svgRecolorPreview")
        self.svg_recolor_preview.setMinimumWidth(190)
        self.svg_recolor_preview.setFixedHeight(30)
        self.svg_recolor_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.svg_recolor_preview.setFrameShape(QFrame.Shape.StyledPanel)
        self.svg_recolor_preview.setToolTip("Selected SVG recolor state")
        svg_format_group.addWidget(self.svg_recolor_preview)

        self.svg_convert_shape_action = svg_format_group.addAction(
            self._svg_convert_shape_icon(),
            "Convert to Shape",
            Qt.ToolButtonStyle.ToolButtonTextUnderIcon,
        )
        self.svg_convert_shape_action.setObjectName("svgConvertShapeAction")
        self.svg_convert_shape_action.setToolTip(
            "Convert the selected SVG icon into editable vector shapes"
        )
        self.svg_convert_shape_action.setStatusTip(
            "Convert to Shape: editable vector preview ready"
        )

        self.svg_convert_shape_preview = QLabel(
            "SVG shape: vector icon", svg_format_group
        )
        self.svg_convert_shape_preview.setObjectName("svgConvertShapePreview")
        self.svg_convert_shape_preview.setMinimumWidth(210)
        self.svg_convert_shape_preview.setFixedHeight(30)
        self.svg_convert_shape_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.svg_convert_shape_preview.setFrameShape(QFrame.Shape.StyledPanel)
        self.svg_convert_shape_preview.setToolTip("Selected SVG shape conversion state")
        svg_format_group.addWidget(self.svg_convert_shape_preview)

    def _create_contextual_page(self):
        tools_group = self.contextual_page.addGroup("Picture Tools")
        self.contextual_group_color_action = tools_group.addAction(
            self._icon(QStyle.StandardPixmap.SP_DriveDVDIcon),
            "Group Color",
            Qt.ToolButtonStyle.ToolButtonTextUnderIcon,
        )
        self.contextual_group_color_action.setObjectName(
            "contextualGroupColorAction"
        )
        self.contextual_group_color_action.setToolTip(
            "Apply a contextual tab group color to Picture Tools"
        )
        self.contextual_group_color_action.setStatusTip(
            "Contextual group color: purple"
        )
        self.contextual_group_color_preview = QLabel(
            "Picture Tools: neutral", tools_group
        )
        self.contextual_group_color_preview.setObjectName(
            "contextualGroupColorPreview"
        )
        self.contextual_group_color_preview.setMinimumWidth(210)
        self.contextual_group_color_preview.setFixedHeight(30)
        self.contextual_group_color_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contextual_group_color_preview.setFrameShape(QFrame.Shape.StyledPanel)
        self.contextual_group_color_preview.setToolTip(
            "Current contextual tab group color"
        )
        tools_group.addWidget(self.contextual_group_color_preview)
        self.contextual_tab_visibility_action = tools_group.addAction(
            self._icon(QStyle.StandardPixmap.SP_DialogYesButton),
            "Show Contextual",
            Qt.ToolButtonStyle.ToolButtonTextUnderIcon,
        )
        self.contextual_tab_visibility_action.setObjectName(
            "contextualTabVisibilityAction"
        )
        self.contextual_tab_visibility_action.setCheckable(True)
        self.contextual_tab_visibility_action.setChecked(True)
        self.contextual_tab_visibility_action.setToolTip(
            "Show or hide contextual ribbon tabs"
        )
        self.contextual_tab_visibility_action.setStatusTip(
            "Contextual tabs: visible"
        )
        self.contextual_tab_visibility_preview = QLabel(
            "Contextual tabs: visible", tools_group
        )
        self.contextual_tab_visibility_preview.setObjectName(
            "contextualTabVisibilityPreview"
        )
        self.contextual_tab_visibility_preview.setMinimumWidth(210)
        self.contextual_tab_visibility_preview.setFixedHeight(30)
        self.contextual_tab_visibility_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contextual_tab_visibility_preview.setFrameShape(QFrame.Shape.StyledPanel)
        self.contextual_tab_visibility_preview.setToolTip(
            "Current contextual tab visibility state"
        )
        tools_group.addWidget(self.contextual_tab_visibility_preview)
        self.title_groups_visibility_action = tools_group.addAction(
            self._icon(QStyle.StandardPixmap.SP_TitleBarMenuButton),
            "Title Groups",
            Qt.ToolButtonStyle.ToolButtonTextUnderIcon,
        )
        self.title_groups_visibility_action.setObjectName(
            "titleGroupsVisibilityAction"
        )
        self.title_groups_visibility_action.setCheckable(True)
        self.title_groups_visibility_action.setChecked(True)
        self.title_groups_visibility_action.setToolTip(
            "Show or hide contextual title groups"
        )
        self.title_groups_visibility_action.setStatusTip("Title groups: visible")
        self.title_groups_visibility_preview = QLabel(
            "Title groups: visible", tools_group
        )
        self.title_groups_visibility_preview.setObjectName(
            "titleGroupsVisibilityPreview"
        )
        self.title_groups_visibility_preview.setMinimumWidth(210)
        self.title_groups_visibility_preview.setFixedHeight(30)
        self.title_groups_visibility_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_groups_visibility_preview.setFrameShape(QFrame.Shape.StyledPanel)
        self.title_groups_visibility_preview.setToolTip(
            "Current contextual title groups visibility state"
        )
        tools_group.addWidget(self.title_groups_visibility_preview)

    def _create_options_page(self):
        accessibility_group = self.options_page.addGroup("Accessibility")
        self.reduced_motion_action = accessibility_group.addAction(
            self._icon(QStyle.StandardPixmap.SP_MediaStop),
            "Reduced Motion",
            Qt.ToolButtonStyle.ToolButtonTextUnderIcon,
        )
        self.reduced_motion_action.setObjectName("reducedMotionAction")
        self.reduced_motion_action.setCheckable(True)
        self.reduced_motion_action.setToolTip(
            "Reduced Motion: minimize animated transitions"
        )
        self.reduced_motion_action.setStatusTip("Reduced Motion: off")

        self.reduced_motion_preview = QLabel(
            "Motion: full animation", accessibility_group
        )
        self.reduced_motion_preview.setObjectName("reducedMotionPreview")
        self.reduced_motion_preview.setMinimumWidth(190)
        self.reduced_motion_preview.setFixedHeight(30)
        self.reduced_motion_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.reduced_motion_preview.setFrameShape(QFrame.Shape.StyledPanel)
        self.reduced_motion_preview.setToolTip("Current motion preference")
        accessibility_group.addWidget(self.reduced_motion_preview)

    def _create_review_page(self):
        insights_group = self.review_page.addGroup("Insights")
        self.smart_lookup_action = insights_group.addAction(
            self._icon(QStyle.StandardPixmap.SP_FileDialogInfoView),
            "Smart Lookup",
            Qt.ToolButtonStyle.ToolButtonTextUnderIcon,
        )
        self.smart_lookup_action.setObjectName("smartLookupAction")
        self.smart_lookup_action.setToolTip(
            "Find contextual insights for selected text"
        )
        self.smart_lookup_action.setStatusTip(
            "Smart Lookup: insights for selected text"
        )
        self.smart_lookup_preview = QLabel(
            "Select text to look up insights", insights_group
        )
        self.smart_lookup_preview.setObjectName("smartLookupPreview")
        self.smart_lookup_preview.setMinimumWidth(220)
        self.smart_lookup_preview.setFixedHeight(30)
        self.smart_lookup_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.smart_lookup_preview.setFrameShape(QFrame.Shape.StyledPanel)
        self.smart_lookup_preview.setToolTip(
            "Preview of the Smart Lookup command surface"
        )
        insights_group.addWidget(self.smart_lookup_preview)
        protection_group = self.review_page.addGroup("Protection")
        self.sensitivity_label_action = protection_group.addAction(
            self._icon(QStyle.StandardPixmap.SP_MessageBoxWarning),
            "Sensitivity",
            Qt.ToolButtonStyle.ToolButtonTextUnderIcon,
        )
        self.sensitivity_label_action.setObjectName("sensitivityLabelAction")
        self.sensitivity_label_action.setToolTip(
            "Apply a sensitivity label to this document"
        )
        self.sensitivity_label_action.setStatusTip(
            "Sensitivity: apply Confidential label"
        )
        self.sensitivity_label_preview = QLabel(
            "Sensitivity: Public", protection_group
        )
        self.sensitivity_label_preview.setObjectName("sensitivityLabelPreview")
        self.sensitivity_label_preview.setMinimumWidth(180)
        self.sensitivity_label_preview.setFixedHeight(30)
        self.sensitivity_label_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sensitivity_label_preview.setFrameShape(QFrame.Shape.StyledPanel)
        self.sensitivity_label_preview.setToolTip(
            "Current document sensitivity label"
        )
        protection_group.addWidget(self.sensitivity_label_preview)
        accessibility_group = self.review_page.addGroup("Accessibility")
        self.accessibility_checker_action = accessibility_group.addAction(
            self._icon(QStyle.StandardPixmap.SP_DialogApplyButton),
            "Check Accessibility",
            Qt.ToolButtonStyle.ToolButtonTextUnderIcon,
        )
        self.accessibility_checker_action.setObjectName(
            "accessibilityCheckerAction"
        )
        self.accessibility_checker_action.setToolTip(
            "Check accessibility issues in this document"
        )
        self.accessibility_checker_action.setStatusTip(
            "Accessibility: inspect document issues"
        )
        self.accessibility_checker_preview = QLabel(
            "Accessibility: not checked", accessibility_group
        )
        self.accessibility_checker_preview.setObjectName(
            "accessibilityCheckerPreview"
        )
        self.accessibility_checker_preview.setMinimumWidth(210)
        self.accessibility_checker_preview.setFixedHeight(30)
        self.accessibility_checker_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.accessibility_checker_preview.setFrameShape(QFrame.Shape.StyledPanel)
        self.accessibility_checker_preview.setToolTip(
            "Accessibility checker result preview"
        )
        accessibility_group.addWidget(self.accessibility_checker_preview)
        editor_group = self.review_page.addGroup("Editor")
        self.editor_pane_action = editor_group.addAction(
            self._icon(QStyle.StandardPixmap.SP_FileDialogDetailedView),
            "Editor",
            Qt.ToolButtonStyle.ToolButtonTextUnderIcon,
        )
        self.editor_pane_action.setObjectName("editorPaneAction")
        self.editor_pane_action.setToolTip(
            "Open the Editor pane for writing suggestions"
        )
        self.editor_pane_action.setStatusTip(
            "Editor: review spelling, grammar, and clarity"
        )
        self.editor_pane_preview = QLabel(
            "Editor: suggestions hidden", editor_group
        )
        self.editor_pane_preview.setObjectName("editorPanePreview")
        self.editor_pane_preview.setMinimumWidth(220)
        self.editor_pane_preview.setFixedHeight(30)
        self.editor_pane_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.editor_pane_preview.setFrameShape(QFrame.Shape.StyledPanel)
        self.editor_pane_preview.setToolTip("Editor pane suggestion preview")
        editor_group.addWidget(self.editor_pane_preview)
        self.spelling_grammar_action = editor_group.addAction(
            self._icon(QStyle.StandardPixmap.SP_MessageBoxQuestion),
            "Spelling & Grammar",
            Qt.ToolButtonStyle.ToolButtonTextUnderIcon,
        )
        self.spelling_grammar_action.setObjectName("spellingGrammarAction")
        self.spelling_grammar_action.setToolTip(
            "Review spelling and grammar issues"
        )
        self.spelling_grammar_action.setStatusTip(
            "Spelling & Grammar: inspect writing checks"
        )
        self.spelling_grammar_card = QLabel(
            "Spelling & Grammar: no scan yet", editor_group
        )
        self.spelling_grammar_card.setObjectName("spellingGrammarCard")
        self.spelling_grammar_card.setMinimumWidth(230)
        self.spelling_grammar_card.setFixedHeight(34)
        self.spelling_grammar_card.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spelling_grammar_card.setFrameShape(QFrame.Shape.StyledPanel)
        self.spelling_grammar_card.setToolTip(
            "Spelling and grammar result card"
        )
        editor_group.addWidget(self.spelling_grammar_card)
        language_group = self.review_page.addGroup("Language")
        self.translator_action = language_group.addAction(
            self._icon(QStyle.StandardPixmap.SP_FileDialogInfoView),
            "Translator",
            Qt.ToolButtonStyle.ToolButtonTextUnderIcon,
        )
        self.translator_action.setObjectName("translatorAction")
        self.translator_action.setToolTip(
            "Translate selected text into another language"
        )
        self.translator_action.setStatusTip(
            "Translator: choose source text and target language"
        )
        self.translator_preview = QLabel(
            "Translator: no selection", language_group
        )
        self.translator_preview.setObjectName("translatorPreview")
        self.translator_preview.setMinimumWidth(210)
        self.translator_preview.setFixedHeight(30)
        self.translator_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.translator_preview.setFrameShape(QFrame.Shape.StyledPanel)
        self.translator_preview.setToolTip("Translator pane preview")
        language_group.addWidget(self.translator_preview)
        self.read_aloud_action = language_group.addAction(
            self._icon(QStyle.StandardPixmap.SP_MediaPlay),
            "Read Aloud",
            Qt.ToolButtonStyle.ToolButtonTextUnderIcon,
        )
        self.read_aloud_action.setObjectName("readAloudAction")
        self.read_aloud_action.setCheckable(True)
        self.read_aloud_action.setToolTip(
            "Read selected text aloud with speech playback"
        )
        self.read_aloud_action.setStatusTip(
            "Read Aloud: start speech playback"
        )
        self.read_aloud_preview = QLabel(
            "Read Aloud: stopped", language_group
        )
        self.read_aloud_preview.setObjectName("readAloudPreview")
        self.read_aloud_preview.setMinimumWidth(190)
        self.read_aloud_preview.setFixedHeight(30)
        self.read_aloud_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.read_aloud_preview.setFrameShape(QFrame.Shape.StyledPanel)
        self.read_aloud_preview.setToolTip("Speech playback status preview")
        language_group.addWidget(self.read_aloud_preview)

    def _create_view_page(self):
        immersive_group = self.view_page.addGroup("Immersive")
        self.immersive_reader_action = immersive_group.addAction(
            self._icon(QStyle.StandardPixmap.SP_FileDialogContentsView),
            "Immersive Reader",
            Qt.ToolButtonStyle.ToolButtonTextUnderIcon,
        )
        self.immersive_reader_action.setObjectName("immersiveReaderAction")
        self.immersive_reader_action.setCheckable(True)
        self.immersive_reader_action.setToolTip(
            "Open Immersive Reader for focused reading"
        )
        self.immersive_reader_action.setStatusTip(
            "Immersive Reader: enter focused reading view"
        )
        self.immersive_reader_preview = QLabel(
            "Immersive Reader: off", immersive_group
        )
        self.immersive_reader_preview.setObjectName("immersiveReaderPreview")
        self.immersive_reader_preview.setMinimumWidth(220)
        self.immersive_reader_preview.setFixedHeight(30)
        self.immersive_reader_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.immersive_reader_preview.setFrameShape(QFrame.Shape.StyledPanel)
        self.immersive_reader_preview.setToolTip(
            "Immersive Reader layout state"
        )
        immersive_group.addWidget(self.immersive_reader_preview)
        self.focus_mode_action = immersive_group.addAction(
            self._icon(QStyle.StandardPixmap.SP_TitleBarMinButton),
            "Focus Mode",
            Qt.ToolButtonStyle.ToolButtonTextUnderIcon,
        )
        self.focus_mode_action.setObjectName("focusModeAction")
        self.focus_mode_action.setCheckable(True)
        self.focus_mode_action.setToolTip(
            "Hide ribbon distractions for focused editing"
        )
        self.focus_mode_action.setStatusTip(
            "Focus Mode: hide ribbon commands"
        )
        self.focus_mode_preview = QLabel(
            "Focus Mode: ribbon visible", immersive_group
        )
        self.focus_mode_preview.setObjectName("focusModePreview")
        self.focus_mode_preview.setMinimumWidth(210)
        self.focus_mode_preview.setFixedHeight(30)
        self.focus_mode_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.focus_mode_preview.setFrameShape(QFrame.Shape.StyledPanel)
        self.focus_mode_preview.setToolTip("Focus Mode visibility state")
        immersive_group.addWidget(self.focus_mode_preview)
        canvas_group = self.view_page.addGroup("Canvas")
        self.dark_canvas_action = canvas_group.addAction(
            self._icon(QStyle.StandardPixmap.SP_DesktopIcon),
            "Dark Canvas",
            Qt.ToolButtonStyle.ToolButtonTextUnderIcon,
        )
        self.dark_canvas_action.setObjectName("darkCanvasAction")
        self.dark_canvas_action.setCheckable(True)
        self.dark_canvas_action.setToolTip(
            "Switch the document canvas to a dark background"
        )
        self.dark_canvas_action.setStatusTip(
            "Dark Canvas: use a dark editing surface"
        )
        self.dark_canvas_preview = QLabel("Canvas: light", canvas_group)
        self.dark_canvas_preview.setObjectName("darkCanvasPreview")
        self.dark_canvas_preview.setMinimumWidth(180)
        self.dark_canvas_preview.setFixedHeight(30)
        self.dark_canvas_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.dark_canvas_preview.setFrameShape(QFrame.Shape.StyledPanel)
        self.dark_canvas_preview.setToolTip("Current document canvas tone")
        canvas_group.addWidget(self.dark_canvas_preview)

    def _create_draw_page(self):
        ink_group = self.draw_page.addGroup("Ink")
        self.draw_mode_action = ink_group.addAction(
            self._icon(QStyle.StandardPixmap.SP_DialogApplyButton),
            "Draw Mode",
            Qt.ToolButtonStyle.ToolButtonTextUnderIcon,
        )
        self.draw_mode_action.setObjectName("drawModeAction")
        self.draw_mode_action.setCheckable(True)
        self.draw_mode_action.setToolTip("Enable ink drawing on the canvas")
        self.draw_mode_action.setStatusTip("Draw Mode: ink disabled")
        self.draw_mode_preview = QLabel("Draw: off", ink_group)
        self.draw_mode_preview.setObjectName("drawModePreview")
        self.draw_mode_preview.setMinimumWidth(170)
        self.draw_mode_preview.setFixedHeight(30)
        self.draw_mode_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.draw_mode_preview.setFrameShape(QFrame.Shape.StyledPanel)
        self.draw_mode_preview.setToolTip("Current drawing mode state")
        ink_group.addWidget(self.draw_mode_preview)
        self.draw_mode_action.toggled.connect(self.update_draw_mode)

        pen_group = self.draw_page.addGroup("Pens")
        pen_gallery_group = RibbonGalleryGroup(self)
        pen_gallery_group.setSize(QSize(96, 36))
        for caption, icon in [
            ("Black Pen", QStyle.StandardPixmap.SP_DialogApplyButton),
            ("Red Pen", QStyle.StandardPixmap.SP_MessageBoxWarning),
            ("Highlighter", QStyle.StandardPixmap.SP_DialogYesButton),
        ]:
            pen_gallery_group.addItem(caption, self._icon(icon))
        self.pen_gallery = RibbonGallery(pen_group)
        self.pen_gallery.setObjectName("penGallery")
        self.pen_gallery.setToolTip("Pen gallery for Draw tab ink tools")
        self.pen_gallery.setGalleryGroup(pen_gallery_group)
        self.pen_gallery.setColumnCount(3)
        self.pen_gallery.setRowCount(1)
        self.pen_gallery.setCheckedIndex(0)
        pen_group.addWidget(RibbonGalleryControl(pen_group, self.pen_gallery))

        tools_group = self.draw_page.addGroup("Tools")
        self.ruler_toggle_action = tools_group.addAction(
            self._icon(QStyle.StandardPixmap.SP_ArrowRight),
            "Ruler",
            Qt.ToolButtonStyle.ToolButtonTextUnderIcon,
        )
        self.ruler_toggle_action.setObjectName("rulerToggleAction")
        self.ruler_toggle_action.setCheckable(True)
        self.ruler_toggle_action.setToolTip("Show a drawing ruler overlay")
        self.ruler_toggle_action.setStatusTip("Ruler: hidden")
        self.ruler_preview = QLabel("Ruler: hidden", tools_group)
        self.ruler_preview.setObjectName("rulerPreview")
        self.ruler_preview.setMinimumWidth(150)
        self.ruler_preview.setFixedHeight(30)
        self.ruler_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.ruler_preview.setFrameShape(QFrame.Shape.StyledPanel)
        self.ruler_preview.setToolTip("Drawing ruler overlay state")
        tools_group.addWidget(self.ruler_preview)
        self.ruler_toggle_action.toggled.connect(self.toggle_ruler_overlay)

    def _create_animation_page(self):
        model_group = self.animation_page.addGroup("3D")
        self.model_3d_animation_action = model_group.addAction(
            self._icon(QStyle.StandardPixmap.SP_MediaPlay),
            "3D Animation",
            Qt.ToolButtonStyle.ToolButtonTextUnderIcon,
        )
        self.model_3d_animation_action.setObjectName("model3DAnimationAction")
        self.model_3d_animation_action.setCheckable(True)
        self.model_3d_animation_action.setToolTip(
            "Preview a 3D model animation from the ribbon"
        )
        self.model_3d_animation_action.setStatusTip("3D Animation: stopped")
        self.model_3d_animation_preview = QLabel("3D Animation: stopped", model_group)
        self.model_3d_animation_preview.setObjectName("model3DAnimationPreview")
        self.model_3d_animation_preview.setMinimumWidth(210)
        self.model_3d_animation_preview.setFixedHeight(30)
        self.model_3d_animation_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.model_3d_animation_preview.setFrameShape(QFrame.Shape.StyledPanel)
        self.model_3d_animation_preview.setToolTip("Current 3D animation preview state")
        model_group.addWidget(self.model_3d_animation_preview)
        self.model_3d_animation_action.toggled.connect(self.toggle_3d_animation)

    def _create_design_page(self):
        ideas_group = self.design_page.addGroup("Ideas")
        self.designer_ideas_action = ideas_group.addAction(
            self._icon(QStyle.StandardPixmap.SP_FileDialogInfoView),
            "Designer Ideas",
            Qt.ToolButtonStyle.ToolButtonTextUnderIcon,
        )
        self.designer_ideas_action.setObjectName("designerIdeasAction")
        self.designer_ideas_action.setToolTip(
            "Generate Designer Ideas layout suggestions"
        )
        self.designer_ideas_action.setStatusTip("Designer Ideas: suggestions ready")
        self.designer_ideas_preview = QLabel("Designer Ideas: not opened", ideas_group)
        self.designer_ideas_preview.setObjectName("designerIdeasPreview")
        self.designer_ideas_preview.setMinimumWidth(220)
        self.designer_ideas_preview.setFixedHeight(30)
        self.designer_ideas_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.designer_ideas_preview.setFrameShape(QFrame.Shape.StyledPanel)
        self.designer_ideas_preview.setToolTip("Designer Ideas suggestion pane state")
        ideas_group.addWidget(self.designer_ideas_preview)

    def _create_data_page(self):
        data_types_group = self.data_page.addGroup("Data Types")
        self.data_types_action = data_types_group.addAction(
            self._icon(QStyle.StandardPixmap.SP_DriveNetIcon),
            "Data Types",
            Qt.ToolButtonStyle.ToolButtonTextUnderIcon,
        )
        self.data_types_action.setObjectName("dataTypesAction")
        self.data_types_action.setToolTip(
            "Convert selected text into linked data types"
        )
        self.data_types_action.setStatusTip("Data Types: ready to convert")
        self.data_types_preview = QLabel("Data Types: plain text", data_types_group)
        self.data_types_preview.setObjectName("dataTypesPreview")
        self.data_types_preview.setMinimumWidth(210)
        self.data_types_preview.setFixedHeight(30)
        self.data_types_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.data_types_preview.setFrameShape(QFrame.Shape.StyledPanel)
        self.data_types_preview.setToolTip("Linked data type conversion state")
        data_types_group.addWidget(self.data_types_preview)

    def _create_command_discovery_page(self):
        discovery_group = self.tell_me_page.addGroup("Command Discovery")
        self.tell_me_lightbulb_action = discovery_group.addAction(
            self._tell_me_lightbulb_icon(),
            "Tell Me",
            Qt.ToolButtonStyle.ToolButtonTextUnderIcon,
        )
        self.tell_me_lightbulb_action.setObjectName("tellMeLightbulbAction")
        self.tell_me_lightbulb_action.setToolTip(
            "Open command discovery for natural-language help"
        )
        self.tell_me_lightbulb_action.setStatusTip(
            "Tell Me: type a command or phrase in Search"
        )
        self.tell_me_entry_preview = QLabel(
            "Ask for a command or phrase", discovery_group
        )
        self.tell_me_entry_preview.setObjectName("tellMeEntryPreview")
        self.tell_me_entry_preview.setMinimumWidth(220)
        self.tell_me_entry_preview.setFixedHeight(30)
        self.tell_me_entry_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tell_me_entry_preview.setFrameShape(QFrame.Shape.StyledPanel)
        self.tell_me_entry_preview.setToolTip(
            "Natural-language command discovery entry"
        )
        discovery_group.addWidget(self.tell_me_entry_preview)
        examples_group = self.tell_me_page.addGroup("Examples")
        self.tell_me_phrase_actions = []
        phrase_items = [
            ("tellMePhraseRibbonDisplayAction", "Change the ribbon display"),
            ("tellMePhraseDriverSettingsAction", "Find driver settings"),
            ("tellMePhraseCustomizeQatAction", "Customize quick access toolbar"),
        ]
        for object_name, phrase in phrase_items:
            action = examples_group.addAction(
                self._tell_me_lightbulb_icon(),
                phrase,
                Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
            )
            action.setObjectName(object_name)
            action.setToolTip(f'Try "{phrase}" in Search')
            action.setStatusTip(f"Tell Me phrase: {phrase}")
            action.triggered.connect(
                lambda _checked=False, text=phrase: self.apply_tell_me_phrase(text)
            )
            self.tell_me_phrase_actions.append(action)

        help_group = self.tell_me_page.addGroup("Help Redirect")
        self.tell_me_help_redirect_action = help_group.addAction(
            self._icon(QStyle.StandardPixmap.SP_MessageBoxQuestion),
            "Open Tell Me Help",
            Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )
        self.tell_me_help_redirect_action.setObjectName(
            "tellMeHelpRedirectAction"
        )
        self.tell_me_help_redirect_action.setToolTip(
            "Redirect unmatched Tell Me phrases to Search help"
        )
        self.tell_me_help_redirect_action.setStatusTip(
            "Tell Me help redirects unmatched phrases"
        )
        self.tell_me_help_redirect_action.triggered.connect(
            self.open_tell_me_help_redirect
        )
        self.tell_me_help_redirect_preview = QLabel(
            "Help redirects unmatched phrases", help_group
        )
        self.tell_me_help_redirect_preview.setObjectName(
            "tellMeHelpRedirectPreview"
        )
        self.tell_me_help_redirect_preview.setMinimumWidth(230)
        self.tell_me_help_redirect_preview.setFixedHeight(30)
        self.tell_me_help_redirect_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tell_me_help_redirect_preview.setFrameShape(QFrame.Shape.StyledPanel)
        self.tell_me_help_redirect_preview.setToolTip(
            "Fallback path for commands that are not found"
        )
        help_group.addWidget(self.tell_me_help_redirect_preview)

        keyboard_group = self.tell_me_page.addGroup("Keyboard")
        self.key_tips_overlay_action = keyboard_group.addAction(
            self._icon(QStyle.StandardPixmap.SP_ArrowUp),
            "KeyTips",
            Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )
        self.key_tips_overlay_action.setObjectName("keyTipsOverlayAction")
        self.key_tips_overlay_action.setCheckable(True)
        self.key_tips_overlay_action.setToolTip(
            "Show KeyTips overlay for keyboard navigation"
        )
        self.key_tips_overlay_action.setStatusTip("KeyTips overlay: hidden")
        self.key_tips_overlay_preview = QLabel("KeyTips: hidden", keyboard_group)
        self.key_tips_overlay_preview.setObjectName("keyTipsOverlayPreview")
        self.key_tips_overlay_preview.setMinimumWidth(190)
        self.key_tips_overlay_preview.setFixedHeight(30)
        self.key_tips_overlay_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.key_tips_overlay_preview.setFrameShape(QFrame.Shape.StyledPanel)
        self.key_tips_overlay_preview.setToolTip(
            "Current keyboard KeyTips overlay state"
        )
        keyboard_group.addWidget(self.key_tips_overlay_preview)
        self.alt_key_tabs_action = keyboard_group.addAction(
            self._icon(QStyle.StandardPixmap.SP_ArrowForward),
            "Alt Tabs",
            Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )
        self.alt_key_tabs_action.setObjectName("altKeyTabsAction")
        self.alt_key_tabs_action.setShortcut(QKeySequence("Alt"))
        self.alt_key_tabs_action.setProperty("shortcutHint", "Alt")
        self.alt_key_tabs_action.setToolTip(
            "Activate ribbon tabs from the Alt key"
        )
        self.alt_key_tabs_action.setStatusTip("Alt key tabs: inactive")
        self.alt_key_tabs_preview = QLabel("Alt tabs: inactive", keyboard_group)
        self.alt_key_tabs_preview.setObjectName("altKeyTabsPreview")
        self.alt_key_tabs_preview.setMinimumWidth(190)
        self.alt_key_tabs_preview.setFixedHeight(30)
        self.alt_key_tabs_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.alt_key_tabs_preview.setFrameShape(QFrame.Shape.StyledPanel)
        self.alt_key_tabs_preview.setToolTip("Current Alt key tab activation state")
        keyboard_group.addWidget(self.alt_key_tabs_preview)

    def _create_shell_page(self):
        window_group = self.shell_page.addGroup("Window")
        self.minimize_ribbon_action = self._add_group_action(
            window_group, QStyle.StandardPixmap.SP_TitleBarShadeButton, "Minimize"
        )
        self.restore_ribbon_action = self._add_group_action(
            window_group,
            QStyle.StandardPixmap.SP_TitleBarUnshadeButton,
            "Restore",
            Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )
        self.toggle_frame_action = self._add_group_action(
            window_group,
            QStyle.StandardPixmap.SP_TitleBarNormalButton,
            "Frame Theme",
            Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )
        self.toggle_frame_action.setCheckable(True)
        self.toggle_frame_action.setChecked(True)

        self.simplified_ribbon_action = self.ribbonBar().simplifiedAction()
        self.simplified_ribbon_action.setIcon(self._icon(QStyle.StandardPixmap.SP_ArrowUp))
        window_group.addAction(
            self.simplified_ribbon_action, Qt.ToolButtonStyle.ToolButtonTextBesideIcon
        )
        self.classic_ribbon_action = self._add_group_action(
            window_group,
            QStyle.StandardPixmap.SP_ArrowDown,
            "Classic Ribbon",
            Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )
        self.pin_ribbon_action = self._add_group_action(
            window_group,
            QStyle.StandardPixmap.SP_DialogApplyButton,
            "Pin Ribbon",
            Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )
        self.unpin_ribbon_action = self._add_group_action(
            window_group,
            QStyle.StandardPixmap.SP_DialogCancelButton,
            "Unpin Ribbon",
            Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )
        self.collapse_state_preview = QLabel(window_group)
        self.collapse_state_preview.setObjectName("collapseStatePreview")
        self.collapse_state_preview.setMinimumWidth(230)
        self.collapse_state_preview.setFixedHeight(30)
        self.collapse_state_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.collapse_state_preview.setFrameShape(QFrame.Shape.StyledPanel)
        self.collapse_state_preview.setToolTip(
            "Ribbon state, tab double-click target, and command density"
        )
        window_group.addWidget(self.collapse_state_preview)
        self.double_click_state_preview = self.collapse_state_preview

        self.runtime_group = self.shell_page.addGroup("Runtime")
        self.add_page_action = self._add_group_action(
            self.runtime_group, QStyle.StandardPixmap.SP_FileDialogNewFolder, "Add Page"
        )
        self.add_page_action.setObjectName("addPageAction")
        self.add_page_action.setToolTip("Create a custom ribbon tab")
        self.add_page_action.setStatusTip("Custom tab: not created")
        self.custom_tab_preview = QLabel("Custom tab: none", self.runtime_group)
        self.custom_tab_preview.setObjectName("customTabPreview")
        self.custom_tab_preview.setMinimumWidth(180)
        self.custom_tab_preview.setFixedHeight(30)
        self.custom_tab_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.custom_tab_preview.setFrameShape(QFrame.Shape.StyledPanel)
        self.custom_tab_preview.setToolTip("Last custom tab created from Customize")
        self.runtime_group.addWidget(self.custom_tab_preview)
        self.add_group_action = self._add_group_action(
            self.runtime_group,
            QStyle.StandardPixmap.SP_FileDialogDetailedView,
            "Add Group",
            Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )
        self.add_group_action.setObjectName("addGroupAction")
        self.add_group_action.setToolTip("Create a custom group on the active tab")
        self.add_group_action.setStatusTip("Custom group: not created")
        self.custom_group_preview = QLabel("Custom group: none", self.runtime_group)
        self.custom_group_preview.setObjectName("customGroupPreview")
        self.custom_group_preview.setMinimumWidth(180)
        self.custom_group_preview.setFixedHeight(30)
        self.custom_group_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.custom_group_preview.setFrameShape(QFrame.Shape.StyledPanel)
        self.custom_group_preview.setToolTip("Last custom group created")
        self.runtime_group.addWidget(self.custom_group_preview)
        self.rename_custom_action = self._add_group_action(
            self.runtime_group,
            QStyle.StandardPixmap.SP_FileDialogInfoView,
            "Rename Custom",
            Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )
        self.rename_custom_action.setObjectName("renameCustomAction")
        self.rename_custom_action.setToolTip("Rename the active custom tab and group")
        self.rename_custom_action.setStatusTip("Rename custom: pending")
        self.rename_custom_preview = QLabel("Rename custom: pending", self.runtime_group)
        self.rename_custom_preview.setObjectName("renameCustomPreview")
        self.rename_custom_preview.setMinimumWidth(190)
        self.rename_custom_preview.setFixedHeight(30)
        self.rename_custom_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.rename_custom_preview.setFrameShape(QFrame.Shape.StyledPanel)
        self.rename_custom_preview.setToolTip("Last custom tab/group rename")
        self.runtime_group.addWidget(self.rename_custom_preview)
        self.add_command_action = self._add_group_action(
            self.runtime_group,
            QStyle.StandardPixmap.SP_DialogApplyButton,
            "Add Command",
            Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )
        self.add_command_action.setObjectName("addCustomCommandAction")
        self.add_command_action.setToolTip("Add a command to the last custom group")
        self.add_command_action.setStatusTip("Custom command: not added")
        self.custom_command_preview = QLabel("Custom command: none", self.runtime_group)
        self.custom_command_preview.setObjectName("customCommandPreview")
        self.custom_command_preview.setMinimumWidth(190)
        self.custom_command_preview.setFixedHeight(30)
        self.custom_command_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.custom_command_preview.setFrameShape(QFrame.Shape.StyledPanel)
        self.custom_command_preview.setToolTip("Last command added to a custom group")
        self.runtime_group.addWidget(self.custom_command_preview)
        self.remove_command_action = self._add_group_action(
            self.runtime_group,
            QStyle.StandardPixmap.SP_DialogCancelButton,
            "Remove Command",
            Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )
        self.remove_command_action.setObjectName("removeCustomCommandAction")
        self.remove_command_action.setToolTip("Remove the last command from the custom group")
        self.remove_command_action.setStatusTip("Custom command: not removed")
        self.removed_command_preview = QLabel("Removed command: none", self.runtime_group)
        self.removed_command_preview.setObjectName("removedCommandPreview")
        self.removed_command_preview.setMinimumWidth(190)
        self.removed_command_preview.setFixedHeight(30)
        self.removed_command_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.removed_command_preview.setFrameShape(QFrame.Shape.StyledPanel)
        self.removed_command_preview.setToolTip("Last command removed from a custom group")
        self.runtime_group.addWidget(self.removed_command_preview)
        self.reset_selected_tab_action = self._add_group_action(
            self.runtime_group,
            QStyle.StandardPixmap.SP_DialogResetButton,
            "Reset Tab",
            Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )
        self.reset_selected_tab_action.setObjectName("resetSelectedTabAction")
        self.reset_selected_tab_action.setToolTip("Reset the selected custom tab")
        self.reset_selected_tab_action.setStatusTip("Selected tab: not reset")
        self.reset_selected_tab_preview = QLabel("Selected tab reset: none", self.runtime_group)
        self.reset_selected_tab_preview.setObjectName("resetSelectedTabPreview")
        self.reset_selected_tab_preview.setMinimumWidth(190)
        self.reset_selected_tab_preview.setFixedHeight(30)
        self.reset_selected_tab_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.reset_selected_tab_preview.setFrameShape(QFrame.Shape.StyledPanel)
        self.reset_selected_tab_preview.setToolTip("Last selected custom tab reset")
        self.runtime_group.addWidget(self.reset_selected_tab_preview)
        self.reset_all_customizations_action = self._add_group_action(
            self.runtime_group,
            QStyle.StandardPixmap.SP_BrowserReload,
            "Reset All",
            Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )
        self.reset_all_customizations_action.setObjectName("resetAllCustomizationsAction")
        self.reset_all_customizations_action.setToolTip("Reset all ribbon customizations")
        self.reset_all_customizations_action.setStatusTip("Ribbon customizations: not reset")
        self.reset_all_customizations_preview = QLabel("All customizations: active", self.runtime_group)
        self.reset_all_customizations_preview.setObjectName("resetAllCustomizationsPreview")
        self.reset_all_customizations_preview.setMinimumWidth(190)
        self.reset_all_customizations_preview.setFixedHeight(30)
        self.reset_all_customizations_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.reset_all_customizations_preview.setFrameShape(QFrame.Shape.StyledPanel)
        self.reset_all_customizations_preview.setToolTip("Ribbon customization reset state")
        self.runtime_group.addWidget(self.reset_all_customizations_preview)
        self.export_customization_action = self._add_group_action(
            self.runtime_group,
            QStyle.StandardPixmap.SP_DialogSaveButton,
            "Export Ribbon",
            Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )
        self.export_customization_action.setObjectName("exportRibbonCustomizationAction")
        self.export_customization_action.setToolTip("Export ribbon customization state")
        self.export_customization_action.setStatusTip("Ribbon export: not created")
        self.export_customization_preview = QLabel("Ribbon export: none", self.runtime_group)
        self.export_customization_preview.setObjectName("exportRibbonCustomizationPreview")
        self.export_customization_preview.setMinimumWidth(190)
        self.export_customization_preview.setFixedHeight(30)
        self.export_customization_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.export_customization_preview.setFrameShape(QFrame.Shape.StyledPanel)
        self.export_customization_preview.setToolTip("Last exported ribbon customization size")
        self.runtime_group.addWidget(self.export_customization_preview)
        self.import_customization_action = self._add_group_action(
            self.runtime_group,
            QStyle.StandardPixmap.SP_DialogOpenButton,
            "Import Ribbon",
            Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )
        self.import_customization_action.setObjectName("importRibbonCustomizationAction")
        self.import_customization_action.setToolTip("Import ribbon customization state")
        self.import_customization_action.setStatusTip("Ribbon import: no export")
        self.import_customization_preview = QLabel("Ribbon import: none", self.runtime_group)
        self.import_customization_preview.setObjectName("importRibbonCustomizationPreview")
        self.import_customization_preview.setMinimumWidth(190)
        self.import_customization_preview.setFixedHeight(30)
        self.import_customization_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.import_customization_preview.setFrameShape(QFrame.Shape.StyledPanel)
        self.import_customization_preview.setToolTip("Last imported ribbon customization size")
        self.runtime_group.addWidget(self.import_customization_preview)
        self.rename_page_action = self._add_group_action(
            self.runtime_group,
            QStyle.StandardPixmap.SP_FileDialogInfoView,
            "Rename Driver",
            Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )
        self.move_gallery_action = self._add_group_action(
            self.runtime_group,
            QStyle.StandardPixmap.SP_ArrowRight,
            "Move Gallery",
            Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )
        self.toggle_group_action = self._add_group_action(
            self.runtime_group,
            QStyle.StandardPixmap.SP_DialogResetButton,
            "Toggle Specialist",
            Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )
        self.width_stress_action = self._add_group_action(
            self.runtime_group,
            QStyle.StandardPixmap.SP_ArrowLeft,
            "Stress Width",
            Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )
        self.width_stress_action.setCheckable(True)
        self.search_mode_group = QActionGroup(self)
        self.search_mode_group.setExclusive(True)
        self.center_search_action = self._add_group_action(
            self.runtime_group,
            QStyle.StandardPixmap.SP_FileDialogContentsView,
            "Center Search",
            Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )
        self.center_search_action.setObjectName("centerSearchAction")
        self.center_search_action.setCheckable(True)
        self.center_search_action.setChecked(True)
        self.search_mode_group.addAction(self.center_search_action)
        self.compact_search_action = self._add_group_action(
            self.runtime_group,
            QStyle.StandardPixmap.SP_FileDialogContentsView,
            "Compact Search",
            Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )
        self.compact_search_action.setObjectName("compactSearchAction")
        self.compact_search_action.setCheckable(True)
        self.search_mode_group.addAction(self.compact_search_action)
        self.hidden_search_action = self._add_group_action(
            self.runtime_group,
            QStyle.StandardPixmap.SP_DialogCloseButton,
            "Hide Search",
            Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )
        self.hidden_search_action.setObjectName("hiddenSearchAction")
        self.hidden_search_action.setCheckable(True)
        self.search_mode_group.addAction(self.hidden_search_action)
        self.focus_search_action = self._add_group_action(
            self.runtime_group,
            QStyle.StandardPixmap.SP_FileDialogContentsView,
            "Focus Search",
            Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )
        self.focus_search_action.setObjectName("focusSearchAction")
        self.focus_search_action.setShortcut(QKeySequence("Alt+Q"))
        self.focus_search_action.setShortcutContext(Qt.ShortcutContext.WindowShortcut)
        self.addAction(self.focus_search_action)
        self.responsive_label_actions = [
            self.rename_page_action,
            self.move_gallery_action,
            self.toggle_group_action,
        ]

        popup_group = self.shell_page.addGroup("Popups")
        self.office_popup_action = self._add_group_action(
            popup_group, QStyle.StandardPixmap.SP_MessageBoxInformation, "Popup"
        )
        self.office_popup_action.setObjectName("officePopupAction")
        self.office_popup_action.setToolTip("Show an Office popup notification")
        self.office_popup_action.setStatusTip("Office popup: notification ready")
        self.office_menu_action = self._add_group_action(
            popup_group,
            QStyle.StandardPixmap.SP_DirOpenIcon,
            "Popup Menu",
            Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )
        self.office_menu_action.setObjectName("officeMenuAction")
        self.office_menu_action.setToolTip("Open a resizable Office popup menu")
        self.office_menu_action.setStatusTip("Office popup menu: grip visible")
        self.color_button = PopupColorButton(popup_group)
        self.color_button.setObjectName("popupColorButton")
        self.color_button.setText("Color")
        self.color_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.color_button.setColor(QColor("#2b579a"))
        self.color_button.setToolTip("Popup Color Button")
        popup_group.addWidget(self.color_button)

        customize_group = self.shell_page.addGroup("Customize")
        self.show_customize_action = self._add_group_action(
            customize_group, QStyle.StandardPixmap.SP_FileDialogDetailedView, "Customize"
        )
        self.save_state_action = self._add_group_action(
            customize_group,
            QStyle.StandardPixmap.SP_DialogSaveButton,
            "Save Layout",
            Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )
        self.load_state_action = self._add_group_action(
            customize_group,
            QStyle.StandardPixmap.SP_DialogOpenButton,
            "Load Layout",
            Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )
        self.reorder_quick_access_action = self._add_group_action(
            customize_group,
            QStyle.StandardPixmap.SP_ArrowRight,
            "Move QAT Right",
            Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )
        self.reorder_quick_access_action.setObjectName("reorderQuickAccessAction")
        self.reset_quick_access_action = self._add_group_action(
            customize_group,
            QStyle.StandardPixmap.SP_DialogResetButton,
            "Reset QAT",
            Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )
        self.reset_quick_access_action.setObjectName("resetQuickAccessAction")
        self.export_quick_access_action = self._add_group_action(
            customize_group,
            QStyle.StandardPixmap.SP_DialogSaveButton,
            "Export QAT",
            Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )
        self.export_quick_access_action.setObjectName("exportQuickAccessAction")
        self.import_quick_access_action = self._add_group_action(
            customize_group,
            QStyle.StandardPixmap.SP_DialogOpenButton,
            "Import QAT",
            Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )
        self.import_quick_access_action.setObjectName("importQuickAccessAction")

        specialist_options_action = QAction(
            self._icon(QStyle.StandardPixmap.SP_FileDialogInfoView),
            "Specialist Options",
            self.specialist_group,
        )
        specialist_options_action.triggered.connect(
            lambda: self._message("Specialist option button clicked")
        )
        self.specialist_group.setOptionButtonAction(specialist_options_action)
        self.specialist_group.setOptionButtonVisible(True)

    def _create_system_surfaces(self):
        self.ribbonBar().addSystemButton(self._icon(QStyle.StandardPixmap.SP_DriveFDIcon), "File")

        self.backstage = RibbonBackstageView(self)
        self.backstage.addAction(self._icon(QStyle.StandardPixmap.SP_DialogOpenButton), "Open")
        self.backstage.addAction(self._icon(QStyle.StandardPixmap.SP_DialogSaveButton), "Save")
        self.save_copy_action = self.backstage.addAction(
            self._icon(QStyle.StandardPixmap.SP_DialogSaveButton), "Save a Copy"
        )
        self.save_copy_action.setObjectName("saveCopyAction")
        self.save_copy_action.setToolTip(
            "Create a separate copy without changing the current document"
        )
        self.save_copy_action.setStatusTip(
            "Save a Copy: create a separate file copy"
        )
        self.save_copy_action.triggered.connect(
            lambda: self._message("Save a Copy: create a separate file copy")
        )
        self.backstage_close_action = self.backstage.addAction(
            self._icon(QStyle.StandardPixmap.SP_DialogCloseButton), "Close"
        )
        self.backstage_close_action.setObjectName("backstageCloseAction")
        self.backstage_close_action.setToolTip("Close Backstage view")
        self.backstage_close_action.setStatusTip(
            "Close: Backstage dismissed when not prevented"
        )
        self.backstage_close_action.triggered.connect(
            lambda: self._message("Close: Backstage dismissed when not prevented")
        )
        self.backstage.addSeparator()

        self.backstage_info_page = QWidget(self.backstage)
        self.backstage_info_page.setObjectName("backstageInfoPage")
        self.backstage_info_page.setWindowTitle("Info")
        backstage_layout = QFormLayout(self.backstage_info_page)
        self.backstage_info_product_label = QLabel("LqRibbon Demo", self.backstage_info_page)
        self.backstage_info_product_label.setObjectName("backstageInfoProductLabel")
        self.backstage_info_mode_label = QLabel("Backstage page", self.backstage_info_page)
        self.backstage_info_mode_label.setObjectName("backstageInfoModeLabel")
        backstage_layout.addRow("Product", self.backstage_info_product_label)
        backstage_layout.addRow("Mode", self.backstage_info_mode_label)
        self.cloud_location_combo = QComboBox(self.backstage_info_page)
        self.cloud_location_combo.setObjectName("cloudLocationPicker")
        self.cloud_location_combo.addItems(
            [
                "OneDrive - Contoso",
                "SharePoint Team Site",
                "Teams Project Files",
            ]
        )
        self.cloud_location_combo.setToolTip(
            "Choose the cloud location used for AutoSave and sharing"
        )
        self.cloud_location_combo.currentTextChanged.connect(
            lambda text: self._message(f"Cloud location: {text}")
        )
        backstage_layout.addRow("Cloud location", self.cloud_location_combo)
        self.upload_before_share_prompt = QLabel(
            "Upload required before sharing",
            self.backstage_info_page,
        )
        self.upload_before_share_prompt.setObjectName("uploadBeforeSharePrompt")
        self.upload_before_share_prompt.setToolTip(
            "Save this local draft to a cloud location before inviting people"
        )
        self.upload_before_share_prompt.setWordWrap(True)
        backstage_layout.addRow("Share readiness", self.upload_before_share_prompt)
        self.backstage_info_action = self.backstage.addPage(self.backstage_info_page)
        self.backstage_info_action.setObjectName("backstageInfoAction")
        self.backstage_info_action.setToolTip("Open document information")
        self.backstage_info_action.setStatusTip("Info: document properties and sharing state")
        self.backstage_info_action.triggered.connect(
            lambda: self._message("Info: document properties and sharing state")
        )
        self.version_history_page = QWidget(self.backstage)
        self.version_history_page.setObjectName("versionHistoryPage")
        self.version_history_page.setWindowTitle("Version History")
        version_history_layout = QFormLayout(self.version_history_page)
        self.version_history_current_label = QLabel(
            "Current version: Saved 2 minutes ago",
            self.version_history_page,
        )
        self.version_history_current_label.setObjectName(
            "versionHistoryCurrentLabel"
        )
        version_history_layout.addRow(
            "Current",
            self.version_history_current_label,
        )
        version_history_layout.addRow(
            "Previous",
            QLabel("Yesterday 18:42 by Alice Chen", self.version_history_page),
        )
        version_history_layout.addRow(
            "Restore",
            QLabel("Restore a previous cloud save", self.version_history_page),
        )
        self.version_history_action = self.backstage.addPage(
            self.version_history_page
        )
        self.version_history_action.setObjectName("versionHistoryAction")
        self.version_history_action.setToolTip("Open document version history")
        self.version_history_action.setStatusTip(
            "Version History: review and restore previous versions"
        )
        self.version_history_action.triggered.connect(
            lambda: self._message(
                "Version History: review and restore previous versions"
            )
        )

        self.system_menu = RibbonSystemMenu(self.ribbonBar())
        self.system_menu.addPopupBarAction("New")
        self.system_menu.addPopupBarAction("Open")
        self.recent_file_default_order = ["drive-layout.lqr", "axis-profile.lqr"]
        self.recent_file_pinned_order = ["axis-profile.lqr", "drive-layout.lqr"]
        self.recent_files = self.system_menu.addPageRecentFile("Recent Files")
        self.recent_files.setObjectName("systemRecentFilesList")
        self.recent_files.setToolTip(
            "System menu recent files list with pinning support"
        )
        self.recent_files.updateRecentFileActions(self.recent_file_default_order)
        export_action = QAction(
            self._icon(QStyle.StandardPixmap.SP_DialogSaveButton), "Export", self.system_menu
        )
        export_action.setObjectName("systemExportAction")
        export_action.setToolTip("Open the system menu export page")
        export_action.setStatusTip("System Export: choose an export format")
        export_action.triggered.connect(
            lambda: self._message("System Export: choose an export format")
        )
        self.system_export_action = export_action
        self.system_export_popup = self.system_menu.addPageSystemPopup(
            "Export", export_action, True
        )
        self.system_export_popup.setObjectName("systemExportPopup")
        self.system_export_popup.setToolTipsVisible(True)
        self.system_export_popup.setToolTip("System menu page popup for export commands")
        self.pin_recent_file_action = QAction(
            self._icon(QStyle.StandardPixmap.SP_DialogApplyButton),
            "Pin Recent File",
            self.system_menu,
        )
        self.pin_recent_file_action.setObjectName("pinRecentFileAction")
        self.pin_recent_file_action.setCheckable(True)
        self.pin_recent_file_action.setToolTip(
            "Pin axis-profile.lqr to the top of Recent Files"
        )
        self.pin_recent_file_action.setStatusTip(
            "Pin or unpin axis-profile.lqr in Recent Files"
        )
        self.pin_recent_file_action.toggled.connect(self._set_recent_file_pinned)
        self.system_menu.addPageSystemPopup(
            "Pin Recent", self.pin_recent_file_action, True
        )

        self.backstage_open_page = QWidget(self.backstage)
        self.backstage_open_page.setObjectName("backstageOpenPage")
        self.backstage_open_page.setWindowTitle("Open")
        open_page_layout = QFormLayout(self.backstage_open_page)
        self.frequent_sites_label = QLabel(
            "OneDrive - Contoso\nSharePoint Team Site",
            self.backstage_open_page,
        )
        self.frequent_sites_label.setObjectName("frequentSitesList")
        self.frequent_groups_label = QLabel(
            "Drive Tuning Team\nFirmware Release Group",
            self.backstage_open_page,
        )
        self.frequent_groups_label.setObjectName("frequentGroupsList")
        self.pinned_folders_label = QLabel(
            "Pinned folders: Customer Projects, Servo Profiles",
            self.backstage_open_page,
        )
        self.pinned_folders_label.setObjectName("pinnedFoldersList")
        self.pinned_folders_label.setToolTip(
            "Pinned Open locations stay at the top of the file picker"
        )
        open_page_layout.addRow("Frequent sites", self.frequent_sites_label)
        open_page_layout.addRow("Frequent groups", self.frequent_groups_label)
        open_page_layout.addRow("Pinned folders", self.pinned_folders_label)
        self.backstage_open_action = self.backstage.addPage(self.backstage_open_page)
        self.backstage_open_action.setObjectName("backstageOpenAction")
        self.backstage_open_action.setToolTip("Open frequent sites and groups")
        self.backstage_open_action.setStatusTip(
            "Open: frequent sites and groups"
        )
        self.backstage_open_action.triggered.connect(
            lambda: self._message("Open: frequent sites and groups")
        )

        self.backstage_export_page = QWidget(self.backstage)
        self.backstage_export_page.setObjectName("backstageExportPage")
        self.backstage_export_page.setWindowTitle("Export")
        export_page_layout = QFormLayout(self.backstage_export_page)
        self.export_formats_label = QLabel(
            "Formats: PDF, XPS, OpenDocument",
            self.backstage_export_page,
        )
        self.export_formats_label.setObjectName("exportFormatsList")
        self.export_formats_label.setToolTip(
            "Document formats available from the Backstage Export page"
        )
        self.export_destination_label = QLabel(
            "Destination: Local file or cloud location",
            self.backstage_export_page,
        )
        self.export_destination_label.setObjectName("exportDestinationLabel")
        self.export_destination_label.setToolTip(
            "Export can save locally or to a connected Office cloud location"
        )
        export_page_layout.addRow("Formats", self.export_formats_label)
        export_page_layout.addRow("Destination", self.export_destination_label)
        self.backstage_export_action = self.backstage.addPage(
            self.backstage_export_page
        )
        self.backstage_export_action.setObjectName("backstageExportAction")
        self.backstage_export_action.setToolTip("Export document formats")
        self.backstage_export_action.setStatusTip(
            "Export: PDF, XPS, and OpenDocument"
        )
        self.backstage_export_action.triggered.connect(
            lambda: self._message("Export: PDF, XPS, and OpenDocument")
        )

        self.backstage_account_page = QWidget(self.backstage)
        self.backstage_account_page.setObjectName("backstageAccountPage")
        self.backstage_account_page.setWindowTitle("Account")
        account_page_layout = QFormLayout(self.backstage_account_page)
        self.account_signed_in_label = QLabel(
            "Local User | local.user@example.com",
            self.backstage_account_page,
        )
        self.account_signed_in_label.setObjectName("accountSignedInLabel")
        self.account_connected_services_label = QLabel(
            "Connected services: OneDrive, SharePoint",
            self.backstage_account_page,
        )
        self.account_connected_services_label.setObjectName(
            "accountConnectedServicesLabel"
        )
        self.account_connected_services_label.setToolTip(
            "Cloud services connected to the current Office account"
        )
        self.account_privacy_summary = QLabel(
            "Connected experiences: optional diagnostics off",
            self.backstage_account_page,
        )
        self.account_privacy_summary.setObjectName("accountPrivacySummary")
        self.account_privacy_summary.setWordWrap(True)
        self.account_privacy_summary.setToolTip(
            "Summary of privacy controls for connected Office experiences"
        )
        self.account_privacy_settings_action = QAction(
            self._icon(QStyle.StandardPixmap.SP_FileDialogInfoView),
            "Privacy Settings",
            self.backstage_account_page,
        )
        self.account_privacy_settings_action.setObjectName(
            "accountPrivacySettingsAction"
        )
        self.account_privacy_settings_action.setToolTip(
            "Open account privacy settings for connected experiences"
        )
        self.account_privacy_settings_action.setStatusTip(
            "Account Privacy: manage connected experiences"
        )
        self.account_privacy_settings_button = QToolButton(self.backstage_account_page)
        self.account_privacy_settings_button.setObjectName(
            "accountPrivacySettingsButton"
        )
        self.account_privacy_settings_button.setDefaultAction(
            self.account_privacy_settings_action
        )
        self.account_privacy_settings_button.setToolButtonStyle(
            Qt.ToolButtonStyle.ToolButtonTextBesideIcon
        )
        account_page_layout.addRow("Signed in", self.account_signed_in_label)
        account_page_layout.addRow(
            "Services", self.account_connected_services_label
        )
        account_page_layout.addRow("Privacy", self.account_privacy_summary)
        account_page_layout.addRow("Settings", self.account_privacy_settings_button)
        self.backstage_account_action = self.backstage.addPage(
            self.backstage_account_page
        )
        self.backstage_account_action.setObjectName("backstageAccountAction")
        self.backstage_account_action.setToolTip(
            "Open account and privacy settings"
        )
        self.backstage_account_action.setStatusTip(
            "Account: signed in as Local User"
        )
        self.backstage_account_action.triggered.connect(
            lambda: self._message("Account: signed in as Local User")
        )
        self.account_privacy_settings_action.triggered.connect(
            self.open_account_privacy_settings
        )

        system_button = self.ribbonBar().systemButton()
        if system_button:
            system_button.setBackstage(self.backstage)
            system_button.setSystemMenu(self.system_menu)

        self.office_menu = OfficePopupMenu.createPopupMenu(self)
        self.office_menu.setObjectName("officePopupMenu")
        self.office_menu.setToolTip("Resizable Office popup menu with grip")
        self.office_menu.setGripVisible(True)
        popup_editor = QPlainTextEdit(self.office_menu)
        popup_editor.setObjectName("officePopupMenuEditor")
        popup_editor.setPlainText("OfficePopupMenu widget host")
        popup_editor.setFixedSize(260, 120)
        self.office_menu.addWidget(popup_editor)

    def _create_status_bar(self):
        status_bar = RibbonStatusBar(self)
        status_bar.addWidget(QLabel("Ready", status_bar))
        status_bar.addWidget(QLabel("|", status_bar))
        status_bar.addWidget(QLabel("Online", status_bar))
        status_bar.addWidget(QLabel("|", status_bar))
        self.collaboration_status_label = QLabel(
            "Saved to cloud | 3 editors",
            status_bar,
        )
        self.collaboration_status_label.setObjectName("collaborationStatusText")
        self.collaboration_status_label.setToolTip(
            "Collaboration status for this document"
        )
        self.collaboration_status_label.setMinimumWidth(160)
        status_bar.addWidget(self.collaboration_status_label)
        status_bar.addWidget(QLabel("|", status_bar))
        self.coauthoring_indicator_dot = QFrame(status_bar)
        self.coauthoring_indicator_dot.setObjectName("coauthoringIndicatorDot")
        self.coauthoring_indicator_dot.setFixedSize(10, 10)
        self.coauthoring_indicator_dot.setStyleSheet(
            "#coauthoringIndicatorDot { background: #107c41; border-radius: 5px; }"
        )
        self.coauthoring_indicator_dot.setToolTip("Live coauthoring is active")
        status_bar.addWidget(self.coauthoring_indicator_dot)
        self.coauthoring_indicator_label = QLabel("Coauthoring", status_bar)
        self.coauthoring_indicator_label.setObjectName("coauthoringIndicator")
        self.coauthoring_indicator_label.setToolTip("Live coauthoring is active")
        self.coauthoring_indicator_label.setMinimumWidth(92)
        status_bar.addWidget(self.coauthoring_indicator_label)
        status_bar.addWidget(QLabel("|", status_bar))
        self.character_count_status_label = QLabel("1,248 characters", status_bar)
        self.character_count_status_label.setObjectName("characterCountStatusItem")
        self.character_count_status_label.setToolTip(
            "Current document character count"
        )
        self.character_count_status_label.setMinimumWidth(112)
        status_bar.addWidget(self.character_count_status_label)
        status_bar.addWidget(QLabel("|", status_bar))
        self.density_status_preview = QLabel(status_bar)
        self.density_status_preview.setObjectName("ribbonDensityStatusPreview")
        self.density_status_preview.setMinimumWidth(180)
        status_bar.addWidget(self.density_status_preview)
        status_bar.addWidget(QLabel("|", status_bar))
        self.responsive_labels_status_preview = QLabel(status_bar)
        self.responsive_labels_status_preview.setObjectName(
            "responsiveLabelsStatusPreview"
        )
        self.responsive_labels_status_preview.setMinimumWidth(140)
        status_bar.addWidget(self.responsive_labels_status_preview)
        status_bar.addWidget(QLabel("|", status_bar))
        self.quick_access_status_preview = QLabel(status_bar)
        self.quick_access_status_preview.setObjectName("quickAccessStatusPreview")
        self.quick_access_status_preview.setMinimumWidth(180)
        status_bar.addWidget(self.quick_access_status_preview)

        switch_group = RibbonStatusBarSwitchGroup(status_bar)
        switch_group.setObjectName("statusViewSwitchGroup")
        view_actions = QActionGroup(switch_group)
        view_actions.setExclusive(True)
        self.normal_status_view_action = view_actions.addAction(
            self._icon(QStyle.StandardPixmap.SP_FileDialogDetailedView), "Normal View"
        )
        self.compact_status_view_action = view_actions.addAction(
            self._icon(QStyle.StandardPixmap.SP_FileDialogListView), "Compact View"
        )
        self.normal_status_view_action.setObjectName("normalStatusViewAction")
        self.compact_status_view_action.setObjectName("compactStatusViewAction")
        self.normal_status_view_action.setToolTip("Switch to Normal document view")
        self.compact_status_view_action.setToolTip("Switch to Compact document view")
        self.normal_status_view_action.setCheckable(True)
        self.compact_status_view_action.setCheckable(True)
        self.normal_status_view_action.setChecked(True)
        self.status_view_mode = "Normal View"
        self.status_view_switch_group = switch_group
        self._add_status_action_button(switch_group, self.normal_status_view_action)
        self._add_status_action_button(switch_group, self.compact_status_view_action)

        self.zoom_status_label = QLabel("100%", status_bar)
        self.zoom_status_label.setObjectName("zoomStatusLabel")
        self.zoom_status_label.setMinimumWidth(48)
        self.zoom_status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.zoom_status_label.setToolTip("Current document zoom")

        zoom_slider = RibbonSliderPane(status_bar)
        zoom_slider.setObjectName("zoomStatusSlider")
        zoom_slider.setToolTip("Adjust document zoom percentage")
        zoom_slider.setRange(10, 200)
        zoom_slider.setSingleStep(10)
        zoom_slider.setValue(100)

        progress_bar = RibbonProgressBar(status_bar)
        progress_bar.setObjectName("zoomStatusProgress")
        progress_bar.setRange(10, 200)
        progress_bar.setValue(100)
        progress_bar.setToolTip("Zoom percentage progress")

        self.sync_status_action = QAction(
            self._icon(QStyle.StandardPixmap.SP_BrowserReload), "Sync", status_bar
        )
        self.sync_status_action.setObjectName("syncStatusAction")
        self.sync_status_action.setToolTip("Sync document changes to cloud")
        status_bar.addPermanentAction(self.sync_status_action)
        status_bar.addPermanentWidget(switch_group)
        status_bar.addPermanentWidget(self.zoom_status_label)
        status_bar.addPermanentWidget(zoom_slider)
        status_bar.addPermanentWidget(progress_bar)
        self.setStatusBar(status_bar)
        self.ribbon_status_bar = status_bar
        self.zoom_slider = zoom_slider
        self.progress_bar = progress_bar
        self.normal_status_view_action.triggered.connect(
            lambda: self.set_status_view_mode("Normal View")
        )
        self.compact_status_view_action.triggered.connect(
            lambda: self.set_status_view_mode("Compact View")
        )
        self.sync_status_action.triggered.connect(self.sync_document_status)
        zoom_slider.valueChanged.connect(self.update_zoom_status)

    def set_status_view_mode(self, mode):
        self.status_view_mode = mode
        self._message(f"View: {mode}")

    def update_zoom_status(self, value):
        self.zoom_status_label.setText(f"{value}%")
        self.progress_bar.setValueSafe(value)
        self._message(f"Zoom: {value}%")

    def sync_document_status(self):
        self.collaboration_status_label.setText("Saved to cloud | synced just now")
        self._message("Sync: Up to date")

    def _create_customize_state(self):
        self.customize_manager = self.ribbonBar().customizeManager()
        for page in [
            self.general_page,
            self.driver_page,
            self.controls_page,
            self.gallery_page,
            self.insert_page,
            self.format_page,
            self.contextual_page,
            self.options_page,
            self.review_page,
            self.view_page,
            self.tell_me_page,
            self.shell_page,
        ]:
            self.customize_manager.addToCategory("Pages", page)
        for action in [
            self.full_screen_action,
            self.high_contrast_style_action,
            self.touch_spacing_action,
            self.add_group_action,
            self.rename_custom_action,
            self.add_command_action,
            self.remove_command_action,
            self.reset_selected_tab_action,
            self.reset_all_customizations_action,
            self.export_customization_action,
            self.import_customization_action,
            self.connect_action,
            self.dictate_microphone_action,
            self.office_popup_action,
            self.show_customize_action,
            self.center_search_action,
            self.compact_search_action,
            self.hidden_search_action,
            self.focus_search_action,
            self.control_modes_action,
            self.smart_lookup_action,
            self.sensitivity_label_action,
            self.accessibility_checker_action,
            self.editor_pane_action,
            self.spelling_grammar_action,
            self.translator_action,
            self.read_aloud_action,
            self.immersive_reader_action,
            self.focus_mode_action,
            self.dark_canvas_action,
            self.draw_mode_action,
            self.ruler_toggle_action,
            self.svg_icon_insert_action,
            self.model_3d_insert_action,
            self.model_3d_animation_action,
            self.designer_ideas_action,
            self.recommended_chart_action,
            self.data_types_action,
            self.svg_recolor_action,
            self.svg_convert_shape_action,
            self.contextual_group_color_action,
            self.contextual_tab_visibility_action,
            self.title_groups_visibility_action,
            self.reduced_motion_action,
            self.account_privacy_settings_action,
            self.tell_me_lightbulb_action,
            self.key_tips_overlay_action,
            self.alt_key_tabs_action,
            self.reorder_quick_access_action,
            self.reset_quick_access_action,
            self.export_quick_access_action,
            self.import_quick_access_action,
        ]:
            self.customize_manager.addToCategory("Actions", action)
        self.customize_manager.setPageId(self.review_page, "review")
        self.customize_manager.setPageId(self.view_page, "view")
        self.customize_manager.setPageId(self.tell_me_page, "tellMe")
        self.customize_manager.setPageId(self.shell_page, "shell")
        self.customize_manager.setGroupId(self.runtime_group, "runtime")

    def _connect_actions(self):
        self.full_screen_action.triggered.connect(self.toggle_full_screen)
        self.high_contrast_style_action.toggled.connect(
            self.toggle_high_contrast_style_preview
        )
        self.touch_spacing_action.toggled.connect(self.toggle_touch_spacing)
        self.mdi_action.triggered.connect(lambda: self.show_mdi_content(tabbed=False))
        self.tab_action.triggered.connect(lambda: self.show_mdi_content(tabbed=True))
        self.settings_action.triggered.connect(lambda: self._message("Settings"))
        self.connect_action.triggered.connect(lambda: self._message("Connect"))
        self.basic_action.triggered.connect(lambda: self._message("Basic Operation"))
        self.driver_action.triggered.connect(lambda: self._message("Driver Configuration"))
        self.dictate_microphone_action.toggled.connect(
            self.toggle_dictate_microphone
        )
        self.smart_lookup_action.triggered.connect(self.open_smart_lookup)
        self.sensitivity_label_action.triggered.connect(self.apply_sensitivity_label)
        self.accessibility_checker_action.triggered.connect(
            self.run_accessibility_checker
        )
        self.editor_pane_action.triggered.connect(self.open_editor_pane)
        self.spelling_grammar_action.triggered.connect(
            self.show_spelling_grammar_card
        )
        self.translator_action.triggered.connect(self.open_translator)
        self.read_aloud_action.toggled.connect(self.toggle_read_aloud)
        self.immersive_reader_action.toggled.connect(
            self.toggle_immersive_reader
        )
        self.focus_mode_action.toggled.connect(self.toggle_focus_mode)
        self.dark_canvas_action.toggled.connect(self.toggle_dark_canvas)
        self.svg_icon_insert_action.triggered.connect(self.insert_svg_icon)
        self.model_3d_insert_action.triggered.connect(self.insert_3d_model)
        self.designer_ideas_action.triggered.connect(self.open_designer_ideas)
        self.recommended_chart_action.triggered.connect(self.open_recommended_chart)
        self.data_types_action.triggered.connect(self.convert_to_data_type)
        self.svg_recolor_action.triggered.connect(self.recolor_svg_icon)
        self.svg_convert_shape_action.triggered.connect(self.convert_svg_to_shape)
        self.contextual_group_color_action.triggered.connect(
            self.apply_contextual_group_color
        )
        self.contextual_tab_visibility_action.toggled.connect(
            self.toggle_contextual_tabs_visible
        )
        self.title_groups_visibility_action.toggled.connect(
            self.toggle_title_groups_visible
        )
        self.reduced_motion_action.toggled.connect(self.toggle_reduced_motion)
        self.tell_me_lightbulb_action.triggered.connect(
            lambda: self._message("Tell Me: type a command or phrase in Search")
        )
        self.key_tips_overlay_action.toggled.connect(self.toggle_key_tips_overlay)
        self.alt_key_tabs_action.triggered.connect(self.activate_alt_key_tabs)
        self.minimize_ribbon_action.triggered.connect(
            lambda: self.ribbonBar().setRibbonMinimized(True)
        )
        self.restore_ribbon_action.triggered.connect(
            lambda: self.ribbonBar().setRibbonMinimized(False)
        )
        self.classic_ribbon_action.triggered.connect(self.restore_classic_ribbon)
        self.pin_ribbon_action.triggered.connect(self.pin_ribbon)
        self.unpin_ribbon_action.triggered.connect(self.unpin_ribbon)
        self.toggle_frame_action.toggled.connect(self.setFrameThemeEnabled)
        self.add_page_action.triggered.connect(self.add_runtime_page)
        self.add_group_action.triggered.connect(self.add_custom_group)
        self.rename_custom_action.triggered.connect(self.rename_custom_tab_and_group)
        self.add_command_action.triggered.connect(self.add_command_to_custom_group)
        self.remove_command_action.triggered.connect(self.remove_command_from_custom_group)
        self.reset_selected_tab_action.triggered.connect(self.reset_selected_custom_tab)
        self.reset_all_customizations_action.triggered.connect(self.reset_all_ribbon_customizations)
        self.export_customization_action.triggered.connect(self.export_ribbon_customization)
        self.import_customization_action.triggered.connect(self.import_ribbon_customization)
        self.rename_page_action.triggered.connect(self.rename_driver_page)
        self.move_gallery_action.triggered.connect(self.move_gallery_page)
        self.toggle_group_action.triggered.connect(self.toggle_specialist_group)
        self.width_stress_action.toggled.connect(
            lambda _checked: self.update_responsive_label_preview()
        )
        self.center_search_action.triggered.connect(
            lambda _checked=False: self.set_search_bar_appearance(SEARCH_BAR_CENTRAL)
        )
        self.compact_search_action.triggered.connect(
            lambda _checked=False: self.set_search_bar_appearance(SEARCH_BAR_COMPACT)
        )
        self.hidden_search_action.triggered.connect(
            lambda _checked=False: self.set_search_bar_appearance(SEARCH_BAR_HIDDEN)
        )
        self.focus_search_action.triggered.connect(
            lambda _checked=False: self.focus_caption_search()
        )
        self.office_popup_action.triggered.connect(self.show_office_popup)
        self.office_menu_action.triggered.connect(self.show_office_menu)
        self.color_button.colorChanged.connect(
            lambda color: self._message(f"Color changed: {color.name()}")
        )
        self.show_customize_action.triggered.connect(self.ribbonBar().showCustomizeDialog)
        self.save_state_action.triggered.connect(self.save_layout_state)
        self.load_state_action.triggered.connect(self.load_layout_state)
        self.reorder_quick_access_action.triggered.connect(
            lambda _checked=False: self.move_quick_access_action(
                self.full_screen_action, 1
            )
        )
        self.reset_quick_access_action.triggered.connect(
            self.reset_quick_access_actions
        )
        self.export_quick_access_action.triggered.connect(
            self.store_exported_quick_access_state
        )
        self.import_quick_access_action.triggered.connect(
            self.import_exported_quick_access_state
        )
        self.ribbonBar().searchAccepted.connect(
            lambda text: self._message(f"No command: {text}")
        )

        self.display_options_menu = QMenu("Ribbon Display Options", self)
        self.display_show_tabs_commands_action = self.display_options_menu.addAction(
            self._icon(QStyle.StandardPixmap.SP_TitleBarUnshadeButton),
            "Show Tabs and Commands",
        )
        self.display_show_tabs_only_action = self.display_options_menu.addAction(
            self._icon(QStyle.StandardPixmap.SP_TitleBarShadeButton),
            "Show Tabs Only",
        )
        self.display_always_show_action = self.display_options_menu.addAction(
            self._icon(QStyle.StandardPixmap.SP_DialogApplyButton),
            "Always Show Ribbon",
        )
        self.display_auto_hide_action = self.display_options_menu.addAction(
            self._icon(QStyle.StandardPixmap.SP_DialogCancelButton),
            "Auto-Hide Ribbon",
        )
        self.display_options_title_action = self.ribbonBar().addTitleButton(
            self._icon(QStyle.StandardPixmap.SP_TitleBarMenuButton),
            "Ribbon Display Options",
        )
        self.display_options_title_action.setToolTip(
            "Ribbon Display Options: choose how much ribbon to show"
        )
        self.display_options_title_action.setMenu(self.display_options_menu)
        display_button = self.ribbonBar()._title_button_bar.widgetForAction(
            self.display_options_title_action
        )
        if isinstance(display_button, QToolButton):
            display_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)

        self.auto_save_title_action = self.ribbonBar().addTitleButton(
            self._icon(QStyle.StandardPixmap.SP_DialogSaveButton),
            "AutoSave",
        )
        self.auto_save_title_action.setObjectName("autoSaveTitleAction")
        self.auto_save_title_action.setCheckable(True)
        self.auto_save_title_action.setChecked(True)
        self._update_auto_save_title_action(True)
        self.share_title_action = self.ribbonBar().addTitleButton(
            self._icon(QStyle.StandardPixmap.SP_DialogOpenButton),
            "Share",
        )
        self.share_title_action.setObjectName("shareTitleAction")
        self.share_title_action.setToolTip("Share: Share this document")
        self.share_title_action.setStatusTip(
            "Share: upload before sharing to invite people"
        )
        self.comments_title_action = self.ribbonBar().addTitleButton(
            self._icon(QStyle.StandardPixmap.SP_FileDialogContentsView),
            "Comments",
        )
        self.comments_title_action.setObjectName("commentsTitleAction")
        self.comments_title_action.setToolTip("Comments: Open document comments")
        self.comments_title_action.setStatusTip("Comments: show conversation pane")
        self.presence_avatar_strip_action = self.ribbonBar().addTitleButton(
            self._avatar_strip_icon(),
            "Presence",
        )
        self.presence_avatar_strip_action.setObjectName("presenceAvatarStripAction")
        self.presence_avatar_strip_action.setToolTip(
            "Presence: Alice Chen, Bo Li, and Maya Patel are editing"
        )
        self.presence_avatar_strip_action.setStatusTip(
            "Presence: 3 collaborators editing"
        )
        self.feedback_title_action = self.ribbonBar().addTitleButton(
            self._icon(QStyle.StandardPixmap.SP_MessageBoxInformation),
            "Feedback",
        )
        self.feedback_title_action.setObjectName("feedbackTitleAction")
        self.feedback_title_action.setToolTip(
            "Feedback: Send feedback about this document"
        )
        self.feedback_title_action.setStatusTip("Feedback: send product feedback")
        self.help_title_action = self.ribbonBar().addTitleButton(
            self._icon(QStyle.StandardPixmap.SP_MessageBoxQuestion), "Help"
        )
        self.help_title_action.setToolTip("Help: Open LqRibbon help")
        self.account_title_action = self.ribbonBar().addTitleButton(
            self._icon(QStyle.StandardPixmap.SP_DirHomeIcon), "Account"
        )
        self.account_title_action.setObjectName("accountTitleAction")
        self.account_title_action.setToolTip(
            "Account: Open account and profile settings"
        )
        self.account_title_action.setStatusTip("Account: signed in as Local User")
        self.auto_save_title_action.triggered.connect(
            self._update_auto_save_title_action
        )
        self.share_title_action.triggered.connect(self._show_upload_before_share_prompt)
        self.comments_title_action.triggered.connect(
            lambda: self._message("Comments: show conversation pane")
        )
        self.presence_avatar_strip_action.triggered.connect(
            lambda: self._message("Presence: 3 collaborators editing")
        )
        self.feedback_title_action.triggered.connect(
            lambda: self._message("Feedback: send product feedback")
        )
        self.help_title_action.triggered.connect(
            lambda: QMessageBox.information(self, "LqRibbon", "Help")
        )
        self.account_title_action.triggered.connect(self.open_account_backstage)
        self.icon_only_title_actions = [
            self.display_options_title_action,
            self.auto_save_title_action,
            self.share_title_action,
            self.comments_title_action,
            self.presence_avatar_strip_action,
            self.feedback_title_action,
            self.help_title_action,
            self.account_title_action,
        ]
        self.accessible_tooltip_actions = list(self.icon_only_title_actions)
        self.screen_reader_title_actions = list(self.icon_only_title_actions)
        self._apply_icon_only_title_buttons()
        self.display_show_tabs_commands_action.triggered.connect(
            self.show_tabs_and_commands
        )
        self.display_show_tabs_only_action.triggered.connect(self.show_tabs_only)
        self.display_always_show_action.triggered.connect(self.always_show_ribbon)
        self.display_auto_hide_action.triggered.connect(self.auto_hide_ribbon)
        self.ribbonBar().ribbonMinimizedChanged.connect(
            lambda _minimized: self.update_collapse_state_preview()
        )
        self.ribbonBar().ribbonTemporaryExpandedChanged.connect(
            lambda _expanded: self.update_collapse_state_preview()
        )
        self.ribbonBar().simplifiedModeChanged.connect(
            lambda _enabled: self.update_collapse_state_preview()
        )
        self.update_collapse_state_preview()
        self.update_responsive_label_preview()

    def _configure_search_and_quick_access(self):
        self.default_quick_access_actions = [
            self.full_screen_action,
            self.connect_action,
            self.minimize_ribbon_action,
        ]
        self.quick_access_actions = list(self.default_quick_access_actions)
        self.exported_quick_access_state = ""
        self.quick_access_action_ids = {
            self.full_screen_action: "fullScreen",
            self.connect_action: "connect",
            self.minimize_ribbon_action: "minimizeRibbon",
            self.rename_page_action: "renamePage",
            self.move_gallery_action: "moveGallery",
            self.toggle_group_action: "toggleGroup",
        }
        self.quick_access_actions_by_id = {
            action_id: action
            for action, action_id in self.quick_access_action_ids.items()
        }
        self.show_quick_access_action = QAction(
            self.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarNormalButton),
            "Show Quick Access Toolbar",
            self,
        )
        self.show_quick_access_action.setObjectName("showQuickAccessBarAction")
        self.show_quick_access_action.setCheckable(True)
        self.show_quick_access_action.toggled.connect(self.set_quick_access_visible)
        self.quick_access_above_action = QAction(
            self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowUp),
            "Show Quick Access Toolbar Above the Ribbon",
            self,
        )
        self.quick_access_above_action.setObjectName("quickAccessAboveAction")
        self.quick_access_above_action.setCheckable(True)
        self.quick_access_above_action.triggered.connect(
            self.set_quick_access_above_ribbon
        )
        self.quick_access_below_action = QAction(
            self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowDown),
            "Show Quick Access Toolbar Below the Ribbon",
            self,
        )
        self.quick_access_below_action.setObjectName("quickAccessBelowAction")
        self.quick_access_below_action.setCheckable(True)
        self.quick_access_below_action.triggered.connect(
            self.set_quick_access_below_ribbon
        )
        self.quick_access_labels_action = QAction(
            self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogContentsView),
            "Show Command Labels",
            self,
        )
        self.quick_access_labels_action.setObjectName("quickAccessLabelsAction")
        self.quick_access_labels_action.setCheckable(True)
        self.quick_access_labels_action.toggled.connect(
            self.set_quick_access_labels_visible
        )
        self.ribbonBar().quickAccessBar().show_customize_menu.connect(
            self.populate_quick_access_menu
        )

        self.search_actions = [
            self.full_screen_action,
            self.high_contrast_style_action,
            self.touch_spacing_action,
            self.mdi_action,
            self.tab_action,
            self.settings_action,
            self.connect_action,
            self.basic_action,
            self.driver_action,
            self.control_modes_action,
            self.minimize_ribbon_action,
            self.restore_ribbon_action,
            self.classic_ribbon_action,
            self.pin_ribbon_action,
            self.unpin_ribbon_action,
            self.add_page_action,
            self.add_group_action,
            self.rename_custom_action,
            self.add_command_action,
            self.remove_command_action,
            self.reset_selected_tab_action,
            self.reset_all_customizations_action,
            self.export_customization_action,
            self.import_customization_action,
            self.rename_page_action,
            self.move_gallery_action,
            self.toggle_group_action,
            self.width_stress_action,
            self.center_search_action,
            self.compact_search_action,
            self.hidden_search_action,
            self.focus_search_action,
            self.show_quick_access_action,
            self.quick_access_above_action,
            self.quick_access_below_action,
            self.quick_access_labels_action,
            self.dictate_microphone_action,
            self.office_popup_action,
            self.office_menu_action,
            self.smart_lookup_action,
            self.sensitivity_label_action,
            self.accessibility_checker_action,
            self.editor_pane_action,
            self.spelling_grammar_action,
            self.translator_action,
            self.read_aloud_action,
            self.immersive_reader_action,
            self.focus_mode_action,
            self.dark_canvas_action,
            self.draw_mode_action,
            self.ruler_toggle_action,
            self.svg_icon_insert_action,
            self.model_3d_insert_action,
            self.model_3d_animation_action,
            self.designer_ideas_action,
            self.recommended_chart_action,
            self.data_types_action,
            self.svg_recolor_action,
            self.svg_convert_shape_action,
            self.contextual_group_color_action,
            self.contextual_tab_visibility_action,
            self.title_groups_visibility_action,
            self.reduced_motion_action,
            self.account_privacy_settings_action,
            self.tell_me_lightbulb_action,
            self.key_tips_overlay_action,
            self.alt_key_tabs_action,
            self.tell_me_help_redirect_action,
            self.show_customize_action,
            self.reorder_quick_access_action,
            self.reset_quick_access_action,
            self.export_quick_access_action,
            self.import_quick_access_action,
        ]
        search_aliases = {
            self.control_modes_action: ["Axis Profile", "Servo Axis Setup"],
        }
        for action in self.search_actions:
            self.ribbonBar().registerSearchAction(
                action, search_aliases.get(action, [])
            )
        for action in self.quick_access_actions:
            self.ribbonBar().addQuickAccessAction(action)
        self.update_quick_access_preview()

    def populate_quick_access_menu(self, menu):
        self.update_quick_access_preview()
        menu.addAction(self.show_quick_access_action)
        menu.addSeparator()
        menu.addAction(self.quick_access_above_action)
        menu.addAction(self.quick_access_below_action)
        menu.addSeparator()
        menu.addAction(self.quick_access_labels_action)
        menu.addSeparator()
        menu.addAction(self.reorder_quick_access_action)
        menu.addAction(self.reset_quick_access_action)
        menu.addAction(self.export_quick_access_action)
        menu.addAction(self.import_quick_access_action)

    def _configure_action_context_menus(self):
        self.action_context_menu_actions = [
            self.rename_page_action,
            self.move_gallery_action,
            self.toggle_group_action,
        ]
        for action in self.action_context_menu_actions:
            button = self._ribbon_button_for_action(action)
            if button is None:
                continue
            button.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            button.customContextMenuRequested.connect(
                lambda pos, act=action, source=button: self.show_action_context_menu(
                    act, source.mapToGlobal(pos)
                )
            )

    def populate_action_context_menu(self, menu, command_action):
        if menu is None or command_action is None or command_action.isSeparator():
            return None
        quick_access_bar = self.ribbonBar().quickAccessBar()
        already_added = (
            command_action in self.quick_access_actions
            or command_action in quick_access_bar.actions()
        )
        if menu.actions():
            menu.addSeparator()
        add_action = menu.addAction(
            self._icon(QStyle.StandardPixmap.SP_ArrowUp),
            "Already in Quick Access Toolbar"
            if already_added
            else "Add to Quick Access Toolbar",
        )
        add_action.setObjectName("addToQuickAccessContextAction")
        add_action.setEnabled(not already_added)
        add_action.triggered.connect(
            lambda _checked=False, action=command_action: self.add_action_to_quick_access(
                action
            )
        )
        return add_action

    def show_action_context_menu(self, command_action, global_pos):
        menu = QMenu(self)
        self.populate_action_context_menu(menu, command_action)
        if not menu.isEmpty():
            menu.exec(global_pos)

    def _configure_quick_access_context_menus(self):
        quick_access_bar = self.ribbonBar().quickAccessBar()
        for action in quick_access_bar.actions():
            if action is None or action == quick_access_bar.actionCustomizeButton():
                continue
            button = quick_access_bar.widgetForAction(action)
            if (
                button is None
                or button.property("quickAccessContextMenuInstalled") is True
            ):
                continue
            button.setProperty("quickAccessContextMenuInstalled", True)
            button.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            button.customContextMenuRequested.connect(
                lambda pos, act=action, source=button: self.show_quick_access_action_context_menu(
                    act, source.mapToGlobal(pos)
                )
            )

    def populate_quick_access_action_context_menu(self, menu, command_action):
        if menu is None or command_action is None or command_action.isSeparator():
            return None
        quick_access_bar = self.ribbonBar().quickAccessBar()
        in_quick_access = (
            command_action != quick_access_bar.actionCustomizeButton()
            and command_action in quick_access_bar.actions()
        )
        if menu.actions():
            menu.addSeparator()
        remove_action = menu.addAction(
            self._icon(QStyle.StandardPixmap.SP_DialogDiscardButton),
            "Remove from Quick Access Toolbar"
            if in_quick_access
            else "Not in Quick Access Toolbar",
        )
        remove_action.setObjectName("removeFromQuickAccessContextAction")
        remove_action.setEnabled(in_quick_access)
        remove_action.triggered.connect(
            lambda _checked=False, action=command_action: self.remove_action_from_quick_access(
                action
            )
        )
        action_index = (
            self.quick_access_actions.index(command_action)
            if command_action in self.quick_access_actions
            else -1
        )
        menu.addSeparator()
        move_left_action = menu.addAction(
            self._icon(QStyle.StandardPixmap.SP_ArrowLeft),
            "Move Left in Quick Access Toolbar",
        )
        move_left_action.setObjectName("moveQuickAccessLeftContextAction")
        move_left_action.setEnabled(in_quick_access and action_index > 0)
        move_left_action.triggered.connect(
            lambda _checked=False, action=command_action: self.move_quick_access_action(
                action, -1
            )
        )
        move_right_action = menu.addAction(
            self._icon(QStyle.StandardPixmap.SP_ArrowRight),
            "Move Right in Quick Access Toolbar",
        )
        move_right_action.setObjectName("moveQuickAccessRightContextAction")
        move_right_action.setEnabled(
            in_quick_access
            and action_index >= 0
            and action_index < len(self.quick_access_actions) - 1
        )
        move_right_action.triggered.connect(
            lambda _checked=False, action=command_action: self.move_quick_access_action(
                action, 1
            )
        )
        return remove_action

    def show_quick_access_action_context_menu(self, command_action, global_pos):
        menu = QMenu(self)
        self.populate_quick_access_action_context_menu(menu, command_action)
        if not menu.isEmpty():
            menu.exec(global_pos)

    def add_action_to_quick_access(self, command_action):
        if command_action is None:
            return
        if command_action not in self.quick_access_actions:
            self.quick_access_actions.append(command_action)
        quick_access_bar = self.ribbonBar().quickAccessBar()
        self.ribbonBar().addQuickAccessAction(command_action)
        quick_access_bar.setActionVisible(command_action, True)
        self._configure_quick_access_context_menus()
        self.update_quick_access_preview()
        self.statusBar().showMessage(
            f"Added {command_action.text()} to Quick Access Toolbar", 2500
        )

    def remove_action_from_quick_access(self, command_action):
        if command_action is None:
            return
        quick_access_bar = self.ribbonBar().quickAccessBar()
        if command_action in quick_access_bar.actions():
            quick_access_bar.removeAction(command_action)
        if command_action in self.quick_access_actions:
            self.quick_access_actions.remove(command_action)
        self.update_quick_access_preview()
        self.statusBar().showMessage(
            f"Removed {command_action.text()} from Quick Access Toolbar", 2500
        )

    def rebuild_quick_access_order(self):
        ribbon = self.ribbonBar()
        quick_access_bar = ribbon.quickAccessBar()
        for action in list(quick_access_bar.actions()):
            if action != quick_access_bar.actionCustomizeButton():
                quick_access_bar.removeAction(action)
        for action in self.quick_access_actions:
            ribbon.addQuickAccessAction(action)
            quick_access_bar.setActionVisible(action, True)
        self._configure_quick_access_context_menus()
        ribbon.setQuickAccessBarPosition(ribbon.quickAccessBarPosition())
        self.update_quick_access_preview()

    def move_quick_access_action(self, command_action, offset):
        if command_action is None or not offset:
            return False
        if command_action not in self.quick_access_actions:
            return False
        current_index = self.quick_access_actions.index(command_action)
        target_index = max(
            0, min(current_index + offset, len(self.quick_access_actions) - 1)
        )
        if target_index == current_index:
            return False
        action = self.quick_access_actions.pop(current_index)
        self.quick_access_actions.insert(target_index, action)
        self.rebuild_quick_access_order()
        self.statusBar().showMessage(
            f"Moved {command_action.text()} in Quick Access Toolbar", 2500
        )
        return True

    def reset_quick_access_actions(self):
        self.quick_access_actions = list(self.default_quick_access_actions)
        self.rebuild_quick_access_order()
        self.statusBar().showMessage("Quick Access Toolbar reset to default", 2500)

    def export_quick_access_state(self):
        quick_access_bar = self.ribbonBar().quickAccessBar()
        return json.dumps(
            {
                "version": 1,
                "actions": [
                    self.quick_access_action_ids[action]
                    for action in self.quick_access_actions
                    if action in self.quick_access_action_ids
                ],
                "position": "below"
                if self.ribbonBar().quickAccessBarPosition()
                == QUICK_ACCESS_BOTTOM_POSITION
                else "above",
                "labels": quick_access_bar.toolButtonStyle()
                == Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
            },
            separators=(",", ":"),
        )

    def store_exported_quick_access_state(self):
        self.exported_quick_access_state = self.export_quick_access_state()
        self.statusBar().showMessage("QAT customization exported", 2500)

    def apply_quick_access_state(self, state_text):
        try:
            state = json.loads(state_text)
        except (TypeError, ValueError):
            return False
        imported_actions = []
        for action_id in state.get("actions", []):
            action = self.quick_access_actions_by_id.get(action_id)
            if action is not None and action not in imported_actions:
                imported_actions.append(action)
        if not imported_actions:
            return False
        self.quick_access_actions = imported_actions
        self.rebuild_quick_access_order()
        if state.get("position") == "below":
            self.ribbonBar().setQuickAccessBarPosition(QUICK_ACCESS_BOTTOM_POSITION)
        else:
            self.ribbonBar().setQuickAccessBarPosition(QUICK_ACCESS_TOP_POSITION)
        self.set_quick_access_labels_visible(bool(state.get("labels", False)))
        self.update_quick_access_preview()
        return True

    def import_exported_quick_access_state(self):
        if not self.exported_quick_access_state:
            self.statusBar().showMessage("No QAT customization exported", 2500)
            return False
        imported = self.apply_quick_access_state(self.exported_quick_access_state)
        self.statusBar().showMessage(
            "QAT customization imported"
            if imported
            else "Invalid QAT customization",
            2500,
        )
        return imported

    def set_search_bar_appearance(self, appearance):
        self.ribbonBar().setSearchBarAppearance(appearance)
        center_blocked = self.center_search_action.blockSignals(True)
        self.center_search_action.setChecked(appearance == SEARCH_BAR_CENTRAL)
        self.center_search_action.blockSignals(center_blocked)
        compact_blocked = self.compact_search_action.blockSignals(True)
        self.compact_search_action.setChecked(appearance == SEARCH_BAR_COMPACT)
        self.compact_search_action.blockSignals(compact_blocked)
        hidden_blocked = self.hidden_search_action.blockSignals(True)
        self.hidden_search_action.setChecked(appearance == SEARCH_BAR_HIDDEN)
        self.hidden_search_action.blockSignals(hidden_blocked)

    def focus_caption_search(self):
        self.set_search_bar_appearance(SEARCH_BAR_CENTRAL)
        search = self.ribbonBar().searchLineEdit()
        search.setFocus(Qt.FocusReason.ShortcutFocusReason)
        search.selectAll()

    def apply_tell_me_phrase(self, phrase):
        self.focus_caption_search()
        self.ribbonBar().setSearchText(phrase)
        self._message(f"Tell Me phrase: {phrase}")

    def open_smart_lookup(self):
        self.smart_lookup_preview.setText("Insights ready for selected text")
        self._message("Smart Lookup: insights for selected text")

    def apply_sensitivity_label(self):
        self.sensitivity_label_preview.setText("Sensitivity: Confidential")
        self.sensitivity_label_preview.setStyleSheet(
            "QLabel#sensitivityLabelPreview { color: #5c2d91; font-weight: 600; }"
        )
        self._message("Sensitivity: Confidential label applied")

    def run_accessibility_checker(self):
        self.accessibility_checker_preview.setText("Accessibility: 2 issues found")
        self.accessibility_checker_preview.setStyleSheet(
            "QLabel#accessibilityCheckerPreview { color: #b35c00; font-weight: 600; }"
        )
        self._message("Accessibility: 2 issues found")

    def open_editor_pane(self):
        self.editor_pane_preview.setText("Editor: 5 suggestions ready")
        self.editor_pane_preview.setStyleSheet(
            "QLabel#editorPanePreview { color: #107c41; font-weight: 600; }"
        )
        self._message("Editor: 5 writing suggestions ready")

    def show_spelling_grammar_card(self):
        self.spelling_grammar_card.setText(
            "Spelling & Grammar: 1 spelling, 2 grammar"
        )
        self.spelling_grammar_card.setStyleSheet(
            "QLabel#spellingGrammarCard { color: #a80000; font-weight: 600; }"
        )
        self._message("Spelling & Grammar: 3 issues ready")

    def open_translator(self):
        self.translator_preview.setText("Translator: English to Chinese")
        self.translator_preview.setStyleSheet(
            "QLabel#translatorPreview { color: #0f6cbd; font-weight: 600; }"
        )
        self._message("Translator: English to Chinese")

    def toggle_read_aloud(self, enabled):
        if enabled:
            self.read_aloud_preview.setText("Read Aloud: playing paragraph")
            self.read_aloud_preview.setStyleSheet(
                "QLabel#readAloudPreview { color: #107c41; font-weight: 600; }"
            )
            self.read_aloud_action.setToolTip("Stop speech playback")
            self._message("Read Aloud: playing paragraph")
        else:
            self.read_aloud_preview.setText("Read Aloud: stopped")
            self.read_aloud_preview.setStyleSheet("")
            self.read_aloud_action.setToolTip(
                "Read selected text aloud with speech playback"
            )
            self._message("Read Aloud: stopped")

    def toggle_immersive_reader(self, enabled):
        if enabled:
            self.immersive_reader_preview.setText(
                "Immersive Reader: line focus on"
            )
            self.immersive_reader_preview.setStyleSheet(
                "QLabel#immersiveReaderPreview { color: #0f6cbd; font-weight: 600; }"
            )
            self.immersive_reader_action.setToolTip(
                "Exit Immersive Reader focused reading"
            )
            self._message("Immersive Reader: line focus on")
        else:
            self.immersive_reader_preview.setText("Immersive Reader: off")
            self.immersive_reader_preview.setStyleSheet("")
            self.immersive_reader_action.setToolTip(
                "Open Immersive Reader for focused reading"
            )
            self._message("Immersive Reader: off")

    def toggle_focus_mode(self, enabled):
        if enabled:
            self.ribbonBar().setRibbonMinimized(True)
            self.focus_mode_preview.setText("Focus Mode: distractions hidden")
            self.focus_mode_preview.setStyleSheet(
                "QLabel#focusModePreview { color: #107c41; font-weight: 600; }"
            )
            self.focus_mode_action.setToolTip(
                "Exit Focus Mode and restore ribbon commands"
            )
            self._message("Focus Mode: distractions hidden")
        else:
            self.ribbonBar().setRibbonMinimized(False)
            self.focus_mode_preview.setText("Focus Mode: ribbon visible")
            self.focus_mode_preview.setStyleSheet("")
            self.focus_mode_action.setToolTip(
                "Hide ribbon distractions for focused editing"
            )
            self._message("Focus Mode: ribbon visible")

    def toggle_dark_canvas(self, enabled):
        canvas = self.centralWidget()
        if enabled:
            if canvas is not None:
                canvas.setStyleSheet(
                    "QWidget { background: #1b1b1b; color: #f3f2f1; } "
                    "QLabel { background: #1b1b1b; color: #f3f2f1; }"
                )
            self.dark_canvas_preview.setText("Canvas: dark")
            self.dark_canvas_preview.setStyleSheet(
                "QLabel#darkCanvasPreview { color: #f3f2f1; background: #1b1b1b; font-weight: 600; }"
            )
            self.dark_canvas_action.setToolTip(
                "Return the document canvas to a light background"
            )
            self._message("Dark Canvas: dark editing surface")
        else:
            if canvas is not None:
                canvas.setStyleSheet("")
            self.dark_canvas_preview.setText("Canvas: light")
            self.dark_canvas_preview.setStyleSheet("")
            self.dark_canvas_action.setToolTip(
                "Switch the document canvas to a dark background"
            )
            self._message("Dark Canvas: light editing surface")

    def update_draw_mode(self, enabled):
        if enabled:
            self.draw_mode_preview.setText("Draw: ink enabled")
            self.draw_mode_preview.setStyleSheet(
                "QLabel#drawModePreview { color: #ffffff; background: #0f6cbd; font-weight: 600; }"
            )
            self.draw_mode_action.setStatusTip("Draw Mode: ink enabled")
            self._message("Draw Mode: ink enabled")
        else:
            self.draw_mode_preview.setText("Draw: off")
            self.draw_mode_preview.setStyleSheet("")
            self.draw_mode_action.setStatusTip("Draw Mode: ink disabled")
            self._message("Draw Mode: ink disabled")

    def toggle_ruler_overlay(self, enabled):
        if enabled:
            self.ruler_preview.setText("Ruler: visible")
            self.ruler_preview.setStyleSheet(
                "QLabel#rulerPreview { color: #5c2d91; background: #f3e8ff; font-weight: 600; }"
            )
            self.ruler_toggle_action.setStatusTip("Ruler: visible")
            self._message("Ruler: visible")
        else:
            self.ruler_preview.setText("Ruler: hidden")
            self.ruler_preview.setStyleSheet("")
            self.ruler_toggle_action.setStatusTip("Ruler: hidden")
            self._message("Ruler: hidden")

    def insert_svg_icon(self):
        self.svg_icon_insert_preview.setText("SVG Icons: 1 inserted")
        self.svg_icon_insert_preview.setStyleSheet(
            "QLabel#svgIconInsertPreview { color: #124078; background: #eef6ff; font-weight: 600; }"
        )
        self._message("SVG Icon: inserted scalable artwork")

    def insert_3d_model(self):
        self.model_3d_preview.setText("3D Models: 1 inserted")
        self.model_3d_preview.setStyleSheet(
            "QLabel#model3DPreview { color: #0f5132; background: #d1e7dd; font-weight: 600; }"
        )
        self._message("3D Model: inserted rotatable asset")

    def toggle_3d_animation(self, playing):
        if playing:
            self.model_3d_animation_preview.setText("3D Animation: playing")
            self.model_3d_animation_preview.setStyleSheet(
                "QLabel#model3DAnimationPreview { color: #ffffff; background: #c43e1c; font-weight: 600; }"
            )
            self.model_3d_animation_action.setStatusTip("3D Animation: playing")
        else:
            self.model_3d_animation_preview.setText("3D Animation: stopped")
            self.model_3d_animation_preview.setStyleSheet("")
            self.model_3d_animation_action.setStatusTip("3D Animation: stopped")
        self._message(self.model_3d_animation_action.statusTip())

    def open_designer_ideas(self):
        self.designer_ideas_preview.setText("Designer Ideas: 3 suggestions")
        self.designer_ideas_preview.setStyleSheet(
            "QLabel#designerIdeasPreview { color: #0f5132; background: #d1e7dd; font-weight: 600; }"
        )
        self._message("Designer Ideas: 3 layout suggestions")

    def open_recommended_chart(self):
        self.recommended_chart_preview.setText("Charts: clustered column")
        self.recommended_chart_preview.setStyleSheet(
            "QLabel#recommendedChartPreview { color: #124078; background: #eef6ff; font-weight: 600; }"
        )
        self._message("Recommended Chart: clustered column")

    def convert_to_data_type(self):
        self.data_types_preview.setText("Data Types: Geography linked")
        self.data_types_preview.setStyleSheet(
            "QLabel#dataTypesPreview { color: #0f5132; background: #d1e7dd; font-weight: 600; }"
        )
        self._message("Data Types: Geography linked")

    def recolor_svg_icon(self):
        self.svg_recolor_preview.setText("SVG color: blue accent")
        self.svg_recolor_preview.setStyleSheet(
            "QLabel#svgRecolorPreview { color: #ffffff; background: #2563eb; font-weight: 600; }"
        )
        self._message("Recolor SVG: blue accent applied")

    def convert_svg_to_shape(self):
        self.svg_convert_shape_preview.setText("SVG shape: editable shape")
        self.svg_convert_shape_preview.setStyleSheet(
            "QLabel#svgConvertShapePreview { color: #0f5132; background: #d1e7dd; font-weight: 600; }"
        )
        self._message("Convert to Shape: editable vector created")

    def apply_contextual_group_color(self):
        self.contextual_group_color_preview.setText("Picture Tools: purple")
        self.contextual_group_color_preview.setStyleSheet(
            "QLabel#contextualGroupColorPreview { color: #ffffff; background: #6f42c1; font-weight: 600; }"
        )
        self._message("Contextual group color: purple")

    def toggle_contextual_tabs_visible(self, visible):
        self.ribbonBar().setContextualTabsVisible(bool(visible))
        if visible:
            self.contextual_tab_visibility_preview.setText("Contextual tabs: visible")
            self.contextual_tab_visibility_preview.setStyleSheet("")
            self.contextual_tab_visibility_action.setStatusTip(
                "Contextual tabs: visible"
            )
        else:
            self.contextual_tab_visibility_preview.setText("Contextual tabs: hidden")
            self.contextual_tab_visibility_preview.setStyleSheet(
                "QLabel#contextualTabVisibilityPreview { color: #5b2d00; background: #fff4ce; font-weight: 600; }"
            )
            self.contextual_tab_visibility_action.setStatusTip(
                "Contextual tabs: hidden"
            )
        self._message(self.contextual_tab_visibility_action.statusTip())

    def toggle_title_groups_visible(self, visible):
        self.ribbonBar().setTitleGroupsVisible(bool(visible))
        if visible:
            self.title_groups_visibility_preview.setText("Title groups: visible")
            self.title_groups_visibility_preview.setStyleSheet("")
            self.title_groups_visibility_action.setStatusTip("Title groups: visible")
        else:
            self.title_groups_visibility_preview.setText("Title groups: hidden")
            self.title_groups_visibility_preview.setStyleSheet(
                "QLabel#titleGroupsVisibilityPreview { color: #5b2d00; background: #fff4ce; font-weight: 600; }"
            )
            self.title_groups_visibility_action.setStatusTip("Title groups: hidden")
        self._message(self.title_groups_visibility_action.statusTip())

    def toggle_reduced_motion(self, enabled):
        self.state_timing_preview.setProperty("reducedMotion", bool(enabled))
        if enabled:
            self.reduced_motion_preview.setText("Motion: reduced")
            self.reduced_motion_preview.setStyleSheet(
                "QLabel#reducedMotionPreview { color: #5b2d00; background: #fff4ce; font-weight: 600; }"
            )
            self.reduced_motion_action.setStatusTip("Reduced Motion: on")
        else:
            self.reduced_motion_preview.setText("Motion: full animation")
            self.reduced_motion_preview.setStyleSheet("")
            self.reduced_motion_action.setStatusTip("Reduced Motion: off")
        self._message(self.reduced_motion_action.statusTip())

    def toggle_touch_spacing(self, enabled):
        self.touch_spacing_enabled = bool(enabled)
        if enabled:
            self.style_preview_widget.setProperty("inputSpacingMode", "touch")
            self.touch_spacing_preview.setText("Touch spacing")
            self.touch_spacing_preview.setStyleSheet(
                "QLabel#touchSpacingPreview { color: #0f5132; background: #d1e7dd; font-weight: 600; }"
            )
            self.touch_spacing_action.setStatusTip("Touch spacing: on")
        else:
            self.style_preview_widget.setProperty("inputSpacingMode", "mouse")
            self.touch_spacing_preview.setText("Mouse spacing")
            self.touch_spacing_preview.setStyleSheet("")
            self.touch_spacing_action.setStatusTip("Touch spacing: off")
        self._message(self.touch_spacing_action.statusTip())

    def toggle_dictate_microphone(self, enabled):
        if enabled:
            self.dictate_microphone_preview.setText("Dictate: listening")
            self.dictate_microphone_preview.setStyleSheet(
                "QLabel#dictateMicrophonePreview { color: #107c41; font-weight: 600; }"
            )
            self.dictate_microphone_action.setToolTip(
                "Stop voice dictation from the microphone"
            )
            self._message("Dictate: listening from microphone")
        else:
            self.dictate_microphone_preview.setText("Dictate: microphone idle")
            self.dictate_microphone_preview.setStyleSheet("")
            self.dictate_microphone_action.setToolTip(
                "Start voice dictation from the microphone"
            )
            self._message("Dictate: microphone idle")

    def open_tell_me_help_redirect(self):
        query = self.ribbonBar().searchText().strip() or "unmatched Tell Me phrase"
        self.focus_caption_search()
        self.ribbonBar().setSearchText(query)
        self.ribbonBar().searchLineEdit().showPopup(query)
        self._message(f"Tell Me help: {query}")

    def toggle_key_tips_overlay(self, enabled):
        if enabled:
            self.key_tips_overlay_preview.setText("KeyTips: F H N P")
            self.key_tips_overlay_preview.setStyleSheet(
                "QLabel#keyTipsOverlayPreview { color: #ffffff; background: #2b579a; font-weight: 600; }"
            )
            self.key_tips_overlay_action.setStatusTip("KeyTips overlay: visible")
        else:
            self.key_tips_overlay_preview.setText("KeyTips: hidden")
            self.key_tips_overlay_preview.setStyleSheet("")
            self.key_tips_overlay_action.setStatusTip("KeyTips overlay: hidden")
        self._message(self.key_tips_overlay_action.statusTip())

    def activate_alt_key_tabs(self):
        ribbon = self.ribbonBar()
        ribbon.setCurrentPageIndex(ribbon.pageIndex(self.general_page))
        if not self.key_tips_overlay_action.isChecked():
            self.key_tips_overlay_action.setChecked(True)
        self.alt_key_tabs_preview.setText("Alt tabs: General F")
        self.alt_key_tabs_preview.setStyleSheet(
            "QLabel#altKeyTabsPreview { color: #ffffff; background: #107c41; font-weight: 600; }"
        )
        self.alt_key_tabs_action.setStatusTip("Alt key tabs: active")
        self._message(self.alt_key_tabs_action.statusTip())

    def set_quick_access_visible(self, visible):
        ribbon = self.ribbonBar()
        ribbon.quickAccessBar().setVisible(bool(visible))
        ribbon.setQuickAccessBarPosition(ribbon.quickAccessBarPosition())
        self.update_quick_access_preview()

    def set_quick_access_above_ribbon(self):
        self.ribbonBar().setQuickAccessBarPosition(QUICK_ACCESS_TOP_POSITION)
        self.update_quick_access_preview()

    def set_quick_access_below_ribbon(self):
        self.ribbonBar().setQuickAccessBarPosition(QUICK_ACCESS_BOTTOM_POSITION)
        self.update_quick_access_preview()

    def set_quick_access_labels_visible(self, visible):
        ribbon = self.ribbonBar()
        quick_access_bar = ribbon.quickAccessBar()
        quick_access_bar.setToolButtonStyle(
            Qt.ToolButtonStyle.ToolButtonTextBesideIcon
            if visible
            else Qt.ToolButtonStyle.ToolButtonIconOnly
        )
        ribbon.setQuickAccessBarPosition(ribbon.quickAccessBarPosition())
        self.update_quick_access_preview()

    def update_quick_access_preview(self):
        quick_access_bar = self.ribbonBar().quickAccessBar()
        visible = not quick_access_bar.isHidden()
        blocked = self.show_quick_access_action.blockSignals(True)
        self.show_quick_access_action.setChecked(visible)
        self.show_quick_access_action.blockSignals(blocked)
        above_blocked = self.quick_access_above_action.blockSignals(True)
        above = self.ribbonBar().quickAccessBarPosition() == QUICK_ACCESS_TOP_POSITION
        self.quick_access_above_action.setChecked(above)
        self.quick_access_above_action.blockSignals(above_blocked)
        below_blocked = self.quick_access_below_action.blockSignals(True)
        self.quick_access_below_action.setChecked(not above)
        self.quick_access_below_action.blockSignals(below_blocked)
        labels_visible = (
            quick_access_bar.toolButtonStyle()
            == Qt.ToolButtonStyle.ToolButtonTextBesideIcon
        )
        labels_blocked = self.quick_access_labels_action.blockSignals(True)
        self.quick_access_labels_action.setChecked(labels_visible)
        self.quick_access_labels_action.blockSignals(labels_blocked)
        self.reorder_quick_access_action.setEnabled(
            self.full_screen_action in self.quick_access_actions
            and self.quick_access_actions.index(self.full_screen_action)
            < len(self.quick_access_actions) - 1
        )
        visible_count = quick_access_bar.visibleCount() if visible else 0
        self.quick_access_status_preview.setText(
            f"QAT: {'Visible' if visible else 'Hidden'} "
            f"{visible_count}/{len(self.quick_access_actions)} | "
            f"{'Above' if above else 'Below'} | "
            f"{'Labels' if labels_visible else 'Icons'}"
        )

    def restore_classic_ribbon(self):
        self.ribbonBar().setRibbonMinimized(False)
        self.ribbonBar().setSimplifiedMode(False)
        self.update_collapse_state_preview()

    def pin_ribbon(self):
        self.ribbonBar().setRibbonMinimized(False)
        self.ribbonBar().setMinimizationEnabled(False)
        self.update_collapse_state_preview()

    def unpin_ribbon(self):
        self.ribbonBar().setMinimizationEnabled(True)
        self.ribbonBar().setRibbonMinimized(True)
        self.update_collapse_state_preview()

    def show_tabs_and_commands(self):
        self.ribbonBar().setMinimizationEnabled(True)
        self.ribbonBar().setSimplifiedMode(False)
        self.ribbonBar().setRibbonMinimized(False)
        self.update_collapse_state_preview()

    def show_tabs_only(self):
        self.ribbonBar().setMinimizationEnabled(True)
        self.ribbonBar().setSimplifiedMode(False)
        self.ribbonBar().setRibbonMinimized(True)
        self.update_collapse_state_preview()

    def auto_hide_ribbon(self):
        self.ribbonBar().setMinimizationEnabled(True)
        self.ribbonBar().setSimplifiedMode(False)
        self.ribbonBar().setRibbonMinimized(True)
        self.update_collapse_state_preview()

    def always_show_ribbon(self):
        self.ribbonBar().setSimplifiedMode(False)
        self.pin_ribbon()

    def _set_recent_file_pinned(self, pinned):
        self.recent_files.updateRecentFileActions(
            self.recent_file_pinned_order if pinned else self.recent_file_default_order
        )
        self.pin_recent_file_action.setText(
            "Unpin Recent File" if pinned else "Pin Recent File"
        )
        self.pin_recent_file_action.setToolTip(
            (
                "Unpin axis-profile.lqr from Recent Files"
                if pinned
                else "Pin axis-profile.lqr to the top of Recent Files"
            )
        )
        self._message(
            (
                "Pinned recent file: axis-profile.lqr"
                if pinned
                else "Unpinned recent file: axis-profile.lqr"
            )
        )

    def _show_upload_before_share_prompt(self):
        self.upload_before_share_prompt.setText(
            "Upload before sharing: save this local draft to OneDrive or "
            "SharePoint before inviting people."
        )
        self.upload_before_share_prompt.setStyleSheet(
            "QLabel#uploadBeforeSharePrompt { color: #8a5700; font-weight: 600; }"
        )
        self.backstage.setActivePage(self.backstage_open_page)
        self._message("Share: upload before sharing to invite people")

    def open_account_backstage(self):
        self.backstage.setActivePage(self.backstage_account_page)
        self._message("Account: signed in as Local User")

    def open_account_privacy_settings(self):
        self.account_privacy_summary.setText(
            "Privacy settings: connected experiences reviewed"
        )
        self.account_privacy_summary.setStyleSheet(
            "QLabel#accountPrivacySummary { color: #0f6cbd; font-weight: 600; }"
        )
        self._message("Account Privacy: settings opened")

    def update_collapse_state_preview(self):
        ribbon = self.ribbonBar()
        if not ribbon.isMinimizationEnabled():
            state = "Pinned"
        elif ribbon.isRibbonTemporaryExpanded():
            state = "Temporary"
        elif ribbon.simplifiedMode():
            state = "Simplified"
        elif ribbon.isRibbonMinimized():
            state = "Collapsed"
        else:
            state = "Expanded"

        if not ribbon.isMinimizationEnabled():
            double_click_state = "Locked"
        elif ribbon.isRibbonMinimized() or ribbon.isRibbonTemporaryExpanded():
            double_click_state = "Restore"
        else:
            double_click_state = "Collapse"

        if ribbon.simplifiedMode():
            density_state = f"Compact {ribbon.rowItemHeight()}px"
            preview_text = f"{state} | {density_state}"
        else:
            density_metric = f"{ribbon.rowItemCount()}x{ribbon.rowItemHeight()}px"
            density_state = f"Expanded {density_metric}"
            preview_text = f"{state} | Tab: {double_click_state} | {density_metric}"
        self.collapse_state_preview.setText(preview_text)
        self.collapse_state_preview.setVisible(not ribbon.simplifiedMode())
        if hasattr(self, "density_status_preview"):
            self.density_status_preview.setText(f"Ribbon density: {density_state}")

    def _ribbon_button_for_action(self, action):
        for button in self.ribbonBar().findChildren(QToolButton):
            if button.defaultAction() is action:
                return button
        return None

    def update_responsive_label_preview(self):
        compressed = self.width_stress_action.isChecked()
        hidden_count = 0
        button_count = 0
        for action in self.responsive_label_actions:
            button = self._ribbon_button_for_action(action)
            if button is None:
                continue
            button_count += 1
            button.setToolButtonStyle(
                Qt.ToolButtonStyle.ToolButtonIconOnly
                if compressed
                else Qt.ToolButtonStyle.ToolButtonTextBesideIcon
            )
            button.setProperty("responsiveLabelHidden", compressed)
            button.setToolTip(action.text())
            if compressed:
                hidden_count += 1
        stress_button = self._ribbon_button_for_action(self.width_stress_action)
        if stress_button is not None:
            stress_button.setToolButtonStyle(
                Qt.ToolButtonStyle.ToolButtonIconOnly
                if compressed
                else Qt.ToolButtonStyle.ToolButtonTextBesideIcon
            )
            stress_button.setToolTip(self.width_stress_action.text())
        self.responsive_labels_status_preview.setText(
            f"Labels hidden: {hidden_count}/{button_count}"
        )

    def install_default_content(self):
        content = QLabel("LqRibbon PySide6 example")
        content.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setCentralWidget(content)
        self.default_content = content

    def show_mdi_content(self, tabbed=False):
        mdi_area = RibbonMdiArea(self)
        mdi_area.setViewMode(
            QMdiArea.ViewMode.TabbedView if tabbed else QMdiArea.ViewMode.SubWindowView
        )
        for index, title in enumerate(["Write Settings", "Control Loop Specialist"]):
            table = QTableWidget(8, 4, mdi_area)
            table.setWindowTitle(title)
            table.setHorizontalHeaderLabels(["Index", "Name", "Value", "State"])
            sub_window = mdi_area.addSubWindow(table)
            sub_window.setWindowTitle(title)
            sub_window.resize(360 if index == 0 else 300, 220)
            sub_window.move(40 if index == 0 else 460, 60 if index == 0 else 80)
            sub_window.show()
        self.setCentralWidget(mdi_area)
        self.mdi_area = mdi_area

    def select_preview_page(self, controls=False, gallery=False, shell=False, style=False):
        if style:
            page = self.general_page
        elif shell:
            page = self.shell_page
        elif gallery:
            page = self.gallery_page
        elif controls:
            page = self.controls_page
        else:
            page = self.driver_page
        self.ribbonBar().setCurrentPageIndex(self.ribbonBar().pageIndex(page))

    def set_ribbon_style(self, style):
        if isinstance(style, str):
            key = (
                style.strip()
                .lower()
                .replace("-", "")
                .replace("_", "")
                .replace(" ", "")
            )
            if key in {"system", "systemdefault"}:
                style = self.system_ribbon_style()
                self.setRibbonStyle(style)
                self._update_style_preview(style)
                style_combo = self.style_combo_control.widget()
                index = style_combo.findData(SYSTEM_RIBBON_STYLE_VALUE)
                if index >= 0:
                    style_combo.setCurrentIndex(index)
                return
        style = LqStyle.coerce_style(style)
        self.setRibbonStyle(style)
        self._update_style_preview(style)
        style_combo = self.style_combo_control.widget()
        index = style_combo.findData(int(style))
        if index >= 0:
            style_combo.setCurrentIndex(index)

    def focus_search_preview(self):
        self.ribbonBar().searchLineEdit().setFocus()
        self.ribbonBar().setSearchText("ba")

    def toggle_high_contrast_style_preview(self, enabled):
        self.high_contrast_style_pass = bool(enabled)
        self.high_contrast_style_action.setStatusTip(
            "High Contrast: preview on" if enabled else "High Contrast: preview off"
        )
        self._update_style_preview(self.ribbonStyle())
        self._message(self.high_contrast_style_action.statusTip())

    def _apply_icon_only_title_buttons(self):
        title_bar = self.ribbonBar()._title_button_bar
        title_bar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        for action in self.icon_only_title_actions:
            button = title_bar.widgetForAction(action)
            if isinstance(button, QToolButton):
                button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
                button.setToolTip(action.toolTip() or action.text())
                button.setAccessibleName(action.text())
                button.setAccessibleDescription(action.toolTip() or action.text())

    def _update_auto_save_title_action(self, enabled):
        state = "on" if enabled else "off"
        detail = (
            "AutoSave is on for this cloud document"
            if enabled
            else "AutoSave is off for this local draft. Save to a cloud location to enable it."
        )
        self.auto_save_title_action.setToolTip(detail)
        status = (
            f"AutoSave: {state}"
            if enabled
            else "AutoSave: off - save to cloud to enable"
        )
        self.auto_save_title_action.setStatusTip(status)
        self._message(status)

    def toggle_full_screen(self):
        if self.windowState() & Qt.WindowState.WindowFullScreen:
            self.showNormal()
        else:
            self.showFullScreen()

    def add_runtime_page(self):
        page_number = self.runtime_page_counter
        page = self.ribbonBar().addPage(f"Runtime {page_number}")
        self.runtime_page_counter += 1
        group = page.addGroup("Generated")
        group.addAction(
            self._icon(QStyle.StandardPixmap.SP_DialogApplyButton),
            "Generated Action",
            Qt.ToolButtonStyle.ToolButtonTextUnderIcon,
        )
        self.customize_manager.addToCategory("Pages", page)
        self.customize_manager.setPageId(page, f"runtime{page_number}")
        self.custom_tab_preview.setText(f"Custom tab: Runtime {page_number}")
        self.custom_tab_preview.setStyleSheet(
            "QLabel#customTabPreview { color: #0f5132; background: #d1e7dd; font-weight: 600; }"
        )
        self.add_page_action.setStatusTip(f"Custom tab: Runtime {page_number}")
        self._message(self.add_page_action.statusTip())
        self.ribbonBar().setCurrentWidget(page)

    def add_custom_group(self):
        page = self.ribbonBar().currentPage()
        if page is None or not page.title().startswith("Runtime"):
            self.add_runtime_page()
            page = self.ribbonBar().currentPage()
        group_number = self.runtime_group_counter
        self.runtime_group_counter += 1
        group = page.addGroup(f"Custom Group {group_number}")
        group.addAction(
            self._icon(QStyle.StandardPixmap.SP_DialogApplyButton),
            "Custom Command",
            Qt.ToolButtonStyle.ToolButtonTextUnderIcon,
        )
        self.customize_manager.addToCategory("Groups", group)
        self.customize_manager.setGroupId(group, f"customGroup{group_number}")
        self.last_custom_group = group
        self.custom_group_preview.setText(f"Custom group: {group.title()}")
        self.custom_group_preview.setStyleSheet(
            "QLabel#customGroupPreview { color: #0f5132; background: #d1e7dd; font-weight: 600; }"
        )
        self.add_group_action.setStatusTip(f"Custom group: {group.title()}")
        self._message(self.add_group_action.statusTip())

    def rename_custom_tab_and_group(self):
        page = self.ribbonBar().currentPage()
        if page is None or not page.title().startswith("Runtime"):
            self.add_runtime_page()
            page = self.ribbonBar().currentPage()
        if self.last_custom_group is None or self.last_custom_group not in page.groups():
            self.add_custom_group()
            page = self.ribbonBar().currentPage()
        rename_number = self.rename_custom_counter
        self.rename_custom_counter += 1
        tab_name = f"Renamed Tab {rename_number}"
        group_name = f"Renamed Group {rename_number}"
        self.customize_manager.setPageName(page, tab_name)
        self.customize_manager.setGroupName(self.last_custom_group, group_name)
        self.custom_tab_preview.setText(f"Custom tab: {tab_name}")
        self.custom_group_preview.setText(f"Custom group: {group_name}")
        self.rename_custom_preview.setText(f"{tab_name} / {group_name}")
        self.rename_custom_preview.setStyleSheet(
            "QLabel#renameCustomPreview { color: #0f5132; background: #d1e7dd; font-weight: 600; }"
        )
        self.rename_custom_action.setStatusTip(f"Renamed custom: {tab_name} / {group_name}")
        self._message(self.rename_custom_action.statusTip())

    def add_command_to_custom_group(self):
        if self.last_custom_group is None:
            self.add_custom_group()
        command_number = self.custom_command_counter
        self.custom_command_counter += 1
        action = QAction(
            self._icon(QStyle.StandardPixmap.SP_DialogApplyButton),
            f"Custom Command {command_number}",
            self,
        )
        action.setObjectName(f"customCommand{command_number}")
        action.setToolTip("Command added through ribbon customization")
        action.setStatusTip(f"Custom command: Custom Command {command_number}")
        self.customize_manager.appendActions(self.last_custom_group, [action])
        self.custom_command_preview.setText(f"Custom command: {action.text()}")
        self.custom_command_preview.setStyleSheet(
            "QLabel#customCommandPreview { color: #0f5132; background: #d1e7dd; font-weight: 600; }"
        )
        self.add_command_action.setStatusTip(f"Custom command: {action.text()}")
        self._message(self.add_command_action.statusTip())

    def remove_command_from_custom_group(self):
        if self.last_custom_group is None:
            self.add_custom_group()
        actions = self.customize_manager.actionsGroup(self.last_custom_group)
        if not actions:
            self.remove_command_action.setStatusTip("Custom command: nothing to remove")
            self._message(self.remove_command_action.statusTip())
            return
        removed_text = actions[-1].text()
        self.customize_manager.removeActionAt(self.last_custom_group, len(actions) - 1)
        self.removed_command_preview.setText(f"Removed command: {removed_text}")
        self.removed_command_preview.setStyleSheet(
            "QLabel#removedCommandPreview { color: #842029; background: #f8d7da; font-weight: 600; }"
        )
        self.remove_command_action.setStatusTip(f"Removed command: {removed_text}")
        self._message(self.remove_command_action.statusTip())

    def reset_selected_custom_tab(self):
        page = self.ribbonBar().currentPage()
        if page is None or not self.customize_manager.pageId(page).startswith("runtime"):
            self.add_runtime_page()
            page = self.ribbonBar().currentPage()
        page_id = self.customize_manager.pageId(page)
        runtime_number = page_id.replace("runtime", "", 1) or "1"
        while page.groupCount() > 1:
            page.removeGroupByIndex(page.groupCount() - 1)
        if page.groupCount() == 0:
            page.addGroup("Generated")
        self.customize_manager.setPageName(page, f"Runtime {runtime_number}")
        self.customize_manager.setGroupName(page.group(0), "Generated")
        self.last_custom_group = None
        self.custom_tab_preview.setText(f"Custom tab: Runtime {runtime_number}")
        self.custom_group_preview.setText("Custom group: none")
        self.custom_command_preview.setText("Custom command: none")
        self.reset_selected_tab_preview.setText(f"Selected tab reset: Runtime {runtime_number}")
        self.reset_selected_tab_preview.setStyleSheet(
            "QLabel#resetSelectedTabPreview { color: #084298; background: #cfe2ff; font-weight: 600; }"
        )
        self.reset_selected_tab_action.setStatusTip(f"Selected tab reset: Runtime {runtime_number}")
        self._message(self.reset_selected_tab_action.statusTip())

    def reset_all_ribbon_customizations(self):
        runtime_pages = [
            page
            for page in list(self.ribbonBar().pages())
            if self.customize_manager.pageId(page).startswith("runtime")
        ]
        for page in runtime_pages:
            self.customize_manager.deletePage(page)
        self.runtime_page_counter = 1
        self.runtime_group_counter = 1
        self.rename_custom_counter = 1
        self.custom_command_counter = 1
        self.last_custom_group = None
        self.custom_tab_preview.setText("Custom tab: none")
        self.custom_group_preview.setText("Custom group: none")
        self.custom_command_preview.setText("Custom command: none")
        self.removed_command_preview.setText("Removed command: none")
        self.reset_selected_tab_preview.setText("Selected tab reset: none")
        self.reset_all_customizations_preview.setText("All customizations: reset")
        self.reset_all_customizations_preview.setStyleSheet(
            "QLabel#resetAllCustomizationsPreview { color: #084298; background: #cfe2ff; font-weight: 600; }"
        )
        self.reset_all_customizations_action.setStatusTip(
            f"Ribbon customizations reset: {len(runtime_pages)} page(s)"
        )
        self._message(self.reset_all_customizations_action.statusTip())

    def export_ribbon_customization(self):
        buffer = io.BytesIO()
        self.customize_manager.saveStateToDevice(buffer)
        self.exported_ribbon_customization_state = buffer.getvalue()
        size = len(self.exported_ribbon_customization_state)
        self.export_customization_preview.setText(f"Ribbon export: {size} bytes")
        self.export_customization_preview.setStyleSheet(
            "QLabel#exportRibbonCustomizationPreview { color: #0f5132; background: #d1e7dd; font-weight: 600; }"
        )
        self.export_customization_action.setStatusTip(f"Ribbon export: {size} bytes")
        self._message(self.export_customization_action.statusTip())

    def import_ribbon_customization(self):
        if not self.exported_ribbon_customization_state:
            self.import_customization_action.setStatusTip("Ribbon import: no export")
            self._message(self.import_customization_action.statusTip())
            return
        self.customize_manager.loadStateFromDevice(
            io.BytesIO(self.exported_ribbon_customization_state)
        )
        size = len(self.exported_ribbon_customization_state)
        self.import_customization_preview.setText(f"Ribbon import: {size} bytes")
        self.import_customization_preview.setStyleSheet(
            "QLabel#importRibbonCustomizationPreview { color: #0f5132; background: #d1e7dd; font-weight: 600; }"
        )
        self.import_customization_action.setStatusTip(f"Ribbon import: {size} bytes")
        self._message(self.import_customization_action.statusTip())

    def rename_driver_page(self):
        self.driver_page.setTitle("Drive" if self.driver_page.title() == "Driver" else "Driver")

    def move_gallery_page(self):
        current_index = self.ribbonBar().pageIndex(self.gallery_page)
        target_index = self.ribbonBar().pageCount() - 1 if current_index == 1 else 1
        self.ribbonBar().movePage(self.gallery_page, target_index)

    def toggle_specialist_group(self):
        self.specialist_group.setVisible(not self.specialist_group.isVisible())
        self.driver_page.updateLayout()

    def show_office_popup(self):
        popup = OfficePopupWindow(self)
        popup.setTitleIcon(self._icon(QStyle.StandardPixmap.SP_MessageBoxInformation))
        popup.setTitleText("LqRibbon")
        popup.setBodyText("Popup window sample")
        popup.setDisplayTime(3000)
        popup.showPopup(self.mapToGlobal(QPoint(40, 90)))
        self._message("Office popup: notification shown")

    def show_office_menu(self):
        self.office_menu.exec(self.mapToGlobal(QPoint(40, 90)))

    def save_layout_state(self):
        buffer = io.BytesIO()
        self.customize_manager.saveStateToDevice(buffer)
        self.saved_ribbon_state = buffer.getvalue()
        self._message("Ribbon layout saved")

    def load_layout_state(self):
        if not self.saved_ribbon_state:
            self._message("No saved Ribbon layout")
            return
        self.customize_manager.loadStateFromDevice(io.BytesIO(self.saved_ribbon_state))
        self._message("Ribbon layout loaded")

    def _add_group_action(
        self,
        group,
        standard_pixmap,
        text,
        style=Qt.ToolButtonStyle.ToolButtonTextUnderIcon,
    ):
        return group.addAction(self._icon(standard_pixmap), text, style)

    def _add_control_modes_button(self, group):
        control_button = QToolButton(group)
        self.control_modes_action = QAction(
            self._icon(QStyle.StandardPixmap.SP_FileDialogListView),
            "Control Modes",
            control_button,
        )
        self.control_modes_action.setObjectName("controlModesAction")
        control_button.setDefaultAction(self.control_modes_action)
        control_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        control_button.setPopupMode(QToolButton.ToolButtonPopupMode.MenuButtonPopup)
        menu = QMenu(control_button)
        menu.addAction("Pulse Mode")
        menu.addAction("Analog Velocity Mode")
        self.control_modes_action.setMenu(menu)
        control_button.setMenu(menu)
        group.addWidget(control_button)

    def _add_status_action_button(self, switch_group, action):
        button = QToolButton(switch_group)
        button.setDefaultAction(action)
        switch_group.layout.addWidget(button)

    def _icon(self, standard_pixmap):
        return self.style().standardIcon(standard_pixmap)

    def _high_dpi_gallery_icon(self):
        icon = QIcon()
        for size, color in ((16, "#0078d4"), (32, "#107c10"), (64, "#5c2d91")):
            pixmap = QPixmap(size, size)
            pixmap.fill(Qt.GlobalColor.transparent)
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setPen(QPen(QColor("#ffffff"), max(1, size // 16)))
            painter.setBrush(QColor(color))
            margin = max(2, size // 8)
            painter.drawRoundedRect(
                QRect(margin, margin, size - margin * 2, size - margin * 2),
                size // 6,
                size // 6,
            )
            painter.setBrush(QColor("#ffffff"))
            inset = max(4, size // 4)
            painter.drawEllipse(QRect(inset, inset, size - inset * 2, size - inset * 2))
            painter.end()
            icon.addPixmap(pixmap)
        return icon

    def _app_icon_color_set_icon(self):
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        colors = ("#185abd", "#107c41", "#c43e1c", "#7719aa")
        rects = (
            QRect(6, 6, 24, 24),
            QRect(34, 6, 24, 24),
            QRect(6, 34, 24, 24),
            QRect(34, 34, 24, 24),
        )
        for rect, color in zip(rects, colors):
            painter.setPen(QPen(QColor("#ffffff"), 2))
            painter.setBrush(QColor(color))
            painter.drawRoundedRect(rect, 6, 6)
        painter.end()
        return QIcon(pixmap)

    def _svg_insert_icon(self):
        pixmap = QPixmap(48, 48)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(QColor("#2563eb"), 3))
        painter.setBrush(QColor("#dbeafe"))
        painter.drawRoundedRect(QRect(7, 5, 34, 38), 5, 5)
        painter.setPen(QPen(QColor("#1e40af"), 2))
        painter.drawText(QRect(7, 13, 34, 18), Qt.AlignmentFlag.AlignCenter, "SVG")
        painter.setBrush(QColor("#10b981"))
        painter.setPen(QPen(QColor("#ffffff"), 2))
        painter.drawEllipse(QRect(27, 27, 14, 14))
        painter.end()
        return QIcon(pixmap)

    def _svg_recolor_icon(self):
        pixmap = QPixmap(48, 48)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(QColor("#1d4ed8"), 3))
        painter.setBrush(QColor("#dbeafe"))
        painter.drawRoundedRect(QRect(8, 6, 31, 36), 5, 5)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#2563eb"))
        painter.drawEllipse(QRect(15, 14, 19, 19))
        painter.setPen(QPen(QColor("#ffffff"), 2))
        painter.drawLine(20, 24, 24, 28)
        painter.drawLine(24, 28, 31, 19)
        painter.end()
        return QIcon(pixmap)

    def _svg_convert_shape_icon(self):
        pixmap = QPixmap(48, 48)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(QColor("#0f766e"), 3))
        painter.setBrush(QColor("#ccfbf1"))
        painter.drawRoundedRect(QRect(7, 7, 34, 34), 6, 6)
        painter.setPen(QPen(QColor("#0f766e"), 2))
        painter.drawLine(17, 17, 31, 17)
        painter.drawLine(31, 17, 31, 31)
        painter.drawLine(31, 31, 17, 31)
        painter.drawLine(17, 31, 17, 17)
        painter.setBrush(QColor("#ffffff"))
        for point in (
            QRect(13, 13, 8, 8),
            QRect(27, 13, 8, 8),
            QRect(27, 27, 8, 8),
            QRect(13, 27, 8, 8),
        ):
            painter.drawEllipse(point)
        painter.end()
        return QIcon(pixmap)

    def _tell_me_lightbulb_icon(self):
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(QColor("#8a6d00"), 2))
        painter.setBrush(QColor("#ffd966"))
        painter.drawEllipse(QRect(8, 4, 16, 16))
        painter.setBrush(QColor("#8a6d00"))
        painter.drawRoundedRect(QRect(11, 19, 10, 6), 2, 2)
        painter.drawLine(12, 27, 20, 27)
        painter.end()
        return QIcon(pixmap)

    def _avatar_strip_icon(self):
        pixmap = QPixmap(48, 32)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        font = painter.font()
        font.setBold(True)
        font.setPointSize(8)
        painter.setFont(font)
        for x, initials, color in (
            (2, "AC", "#2f7ed8"),
            (14, "BL", "#17865c"),
            (26, "MP", "#b55416"),
        ):
            painter.setPen(QPen(QColor("#ffffff"), 1))
            painter.setBrush(QColor(color))
            avatar_rect = QRect(x, 5, 22, 22)
            painter.drawEllipse(avatar_rect)
            painter.drawText(avatar_rect, Qt.AlignmentFlag.AlignCenter, initials)
        painter.end()
        return QIcon(pixmap)

    def _message(self, text, timeout=2500):
        self.statusBar().showMessage(text, timeout)
