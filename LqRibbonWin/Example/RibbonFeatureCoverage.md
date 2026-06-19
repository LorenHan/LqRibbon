# LqRibbon Feature Coverage

This matrix tracks the C++ Ribbon feature set against the local reference
headers and examples. The goal is compatible public usage and visual behavior,
not copied implementation.

| Area | Reference capability | LqRibbon status | Verification entry |
| --- | --- | --- | --- |
| Main window | Ribbon host, central widget, themed frame, native gestures | Partial | `main.cpp`, `--grab-preview`, `--grab-mdi-preview` |
| Ribbon bar | Pages, current page, minimized mode, title background, tab moving, elide mode | Partial | `main.cpp`, `--grab-collapsed-preview` |
| Quick access | Toolbar actions, customization entry points, top/bottom placement | Partial | `main.cpp`, preview screenshot |
| Title widgets | Caption-row buttons and custom title controls | Implemented | `main.cpp`, preview screenshot |
| Pages | Add/insert/remove pages, visible/enabled state, contextual page groups | Missing contextual groups | Planned example tab coverage |
| Groups | Command groups, option button, row layout, group collapse/scroll | Partial | `main.cpp`, planned scroll preview |
| Buttons | Large/small buttons, popup modes, word wrap | Partial | `main.cpp` |
| Input controls | Check box, radio, combo box, font combo, line edit, spin boxes | Missing wrappers | Planned controls example |
| Galleries | In-ribbon gallery, popup gallery, gallery groups/items | Missing | Planned gallery example |
| Backstage | File page, backstage buttons, pages, separators, close behavior | Missing | Planned backstage example |
| System menu | File button menu, recent files, page popup | Missing | Planned system-menu example |
| Search | Search box, suggestions, actions, recent commands | Partial | `--grab-search-preview` |
| Status bar | Permanent area, switch group, sliders, progress | Missing | Planned status example |
| Workspace | Scroll area, MDI-aware workspace, tab/subwindow polish | Partial | `--grab-mdi-preview`, `--grab-tab-preview` |
| Customization | Customize manager/page/dialog, save and restore layout | Missing | Planned customization example |
| Style | Office-like metrics, colors, theme hooks, high-DPI behavior | Partial | screenshot comparison checklist |

## Current Gap Summary

- LqRibbon currently covers the core visual shell but still lacks several
  standalone widgets from the reference API.
- The highest-value next features are contextual page groups, group scrolling,
  backstage/system menu, status bar helpers, and gallery controls.
- Each new feature must add or extend an example path, build with Qt 5.15.2,
  run to a screenshot, and be committed separately.
