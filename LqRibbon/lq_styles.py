"""
LqRibbon Style Module - Blue flat style definitions
"""

class LqStyle:
    """Blue flat style for LqRibbon"""

    # Color scheme aligned with the captured Ribbon baseline
    PRIMARY_COLOR = "#2B579A"        # Main blue color
    TAB_SELECTED = "#124078"         # Selected tab text blue
    TAB_HOVER = "#3A6AB1"            # Hover blue
    RIBBON_BG = "#F3F3F3"            # Ribbon background
    GROUP_BG = "#F3F3F3"             # Group background
    TEXT_COLOR = "#202020"           # Dark text
    GROUP_TITLE_COLOR = "#202020"    # Group title black
    SEPARATOR_COLOR = "#C2C2C2"      # Word-style separator

    @staticmethod
    def get_ribbon_style():
        """Get the main ribbon style sheet"""
        return """
        /* Tab Widget */
        QTabWidget::pane {
            background-color: #F3F3F3;
            border: none;
        }

        /* Tab Bar */
        QTabBar {
            background-color: #2B579A;
            border: none;
        }

        QTabBar::tab {
            background-color: transparent;
            color: rgba(255, 255, 255, 1.0);
            padding: 2px 10px 1px 10px;
            margin: 0;
            border: none;
            font-size: 12px;
            font-weight: normal;
            min-width: 46px;
            min-height: 21px;
        }

        QTabBar::tab:selected {
            background-color: #FFFFFF;
            color: #124078;
            font-weight: normal;
            border-left: 1px solid #C8C8C8;
            border-right: 1px solid #C8C8C8;
            border-top: 1px solid #C8C8C8;
        }

        QTabBar::tab:hover:!selected {
            color: rgba(255, 255, 255, 0.9);
        }

        /* Ribbon Page */
        QWidget#ribbon_page {
            background-color: #F3F3F3;
            border: none;
        }
        """

    @staticmethod
    def get_window_style():
        """Get the main window style sheet"""
        return """
        /* Main Window */
        QMainWindow {
            background-color: #F5F5F5;
        }

        /* Central Widget */
        QWidget {
            font-family: "Segoe UI", "Microsoft YaHei", Arial, sans-serif;
        }

        /* Display Area */
        QTextEdit#display_area {
            background-color: #F5F5F5;
            border: none;
            font-size: 13px;
            font-family: Consolas, Monaco, monospace;
            padding: 10px;
            color: #333333;
        }

        /* Status Bar */
        QStatusBar {
            background-color: #2B579A;
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
        QGroupBox#lqRibbonGroup {
            background-color: transparent;
            border: none;
            margin: 0px;
            padding: 0px;
            font-size: 11px;
            color: #202020;
            min-width: 44px;
        }

        QGroupBox#lqRibbonGroup QLabel#lqRibbonGroupTitle {
            color: #202020;
            font-size: 11px;
            font-weight: normal;
            background-color: transparent;
            padding: 0px 4px 3px 4px;
        }
        """

    @staticmethod
    def get_button_style():
        """Get the ribbon button style sheet"""
        return """
        /* All Ribbon Buttons */
        QToolButton {
            background-color: transparent;
            border: 1px solid transparent;
            border-radius: 1px;
            padding: 1px 2px;
            color: #202020;
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

        /* Hover Effect (Office2016 flat highlight) */
        QToolButton:hover {
            background-color: #DCEBFF;
            border: 1px solid #80A9DC;
            border-radius: 0px;
        }

        /* Pressed Effect */
        QToolButton:pressed {
            background-color: #C5DDFA;
            border: 1px solid #5F95D0;
            border-radius: 0px;
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
