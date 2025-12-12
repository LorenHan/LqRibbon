"""
GroupVersion - Version group with version-related actions
"""

from PySide6.QtCore import QObject
from PySide6.QtGui import QAction, QIcon


class GroupVersion(QObject):
    """Version group containing version and update actions"""

    def __init__(self, main_window, ribbon_group, parent=None):
        super().__init__(parent)

        self.main_window = main_window
        self.ribbon_group = ribbon_group

        # Create Version action
        self.version_act = QAction(QIcon(":/view/pictures/full_screen.svg"), "Version", self)
        self.version_act.setToolTip("Version")
        ribbon_group.add_action(self.version_act, "icon_text")

        # Create Check Update action
        self.check_update_act = QAction(QIcon(":/view/pictures/full_screen.svg"), "Check Update", self)
        self.check_update_act.setToolTip("Check Update")
        ribbon_group.add_action(self.check_update_act, "icon_text")

        # Connect signals and slots
        self.version_act.triggered.connect(self.on_version_triggered)
        self.check_update_act.triggered.connect(self.on_check_update_triggered)

    def on_version_triggered(self):
        """Handle version action triggered"""
        self.main_window.append_display_text("LqRibbon Version 1.0.0")

    def on_check_update_triggered(self):
        """Handle check update action triggered"""
        self.main_window.append_display_text("Checking for updates... No updates available.")

    @staticmethod
    def create_group_version(main_window, ribbon_group):
        """Create GroupVersion instance

        Args:
            main_window: Reference to the main window
            ribbon_group: The ribbon group to add actions to

        Returns:
            GroupVersion: The created group instance
        """
        return GroupVersion(main_window, ribbon_group, ribbon_group)
