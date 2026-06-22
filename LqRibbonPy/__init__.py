"""
LqRibbon - A PySide6 Ribbon library with blue flat style
"""

from .lq_ribbon_window import LqRibbonWindow
from .lq_ribbon_bar import LqRibbonBar
from .lq_ribbon_page import LqRibbonPage
from .lq_ribbon_group import LqRibbonGroup
from .lq_ribbon_button import LqRibbonButton
from . import lq_ribbon_extras as _extras
from .lq_ribbon_extras import *
from .lq_styles import LqStyle, RibbonPlatformLayout, RibbonStyle
from .lq_icon_generator import LqIconGenerator

RibbonMainWindow = LqRibbonWindow
RibbonBar = LqRibbonBar
RibbonPage = LqRibbonPage
RibbonGroup = LqRibbonGroup
RibbonButton = LqRibbonButton

__version__ = "6.8.0-compatible"
__author__ = "LqRibbon"

__all__ = [
    "LqRibbonWindow",
    "LqRibbonBar",
    "LqRibbonPage",
    "LqRibbonGroup",
    "LqRibbonButton",
    "RibbonMainWindow",
    "RibbonBar",
    "RibbonPage",
    "RibbonGroup",
    "RibbonButton",
    "LqStyle",
    "RibbonPlatformLayout",
    "RibbonStyle",
    "LqIconGenerator"
] + [
    name for name in dir(_extras)
    if not name.startswith("_")
]
