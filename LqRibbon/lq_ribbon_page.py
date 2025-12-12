"""
LqRibbonPage - Ribbon page that contains ribbon groups
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QScrollArea
from PySide6.QtCore import Qt


class LqRibbonPage(QWidget):
    """Ribbon page that contains multiple ribbon groups"""

    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.title = title
        self.groups = []
        self.init_ui()

    def init_ui(self):
        """Initialize the page UI"""
        # Set object name for styling
        self.setObjectName("ribbon_page")

        # Create main layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        # Create scroll area for groups
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)

        # Create container widget for groups
        self.groups_container = QWidget()
        self.groups_layout = QHBoxLayout(self.groups_container)
        self.groups_layout.setContentsMargins(0, 0, 0, 0)
        self.groups_layout.setSpacing(1)
        self.groups_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.scroll_area.setWidget(self.groups_container)
        main_layout.addWidget(self.scroll_area)

    def add_group(self, title):
        """Add a new ribbon group to the page

        Args:
            title: Title of the group

        Returns:
            LqRibbonGroup: The created group
        """
        from .lq_ribbon_group import LqRibbonGroup

        group = LqRibbonGroup(title, self)
        self.groups.append(group)
        self.groups_layout.addWidget(group)

        return group

    def get_group(self, index):
        """Get a group by index

        Args:
            index: Index of the group

        Returns:
            LqRibbonGroup: The group at the given index
        """
        if 0 <= index < len(self.groups):
            return self.groups[index]
        return None

    def get_group_by_title(self, title):
        """Get a group by its title

        Args:
            title: Title of the group

        Returns:
            LqRibbonGroup: The group with the given title
        """
        for group in self.groups:
            if group.title == title:
                return group
        return None

    def remove_group(self, group):
        """Remove a group from the page

        Args:
            group: The group to remove
        """
        if group in self.groups:
            self.groups.remove(group)
            self.groups_layout.removeWidget(group)
            group.deleteLater()

    def clear_groups(self):
        """Remove all groups from the page"""
        for group in self.groups:
            self.groups_layout.removeWidget(group)
            group.deleteLater()
        self.groups.clear()

    def set_title(self, title):
        """Set the page title

        Args:
            title: New title for the page
        """
        self.title = title
        # Update the tab text in parent ribbon bar
        if self.parent():
            parent = self.parent()
            if hasattr(parent, 'setTabText'):
                index = parent.indexOf(self)
                if index >= 0:
                    parent.setTabText(index, title)