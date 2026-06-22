import pytest
from PySide6.QtWidgets import QApplication


@pytest.fixture(autouse=True)
def qapplication():
    app = QApplication.instance() or QApplication([])
    yield app

