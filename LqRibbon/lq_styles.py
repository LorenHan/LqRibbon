"""
LqRibbon Style Module - Office-style Fluent theme definitions.
"""

class LqStyle:
    """Modern Office-style theme for LqRibbon."""

    # Microsoft 365 / Fluent inspired palette.
    PRIMARY_COLOR = "#185ABD"
    PRIMARY_HOVER = "#2B6FD8"
    PRIMARY_PRESSED = "#0F4AA8"
    RIBBON_BG = "#FFFFFF"
    APP_BG = "#F5F6F8"
    GROUP_BG = "#FFFFFF"
    TEXT_COLOR = "#242424"
    MUTED_TEXT_COLOR = "#616161"
    GROUP_TITLE_COLOR = "#5F6368"
    SEPARATOR_COLOR = "#E1DFDD"
    HOVER_BG = "#F3F8FF"
    HOVER_BORDER = "#8CB7E8"
    PRESSED_BG = "#DDEBFF"
    PRESSED_BORDER = "#5B9BE5"

    # Word-like classic ribbon density.
    RIBBON_HEIGHT = 116
    TAB_BAR_HEIGHT = 30
    TAB_MIN_WIDTH = 64
    GROUP_MIN_WIDTH = 76
    GROUP_MIN_HEIGHT = 88
    PAGE_GROUP_SPACING = 0
    GROUP_LAYOUT_MARGINS = (4, 2, 4, 7)
    GROUP_BUTTON_SPACING = 2
    GROUP_GRID_SPACING = 1
    LARGE_BUTTON_MIN_WIDTH = 58
    LARGE_BUTTON_MIN_HEIGHT = 60
    SMALL_BUTTON_MIN_WIDTH = 76
    SMALL_BUTTON_HEIGHT = 22
    ICON_ONLY_BUTTON_SIZE = 28
    LARGE_ICON_SIZE = 28
    SMALL_ICON_SIZE = 16
    ICON_ONLY_ICON_SIZE = 18
    SIMPLIFIED_RIBBON_HEIGHT = 64
    SIMPLIFIED_GROUP_MIN_HEIGHT = 34
    SIMPLIFIED_GROUP_LAYOUT_MARGINS = (3, 3, 3, 3)
    SIMPLIFIED_BUTTON_MIN_WIDTH = 68
    SIMPLIFIED_BUTTON_HEIGHT = 24
    SIMPLIFIED_ICON_SIZE = 16

    @staticmethod
    def get_ribbon_style():
        """Get the main ribbon style sheet"""
        return """
        /* Tab Widget */
        QTabWidget::pane {
            background-color: #FFFFFF;
            border: none;
            border-bottom: 1px solid #E1DFDD;
        }

        /* Tab Bar */
        QTabBar {
            background-color: #185ABD;
            border: none;
        }

        QTabBar::tab {
            background-color: transparent;
            color: rgba(255, 255, 255, 1.0);
            padding: 5px 18px;
            margin: 0;
            margin-bottom: -1px;
            border: none;
            font-size: 13px;
            font-weight: normal;
            min-width: 64px;
        }

        QTabBar::tab:selected {
            background-color: #FFFFFF;
            color: #185ABD;
            font-weight: normal;
            padding-bottom: 6px;
            border-top-left-radius: 3px;
            border-top-right-radius: 3px;
        }

        QTabBar::tab:hover:!selected {
            background-color: #2B6FD8;
            color: rgba(255, 255, 255, 1.0);
        }

        /* Ribbon Page */
        QWidget#ribbon_page {
            background-color: #FFFFFF;
            border: none;
        }
        """

    @staticmethod
    def get_window_style():
        """Get the main window style sheet"""
        return """
        /* Main Window */
        QMainWindow {
            background-color: #F5F6F8;
        }

        QWidget#lq_ribbon_root {
            background-color: #F5F6F8;
            border: none;
        }

        /* Central Widget */
        QWidget {
            font-family: "Segoe UI", "Microsoft YaHei", Arial, sans-serif;
        }

        /* Frameless Title Bar */
        QWidget#title_bar {
            background-color: #185ABD;
            border: none;
        }

        QWidget#title_bar[active="false"] {
            background-color: #687182;
        }

        QLabel#title_label {
            color: white;
            font-size: 13px;
            font-weight: 500;
            padding-left: 2px;
        }

        /* Display Area */
        QTextEdit#display_area {
            background-color: #F5F6F8;
            border: none;
            font-size: 13px;
            font-family: Consolas, Monaco, monospace;
            padding: 10px;
            color: #242424;
        }

        /* Status Bar */
        QStatusBar {
            background-color: #185ABD;
            color: white;
            border: none;
            min-height: 22px;
            font-size: 12px;
        }

        QStatusBar::item {
            border: none;
        }
        """

    @staticmethod
    def get_group_style():
        """Get the ribbon group style sheet"""
        return """
        /* Ribbon Group */
        QGroupBox {
            background-color: #FFFFFF;
            border: none;
            border-right: 1px solid #E1DFDD;
            margin: 0px 0px;
            padding: 2px 4px 20px 4px;
            font-size: 11px;
            color: #5F6368;
            min-width: 76px;
        }

        QGroupBox:last-child {
            border-right: none;
        }

        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: bottom center;
            left: 0;
            right: 0;
            bottom: 3px;
            padding: 0 4px;
            color: #5F6368;
            font-size: 11px;
            font-weight: normal;
            background-color: transparent;
            min-height: 12px;
        }

        QGroupBox[simplified="true"] {
            padding: 2px 4px 2px 4px;
            min-width: 0px;
        }

        QGroupBox[simplified="true"]::title {
            color: transparent;
            min-height: 0px;
            padding: 0px;
        }
        """

    @staticmethod
    def get_button_style():
        """Get the ribbon button style sheet"""
        return """
        /* All Ribbon Buttons */
        QToolButton {
            background-color: transparent;
            border: none;
            color: #242424;
            font-size: 11px;
            font-family: "Segoe UI", "Microsoft YaHei", Arial, sans-serif;
        }

        /* Icon + Text Under (Large Button) */
        QToolButton[buttonStyle="0"] {
            padding: 2px 3px 3px 3px;
            margin: 0px;
            min-width: 58px;
            min-height: 60px;
            text-align: center;
        }

        /* Text Beside Icon (Small Button) */
        QToolButton[buttonStyle="1"] {
            padding: 2px 5px;
            margin: 0px;
            min-height: 22px;
            max-height: 23px;
            min-width: 76px;
            text-align: left;
        }

        /* Icon Only */
        QToolButton[buttonStyle="2"] {
            padding: 2px;
            margin: 0px;
            min-width: 28px;
            min-height: 28px;
            max-width: 28px;
            max-height: 28px;
        }

        QToolButton[simplified="true"] {
            min-height: 24px;
            max-height: 24px;
            qproperty-iconSize: 16px;
        }

        QToolButton[simplified="true"][buttonStyle="1"] {
            min-width: 68px;
            padding: 2px 6px;
        }

        QToolButton[simplified="true"][buttonStyle="2"] {
            min-width: 28px;
            max-width: 28px;
        }

        /* Hover Effect (Microsoft 365 Fluent highlight) */
        QToolButton:hover {
            background-color: #F3F8FF;
            border: 1px solid #8CB7E8;
            border-radius: 3px;
        }

        /* Pressed Effect */
        QToolButton:pressed {
            background-color: #DDEBFF;
            border: 1px solid #5B9BE5;
            border-radius: 3px;
        }

        /* Icon size for buttons */
        QToolButton {
            qproperty-iconSize: 28px;
        }

        QToolButton[buttonStyle="1"] {
            qproperty-iconSize: 16px;
        }

        QToolButton[buttonStyle="2"] {
            qproperty-iconSize: 18px;
        }
        """

    @staticmethod
    def get_full_style():
        """Get the complete style sheet"""
        styles = [
            LqStyle.get_window_style(),
            LqStyle.get_ribbon_style(),
            LqStyle.get_group_style(),
            LqStyle.get_button_style()
        ]
        return "\n".join(styles)
