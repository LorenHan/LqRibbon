"""
GroupSystem - System group with system-related actions
"""

from PySide6.QtCore import QObject
from PySide6.QtGui import QAction, QIcon


class GroupSystem(QObject):
    """System group containing system and language actions"""

    def __init__(self, main_window, ribbon_group, parent=None):
        super().__init__(parent)

        self.main_window = main_window
        self.ribbon_group = ribbon_group

        # Create Language action
        self.language_act = QAction(QIcon(":/view/pictures/full_screen.svg"), "Language", self)
        self.language_act.setToolTip("Language")
        ribbon_group.add_action(self.language_act, "icon_text")

        # Connect signals and slots
        self.language_act.triggered.connect(self.on_language_triggered)

    def on_language_triggered(self):
        """Handle language action triggered"""
        self.main_window.append_display_text("Language Settings Opened")

    @staticmethod
    def create_group_system(main_window, ribbon_group):
        """Create GroupSystem instance

        Args:
            main_window: Reference to the main window
            ribbon_group: The ribbon group to add actions to

        Returns:
            GroupSystem: The created group instance
        """
        return GroupSystem(main_window, ribbon_group, ribbon_group)
