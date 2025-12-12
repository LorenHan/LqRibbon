"""
PageGeneral - General page implementation
"""

from PySide6.QtCore import QObject

from view.groups import GroupView, GroupSystem


class PageGeneral(QObject):
    """General page with View and System groups"""

    def __init__(self, main_window, parent=None):
        super().__init__(parent)

        self.main_window = main_window

        # Create page
        self.page = main_window.ribbon_bar.add_page("General")

        # Create View group
        group_view = self.page.add_group("View")
        GroupView.create_group_view(main_window, group_view)

        # Create System group
        group_system = self.page.add_group("System")
        GroupSystem.create_group_system(main_window, group_system)

    @staticmethod
    def create_page_general(main_window):
        """Create PageGeneral instance

        Args:
            main_window: Reference to the main window

        Returns:
            PageGeneral: The created page instance
        """
        return PageGeneral(main_window, main_window)
