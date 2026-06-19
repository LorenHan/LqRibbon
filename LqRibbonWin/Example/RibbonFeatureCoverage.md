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
| Input controls | Check box, radio, combo box, font combo, line edit, spin boxes | Complete | `--grab-controls-preview` |
| Galleries | In-ribbon gallery, popup gallery, gallery groups/items | Complete | `--grab-gallery-preview` |
| Backstage | File page, backstage buttons, pages, separators, close behavior | Missing | Planned backstage example |
| System menu | File button menu, recent files, page popup | Missing | Planned system-menu example |
| Search | Search box, suggestions, actions, recent commands | Partial | `--grab-search-preview` |
| Status bar | Permanent area, switch group, sliders, progress | Complete | `--grab-preview` status area |
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
| `QtnRibbonBar.h` | Menu-bar based Ribbon root, page management, title groups, backstage, search, simplify mode, customization | `RibbonBar` covers add page, current page, search, minimize, frame theme, quick access, title buttons; missing backstage, system button, contextual/title groups, simplify mode, movable tabs, customize manager | Partial |
| `QtnRibbonPage.h` | Page group management, contextual metadata, visibility/enabled state | `RibbonPage` covers title and append group; missing insert/remove groups and contextual integration | Partial |
| `QtnRibbonGroup.h` | Group controls, option button, size reduction, scrolling | `RibbonGroup` covers title, actions, widgets, large/small rows; missing option button, size definitions, reduced popup, group scrolling | Partial |
| `QtnRibbonButton.h` | Dedicated word-wrapped Ribbon button | LqRibbon currently uses configured `QToolButton`; no dedicated button class | Partial |
| `QtnRibbonControls.h` | Base control abstraction, size definitions, label/toolbar/column break controls | `RibbonControl`, `RibbonWidgetControl`, label, toolbar, and column break controls cover public usage | Complete |
| `QtnRibbonButtonControls.h` | Button, check box, radio button controls | `RibbonButtonControl`, `RibbonCheckBoxControl`, and `RibbonRadioButtonControl` cover public usage | Complete |
| `QtnRibbonInputControls.h` | Font combo, line edit, combo, spin, slider, date/time controls | Input wrappers cover native Qt input widgets and slider pane; controls preview is verified by screenshot | Complete |
| `QtnRibbonGallery.h` | Gallery item, gallery group, in-ribbon gallery, popup gallery | `RibbonGalleryItem`, `RibbonGalleryGroup`, and `RibbonGallery` cover public usage; gallery preview is verified by screenshot | Complete |
| `QtnRibbonGalleryControls.h` | Gallery control wrapper for groups | `RibbonGalleryControl` embeds galleries in Ribbon groups; gallery preview is verified by screenshot | Complete |
| `QtnRibbonBackstageView.h` | Backstage view, pages, buttons, separators, close prevention | No backstage module yet | Missing |
| `QtnRibbonSystemMenu.h` | File/system button, menu, recent files, page popup | No system menu module yet | Missing |
| `QtnRibbonQuickAccessBar.h` | Quick access toolbar, visibility per action, customize menu | LqRibbon has quick access actions; missing standalone class, per-action visibility, visible count, customize signal | Partial |
| `QtnRibbonSearchBar.h` | Search field, compact mode, help, suggested actions, popup | LqRibbon has search field, suggestions, action matching, recent actions; missing standalone class, compact/help APIs, animation hooks | Partial |
| `QtnRibbonStatusBar.h` | Status bar, permanent action area, switch group | `RibbonStatusBar` and `RibbonStatusBarSwitchGroup` cover public usage; example status bar is verified by preview | Complete |
| `QtnRibbonSliderPane.h` | Compact slider with scroll buttons and value signals | `RibbonSliderPane` covers range, buttons, value, position, and signals; example status bar is verified by preview | Complete |
| `QtnRibbonProgressBar.h` | Compact progress bar and threaded operation helper | `RibbonProgressBar`, `RibbonProgressData`, and `RibbonProgressOperation` cover public usage; progress bar is verified by preview | Complete |
| `QtnRibbonWorkspace.h` | Ribbon scroll area, workspace, MDI area | LqRibbon polishes standard `QMdiArea`; standalone scroll/workspace/MDI classes are missing | Partial |
| `QtnRibbonCustomizeManager.h` | Runtime customization model and persistence | No customization manager yet | Missing |
| `QtnRibbonCustomizeDialog.h` | Customization dialog | No customization dialog yet | Missing |
| `QtnRibbonCustomizePage.h` | Quick access and Ribbon customize pages | No customization pages yet | Missing |
| `QtnOfficePopupMenu.h` | Office-style popup menu | No dedicated popup menu module yet | Missing |
| `QtnOfficePopupWindow.h` | Toast/popup notification window | No popup notification module yet | Missing |
| `QtnOfficePopupColorButton.h` | Popup color button | No popup color button module yet | Missing |

Style headers and unrelated base widgets are tracked separately from Ribbon
feature coverage unless they are pulled in by the aggregate Ribbon include.
