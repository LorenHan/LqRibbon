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
            padding: 6px 20px;
            margin: 0;
            margin-bottom: -1px;
            border: none;
            font-size: 13px;
            font-weight: normal;
            min-width: 70px;
        }

        QTabBar::tab:selected {
            background-color: #FFFFFF;
            color: #185ABD;
            font-weight: normal;
            padding-bottom: 7px;
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
            padding: 2px 5px 24px 5px;
            font-size: 11px;
            color: #5F6368;
            min-width: 80px;
        }

        QGroupBox:last-child {
            border-right: none;
        }

        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: bottom center;
            left: 0;
            right: 0;
            bottom: 4px;
            padding: 0 5px;
            color: #5F6368;
            font-size: 11px;
            font-weight: normal;
            background-color: transparent;
            min-height: 12px;
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
            padding: 2px 1px 4px 1px;
            margin: 1px;
            min-width: 54px;
            min-height: 58px;
            text-align: center;
        }

        /* Text Beside Icon (Small Button) */
        QToolButton[buttonStyle="1"] {
            padding: 2px 6px;
            margin: 1px;
            min-height: 22px;
            max-height: 24px;
            min-width: 75px;
            text-align: left;
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
            qproperty-iconSize: 24px;
        }

        QToolButton[buttonStyle="1"] {
            qproperty-iconSize: 16px;
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
