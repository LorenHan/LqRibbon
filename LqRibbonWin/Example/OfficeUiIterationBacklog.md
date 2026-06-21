# Office UI Iteration Backlog

This backlog converts recent Office UI and interaction changes into LqRibbon
Example work items. Each item must be implemented in both the C++ and Python
examples, tested, visually verified when applicable, and committed separately.

Default style remains `Office 2016 Blue`.

## Sources Checked

- Microsoft Source, "Microsoft Office gets a makeover", 2018-06-13:
  simplified ribbon, new icons/colors, AI-backed search, user control.
- Microsoft Support, "The new look of Office": Fluent visual refresh,
  Office theme switching, ribbon pinning.
- Microsoft Support, "Find what you need with Microsoft Search": title search,
  `Alt+Q`, recent/suggested actions, help and related files.
- Microsoft Support, "Do things quickly with Tell Me": command discovery with
  natural phrases.
- Microsoft Support, "Customize the Quick Access Toolbar": show/hide, move,
  labels, add/remove/reorder, import/export.
- Microsoft Support, "Customize the ribbon in Office": tabs, groups, commands,
  rename/reset/import/export.
- Microsoft Support, "What's new in Office 2024 and Office LTSC 2024": Fluent
  default Office theme.
- Microsoft Learn Office update release notes: rolling command, collaboration,
  accessibility, icon, and Copilot surface changes.

## Items

| # | Iteration | Example target | Status |
| --- | --- | --- | --- |
| 001 | Style switcher with Office 2016 Blue default | C++ and Python style combo plus API | Complete |
| 002 | Office 2019 Colorful theme option | C++ and Python style combo | Complete |
| 003 | Microsoft 365 Light theme option | C++ and Python style combo | Complete |
| 004 | Microsoft 365 Dark theme option | C++ and Python style combo | Complete |
| 005 | System theme follow mode | Theme selector and system palette bridge | Complete |
| 006 | Theme live preview before apply | Preview swatch panel | Complete |
| 007 | Persisted Office theme choice | Save/load example settings | Complete |
| 008 | Fluent rounded tab geometry | Style preview page | Complete |
| 009 | Fluent softer border model | Style preview page | Complete |
| 010 | Fluent hover and pressed state timing | Style preview page | Complete |
| 011 | Simplified one-line ribbon | Ribbon display toggle | Complete |
| 012 | Classic multi-line ribbon restore | Ribbon display toggle | Complete |
| 013 | Ribbon pin and unpin command | Ribbon display menu | Complete |
| 014 | Ribbon display options menu | Caption control | Complete |
| 015 | Collapse button state preview | Shell page | Complete |
| 016 | Temporary ribbon expansion on tab click | Shell page | Complete |
| 017 | Double-click tab minimize behavior | Shell page | Complete |
| 018 | Compact command row density | Simplified ribbon preview | Complete |
| 019 | Expanded command row density | Classic ribbon preview | Complete |
| 020 | Responsive command label hiding | Width stress preview | Complete |
| 021 | Quick Access Toolbar show/hide | QAT menu | Complete |
| 022 | QAT above-ribbon position | QAT menu | Complete |
| 023 | QAT below-ribbon position | QAT menu | Complete |
| 024 | QAT command labels on/off | QAT menu | Complete |
| 025 | Add command to QAT from context menu | Action context menu | Complete |
| 026 | Remove command from QAT | QAT context menu | Complete |
| 027 | Reorder QAT commands | Customize dialog | Complete |
| 028 | Reset QAT to default | Customize dialog | Complete |
| 029 | Export QAT customization | Customize dialog | Complete |
| 030 | Import QAT customization | Customize dialog | Complete |
| 031 | Centered Microsoft Search box | Caption search | Complete |
| 032 | Compact search icon mode | Caption search | Complete |
| 033 | Hidden search mode | Caption search | Complete |
| 034 | `Alt+Q` focuses search | Keyboard test path | Complete |
| 035 | Zero-query search suggestions | Search popup | Complete |
| 036 | Recently used action section | Search popup | Complete |
| 037 | Suggested action section | Search popup | Complete |
| 038 | Document/find result section | Search popup | Complete |
| 039 | Help result section | Search popup | Complete |
| 040 | Related file result section | Search popup | Complete |
| 041 | Search action trigger on Enter | Search popup | Complete |
| 042 | Search keyboard navigation | Search popup | Complete |
| 043 | Search command aliases | Search registry | Complete |
| 044 | Search fuzzy phrase matching | Search registry | Complete |
| 045 | Search no-result affordance | Search popup | Complete |
| 046 | Tell Me lightbulb entry | Command discovery page | Complete |
| 047 | Tell Me natural phrase examples | Command discovery page | Complete |
| 048 | Tell Me help redirect row | Command discovery page | Complete |
| 049 | Smart Lookup command surface | Review page | Complete |
| 050 | Feedback button in title area | Title buttons | Complete |
| 051 | Account/profile button in title area | Title buttons | Complete |
| 052 | Share button in title area | Title buttons | Complete |
| 053 | Comments button in title area | Title buttons | Complete |
| 054 | Presence avatar strip | Title buttons | Complete |
| 055 | Collaboration status text | Status bar | Complete |
| 056 | Coauthoring indicator | Status bar | Complete |
| 057 | Version history entry | Backstage | Complete |
| 058 | AutoSave toggle in title/QAT | Title/QAT command | Complete |
| 059 | AutoSave disabled explanation | Tooltip/callout | Complete |
| 060 | Save a Copy command replacing Save As | Backstage | Complete |
| 061 | Cloud location picker | Backstage | Complete |
| 062 | Recent file pinning | Backstage recent list | Complete |
| 063 | Frequent sites and groups | Backstage open page | Complete |
| 064 | Upload-before-share prompt | Backstage/share flow | Complete |
| 065 | Sensitivity label command | Title or Review page | Complete |
| 066 | Account privacy settings entry | Backstage account page | Complete |
| 067 | Accessibility checker command | Review page | Complete |
| 068 | Editor pane command | Review page | Complete |
| 069 | Spelling and grammar card | Review page | Complete |
| 070 | Dictate microphone command | Home page | Complete |
| 071 | Translator command | Review page | Complete |
| 072 | Read Aloud command | Review page | Complete |
| 073 | Immersive Reader command | View page | Complete |
| 074 | Focus mode command | View page | Complete |
| 075 | Dark canvas toggle | View page | Complete |
| 076 | Zoom slider in status bar | Status bar | Complete |
| 077 | View switch buttons in status bar | Status bar | Complete |
| 078 | Character count status item | Status bar | Complete |
| 079 | Sync status action | Status bar | Complete |
| 080 | High-DPI scalable icons | Icon gallery | Complete |
| 081 | New app icon color set | Icon gallery | Complete |
| 082 | SVG icon insert command | Insert page | Complete |
| 083 | SVG recolor command | Format page | Complete |
| 084 | Convert SVG to shape command | Format page | Complete |
| 085 | Icon-only title commands | Title buttons | Complete |
| 086 | Accessible tooltip names | Tooltip test path | Complete |
| 087 | Screen-reader names for commands | Accessibility test path | Complete |
| 088 | High contrast style pass | Style preview page | Complete |
| 089 | Reduced motion option | Options page | Complete |
| 090 | Touch/mouse spacing toggle | Style preview page | Complete |
| 091 | KeyTips overlay | Keyboard overlay | Complete |
| 092 | Alt key tab activation | Keyboard overlay | Complete |
| 093 | Contextual tab group color | Contextual page preview | Complete |
| 094 | Contextual tab show/hide | Contextual page preview | Complete |
| 095 | Title groups visibility toggle | Contextual page preview | Complete |
| 096 | Custom tab creation | Customize dialog | Complete |
| 097 | Custom group creation | Customize dialog | Complete |
| 098 | Rename tab/group | Customize dialog | Complete |
| 099 | Add command to custom group | Customize dialog | Complete |
| 100 | Remove command from custom group | Customize dialog | Complete |
| 101 | Reset selected tab | Customize dialog | Planned |
| 102 | Reset all ribbon customizations | Customize dialog | Planned |
| 103 | Export ribbon customization | Customize dialog | Planned |
| 104 | Import ribbon customization | Customize dialog | Planned |
| 105 | Backstage info page | Backstage | Planned |
| 106 | Backstage account page | Backstage | Planned |
| 107 | Backstage open page | Backstage | Planned |
| 108 | Backstage export page | Backstage | Planned |
| 109 | Backstage close behavior | Backstage | Planned |
| 110 | System menu recent files | System menu | Planned |
| 111 | System menu page popup | System menu | Planned |
| 112 | Office popup notification | Popup page | Planned |
| 113 | Resizable Office popup menu grip | Popup page | Planned |
| 114 | Popup color button | Popup page | Planned |
| 115 | In-ribbon gallery | Gallery page | Planned |
| 116 | Popup gallery menu | Gallery page | Planned |
| 117 | Gallery checked-item state | Gallery page | Planned |
| 118 | Gallery keyboard navigation | Gallery page | Planned |
| 119 | Draw tab | Draw page | Planned |
| 120 | Pen gallery | Draw page | Planned |
| 121 | Ruler toggle | Draw page | Planned |
| 122 | 3D model command | Insert page | Planned |
| 123 | 3D animation command | Animation page | Planned |
| 124 | Designer/Ideas command | Design page | Planned |
| 125 | Recommended chart command | Insert page | Planned |
| 126 | Data types command | Data page | Planned |
| 127 | Pivot recommendation command | Data page | Planned |
| 128 | Live captions command | Slide Show page | Planned |
| 129 | Copilot button | Title buttons | Planned |
| 130 | Copilot command center visibility | Title buttons | Planned |
| 131 | Copilot prompt gallery | Copilot page | Planned |
| 132 | Loop component command | Insert page | Planned |
| 133 | Comments link opening | Collaboration page | Planned |
| 134 | Macro blocking status command | Security page | Planned |
| 135 | Font picker large-list scrollbar state | Font controls | Planned |
