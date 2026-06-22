"""
LqIconGenerator - Generate simple colored icons for buttons
"""

from PySide6.QtGui import QIcon, QPixmap, QPainter, QBrush, QPen, QFont, QPainterPath
from PySide6.QtCore import Qt, QRect, QRectF


class LqIconGenerator:
    """Generate simple colored icons"""

    @staticmethod
    def create_colored_icon(text="", bg_color="#2B579A", text_color="white", size=24, icon_type=None):
        """Create a simple colored icon with text or shape

        Args:
            text: Text to display (1-2 characters)
            bg_color: Background color
            text_color: Text color
            size: Icon size
            icon_type: Special icon type for drawing shapes

        Returns:
            QIcon: Generated icon
        """
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Import QColor here
        from PySide6.QtGui import QColor

        # Draw background only if we have content
        if text or icon_type:
            # Draw flat background
            brush = QBrush(QColor(bg_color))
            painter.setBrush(brush)
            painter.setPen(Qt.PenStyle.NoPen)

            # Draw rounded rectangle with minimal radius for flat look
            rect = QRect(2, 2, size-4, size-4)
            painter.drawRoundedRect(rect, 3, 3)

            # Draw content
            if icon_type == "fullscreen":
                # Draw fullscreen icon
                painter.setPen(QPen(QColor(text_color), 2))
                painter.setBrush(Qt.BrushStyle.NoBrush)
                inner_rect = QRect(8, 8, size-16, size-16)
                painter.drawRect(inner_rect)

            elif icon_type == "grid":
                # Draw grid icon for MDI/Tile
                painter.setPen(QPen(QColor(text_color), 1.5))
                painter.setBrush(Qt.BrushStyle.NoBrush)
                # Draw 4 squares
                w = (size - 16) // 2
                painter.drawRect(8, 8, w, w)
                painter.drawRect(8 + w + 2, 8, w, w)
                painter.drawRect(8, 8 + w + 2, w, w)
                painter.drawRect(8 + w + 2, 8 + w + 2, w, w)

            elif icon_type == "tab":
                # Draw tab icon
                painter.setPen(QPen(QColor(text_color), 1.5))
                painter.setBrush(Qt.BrushStyle.NoBrush)
                # Draw tab shape
                tab_w = size - 14
                tab_h = 6
                painter.drawRect(7, 10, tab_w, tab_h)
                painter.drawRect(7, 18, tab_w, size - 28)

            elif text:
                # Draw text
                painter.setPen(QPen(QColor(text_color)))
                font = QFont("Segoe UI", int(size * 0.35), QFont.Weight.Normal)
                painter.setFont(font)
                painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, text)

        painter.end()
        return QIcon(pixmap)

    @staticmethod
    def get_action_icons():
        """Get predefined icons for all actions"""
        icons = {
            "Full Screen": LqIconGenerator.create_colored_icon(icon_type="fullscreen", bg_color="#4682B4"),
            "MDI Mode": LqIconGenerator.create_colored_icon(icon_type="grid", bg_color="#5F9EA0"),
            "Tab Mode": LqIconGenerator.create_colored_icon(icon_type="tab", bg_color="#6495ED"),
            "Tile Window": LqIconGenerator.create_colored_icon(icon_type="grid", bg_color="#7B68EE"),
            "Language": LqIconGenerator.create_colored_icon("A", "#4682B4"),
            "Version": LqIconGenerator.create_colored_icon("V", "#5F9EA0"),
            "Check Update": LqIconGenerator.create_colored_icon("↻", "#6495ED"),
            "Help Document": LqIconGenerator.create_colored_icon("?", "#4682B4"),
            "Assistant": LqIconGenerator.create_colored_icon("☺", "#5F9EA0"),
        }
        return icons


# Import QColor for the module
from PySide6.QtGui import QColor