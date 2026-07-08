"""
Smoke tests for Ribbon group/page mutation helpers.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QLabel

from LqRibbon import LqRibbonGroup, LqRibbonPage


def _group_titles(page):
    return [str(group.title) for group in page.groups]


def test_insert_existing_group_keeps_requested_order():
    page = LqRibbonPage("Home")
    one = page.addGroup("One")
    page.addGroup("Two")
    page.addGroup("Three")

    page.insertGroup(2, one)

    assert _group_titles(page) == ["Two", "One", "Three"]
    page.deleteLater()


def test_group_clear_removes_all_action_widgets():
    group = LqRibbonGroup("Tools")
    action = group.addAction(
        QIcon(),
        "Apply",
        Qt.ToolButtonStyle.ToolButtonTextUnderIcon,
    )
    separator_action = group.addSeparator()
    custom_widget = QLabel("custom")
    custom_action = group.addWidget(custom_widget)

    assert group.controlByAction(action) is not None
    assert group.controlByAction(separator_action) is not None
    assert group.controlByAction(custom_action) is custom_widget

    group.clear()

    assert list(group.actions) == []
    assert list(group.buttons) == []
    assert group.controlByAction(action) is None
    assert group.controlByAction(separator_action) is None
    assert group.controlByAction(custom_action) is None
    assert group.main_layout.indexOf(custom_widget) == -1
    group.deleteLater()
