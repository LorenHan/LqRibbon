"""
LqRibbon style definitions shared by the Python Ribbon widgets.
"""

from enum import IntEnum


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
    def get_ribbon_style(style=RibbonStyle.Office2016Blue, platform_layout=RibbonPlatformLayout.Classic):
        p = LqStyle.palette(style)
        platform_layout = _coerce_platform_layout(platform_layout)
        if platform_layout == RibbonPlatformLayout.MacOS:
            is_dark = _coerce_style(style) == RibbonStyle.Microsoft365Dark
            title_bg = "#202020" if is_dark else "#f7f7f7"
            title_text = p["text"]
            tab_hover = "#363636" if is_dark else "#ececec"
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
                background: transparent;
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
                border-radius: 4px;
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
