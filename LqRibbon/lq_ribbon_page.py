"""
LqRibbonPage - Ribbon page that contains ribbon groups
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QScrollArea
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QColor, QIcon
from .lq_ribbon_extras import CallableString, CallableList, ContextColor


class LqRibbonPage(QWidget):
    """Ribbon page that contains multiple ribbon groups"""

    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.title = CallableString(title)
        self.groups = CallableList()
        self._default_action = QAction(title, self)
        self._context_color = QColor()
        self._context_title = ""
        self._context_group_name = ""
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
        self.addGroup(group)

        return group

    def addGroup(self, *args):
        """Qtitan/C++ compatible group add overload."""
        from .lq_ribbon_group import LqRibbonGroup

        if len(args) == 1 and isinstance(args[0], LqRibbonGroup):
            group = args[0]
            if group in self.groups:
                return group
            self.groups.append(group)
            group.setParent(self.groups_container)
            self.groups_layout.addWidget(group)
            return group
        if len(args) == 1:
            return self.add_group(args[0])
        if len(args) == 2:
            icon, title = args
            group = self.add_group(title)
            group.setIcon(icon if isinstance(icon, QIcon) else QIcon(icon))
            return group
        return None

    def insertGroup(self, index, *args):
        """Insert a group or create one at index."""
        from .lq_ribbon_group import LqRibbonGroup

        if len(args) == 1 and isinstance(args[0], LqRibbonGroup):
            group = args[0]
        elif len(args) == 1:
            group = LqRibbonGroup(args[0], self)
        elif len(args) == 2:
            icon, title = args
            group = LqRibbonGroup(title, self)
            group.setIcon(icon if isinstance(icon, QIcon) else QIcon(icon))
        else:
            return None
        if group in self.groups:
            self.groups.remove(group)
            self.groups_layout.removeWidget(group)
        if index < 0 or index > len(self.groups):
            index = len(self.groups)
        self.groups.insert(index, group)
        group.setParent(self.groups_container)
        self.groups_layout.insertWidget(index, group)
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

    def group(self, index):
        return self.get_group(index)

    def groupCount(self):
        return len(self.groups)

    def groupIndex(self, group):
        return self.groups.index(group) if group in self.groups else -1

    def defaultAction(self):
        return self._default_action

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

    def removeGroup(self, group):
        self.remove_group(group)

    def removeGroupByIndex(self, index):
        group = self.get_group(index)
        if group:
            self.remove_group(group)

    def detachGroup(self, group):
        if group in self.groups:
            self.groups.remove(group)
            self.groups_layout.removeWidget(group)
            group.setParent(None)

    def detachGroupByIndex(self, index):
        group = self.get_group(index)
        if group:
            self.detachGroup(group)

    def clear_groups(self):
        """Remove all groups from the page"""
        for group in self.groups:
            self.groups_layout.removeWidget(group)
            group.deleteLater()
        self.groups.clear()

    def clearGroups(self):
        self.clear_groups()

    def set_title(self, title):
        """Set the page title

        Args:
            title: New title for the page
        """
        self.title = CallableString(title)
        self._default_action.setText(title)
        # Update the tab text in parent ribbon bar
        if self.parent():
            parent = self.parent()
            if hasattr(parent, 'setTabText'):
                index = parent.indexOf(self)
                if index >= 0:
                    parent.setTabText(index, title)

    def setTitle(self, title):
        self.set_title(title)

    def ribbonBar(self):
        parent = self.parent()
        return parent if parent and hasattr(parent, "pageIndex") else None

    def contextColor(self):
        return self._context_color

    def contextTitle(self):
        return self._context_title

    def contextGroupName(self):
        return self._context_group_name

    def setContextColor(self, color):
        if isinstance(color, QColor):
            self._context_color = color
        else:
            mapping = {
                ContextColor.ContextColorBlue: QColor("#2b579a"),
                ContextColor.ContextColorYellow: QColor("#f2c811"),
                ContextColor.ContextColorGreen: QColor("#107c10"),
                ContextColor.ContextColorRed: QColor("#d13438"),
                ContextColor.ContextColorPurple: QColor("#5c2d91"),
                ContextColor.ContextColorCyan: QColor("#008575"),
                ContextColor.ContextColorOrange: QColor("#ca5010"),
            }
            self._context_color = mapping.get(color, QColor())

    def setContextTitle(self, title):
        self._context_title = title

    def setContextGroupName(self, group_name):
        self._context_group_name = group_name

    def updateLayout(self):
        self.updateGeometry()


RibbonPage = LqRibbonPage
