"""
GroupView - View group with display-related actions
"""

from PySide6.QtCore import QObject
from PySide6.QtGui import QAction, QIcon


class GroupView(QObject):
    """View group containing display and window management actions"""

    def __init__(self, main_window, ribbon_group, parent=None):
        super().__init__(parent)

        self.main_window = main_window
        self.ribbon_group = ribbon_group
        self.is_fullscreen = False

        # Create Full Screen action
        self.full_screen_act = QAction(QIcon(":/view/pictures/full_screen.svg"), "Full Screen", self)
        self.full_screen_act.setToolTip("Full Screen")
        ribbon_group.add_action(self.full_screen_act, "icon_text")

        # Create MDI Mode action
        self.mdi_mode_act = QAction(QIcon(":/view/pictures/full_screen.svg"), "MDI Mode", self)
        self.mdi_mode_act.setToolTip("MDI Mode")
        ribbon_group.add_action(self.mdi_mode_act, "text_beside")

        # Create Tab Mode action
        self.tab_mode_act = QAction(QIcon(":/view/pictures/full_screen.svg"), "Tab Mode", self)
        self.tab_mode_act.setToolTip("Tab Mode")
        ribbon_group.add_action(self.tab_mode_act, "text_beside")

        # Create Tile Window action
        self.tile_window_act = QAction(QIcon(":/view/pictures/full_screen.svg"), "Tile Window", self)
        self.tile_window_act.setToolTip("Tile Window")
        ribbon_group.add_action(self.tile_window_act, "text_beside")

        # Connect signals and slots
        self.full_screen_act.triggered.connect(self.on_full_screen_triggered)
        self.mdi_mode_act.triggered.connect(self.on_mdi_mode_triggered)
        self.tab_mode_act.triggered.connect(self.on_tab_mode_triggered)
        self.tile_window_act.triggered.connect(self.on_tile_window_triggered)

    def on_full_screen_triggered(self):
        """Handle full screen action triggered"""
        if self.is_fullscreen:
            self.main_window.showNormal()
            self.is_fullscreen = False
            self.main_window.append_display_text("Exited full screen mode")
        else:
            self.main_window.showFullScreen()
            self.is_fullscreen = True
            self.main_window.append_display_text("Entered full screen mode")

    def on_mdi_mode_triggered(self):
        """Handle MDI mode action triggered"""
        self.main_window.append_display_text("Switched to MDI Mode")

    def on_tab_mode_triggered(self):
        """Handle tab mode action triggered"""
        self.main_window.append_display_text("Switched to Tab Mode")

    def on_tile_window_triggered(self):
        """Handle tile window action triggered"""
        self.main_window.append_display_text("Tiled Windows")

    @staticmethod
    def create_group_view(main_window, ribbon_group):
        """Create GroupView instance

        Args:
            main_window: Reference to the main window
            ribbon_group: The ribbon group to add actions to

        Returns:
            GroupView: The created group instance
        """
        return GroupView(main_window, ribbon_group, ribbon_group)
