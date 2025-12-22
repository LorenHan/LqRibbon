# LqRibbon - PySide6 Ribbon Library

A modern, blue flat-style ribbon interface library for PySide6 applications.

## Features

- **Blue Flat Style**: Modern blue theme with clean, flat design
- **Modular Architecture**: Separate files for pages, groups, and actions for easy maintenance
- **Customizable**: Easy to extend with new pages, groups, and actions
- **Professional Look**: Similar to Microsoft Office ribbon interface

## Installation

This repo is not packaged on PyPI by default. For the demo app, install runtime deps:

```bash
pip install -r example/requirements.txt
```

## Quick Start

```python
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from LqRibbon import LqRibbonWindow, LqRibbonBar

class MyWindow(LqRibbonWindow):
    def __init__(self):
        super().__init__()
        ribbon_bar = self.get_ribbon_bar()

        # Add pages
        page = ribbon_bar.add_page("Home")

        # Add groups
        group = page.add_group("File")

        # Add actions (One-liner)
        settings_act = group.addAction(QIcon("settings.svg"), "Settings", Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        settings_act.triggered.connect(self.on_settings)
```

## Example Application

Run the example application to see LqRibbon in action:

```bash
python example/main.py
```

## Project Structure

```
.
├── LqRibbon/                  # Core library
│   ├── __init__.py
│   ├── lq_ribbon_window.py    # Main window class
│   ├── lq_ribbon_bar.py       # Ribbon bar container
│   ├── lq_ribbon_page.py      # Ribbon page (tab)
│   ├── lq_ribbon_group.py     # Ribbon group
│   ├── lq_ribbon_button.py    # Ribbon button
│   ├── lq_icon_generator.py   # Icon helper
│   └── lq_styles.py           # Blue flat style definitions
│
└── example/                   # Example application
    ├── main.py                # Entry point
    ├── main_window.py         # Main window implementation
    ├── picture.qrc            # Qt resource file
    ├── picture_rc.py          # Generated resources (imported by main.py)
    └── view/
        ├── pages/             # Ribbon pages
        │   ├── page_general.py
        │   └── page_help.py
        ├── groups/            # Ribbon groups
        │   ├── group_view.py
        │   ├── group_system.py
        │   ├── group_version.py
        │   └── group_help.py
        └── actions/           # Action modules
```

## Key Components

### LqRibbonWindow
Main window class with integrated ribbon interface, custom title bar, and display area.

### LqRibbonBar
Container for ribbon pages (tabs).

### LqRibbonPage
Individual page/tab in the ribbon containing groups.

### LqRibbonGroup
Group container for related actions and controls.

### LqRibbonButton
Customizable button that supports standard `Qt.ToolButtonStyle` enums:
- `ToolButtonTextUnderIcon`: Large button with icon above text
- `ToolButtonTextBesideIcon`: Medium button with icon beside text
- `ToolButtonIconOnly`: Icon only button

## Usage Example

```python
# Import the library
from LqRibbon import LqRibbonWindow

# Import page implementations
from example.view.pages import PageGeneral, PageHelp

class MainWindow(LqRibbonWindow):
    def __init__(self):
        super().__init__()

        # Get ribbon bar
        ribbon_bar = self.get_ribbon_bar()

        # Add pages with groups and actions
        PageGeneral(ribbon_bar, self)
        PageHelp(ribbon_bar, self)
```

## Action Handling

When any action button is clicked, the action name is displayed in the main window's display area. Each action can be extended with custom functionality.

## Customization

The blue flat style can be customized by modifying `lq_styles.py`. Colors, fonts, and sizes can be adjusted to match your application's design requirements.

## License

This project is licensed under the MIT License.

MIT is a permissive license: it allows commercial use and closed-source distribution, as long as you keep the copyright notice and the license text in redistributions.