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
        self.saved_ribbon_state = b""
        self.search_actions = []
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

        self.review_page = ribbon.addPage("Review")
        self._create_review_page()

        self.view_page = ribbon.addPage("View")
        self._create_view_page()

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
        style_group.addWidget(self.style_preview_widget)
        style_group.addWidget(self.state_timing_preview)
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
        self.style_preview_widget.setToolTip(LqStyle.ribbon_style_name(style))
        for object_name, palette_key in [
            ("lqRibbonStylePreviewAccent", "accent"),
            ("lqRibbonStylePreviewRibbon", "ribbon_bg"),
            ("lqRibbonStylePreviewField", "field_bg"),
            ("lqRibbonStylePreviewText", "text"),
        ]:
            swatch = self.style_preview_widget.findChild(QFrame, object_name)
            if swatch is None:
                continue
            color = palette[palette_key]
            swatch.setProperty("previewColor", color)
            border = palette["control_border"]
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
        self.style_gallery.setGalleryGroup(gallery_group)
        self.style_gallery.setColumnCount(4)
        self.style_gallery.setRowCount(2)
        self.style_gallery.setCheckedIndex(1)

        self.gallery_menu = QMenu(self.style_gallery)
        self.gallery_menu.addAction("More styles")
        self.gallery_menu.addAction("Reset style")
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
        self.office_menu_action = self._add_group_action(
            popup_group,
            QStyle.StandardPixmap.SP_DirOpenIcon,
            "Popup Menu",
            Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
        )
        self.color_button = PopupColorButton(popup_group)
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
        self.backstage.addSeparator()

        backstage_page = QWidget(self.backstage)
        backstage_page.setWindowTitle("Info")
        backstage_layout = QFormLayout(backstage_page)
        backstage_layout.addRow("Product", QLabel("LqRibbon Demo", backstage_page))
        backstage_layout.addRow("Mode", QLabel("Backstage page", backstage_page))
        self.cloud_location_combo = QComboBox(backstage_page)
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
            backstage_page,
        )
        self.upload_before_share_prompt.setObjectName("uploadBeforeSharePrompt")
        self.upload_before_share_prompt.setToolTip(
            "Save this local draft to a cloud location before inviting people"
        )
        self.upload_before_share_prompt.setWordWrap(True)
        backstage_layout.addRow("Share readiness", self.upload_before_share_prompt)
        self.backstage.addPage(backstage_page)
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
        self.recent_files.updateRecentFileActions(self.recent_file_default_order)
        export_action = QAction(
            self._icon(QStyle.StandardPixmap.SP_DialogSaveButton), "Export", self.system_menu
        )
        self.system_menu.addPageSystemPopup("Export", export_action, True)
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
        open_page_layout.addRow("Frequent sites", self.frequent_sites_label)
        open_page_layout.addRow("Frequent groups", self.frequent_groups_label)
        self.backstage_open_action = self.backstage.addPage(self.backstage_open_page)
        self.backstage_open_action.setObjectName("backstageOpenAction")
        self.backstage_open_action.setToolTip("Open frequent sites and groups")
        self.backstage_open_action.setStatusTip(
            "Open: frequent sites and groups"
        )
        self.backstage_open_action.triggered.connect(
            lambda: self._message("Open: frequent sites and groups")
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
        self.office_menu.setGripVisible(True)
        popup_editor = QPlainTextEdit(self.office_menu)
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
            self.review_page,
            self.view_page,
            self.tell_me_page,
            self.shell_page,
        ]:
            self.customize_manager.addToCategory("Pages", page)
        for action in [
            self.full_screen_action,
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
            self.svg_icon_insert_action,
            self.account_privacy_settings_action,
            self.tell_me_lightbulb_action,
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
        self.tell_me_lightbulb_action.triggered.connect(
            lambda: self._message("Tell Me: type a command or phrase in Search")
        )
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
        self.share_title_action.setToolTip("Share this document")
        self.share_title_action.setStatusTip(
            "Share: upload before sharing to invite people"
        )
        self.comments_title_action = self.ribbonBar().addTitleButton(
            self._icon(QStyle.StandardPixmap.SP_FileDialogContentsView),
            "Comments",
        )
        self.comments_title_action.setObjectName("commentsTitleAction")
        self.comments_title_action.setToolTip("Open document comments")
        self.comments_title_action.setStatusTip("Comments: show conversation pane")
        self.presence_avatar_strip_action = self.ribbonBar().addTitleButton(
            self._avatar_strip_icon(),
            "Presence",
        )
        self.presence_avatar_strip_action.setObjectName("presenceAvatarStripAction")
        self.presence_avatar_strip_action.setToolTip(
            "Alice Chen, Bo Li, and Maya Patel are editing"
        )
        self.presence_avatar_strip_action.setStatusTip(
            "Presence: 3 collaborators editing"
        )
        self.feedback_title_action = self.ribbonBar().addTitleButton(
            self._icon(QStyle.StandardPixmap.SP_MessageBoxInformation),
            "Feedback",
        )
        self.feedback_title_action.setObjectName("feedbackTitleAction")
        self.feedback_title_action.setToolTip("Send feedback about this document")
        self.feedback_title_action.setStatusTip("Feedback: send product feedback")
        self.help_title_action = self.ribbonBar().addTitleButton(
            self._icon(QStyle.StandardPixmap.SP_MessageBoxQuestion), "Help"
        )
        self.account_title_action = self.ribbonBar().addTitleButton(
            self._icon(QStyle.StandardPixmap.SP_DirHomeIcon), "Account"
        )
        self.account_title_action.setObjectName("accountTitleAction")
        self.account_title_action.setToolTip("Open account and profile settings")
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
            self.svg_icon_insert_action,
            self.account_privacy_settings_action,
            self.tell_me_lightbulb_action,
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

    def insert_svg_icon(self):
        self.svg_icon_insert_preview.setText("SVG Icons: 1 inserted")
        self.svg_icon_insert_preview.setStyleSheet(
            "QLabel#svgIconInsertPreview { color: #124078; background: #eef6ff; font-weight: 600; }"
        )
        self._message("SVG Icon: inserted scalable artwork")

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
        page = self.ribbonBar().addPage(f"Runtime {self.runtime_page_counter}")
        self.runtime_page_counter += 1
        group = page.addGroup("Generated")
        group.addAction(
            self._icon(QStyle.StandardPixmap.SP_DialogApplyButton),
            "Generated Action",
            Qt.ToolButtonStyle.ToolButtonTextUnderIcon,
        )
        self.ribbonBar().setCurrentWidget(page)

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
