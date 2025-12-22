"""
MainWindow - Example application main window
"""

from LqRibbon import LqRibbonWindow

from view.pages import PageGeneral, PageHelp


class MainWindow(LqRibbonWindow):
    """Main window for the example application"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("LqRibbon Example Application")
        self.create_ribbon()

    def create_ribbon(self):
        """Create the ribbon with pages and groups"""
        PageGeneral.create_page_general(self)
        PageHelp.create_page_help(self)

        # Set default page to "General"
        self.ribbon_bar.setCurrentIndex(0)

        # Set initial message
        self.append_display_text("LqRibbon Example Application Started")
        self.append_display_text("Click any action button to see its name here...")
        self.append_display_text("-" * 50)
