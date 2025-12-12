"""
View module - Contains all UI components (pages, groups)
"""

from . import groups
from . import pages

# Re-export commonly used classes for convenience
from .pages import PageGeneral, PageHelp
from .groups import GroupView, GroupSystem, GroupVersion, GroupHelp

__all__ = [
    "groups", "pages",
    "PageGeneral", "PageHelp",
    "GroupView", "GroupSystem", "GroupVersion", "GroupHelp"
]
