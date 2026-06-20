# LqRibbon Feature Coverage

This matrix tracks the C++ Ribbon feature set against the local reference
headers and examples. The goal is compatible public usage and visual behavior,
not copied implementation.

| Area | Reference capability | LqRibbon status | Verification entry |
| --- | --- | --- | --- |
| Main window | Ribbon host, central widget, themed frame, native gestures | Partial | `main.cpp`, `--grab-preview`, `--grab-mdi-preview` |
| Ribbon bar | Pages, current page, minimized mode, temporary tab expansion, tab double-click minimize/restore preview, simplified one-line mode, compact and expanded command density previews, responsive command label hiding preview, classic multi-line restore, pin/unpin display policy, display options menu, collapse button state preview, title background, tab moving, elide mode | Partial | `main.cpp`, `--grab-collapsed-preview`, `--grab-temporary-preview`, `--grab-double-click-preview`, `--grab-simplified-preview`, `--grab-width-stress-preview`, `--run-collapse-tests` |
| Quick access | Toolbar actions, QAT menu show/hide control, QAT above-ribbon position, customization entry points, top/bottom placement | Partial | `main.cpp`, `--grab-qat-hidden-preview`, `--grab-qat-above-preview`, preview screenshot |
| Title widgets | Caption-row buttons and custom title controls | Implemented | `main.cpp`, preview screenshot |
| Pages | Add/insert/remove pages, visible/enabled state, contextual page groups | Missing contextual groups | Planned example tab coverage |
| Groups | Command groups, option button, row layout, group collapse/scroll | Partial | `main.cpp`, planned scroll preview |
| Buttons | Large/small buttons, popup modes, word wrap | Partial | `main.cpp` |
| Input controls | Check box, radio, combo box, font combo, line edit, spin boxes | Complete | `--grab-controls-preview` |
| Galleries | In-ribbon gallery, popup gallery, gallery groups/items | Complete | `--grab-gallery-preview` |
| Backstage | File page, backstage buttons, pages, separators, close behavior | Implemented basic API | Planned backstage example |
| System menu | File button menu, recent files, page popup | Implemented basic API | Planned system-menu example |
| Search | Search box, suggestions, actions, recent commands | Implemented | `--grab-search-preview` |
| Status bar | Permanent area, switch group, sliders, progress | Complete | `--grab-preview` status area |
| Workspace | Scroll area, MDI-aware workspace, tab/subwindow polish | Implemented basic API | `--grab-mdi-preview`, `--grab-tab-preview` |
| Customization | Customize manager/page/dialog, save and restore layout | Implemented basic API | Planned customization example |
| Style | Office-like metrics, colors, theme hooks, high-DPI behavior | Basic style switching, system follow mode, live preview swatch, persisted theme choice, Fluent rounded tab geometry, softer Fluent border tokens, and Fluent hover/pressed timing preview implemented | `--grab-style-preview`, `--run-style-tests` |

## Current Gap Summary

- LqRibbon now covers the core visual shell plus the standalone Ribbon widgets
  that are exposed by the Qtitan aggregate header.
- The remaining gaps are advanced Qtitan internals: binary compatibility,
  Designer integration, proprietary theme engines, key-tip overlay rendering,
  and pixel-identical backstage/customization visuals.
- Each new feature must add or extend an example path, build with Qt 5.15.2,
  run to a screenshot, and be committed separately.
- Office UI iteration candidates are tracked in
  `OfficeUiIterationBacklog.md`; each item must land as its own verified
  feature slice.

## File-by-File Coverage

Status rules:

- `Complete`: public usage, visual behavior, example path, build, and screenshot
  verification are all done.
- `Partial`: a comparable LqRibbon feature exists, but public usage or behavior
  is incomplete.
- `Missing`: no LqRibbon feature covers the file yet.
- `Planned`: scheduled next, but no verified LqRibbon feature exists yet.

| Reference file | Main capability | LqRibbon coverage | Status |
| --- | --- | --- | --- |
| `QtnRibbonDef.h` | Shared constants, list typedefs, version/custom text | Built-in text exists for search/frame strings; version and customize constants are missing | Partial |
| `QtnRibbonMainWindow.h` | Ribbon host, replaceable Ribbon bar, central widget overloads | `RibbonMainWindow` hosts a bar and central widget; replaceable bar and style central widget overload are missing | Partial |
| `QtnRibbonBar.h` | Menu-bar based Ribbon root, page management, title groups, backstage, search, simplify mode, customization | `RibbonBar` covers add page, current page, search, minimize, simplify mode, frame theme, quick access, title buttons; missing backstage, system button, contextual/title groups, movable tabs, customize manager | Partial |
| `QtnRibbonPage.h` | Page group management, contextual metadata, visibility/enabled state | `RibbonPage` covers title and append group; missing insert/remove groups and contextual integration | Partial |
| `QtnRibbonGroup.h` | Group controls, option button, size reduction, scrolling | `RibbonGroup` covers title, actions, widgets, large/small rows; missing option button, size definitions, reduced popup, group scrolling | Partial |
| `QtnRibbonButton.h` | Dedicated word-wrapped Ribbon button | `RibbonButton` covers word wrap, large/small icon, simplified mode, and action changes | Implemented |
| `QtnRibbonControls.h` | Base control abstraction, size definitions, label/toolbar/column break controls | `RibbonControl`, `RibbonWidgetControl`, label, toolbar, and column break controls cover public usage | Complete |
| `QtnRibbonButtonControls.h` | Button, check box, radio button controls | `RibbonButtonControl`, `RibbonCheckBoxControl`, and `RibbonRadioButtonControl` cover public usage | Complete |
| `QtnRibbonInputControls.h` | Font combo, line edit, combo, spin, slider, date/time controls | Input wrappers cover native Qt input widgets and slider pane; controls preview is verified by screenshot | Complete |
| `QtnRibbonGallery.h` | Gallery item, gallery group, in-ribbon gallery, popup gallery | `RibbonGalleryItem`, `RibbonGalleryGroup`, and `RibbonGallery` cover public usage; gallery preview is verified by screenshot | Complete |
| `QtnRibbonGalleryControls.h` | Gallery control wrapper for groups | `RibbonGalleryControl` embeds galleries in Ribbon groups; gallery preview is verified by screenshot | Complete |
| `QtnRibbonBackstageView.h` | Backstage view, pages, buttons, separators, close prevention | `RibbonBackstageView`, page/button/separator classes, active-page management, and close prevention are available | Implemented basic API |
| `QtnRibbonSystemMenu.h` | File/system button, menu, recent files, page popup | `RibbonSystemButton`, `RibbonSystemMenu`, recent-file list, and system popup are available | Implemented basic API |
| `QtnRibbonQuickAccessBar.h` | Quick access toolbar, visibility per action, customize menu | `RibbonQuickAccessBar` covers customize action, per-action visibility, visible count, and customize signal | Implemented |
| `QtnRibbonSearchBar.h` | Search field, compact mode, help, suggested actions, popup | `RibbonSearchBar` covers compact/help/suggested-action APIs and integrates with Ribbon action search | Implemented |
| `QtnRibbonStatusBar.h` | Status bar, permanent action area, switch group | `RibbonStatusBar` and `RibbonStatusBarSwitchGroup` cover public usage; example status bar is verified by preview | Complete |
| `QtnRibbonSliderPane.h` | Compact slider with scroll buttons and value signals | `RibbonSliderPane` covers range, buttons, value, position, and signals; example status bar is verified by preview | Complete |
| `QtnRibbonProgressBar.h` | Compact progress bar and threaded operation helper | `RibbonProgressBar`, `RibbonProgressData`, and `RibbonProgressOperation` cover public usage; progress bar is verified by preview | Complete |
| `QtnRibbonWorkspace.h` | Ribbon scroll area, workspace, MDI area | `RibbonScrollArea`, `RibbonWorkspace`, and `RibbonMdiArea` are available | Implemented basic API |
| `QtnRibbonCustomizeManager.h` | Runtime customization model and persistence | `RibbonCustomizeManager` covers categories, page/group/action edits, and simple XML save/load | Implemented basic API |
| `QtnRibbonCustomizeDialog.h` | Customization dialog | `RibbonCustomizeDialog` covers page insertion, current-page switching, accept/reject | Implemented basic API |
| `QtnRibbonCustomizePage.h` | Quick access and Ribbon customize pages | Quick access and Ribbon customize page widgets are available | Implemented basic API |
| `QtnOfficePopupMenu.h` | Office-style popup menu | `OfficePopupMenu` covers widget hosting and grip visibility | Implemented basic API |
| `QtnOfficePopupWindow.h` | Toast/popup notification window | `OfficePopupWindow` covers title/body/central widget, close button, location, timers, and show/close signals | Implemented basic API |
| `QtnOfficePopupColorButton.h` | Popup color button | `PopupColorButton` covers color state, color dialog, and change signal | Implemented |

## Python Parity

The Python package under `LqRibbon/` now exposes the same high-level class
families as the C++ package:

- Core: `RibbonMainWindow`, `RibbonBar`, `RibbonPage`, `RibbonGroup`,
  `RibbonButton`.
- Controls/status: control-size definitions, widget controls, button/input
  controls, slider pane, progress bar, status bar, and switch group.
- Ribbon shell extras: quick access bar, search bar, backstage view, system
  menu, recent-file list, popup menu/window/color button, workspace, MDI area,
  customization manager/dialog/pages.

Python parity is source-level and behavior-level for normal PySide6 usage. It
is not binary parity with Qtitan and does not implement Qtitan Designer plugins
or proprietary style engines.

The Python example mirrors the C++ style switcher with the same style names,
system follow mode, live preview swatch, persisted theme choice, Fluent rounded
  tab geometry, softer Fluent border tokens, Fluent hover/pressed timing preview,
  simplified one-line ribbon display, compact and expanded command density previews,
  responsive command label hiding preview, Quick Access Toolbar show/hide menu,
  Quick Access Toolbar above-ribbon menu position,
  temporary tab expansion state, tab double-click minimize/restore preview,
  classic multi-line restore, ribbon pin/unpin display policy, caption display
  options menu, collapse state preview, and default `Office 2016 Blue`
  behavior.
