# Ribbon Pixel Comparison Checklist

Scope: Ribbon framework only. Business logic, CAN communication, OD data, and
servo-specific dialogs are out of scope unless they expose Ribbon chrome.

## Title Bar And Frame

1. Window icon size.
2. Window icon sharpness.
3. Window icon left margin.
4. Window title baseline.
5. Window title font family.
6. Window title font size.
7. Window title color.
8. Caption bar blue color.
9. Caption bar height.
10. Caption bar bottom boundary.
11. Caption bar double-click maximize.
12. Caption bar drag move.
13. Caption drag restore from maximized.
14. Caption right-click system menu.
15. Alt+Space system menu.
16. Top resize grip.
17. Left resize grip.
18. Right resize grip.
19. Bottom resize grip.
20. Corner resize grips.
21. Snap layout hit area on maximize button.
22. Minimize button glyph.
23. Maximize button glyph.
24. Restore button glyph.
25. Close button glyph.
26. Window button width.
27. Window button height.
28. Window button top alignment.
29. Window button right alignment.
30. Window button hover fill.
31. Window button pressed fill.
32. Close hover fill.
33. Close pressed fill.
34. Disabled maximize state.
35. Frameless border absence.

## Ribbon Tabs

36. General tab left edge.
37. Driver tab left edge.
38. Tab height.
39. Selected tab background.
40. Selected tab text color.
41. Unselected tab text color.
42. Tab text vertical alignment.
43. Tab text horizontal padding.
44. Tab overlap with caption bar.
45. Tab bottom boundary.
46. Tab hover background.
47. Tab press state.
48. Tab focus rectangle.
49. Tab keyboard navigation.
50. Current page switch animation absence.

## Ribbon Groups

51. Ribbon page background color.
52. Ribbon page height.
53. Group separator color.
54. Group separator width.
55. Group separator top margin.
56. Group separator bottom margin.
57. Group title font.
58. Group title color.
59. Group title baseline.
60. Group title bottom margin.
61. Communication group width.
62. Function group width.
63. Specialist group width.
64. Group left padding.
65. Group right padding.
66. Group top padding.
67. Group title alignment.
68. Empty trailing page area color.
69. Group stretch behavior.
70. Ribbon resize behavior.

## Ribbon Buttons

71. Large button icon size.
72. Large button icon sharpness.
73. Large button text font.
74. Large button text wrapping.
75. Large button text baseline.
76. Large button hover border.
77. Large button hover fill.
78. Large button pressed fill.
79. Large button checked fill.
80. Small button icon size.
81. Small button row height.
82. Small button text baseline.
83. Small button left icon gap.
84. Small button hover fill.
85. Small button pressed fill.
86. Menu arrow position.
87. Menu arrow color.
88. Split button menu area width.
89. Disabled button opacity.
90. Button tooltip timing.

## Search Box

91. Search box width.
92. Search box height.
93. Search box x-position.
94. Search box y-position.
95. Search placeholder text.
96. Search edit border color.
97. Search edit focus border.
98. Search clear button glyph.
99. Search popup width.
100. Search popup shadow/border.
101. Search popup section header height.
102. Search popup row height.
103. Search popup selected row color.
104. Search popup icon size.
105. Search popup keyboard navigation.
106. Search Enter action.
107. Search Escape close.
108. Search no-result help row.

## MDI And Tabbed Workspace

109. MDI area background color.
110. MDI subwindow title color.
111. MDI title height.
112. MDI title icon size.
113. MDI title text baseline.
114. MDI minimize glyph.
115. MDI maximize glyph.
116. MDI restore glyph.
117. MDI close glyph.
118. MDI subwindow border color.
119. MDI active/inactive title behavior.
120. MDI subwindow drag behavior.
121. MDI subwindow resize behavior.
122. MDI double-click maximize.
123. MDI system menu behavior.
124. Tabbed MDI tab left alignment.
125. Tabbed MDI tab width policy.
126. Tabbed MDI selected tab color.
127. Tabbed MDI close button glyph.
128. Tabbed MDI maximized child buttons.

## Cross Platform Behavior

129. Windows native move gesture.
130. Windows native resize gesture.
131. Windows snap assist compatibility.
132. Windows taskbar minimize/restore.
133. Windows DPI scaling.
134. macOS title integration fallback.
135. macOS traffic-light avoidance.
136. Linux window manager fallback.
137. Linux resize fallback.
138. High contrast palette fallback.

## Current Baseline Notes

- Reference pinned baseline executable:
  `D:/backup/KincoServo3/kincoservo-pro/KincoServo3_MSVC32/KincoServo3_V2.exe`.
- LqRibbon comparison executable:
  `KincoServo3_MinGW32/KincoServo3_V2.exe`.
- First high-priority mismatch found:
  LqRibbon window controls can fall back too close to the search box on wide
  captures; they must stay at the visible title-bar right edge unless the
  window geometry is clearly invalid.
- First metric fixes completed:
  caption height, page height, search box size/position, top-left icon position,
  title baseline, and wide-titlebar window-control fallback.
