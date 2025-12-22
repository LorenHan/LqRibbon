"""
GroupHelp - Help group with help-related actions
"""

from PySide6.QtCore import QObject, Qt
from PySide6.QtGui import QAction, QIcon


class GroupHelp(QObject):
    """Help group containing documentation and assistant actions"""

    def __init__(self, main_window, ribbon_group, parent=None):
        super().__init__(parent)

        self.main_window = main_window
        self.ribbon_group = ribbon_group

        # Create Help Document action
        self.help_document_act = ribbon_group.addAction(QIcon(":/view/pictures/full_screen.svg"), "Help Document", "Open Help Documentation")

        # Create Assistant action
        self.assistant_act = ribbon_group.addAction(QIcon(":/view/pictures/full_screen.svg"), "Assistant", "Open Assistant (Ctrl+H)")

        # Connect signals and slots
        self.help_document_act.triggered.connect(self.on_help_document_triggered)
        self.assistant_act.triggered.connect(self.on_assistant_triggered)

    def on_help_document_triggered(self):
        """Handle help document action triggered"""
        self.main_window.append_display_text("Opening Help Documentation...")

    def on_assistant_triggered(self):
        """Handle assistant action triggered"""
        self.main_window.append_display_text("Opening Assistant...")

    @staticmethod
    def create_group_help(main_window, ribbon_group):
        """Create GroupHelp instance

        Args:
            main_window: Reference to the main window
            ribbon_group: The ribbon group to add actions to

        Returns:
            GroupHelp: The created group instance
        """
        return GroupHelp(main_window, ribbon_group, ribbon_group)
