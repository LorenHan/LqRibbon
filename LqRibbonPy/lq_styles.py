"""
LqRibbon style definitions shared by the Python Ribbon widgets.
"""

from enum import IntEnum
from pathlib import Path


class RibbonStyle(IntEnum):
    """Named Ribbon styles that mirror the C++ example API."""

    Office2016Blue = 1
    Office2019Colorful = 2
    Microsoft365Light = 3
    Microsoft365Dark = 4


class RibbonPlatformLayout(IntEnum):
    """Platform layout variants independent from color/style choices."""

    Classic = 1
    MacOS = 2


def _coerce_style(style):
    if isinstance(style, RibbonStyle):
        return style
    if isinstance(style, str):
        key = style.strip().lower().replace("-", "").replace("_", "").replace(" ", "")
        aliases = {
            "office2016blue": RibbonStyle.Office2016Blue,
            "blue": RibbonStyle.Office2016Blue,
            "office2019colorful": RibbonStyle.Office2019Colorful,
            "colorful": RibbonStyle.Office2019Colorful,
            "microsoft365light": RibbonStyle.Microsoft365Light,
            "m365light": RibbonStyle.Microsoft365Light,
            "light": RibbonStyle.Microsoft365Light,
            "microsoft365dark": RibbonStyle.Microsoft365Dark,
            "m365dark": RibbonStyle.Microsoft365Dark,
            "dark": RibbonStyle.Microsoft365Dark,
        }
        return aliases.get(key, RibbonStyle.Office2016Blue)
    try:
        return RibbonStyle(int(style))
    except (TypeError, ValueError):
        return RibbonStyle.Office2016Blue


def _coerce_platform_layout(layout):
    if isinstance(layout, RibbonPlatformLayout):
        return layout
    if isinstance(layout, str):
        key = layout.strip().lower().replace("-", "").replace("_", "").replace(" ", "")
        aliases = {
            "classic": RibbonPlatformLayout.Classic,
            "windows": RibbonPlatformLayout.Classic,
            "win": RibbonPlatformLayout.Classic,
            "mac": RibbonPlatformLayout.MacOS,
            "macos": RibbonPlatformLayout.MacOS,
            "darwin": RibbonPlatformLayout.MacOS,
        }
        return aliases.get(key, RibbonPlatformLayout.Classic)
    try:
        return RibbonPlatformLayout(int(layout))
    except (TypeError, ValueError):
        return RibbonPlatformLayout.Classic


_STYLE_PALETTES = {
    RibbonStyle.Office2016Blue: {
        "accent": "#2b579a",
        "caption_bg": "#2b579a",
        "caption_hover": "#386caf",
        "selected_tab_bg": "#ffffff",
        "selected_tab_text": "#124078",
        "ribbon_bg": "#f3f3f3",
        "field_bg": "#ffffff",
        "popup_bg": "#f4f4f4",
        "text": "#202020",
        "border": "#c8c8c8",
        "search_border": "#b7cbe6",
        "focus": "#5f95d0",
        "popup_selection": "#e8f2ff",
        "group_hover": "#8cc8f7",
        "group_pressed": "#c5ddfa",
        "quick_bg": "#2f63a3",
        "quick_border": "#6f9fd0",
        "page_border": "#bdbdbd",
        "window_bg": "#f5f5f5",
        "status_text": "#ffffff",
        "tab_radius": "0px",
        "tab_border": "#c8c8c8",
        "tab_top_border": "transparent",
        "tab_indicator": "transparent",
        "control_border": "#b7cbe6",
        "command_hover_border": "#8cc8f7",
        "command_pressed_border": "#5f95d0",
        "hover_duration_ms": 0,
        "pressed_hold_ms": 0,
    },
    RibbonStyle.Office2019Colorful: {
        "accent": "#185abd",
        "caption_bg": "#185abd",
        "caption_hover": "#2f6fca",
        "selected_tab_bg": "#ffffff",
        "selected_tab_text": "#124078",
        "ribbon_bg": "#f3f2f1",
        "field_bg": "#ffffff",
        "popup_bg": "#f7f7f7",
        "text": "#202020",
        "border": "#c8c8c8",
        "search_border": "#b7cbe6",
        "focus": "#5f95d0",
        "popup_selection": "#e8f2ff",
        "group_hover": "#deecf9",
        "group_pressed": "#c7e0f4",
        "quick_bg": "#2466b1",
        "quick_border": "#8fb9ec",
        "page_border": "#bdbdbd",
        "window_bg": "#f5f5f5",
        "status_text": "#ffffff",
        "tab_radius": "0px",
        "tab_border": "#c8c8c8",
        "tab_top_border": "transparent",
        "tab_indicator": "transparent",
        "control_border": "#b7cbe6",
        "command_hover_border": "#deecf9",
        "command_pressed_border": "#5f95d0",
        "hover_duration_ms": 0,
        "pressed_hold_ms": 0,
    },
    RibbonStyle.Microsoft365Light: {
        "accent": "#0f6cbd",
        "caption_bg": "#f8f8f8",
        "caption_hover": "#e5f1fb",
        "selected_tab_bg": "#ffffff",
        "selected_tab_text": "#0f6cbd",
        "ribbon_bg": "#fbfbfb",
        "field_bg": "#ffffff",
        "popup_bg": "#ffffff",
        "text": "#242424",
        "border": "#d1d1d1",
        "search_border": "#c7c7c7",
        "focus": "#0f6cbd",
        "popup_selection": "#e5f1fb",
        "group_hover": "#e5f1fb",
        "group_pressed": "#cfe4fa",
        "quick_bg": "#ffffff",
        "quick_border": "#e5e5e5",
        "page_border": "#d0cecc",
        "window_bg": "#ffffff",
        "status_text": "#242424",
        "tab_radius": "6px 6px 0px 0px",
        "tab_border": "#e5e5e5",
        "tab_top_border": "transparent",
        "tab_indicator": "#0f6cbd",
        "control_border": "#e5e5e5",
        "command_hover_border": "#e5e5e5",
        "command_pressed_border": "#c7c7c7",
        "hover_duration_ms": 120,
        "pressed_hold_ms": 80,
    },
    RibbonStyle.Microsoft365Dark: {
        "accent": "#60cdff",
        "caption_bg": "#202020",
        "caption_hover": "#3a3a3a",
        "selected_tab_bg": "#2d2d2d",
        "selected_tab_text": "#ffffff",
        "ribbon_bg": "#1f1f1f",
        "field_bg": "#2d2d2d",
        "popup_bg": "#2d2d2d",
        "text": "#f3f2f1",
        "border": "#525252",
        "search_border": "#5f5f5f",
        "focus": "#60cdff",
        "popup_selection": "#3b3a39",
        "group_hover": "#3a3a3a",
        "group_pressed": "#4a4a4a",
        "quick_bg": "#2d2d2d",
        "quick_border": "#3a3a3a",
        "page_border": "#555555",
        "window_bg": "#1f1f1f",
        "status_text": "#f3f2f1",
        "tab_radius": "6px 6px 0px 0px",
        "tab_border": "#3a3a3a",
        "tab_top_border": "transparent",
        "tab_indicator": "#60cdff",
        "control_border": "#3a3a3a",
        "command_hover_border": "#3a3a3a",
        "command_pressed_border": "#5f5f5f",
        "hover_duration_ms": 120,
        "pressed_hold_ms": 80,
    },
}

_STYLE_ASSET_DIR = Path(__file__).resolve().parent / "assets"


def _style_asset_url(file_name):
    return (_STYLE_ASSET_DIR / file_name).as_posix()


def _style_arrow_urls(style):
    style = _coerce_style(style)
    asset_prefixes = {
        RibbonStyle.Office2016Blue: "office2016_blue",
        RibbonStyle.Office2019Colorful: "office2019_blue",
        RibbonStyle.Microsoft365Light: "m365_blue",
        RibbonStyle.Microsoft365Dark: "m365_cyan",
    }
    prefix = asset_prefixes[style]
    return (
        _style_asset_url(f"lq_arrow_down_{prefix}.svg"),
        _style_asset_url(f"lq_arrow_up_{prefix}.svg"),
    )


class LqStyle:
    """Ribbon style sheet factory."""

    @staticmethod
    def coerce_style(style):
        return _coerce_style(style)

    @staticmethod
    def palette(style=RibbonStyle.Office2016Blue):
        return _STYLE_PALETTES[_coerce_style(style)]

    @staticmethod
    def ribbon_style_name(style):
        names = {
            RibbonStyle.Office2016Blue: "Office 2016 Blue",
            RibbonStyle.Office2019Colorful: "Office 2019 Colorful",
            RibbonStyle.Microsoft365Light: "Microsoft 365 Light",
            RibbonStyle.Microsoft365Dark: "Microsoft 365 Dark",
        }
        return names[_coerce_style(style)]

    @staticmethod
    def get_ribbon_control_style(style=RibbonStyle.Office2016Blue):
        """Return scoped styling for ordinary Qt widgets embedded in the Ribbon."""
        p = LqStyle.palette(style)
        style = _coerce_style(style)
        is_dark = style == RibbonStyle.Microsoft365Dark
        input_hover = "#343434" if is_dark else "#f8fbff"
        disabled_bg = "#202020" if is_dark else "#f3f3f3"
        disabled_text = "#888888" if is_dark else "#8a8a8a"
        selected_text = "#000000" if is_dark else "#ffffff"
        button_text = "#000000" if is_dark else "#ffffff"
        check_mark_url = _style_asset_url("lq_checkbox_checked_white.svg")
        radio_dot_url = _style_asset_url("lq_radio_checked_white.svg")
        arrow_down_url, arrow_up_url = _style_arrow_urls(style)
        return f"""
        LqRibbonBar QComboBox,
        LqRibbonBar QLineEdit,
        LqRibbonBar QAbstractSpinBox {{
            min-height: 22px;
            padding: 1px 8px;
            background-color: {p["field_bg"]};
            color: {p["text"]};
            border: 1px solid {p["control_border"]};
            border-radius: 2px;
            selection-background-color: {p["accent"]};
            selection-color: {selected_text};
        }}
        LqRibbonBar QComboBox:hover,
        LqRibbonBar QLineEdit:hover,
        LqRibbonBar QAbstractSpinBox:hover,
        LqRibbonBar QComboBox:focus,
        LqRibbonBar QLineEdit:focus,
        LqRibbonBar QAbstractSpinBox:focus {{
            background-color: {input_hover};
            border-color: {p["focus"]};
        }}
        LqRibbonBar QComboBox:disabled,
        LqRibbonBar QLineEdit:disabled,
        LqRibbonBar QAbstractSpinBox:disabled {{
            background-color: {disabled_bg};
            color: {disabled_text};
            border-color: {p["border"]};
        }}
        LqRibbonBar QComboBox::drop-down {{
            width: 18px;
            subcontrol-origin: padding;
            subcontrol-position: top right;
            border-left: 1px solid {p["control_border"]};
            background: transparent;
        }}
        LqRibbonBar QComboBox::down-arrow {{
            width: 9px;
            height: 6px;
            image: url("{arrow_down_url}");
        }}
        LqRibbonBar QComboBox QAbstractItemView {{
            background-color: {p["popup_bg"]};
            color: {p["text"]};
            border: 1px solid {p["control_border"]};
            outline: 0px;
            selection-background-color: {p["popup_selection"]};
            selection-color: {p["text"]};
        }}
        LqRibbonBar QAbstractSpinBox::up-button,
        LqRibbonBar QAbstractSpinBox::down-button {{
            width: 16px;
            background: transparent;
            border-left: 1px solid {p["control_border"]};
            subcontrol-origin: border;
        }}
        LqRibbonBar QAbstractSpinBox::up-button {{
            subcontrol-position: top right;
        }}
        LqRibbonBar QAbstractSpinBox::down-button {{
            subcontrol-position: bottom right;
        }}
        LqRibbonBar QAbstractSpinBox::up-button:hover,
        LqRibbonBar QAbstractSpinBox::down-button:hover {{
            background: {input_hover};
        }}
        LqRibbonBar QAbstractSpinBox::up-arrow {{
            width: 9px;
            height: 6px;
            image: url("{arrow_up_url}");
        }}
        LqRibbonBar QAbstractSpinBox::down-arrow {{
            width: 9px;
            height: 6px;
            image: url("{arrow_down_url}");
        }}
        LqRibbonBar QPushButton {{
            min-height: 22px;
            padding: 2px 12px;
            color: {button_text};
            background-color: {p["accent"]};
            border: 1px solid {p["accent"]};
            border-radius: 2px;
        }}
        LqRibbonBar QPushButton:hover {{
            background-color: {p["focus"]};
            border-color: {p["focus"]};
        }}
        LqRibbonBar QPushButton:disabled {{
            background-color: {disabled_bg};
            border-color: {p["border"]};
            color: {disabled_text};
        }}
        LqRibbonBar QCheckBox,
        LqRibbonBar QRadioButton {{
            color: {p["text"]};
            spacing: 5px;
        }}
        LqRibbonBar QCheckBox::indicator,
        LqRibbonBar QRadioButton::indicator {{
            width: 13px;
            height: 13px;
            background: {p["field_bg"]};
            border: 1px solid {p["control_border"]};
        }}
        LqRibbonBar QCheckBox::indicator {{
            border-radius: 2px;
        }}
        LqRibbonBar QRadioButton::indicator {{
            border-radius: 7px;
        }}
        LqRibbonBar QCheckBox::indicator:checked {{
            background: {p["accent"]};
            border-color: {p["accent"]};
            image: url("{check_mark_url}");
        }}
        LqRibbonBar QRadioButton::indicator:checked {{
            background: {p["accent"]};
            border-color: {p["accent"]};
            image: url("{radio_dot_url}");
        }}
        LqRibbonBar QSlider::groove:horizontal {{
            height: 4px;
            background: {p["control_border"]};
            border-radius: 2px;
        }}
        LqRibbonBar QSlider::sub-page:horizontal {{
            background: {p["accent"]};
            border-radius: 2px;
        }}
        LqRibbonBar QSlider::handle:horizontal {{
            width: 12px;
            margin: -5px 0px;
            border-radius: 6px;
            background: {p["field_bg"]};
            border: 1px solid {p["focus"]};
        }}
        LqRibbonBar QProgressBar {{
            min-height: 16px;
            background: {p["field_bg"]};
            color: {button_text};
            border: 1px solid {p["control_border"]};
            border-radius: 2px;
            text-align: center;
        }}
        LqRibbonBar QProgressBar::chunk {{
            background-color: {p["accent"]};
            border-radius: 2px;
        }}
        """

    @staticmethod
    def get_ribbon_style(style=RibbonStyle.Office2016Blue, platform_layout=RibbonPlatformLayout.Classic):
        p = LqStyle.palette(style)
        style = _coerce_style(style)
        platform_layout = _coerce_platform_layout(platform_layout)
        control_style = LqStyle.get_ribbon_control_style(style)
        if platform_layout == RibbonPlatformLayout.MacOS:
            is_dark = style == RibbonStyle.Microsoft365Dark
            is_legacy_office = style in (
                RibbonStyle.Office2016Blue,
                RibbonStyle.Office2019Colorful,
            )
            title_bg = (
                p["caption_bg"]
                if is_legacy_office
                else "#202020"
                if is_dark
                else "#f7f7f7"
            )
            title_text = p["status_text"] if is_legacy_office else p["text"]
            selected_tab_bg = p["selected_tab_bg"] if is_legacy_office else "transparent"
            tab_hover = (
                p["caption_hover"]
                if is_legacy_office
                else "#363636"
                if is_dark
                else "#ececec"
            )
            tab_hover_radius = p["tab_radius"] if is_legacy_office else "4px"
            return f"""
            LqRibbonBar, QTabWidget#lqRibbonBar {{
                background: {p["ribbon_bg"]};
                border: none;
            }}
            QTabWidget#lqRibbonBar::pane {{
                background: {p["ribbon_bg"]};
                border: none;
                border-bottom-left-radius: 0px;
                border-bottom-right-radius: 0px;
            }}
            QTabBar#lqRibbonTabBar {{
                background: {title_bg};
                border: none;
            }}
            QTabBar#lqRibbonTabBar::tab {{
                min-width: 48px;
                min-height: 25px;
                padding: 3px 9px 2px 9px;
                color: {title_text};
                background: transparent;
                border: none;
                font-size: 12px;
            }}
            QTabBar#lqRibbonTabBar::tab:selected {{
                background: {selected_tab_bg};
                color: {p["selected_tab_text"]};
                border-left: none;
                border-right: none;
                border-top: none;
                border-bottom: 2px solid {p["accent"]};
                border-radius: 0px;
                font-weight: 600;
            }}
            QTabBar#lqRibbonTabBar::tab:hover:!selected {{
                background: {tab_hover};
                border-radius: {tab_hover_radius};
            }}
            QLineEdit#lqRibbonSearchEdit {{
                min-height: 22px;
                padding: 0px 24px 0px 10px;
                border: 1px solid {p["control_border"]};
                border-radius: 12px;
                background: {p["field_bg"]};
                color: {p["text"]};
                selection-background-color: {p["accent"]};
            }}
            QLineEdit#lqRibbonSearchEdit:focus {{
                border-color: {p["focus"]};
            }}
            QToolBar#lqRibbonTitleButtonBar {{
                background: transparent;
                border: none;
                spacing: 2px;
            }}
            QStackedWidget#lqRibbonCommandArea {{
                border: none;
                border-radius: 0px;
            }}
            QWidget#ribbon_page {{
                background-color: {p["ribbon_bg"]};
                border: none;
            }}
            {control_style}
            """
        return f"""
        LqRibbonBar, QTabWidget#lqRibbonBar {{
            background: {p["ribbon_bg"]};
            border: none;
        }}
        QTabWidget#lqRibbonBar::pane {{
            background: {p["ribbon_bg"]};
            border: none;
            border-bottom-left-radius: 8px;
            border-bottom-right-radius: 8px;
        }}
        QTabBar#lqRibbonTabBar {{
            background: transparent;
            border: none;
        }}
        QTabBar#lqRibbonTabBar::tab {{
            min-width: 46px;
            min-height: 21px;
            padding: 2px 10px 1px 10px;
            color: {p["status_text"]};
            background: transparent;
            border: none;
            font-size: 12px;
        }}
        QTabBar#lqRibbonTabBar::tab:selected {{
            background: {p["selected_tab_bg"]};
            color: {p["selected_tab_text"]};
            border-left: 1px solid {p["tab_border"]};
            border-right: 1px solid {p["tab_border"]};
            border-top: 1px solid {p["tab_top_border"]};
            border-bottom: 2px solid {p["tab_indicator"]};
            border-radius: {p["tab_radius"]};
        }}
        QTabBar#lqRibbonTabBar::tab:hover:!selected {{
            background: {p["caption_hover"]};
            border-radius: {p["tab_radius"]};
        }}
        QLineEdit#lqRibbonSearchEdit {{
            min-height: 18px;
            padding: 0px 22px 0px 6px;
            border: 1px solid {p["control_border"]};
            border-radius: 1px;
            background: {p["field_bg"]};
            color: {p["text"]};
            selection-background-color: {p["accent"]};
        }}
        QLineEdit#lqRibbonSearchEdit:focus {{
            border-color: {p["focus"]};
        }}
        QStackedWidget#lqRibbonCommandArea {{
            border: none;
            border-bottom-left-radius: 8px;
            border-bottom-right-radius: 8px;
        }}
        QWidget#ribbon_page {{
            background-color: {p["ribbon_bg"]};
            border: none;
        }}
        {control_style}
        """

    @staticmethod
    def get_window_style(style=RibbonStyle.Office2016Blue, platform_layout=RibbonPlatformLayout.Classic):
        p = LqStyle.palette(style)
        platform_layout = _coerce_platform_layout(platform_layout)
        mac_layout = platform_layout == RibbonPlatformLayout.MacOS
        status_bg = "#f6f6f6" if mac_layout else p["caption_bg"]
        status_text = "#5f5f5f" if mac_layout else p["status_text"]
        display_bg = "#ececec" if mac_layout else p["window_bg"]
        font_family = (
            '"SF Pro Text", ".AppleSystemUIFont", "Segoe UI", "Microsoft YaHei", Arial, sans-serif'
            if mac_layout
            else '"Segoe UI", "Microsoft YaHei", Arial, sans-serif'
        )
        return f"""
        QMainWindow {{
            background-color: {display_bg};
        }}
        QWidget {{
            font-family: {font_family};
        }}
        QTextEdit#display_area {{
            background-color: {display_bg};
            border: none;
            font-size: 13px;
            font-family: Consolas, Monaco, monospace;
            padding: 10px;
            color: {p["text"]};
        }}
        QStatusBar {{
            background-color: {status_bg};
            color: {status_text};
            border: none;
            min-height: 22px;
            font-size: 12px;
        }}
        QStatusBar::item {{
            border: none;
        }}
        QStatusBar QLabel {{
            color: {status_text};
            background: transparent;
        }}
        QStatusBar QToolButton {{
            min-width: 22px;
            min-height: 20px;
            padding: 1px 5px;
            color: {status_text};
            background: transparent;
            border: 1px solid transparent;
            border-radius: 3px;
        }}
        QStatusBar QToolButton:hover,
        QStatusBar QToolButton:checked {{
            background-color: {p["field_bg"]};
            border-color: {p["control_border"]};
        }}
        QStatusBar QSlider::groove:horizontal {{
            height: 4px;
            background: {p["border"]};
            border-radius: 2px;
        }}
        QStatusBar QSlider::sub-page:horizontal {{
            background: {p["accent"]};
            border-radius: 2px;
        }}
        QStatusBar QSlider::handle:horizontal {{
            width: 12px;
            margin: -5px 0px;
            border-radius: 6px;
            background: {p["field_bg"]};
            border: 1px solid {p["control_border"]};
        }}
        QStatusBar QProgressBar {{
            background: {p["field_bg"]};
            color: {status_text};
            border: 1px solid {p["control_border"]};
            border-radius: 2px;
            text-align: center;
        }}
        QStatusBar QProgressBar::chunk {{
            background-color: {p["accent"]};
            border-radius: 2px;
        }}
        """

    @staticmethod
    def get_common_control_style(
        style=RibbonStyle.Office2016Blue,
        root_object_name="lqRibbonDemoSurface",
    ):
        """Return a scoped stylesheet for host-app controls below the Ribbon."""
        p = LqStyle.palette(style)
        style = _coerce_style(style)
        is_dark = style == RibbonStyle.Microsoft365Dark
        surface_bg = "#262626" if is_dark else "#ffffff"
        panel_bg = "#2b2b2b" if is_dark else "#fafafa"
        panel_alt_bg = "#242424" if is_dark else "#f5f5f5"
        muted_text = "#c8c8c8" if is_dark else "#616161"
        input_bg = p["field_bg"]
        input_hover = "#343434" if is_dark else "#f8fbff"
        disabled_bg = "#202020" if is_dark else "#f3f3f3"
        disabled_text = "#888888" if is_dark else "#8a8a8a"
        selected_text = "#000000" if is_dark else "#ffffff"
        progress_text = "#000000" if is_dark else "#ffffff"
        accent_soft = "#12384a" if is_dark else "#e5f1fb"
        row_alt = "#292929" if is_dark else "#f8f8f8"
        primary_bg = "#0f6cbd" if is_dark else p["accent"]
        primary_hover = "#115ea3" if is_dark else p["focus"]
        primary_pressed = "#0f548c" if is_dark else p["caption_bg"]
        check_mark_url = _style_asset_url("lq_checkbox_checked_white.svg")
        radio_dot_url = _style_asset_url("lq_radio_checked_white.svg")
        arrow_down_url, arrow_up_url = _style_arrow_urls(style)
        root = root_object_name.replace('"', "").replace("'", "")
        return f"""
        QWidget#{root} {{
            background-color: {p["window_bg"]};
            color: {p["text"]};
            font-family: "Segoe UI", "Microsoft YaHei", Arial, sans-serif;
            font-size: 12px;
        }}
        QWidget#{root} QLabel {{
            color: {p["text"]};
            background: transparent;
        }}
        QWidget#{root} QLabel#demoSurfaceTitle {{
            color: {p["text"]};
            font-size: 18px;
            font-weight: 600;
        }}
        QWidget#{root} QLabel#demoSurfaceSubtitle,
        QWidget#{root} QLabel#demoFieldHint {{
            color: {muted_text};
            font-size: 12px;
        }}
        QWidget#{root} QLabel#demoThemeBadge {{
            color: {p["text"]};
            background: {accent_soft};
            border: 1px solid {p["control_border"]};
            border-radius: 6px;
            padding: 4px 10px;
            font-weight: 600;
        }}
        QWidget#{root} QFrame#demoControlPanel,
        QWidget#{root} QFrame#demoTablePanel,
        QWidget#{root} QFrame#demoPickerPanel,
        QWidget#{root} QFrame#demoOverridePanel {{
            background-color: {surface_bg};
            border: 1px solid {p["control_border"]};
            border-radius: 6px;
        }}
        QWidget#{root} QLabel#demoSectionTitle {{
            color: {p["text"]};
            font-size: 13px;
            font-weight: 600;
        }}
        QWidget#{root} QComboBox,
        QWidget#{root} QLineEdit,
        QWidget#{root} QDateEdit,
        QWidget#{root} QTimeEdit,
        QWidget#{root} QDateTimeEdit,
        QWidget#{root} QSpinBox,
        QWidget#{root} QDoubleSpinBox,
        QWidget#{root} QPlainTextEdit {{
            background-color: {input_bg};
            color: {p["text"]};
            border: 1px solid {p["control_border"]};
            border-radius: 4px;
            selection-background-color: {p["accent"]};
            selection-color: {selected_text};
        }}
        QWidget#{root} QComboBox,
        QWidget#{root} QLineEdit,
        QWidget#{root} QDateEdit,
        QWidget#{root} QTimeEdit,
        QWidget#{root} QDateTimeEdit,
        QWidget#{root} QSpinBox,
        QWidget#{root} QDoubleSpinBox {{
            min-height: 28px;
            padding: 2px 8px;
        }}
        QWidget#{root} QPlainTextEdit {{
            padding: 8px;
        }}
        QWidget#{root} QComboBox:hover,
        QWidget#{root} QLineEdit:hover,
        QWidget#{root} QDateEdit:hover,
        QWidget#{root} QTimeEdit:hover,
        QWidget#{root} QDateTimeEdit:hover,
        QWidget#{root} QSpinBox:hover,
        QWidget#{root} QDoubleSpinBox:hover,
        QWidget#{root} QPlainTextEdit:hover {{
            background-color: {input_hover};
            border-color: {p["focus"]};
        }}
        QWidget#{root} QComboBox:focus,
        QWidget#{root} QLineEdit:focus,
        QWidget#{root} QDateEdit:focus,
        QWidget#{root} QTimeEdit:focus,
        QWidget#{root} QDateTimeEdit:focus,
        QWidget#{root} QSpinBox:focus,
        QWidget#{root} QDoubleSpinBox:focus,
        QWidget#{root} QPlainTextEdit:focus {{
            border-color: {p["focus"]};
        }}
        QWidget#{root} QComboBox:disabled,
        QWidget#{root} QLineEdit:disabled,
        QWidget#{root} QDateEdit:disabled,
        QWidget#{root} QTimeEdit:disabled,
        QWidget#{root} QDateTimeEdit:disabled,
        QWidget#{root} QSpinBox:disabled,
        QWidget#{root} QDoubleSpinBox:disabled,
        QWidget#{root} QPlainTextEdit:disabled {{
            background-color: {disabled_bg};
            color: {disabled_text};
            border-color: {p["border"]};
        }}
        QWidget#{root} QComboBox QAbstractItemView {{
            background-color: {input_bg};
            color: {p["text"]};
            border: 1px solid {p["control_border"]};
            outline: 0px;
            selection-background-color: {p["accent"]};
            selection-color: {selected_text};
        }}
        QWidget#{root} QComboBox::drop-down {{
            width: 20px;
            subcontrol-origin: padding;
            subcontrol-position: top right;
            border-left: 1px solid {p["control_border"]};
            background: transparent;
        }}
        QWidget#{root} QComboBox::down-arrow {{
            width: 9px;
            height: 6px;
            image: url("{arrow_down_url}");
        }}
        QWidget#{root} QAbstractSpinBox::up-button,
        QWidget#{root} QAbstractSpinBox::down-button {{
            width: 18px;
            background: transparent;
            border-left: 1px solid {p["control_border"]};
            subcontrol-origin: border;
        }}
        QWidget#{root} QAbstractSpinBox::up-button {{
            subcontrol-position: top right;
        }}
        QWidget#{root} QAbstractSpinBox::down-button {{
            subcontrol-position: bottom right;
        }}
        QWidget#{root} QAbstractSpinBox::up-button:hover,
        QWidget#{root} QAbstractSpinBox::down-button:hover {{
            background: {input_hover};
        }}
        QWidget#{root} QAbstractSpinBox::up-arrow {{
            width: 9px;
            height: 6px;
            image: url("{arrow_up_url}");
        }}
        QWidget#{root} QAbstractSpinBox::down-arrow {{
            width: 9px;
            height: 6px;
            image: url("{arrow_down_url}");
        }}
        QWidget#{root} QToolButton {{
            min-height: 28px;
            padding: 3px 10px;
            color: {p["text"]};
            background-color: {input_bg};
            border: 1px solid {p["control_border"]};
            border-radius: 4px;
        }}
        QWidget#{root} QToolButton:hover,
        QWidget#{root} QToolButton:checked {{
            background-color: {input_hover};
            border-color: {p["focus"]};
        }}
        QWidget#{root} QPushButton {{
            min-height: 30px;
            padding: 4px 14px;
            color: #ffffff;
            background-color: {primary_bg};
            border: 1px solid {primary_bg};
            border-radius: 4px;
            font-weight: 600;
        }}
        QWidget#{root} QPushButton:hover {{
            background-color: {primary_hover};
            border-color: {primary_hover};
            color: #ffffff;
        }}
        QWidget#{root} QPushButton:pressed {{
            background-color: {primary_pressed};
            border-color: {primary_pressed};
            color: #ffffff;
        }}
        QWidget#{root} QCheckBox,
        QWidget#{root} QRadioButton {{
            color: {p["text"]};
            spacing: 8px;
        }}
        QWidget#{root} QCheckBox::indicator,
        QWidget#{root} QRadioButton::indicator {{
            width: 15px;
            height: 15px;
            border: 1px solid {p["control_border"]};
            background: {input_bg};
        }}
        QWidget#{root} QCheckBox::indicator {{
            border-radius: 3px;
        }}
        QWidget#{root} QRadioButton::indicator {{
            border-radius: 8px;
        }}
        QWidget#{root} QCheckBox::indicator:checked {{
            background: {primary_bg};
            border-color: {primary_bg};
            image: url("{check_mark_url}");
        }}
        QWidget#{root} QRadioButton::indicator:checked {{
            background: {primary_bg};
            border-color: {primary_bg};
            image: url("{radio_dot_url}");
        }}
        QWidget#{root} QSlider::groove:horizontal {{
            height: 4px;
            background: {p["control_border"]};
            border-radius: 2px;
        }}
        QWidget#{root} QSlider::sub-page:horizontal {{
            background: {p["accent"]};
            border-radius: 2px;
        }}
        QWidget#{root} QSlider::handle:horizontal {{
            width: 16px;
            margin: -6px 0px;
            border-radius: 8px;
            background: {p["field_bg"]};
            border: 2px solid {p["accent"]};
        }}
        QWidget#{root} QProgressBar {{
            min-height: 18px;
            background: {input_bg};
            color: {progress_text};
            border: 1px solid {p["control_border"]};
            border-radius: 4px;
            text-align: center;
        }}
        QWidget#{root} QProgressBar::chunk {{
            background-color: {p["accent"]};
            border-radius: 3px;
        }}
        QWidget#{root} QTableWidget,
        QWidget#{root} QListWidget,
        QWidget#{root} QTreeWidget {{
            background-color: {input_bg};
            alternate-background-color: {row_alt};
            color: {p["text"]};
            border: 1px solid {p["control_border"]};
            border-radius: 4px;
            gridline-color: {p["border"]};
            selection-background-color: {p["accent"]};
            selection-color: {selected_text};
        }}
        QWidget#{root} QTableWidget::item,
        QWidget#{root} QListWidget::item,
        QWidget#{root} QTreeWidget::item {{
            padding: 5px 7px;
            border: none;
        }}
        QWidget#{root} QTableWidget::item:selected,
        QWidget#{root} QListWidget::item:selected,
        QWidget#{root} QTreeWidget::item:selected {{
            background: {p["accent"]};
            color: {selected_text};
        }}
        QWidget#{root} QHeaderView::section {{
            background-color: {panel_alt_bg};
            color: {p["text"]};
            padding: 6px 7px;
            border: none;
            border-right: 1px solid {p["border"]};
            border-bottom: 1px solid {p["border"]};
            font-weight: 600;
        }}
        QWidget#{root} QTabWidget::pane {{
            background: {input_bg};
            border: 1px solid {p["control_border"]};
            border-radius: 4px;
            top: -1px;
        }}
        QWidget#{root} QTabBar::tab {{
            min-height: 26px;
            min-width: 78px;
            padding: 4px 10px;
            color: {p["text"]};
            background: {panel_alt_bg};
            border: 1px solid {p["control_border"]};
            border-bottom: none;
        }}
        QWidget#{root} QTabBar::tab:selected {{
            background: {input_bg};
            color: {p["text"]};
            border-top: 2px solid {p["accent"]};
        }}
        QWidget#{root} QScrollBar:vertical,
        QWidget#{root} QScrollBar:horizontal {{
            background: {panel_bg};
            border: none;
            width: 12px;
            height: 12px;
        }}
        QWidget#{root} QScrollBar::handle:vertical,
        QWidget#{root} QScrollBar::handle:horizontal {{
            background: {p["border"]};
            border-radius: 6px;
            min-height: 24px;
            min-width: 24px;
        }}
        QWidget#{root} QScrollBar::handle:vertical:hover,
        QWidget#{root} QScrollBar::handle:horizontal:hover {{
            background: {p["focus"]};
        }}
        QWidget#{root} QScrollBar::add-line,
        QWidget#{root} QScrollBar::sub-line,
        QWidget#{root} QScrollBar::add-page,
        QWidget#{root} QScrollBar::sub-page {{
            background: transparent;
            border: none;
        }}
        """

    @staticmethod
    def get_group_style(style=RibbonStyle.Office2016Blue):
        p = LqStyle.palette(style)
        return f"""
        QGroupBox#lqRibbonGroup {{
            background-color: transparent;
            border: none;
            margin: 0px;
            padding: 0px;
            font-size: 11px;
            color: {p["text"]};
            min-width: 44px;
        }}
        QGroupBox#lqRibbonGroup QLabel#lqRibbonGroupTitle {{
            color: {p["text"]};
            font-size: 11px;
            font-weight: normal;
            background-color: transparent;
            padding: 0px 4px 3px 4px;
        }}
        """

    @staticmethod
    def get_button_style(style=RibbonStyle.Office2016Blue):
        p = LqStyle.palette(style)
        return f"""
        QToolButton {{
            background-color: transparent;
            border: 1px solid transparent;
            border-radius: 1px;
            padding: 1px 2px;
            color: {p["text"]};
            font-size: 11px;
            font-family: "Segoe UI", "Microsoft YaHei", Arial, sans-serif;
            qproperty-iconSize: 24px;
        }}
        QToolButton[buttonStyle="0"] {{
            padding: 2px 1px 4px 1px;
            margin: 1px;
            min-width: 54px;
            min-height: 58px;
            text-align: center;
        }}
        QToolButton[buttonStyle="1"] {{
            padding: 2px 6px;
            margin: 1px;
            min-height: 22px;
            max-height: 24px;
            min-width: 75px;
            text-align: left;
            qproperty-iconSize: 16px;
        }}
        QToolButton:hover {{
            background-color: {p["group_hover"]};
            border-color: {p["command_hover_border"]};
            border-radius: 0px;
        }}
        QToolButton:pressed {{
            background-color: {p["group_pressed"]};
            border-color: {p["command_pressed_border"]};
            border-radius: 0px;
        }}
        QMenu::item:selected {{
            background-color: {p["group_hover"]};
            color: {p["text"]};
        }}
        """

    @staticmethod
    def get_full_style(style=RibbonStyle.Office2016Blue, platform_layout=RibbonPlatformLayout.Classic):
        return "\n".join(
            [
                LqStyle.get_window_style(style, platform_layout),
                LqStyle.get_ribbon_style(style, platform_layout),
                LqStyle.get_group_style(style),
                LqStyle.get_button_style(style),
            ]
        )
