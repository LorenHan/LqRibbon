"""
PageHelp - Help page implementation
"""

from PySide6.QtCore import QObject

from view.groups import GroupVersion, GroupHelp


class PageHelp(QObject):
    """Help page with Version and Help groups"""

    def __init__(self, main_window, parent=None):
        super().__init__(parent)

        self.main_window = main_window

        # Create page
        self.page = main_window.ribbon_bar.add_page("Help")

        # Create Version group
        group_version = self.page.add_group("Version")
        GroupVersion.create_group_version(main_window, group_version)

        # Create Help group
        group_help = self.page.add_group("Help")
        GroupHelp.create_group_help(main_window, group_help)

    @staticmethod
    def create_page_help(main_window):
        """Create PageHelp instance

        Args:
            main_window: Reference to the main window

        Returns:
            PageHelp: The created page instance
        """
        return PageHelp(main_window, main_window)
