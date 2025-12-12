"""
LqRibbon - A PySide6 Ribbon library with blue flat style
"""

from .lq_ribbon_window import LqRibbonWindow
from .lq_ribbon_bar import LqRibbonBar
from .lq_ribbon_page import LqRibbonPage
from .lq_ribbon_group import LqRibbonGroup
from .lq_ribbon_button import LqRibbonButton
from .lq_styles import LqStyle
from .lq_icon_generator import LqIconGenerator

__version__ = "1.0.0"
__author__ = "LqRibbon"

__all__ = [
    "LqRibbonWindow",
    "LqRibbonBar",
    "LqRibbonPage",
    "LqRibbonGroup",
    "LqRibbonButton",
    "LqStyle",
    "LqIconGenerator"
]