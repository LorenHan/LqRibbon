"""
LqRibbon Style Module - Blue flat style definitions
"""

class LqStyle:
    """Blue flat style for LqRibbon"""

    # Color scheme - matching QtitanRibbon screenshot
    PRIMARY_COLOR = "#2B579A"        # Main blue color
    TAB_SELECTED = "#2B579A"         # Selected tab blue
    TAB_HOVER = "#3A6AB1"            # Hover blue
    RIBBON_BG = "#FFFFFF"            # White ribbon background
    GROUP_BG = "#FFFFFF"             # White group background
    TEXT_COLOR = "#333333"           # Dark text
    GROUP_TITLE_COLOR = "#666666"    # Group title gray
    SEPARATOR_COLOR = "#D8D8D8"      # Light separator

    @staticmethod
    def get_ribbon_style():
        """Get the main ribbon style sheet"""
        return """
        /* Tab Widget */
        QTabWidget::pane {
            background-color: #FFFFFF;
            border: none;
            border-bottom: 1px solid #D8D8D8;
        }

        /* Tab Bar */
        QTabBar {
            background-color: #2B579A;
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
            color: #2B579A;
            font-weight: normal;
            padding-bottom: 7px;
        }

        QTabBar::tab:hover:!selected {
            color: rgba(255, 255, 255, 0.9);
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
        QGroupBox {
            background-color: #FFFFFF;
            border: none;
            border-right: 1px solid #E5E5E5;
            margin: 0px 0px;
            padding: 2px 5px 24px 5px;
            font-size: 11px;
            color: #666666;
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
            color: #666666;
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
            color: #333333;
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
            background-color: #E5F1FB;
            border: 1px solid #9DC7F1;
            border-radius: 0px;
        }

        /* Pressed Effect */
        QToolButton:pressed {
            background-color: #CCE4F7;
            border: 1px solid #6AADE4;
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