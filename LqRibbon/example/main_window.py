"""
MainWindow - feature parity demo for the C++ example.
"""

import io

from PySide6.QtCore import QDate, QPoint, QSize, Qt
from PySide6.QtGui import QAction, QActionGroup, QColor
from PySide6.QtWidgets import (
    QFormLayout,
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
    RibbonSystemMenu,
    RibbonToolBarControl,
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

        self.shell_page = ribbon.addPage("Shell")
        self._create_shell_page()
        self._create_system_surfaces()
        self._create_status_bar()
        self._create_customize_state()
        self._connect_actions()
        self._configure_search_and_quick_access()

        ribbon.setCurrentPageIndex(ribbon.pageIndex(self.driver_page))
        self.setFrameThemeEnabled(True)
        ribbon.setSearchVisible(True)
        ribbon.setSearchPlaceholderText("Search commands")
        ribbon.setRecentSearchLimit(5)

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

        self.style_gallery = RibbonGallery(style_group)
        self.style_gallery.setGalleryGroup(gallery_group)
        self.style_gallery.setColumnCount(3)
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
        self.backstage.addSeparator()

        backstage_page = QWidget(self.backstage)
        backstage_page.setWindowTitle("Info")
        backstage_layout = QFormLayout(backstage_page)
        backstage_layout.addRow("Product", QLabel("LqRibbon Demo", backstage_page))
        backstage_layout.addRow("Mode", QLabel("Backstage page", backstage_page))
        self.backstage.addPage(backstage_page)

        self.system_menu = RibbonSystemMenu(self.ribbonBar())
        self.system_menu.addPopupBarAction("New")
        self.system_menu.addPopupBarAction("Open")
        recent_files = self.system_menu.addPageRecentFile("Recent Files")
        recent_files.updateRecentFileActions(["axis-profile.lqr", "drive-layout.lqr"])
        export_action = QAction(
            self._icon(QStyle.StandardPixmap.SP_DialogSaveButton), "Export", self.system_menu
        )
        self.system_menu.addPageSystemPopup("Export", export_action, True)

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

        switch_group = RibbonStatusBarSwitchGroup(status_bar)
        view_actions = QActionGroup(switch_group)
        view_actions.setExclusive(True)
        normal_view_action = view_actions.addAction(
            self._icon(QStyle.StandardPixmap.SP_FileDialogDetailedView), "Normal View"
        )
        compact_view_action = view_actions.addAction(
            self._icon(QStyle.StandardPixmap.SP_FileDialogListView), "Compact View"
        )
        normal_view_action.setCheckable(True)
        compact_view_action.setCheckable(True)
        normal_view_action.setChecked(True)
        self._add_status_action_button(switch_group, normal_view_action)
        self._add_status_action_button(switch_group, compact_view_action)

        zoom_slider = RibbonSliderPane(status_bar)
        zoom_slider.setRange(10, 200)
        zoom_slider.setSingleStep(10)
        zoom_slider.setValue(100)

        progress_bar = RibbonProgressBar(status_bar)
        progress_bar.setValue(42)

        sync_action = QAction(
            self._icon(QStyle.StandardPixmap.SP_BrowserReload), "Sync", status_bar
        )
        status_bar.addPermanentAction(sync_action)
        status_bar.addPermanentWidget(switch_group)
        status_bar.addPermanentWidget(zoom_slider)
        status_bar.addPermanentWidget(progress_bar)
        self.setStatusBar(status_bar)
        self.ribbon_status_bar = status_bar
        self.zoom_slider = zoom_slider
        self.progress_bar = progress_bar
        zoom_slider.valueChanged.connect(progress_bar.setValueSafe)

    def _create_customize_state(self):
        self.customize_manager = self.ribbonBar().customizeManager()
        for page in [
            self.general_page,
            self.driver_page,
            self.controls_page,
            self.gallery_page,
            self.shell_page,
        ]:
            self.customize_manager.addToCategory("Pages", page)
        for action in [
            self.full_screen_action,
            self.connect_action,
            self.office_popup_action,
            self.show_customize_action,
        ]:
            self.customize_manager.addToCategory("Actions", action)
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
        self.minimize_ribbon_action.triggered.connect(
            lambda: self.ribbonBar().setRibbonMinimized(True)
        )
        self.restore_ribbon_action.triggered.connect(
            lambda: self.ribbonBar().setRibbonMinimized(False)
        )
        self.toggle_frame_action.toggled.connect(self.setFrameThemeEnabled)
        self.add_page_action.triggered.connect(self.add_runtime_page)
        self.rename_page_action.triggered.connect(self.rename_driver_page)
        self.move_gallery_action.triggered.connect(self.move_gallery_page)
        self.toggle_group_action.triggered.connect(self.toggle_specialist_group)
        self.office_popup_action.triggered.connect(self.show_office_popup)
        self.office_menu_action.triggered.connect(self.show_office_menu)
        self.color_button.colorChanged.connect(
            lambda color: self._message(f"Color changed: {color.name()}")
        )
        self.show_customize_action.triggered.connect(self.ribbonBar().showCustomizeDialog)
        self.save_state_action.triggered.connect(self.save_layout_state)
        self.load_state_action.triggered.connect(self.load_layout_state)
        self.ribbonBar().searchAccepted.connect(
            lambda text: self._message(f"No command: {text}")
        )

        self.help_title_action = self.ribbonBar().addTitleButton(
            self._icon(QStyle.StandardPixmap.SP_MessageBoxQuestion), "Help"
        )
        self.account_title_action = self.ribbonBar().addTitleButton(
            self._icon(QStyle.StandardPixmap.SP_DirHomeIcon), "Account"
        )
        self.help_title_action.triggered.connect(
            lambda: QMessageBox.information(self, "LqRibbon", "Help")
        )
        self.account_title_action.triggered.connect(
            lambda: QMessageBox.information(self, "LqRibbon", "Account")
        )

    def _configure_search_and_quick_access(self):
        self.search_actions = [
            self.full_screen_action,
            self.mdi_action,
            self.tab_action,
            self.settings_action,
            self.connect_action,
            self.basic_action,
            self.driver_action,
            self.minimize_ribbon_action,
            self.restore_ribbon_action,
            self.add_page_action,
            self.rename_page_action,
            self.move_gallery_action,
            self.toggle_group_action,
            self.office_popup_action,
            self.office_menu_action,
            self.show_customize_action,
        ]
        for action in self.search_actions:
            self.ribbonBar().registerSearchAction(action)
        self.ribbonBar().addQuickAccessAction(self.full_screen_action)
        self.ribbonBar().addQuickAccessAction(self.connect_action)
        self.ribbonBar().addQuickAccessAction(self.minimize_ribbon_action)

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

    def select_preview_page(self, controls=False, gallery=False, shell=False):
        if shell:
            page = self.shell_page
        elif gallery:
            page = self.gallery_page
        elif controls:
            page = self.controls_page
        else:
            page = self.driver_page
        self.ribbonBar().setCurrentPageIndex(self.ribbonBar().pageIndex(page))

    def focus_search_preview(self):
        self.ribbonBar().searchLineEdit().setFocus()
        self.ribbonBar().setSearchText("ba")

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
        control_button.setText("Control Modes")
        control_button.setIcon(self._icon(QStyle.StandardPixmap.SP_FileDialogListView))
        control_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        control_button.setPopupMode(QToolButton.ToolButtonPopupMode.MenuButtonPopup)
        menu = QMenu(control_button)
        menu.addAction("Pulse Mode")
        menu.addAction("Analog Velocity Mode")
        control_button.setMenu(menu)
        group.addWidget(control_button)

    def _add_status_action_button(self, switch_group, action):
        button = QToolButton(switch_group)
        button.setDefaultAction(action)
        switch_group.layout.addWidget(button)

    def _icon(self, standard_pixmap):
        return self.style().standardIcon(standard_pixmap)

    def _message(self, text, timeout=2500):
        self.statusBar().showMessage(text, timeout)
