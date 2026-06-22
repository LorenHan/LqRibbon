"""
LqRibbonPage - Ribbon page that contains ribbon groups
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QScrollArea
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction, QColor, QIcon, QPainter, QPainterPath, QPalette
from .lq_ribbon_extras import CallableString, CallableList, ContextColor


RIBBON_COMMAND_FRAME_LINE_WIDTH = 2
RIBBON_COMMAND_FRAME_CORNER_RADIUS = 8


class _RibbonGroupsContainer(QWidget):
    """Content widget that paints Word-style group separators."""

    def __init__(self, page):
        super().__init__(page)
        self._page = page

    def paintEvent(self, event):
        super().paintEvent(event)

        painter = QPainter(self)
        top = 5
        bottom = max(top, self.height() - 4)
        spacing = max(1, self._page.groups_layout.spacing() // 2)
        for group in self._page.groups:
            if not group or not group.isVisible():
                continue
            x = group.geometry().right() + spacing
            painter.setPen(QColor("#c2c2c2"))
            painter.drawLine(x, top, x, bottom)
            painter.setPen(QColor("#f4f4f4"))
            painter.drawLine(x + 1, top, x + 1, bottom)


class LqRibbonPage(QWidget):
    """Ribbon page that contains multiple ribbon groups"""

    titleChanged = Signal(str)
    activated = Signal()
    activating = Signal(object)

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
        main_layout.setContentsMargins(
            RIBBON_COMMAND_FRAME_LINE_WIDTH,
            0,
            RIBBON_COMMAND_FRAME_LINE_WIDTH,
            RIBBON_COMMAND_FRAME_LINE_WIDTH,
        )
        main_layout.setSpacing(0)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        # Create scroll area for groups
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)
        self.scroll_area.setAutoFillBackground(True)

        # Create container widget for groups
        self.groups_container = _RibbonGroupsContainer(self)
        self.groups_container.setAutoFillBackground(True)
        self.groups_layout = QHBoxLayout(self.groups_container)
        self.groups_layout.setContentsMargins(0, 0, 0, 0)
        self.groups_layout.setSpacing(4)
        self.groups_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.scroll_area.setWidget(self.groups_container)
        main_layout.addWidget(self.scroll_area)

    def _apply_surface_palette(self, background_color):
        for widget in (self, self.scroll_area, self.scroll_area.viewport(), self.groups_container):
            widget.setAutoFillBackground(True)
            palette = widget.palette()
            palette.setColor(QPalette.ColorRole.Window, background_color)
            palette.setColor(QPalette.ColorRole.Base, background_color)
            widget.setPalette(palette)

    def paintEvent(self, event):
        super().paintEvent(event)

        from .lq_styles import LqStyle, RibbonStyle

        ribbon_bar = self.ribbonBar()
        style = (
            ribbon_bar.ribbonStyle()
            if ribbon_bar and hasattr(ribbon_bar, "ribbonStyle")
            else RibbonStyle.Office2016Blue
        )
        palette = LqStyle.palette(style)
        frame_color = QColor(palette["page_border"])
        if not frame_color.isValid() or self.width() <= 1 or self.height() <= 1:
            return

        background_color = QColor(palette["ribbon_bg"])
        self._apply_surface_palette(background_color)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        line_width = RIBBON_COMMAND_FRAME_LINE_WIDTH
        window = self.window()
        radius_px = 0 if window and window.isMaximized() else RIBBON_COMMAND_FRAME_CORNER_RADIUS
        radius = min(float(radius_px), self.width() / 2.0, self.height() / 2.0)
        outer_color = (
            self.parentWidget().palette().color(QPalette.ColorRole.Window)
            if self.parentWidget()
            else QColor(Qt.GlobalColor.transparent)
        )
        surface_path = QPainterPath()
        surface_path.moveTo(0.0, 0.0)
        surface_path.lineTo(float(self.width()), 0.0)
        surface_path.lineTo(float(self.width()), float(self.height()) - radius)
        surface_path.quadTo(
            float(self.width()),
            float(self.height()),
            float(self.width()) - radius,
            float(self.height()),
        )
        surface_path.lineTo(radius, float(self.height()))
        surface_path.quadTo(0.0, float(self.height()), 0.0, float(self.height()) - radius)
        surface_path.closeSubpath()
        painter.fillRect(self.rect(), outer_color)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.fillPath(surface_path, background_color)

        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        painter.fillRect(0, 0, line_width, max(1, self.height() - radius_px), frame_color)
        painter.fillRect(
            self.width() - line_width,
            0,
            line_width,
            max(1, self.height() - radius_px),
            frame_color,
        )
        painter.fillRect(
            radius_px,
            self.height() - line_width,
            max(1, self.width() - (radius_px * 2)),
            line_width,
            frame_color,
        )

        painter.setPen(frame_color)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        left = 0.5
        right = self.width() - 1.5
        bottom = self.height() - 1.5
        corner_path = QPainterPath()
        corner_path.moveTo(left, bottom - radius)
        corner_path.quadTo(left, bottom, left + radius, bottom)
        corner_path.moveTo(right - radius, bottom)
        corner_path.quadTo(right, bottom, right, bottom - radius)
        painter.drawPath(corner_path)

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
            self.updateLayout()
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
        self.updateLayout()
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
            self.updateLayout()

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
            self.updateLayout()

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
        self.updateLayout()

    def clearGroups(self):
        self.clear_groups()

    def set_title(self, title):
        """Set the page title

        Args:
            title: New title for the page
        """
        self.title = CallableString(title)
        self._default_action.setText(title)
        self.titleChanged.emit(title)
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
        while parent:
            if hasattr(parent, "pageIndex") and hasattr(parent, "setRibbonMinimized"):
                return parent
            parent = parent.parent()
        return None

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
        self.groups_container.updateGeometry()
        self.groups_container.update()


RibbonPage = LqRibbonPage
