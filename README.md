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
from pathlib import Path

from LqRibbon import LqRibbonWindow

class MyWindow(LqRibbonWindow):
    def __init__(self):
        super().__init__(frameless=True, default_content=False)
        self.load_ui(Path(__file__).with_name("mainwindow.ui"))

        self.add_ribbon_action("Home", "File", "Settings", self.on_settings, "settings.svg")

    def on_settings(self):
        self.append_display_text("Open settings")
```

`LqRibbonWindow` uses a frameless window by default. If you need the native system frame,
pass `frameless=False`:

```python
window = LqRibbonWindow(frameless=False)
```

The frameless implementation keeps the common native frame behaviors:

- vector minimize, maximize/restore, and close buttons
- title bar dragging, double-click maximize/restore, and right-click system menu
- `Alt+Space` system menu shortcut
- edge and corner resizing
- drag-to-top maximize, drag-to-side half snap, and drag-to-corner quarter snap fallback
- drag a maximized title bar downward to restore and keep dragging
- Windows native maximize/restore animation and hit testing for resize, system buttons, Aero Snap, and high-DPI cursor mapping
- short custom maximize/restore geometry animation on non-Windows platforms
- multi-monitor aware screen selection, restore geometry clamping, and snap fallback
- macOS-style left-side traffic-light controls when running on macOS

## Example Application

Run the example application to see LqRibbon in action:

```bash
python example/main.py
```

The example loads its business area from `example/mainwindow.ui`; the ribbon is
added by `LqRibbonWindow` above that UI content.

Run the frameless window regression checks on Windows:

```bash
python tools/verify_frameless_window.py
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
from LqRibbon import LqRibbonWindow

class MainWindow(LqRibbonWindow):
    def __init__(self):
        super().__init__(default_content=False)
        self.load_ui("mainwindow.ui")
        self.add_ribbon_action("General", "View", "Full Screen", self.toggle_fullscreen)
```

## Action Handling

When any action button is clicked, the action name is displayed in the main window's display area. Each action can be extended with custom functionality.

## Customization

The blue flat style can be customized by modifying `lq_styles.py`. Colors, fonts, and sizes can be adjusted to match your application's design requirements.

## License

This project is licensed under the MIT License.

MIT is a permissive license: it allows commercial use and closed-source distribution, as long as you keep the copyright notice and the license text in redistributions.
