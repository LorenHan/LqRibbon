# LqRibbon 无边框原生手势测试

## 参考源码

已下载到本机临时目录：
`C:\Users\39401\AppData\Local\Temp\lqribbon-frameless-references`

1. `stdware/qwindowkit`
   - Qt 5.12+，Windows/macOS/Linux。
   - Windows 方案：保留原生窗口样式，处理 `WM_NCCALCSIZE` 和 `WM_NCHITTEST`。
   - macOS 方案：对接 `NSWindow` 和系统窗口按钮区域。
   - Linux 方案：优先使用平台窗口系统的原生 move/resize。
2. `Bringer-of-Light/Qt-Nice-Frameless-Window`
   - Windows/macOS。
   - Windows 方案：`WM_NCHITTEST` 返回标题栏和 8 个缩放区域。
   - 约束方案：固定宽高时禁用对应方向缩放。
3. `wangwenx190/framelesshelper`
   - Windows/macOS/Linux。
   - Qt 5.15+ 优先使用 `QWindow::startSystemMove()` 和
     `QWindow::startSystemResize()`。
   - Linux X11 方案对齐 `_NET_WM_MOVERESIZE`。

## LqRibbon 当前实现

位置：

- `LqRibbonWin/Code/LqRibbon.h`
- `LqRibbonWin/Code/LqRibbon.cpp`
- `LqRibbonWin/Example/main.cpp`

实现策略：

1. Windows 保留 `WS_CAPTION | WS_SYSMENU | WS_THICKFRAME`，通过
   `WM_NCCALCSIZE` 隐藏系统非客户区，继续把系统拖动、Aero Snap、
   Win11 Snap Assist、拖下恢复、系统阴影、系统菜单交给 Windows。
2. Windows `WM_NCHITTEST` 返回 `HTCAPTION` 和 8 个原生缩放命中区。
3. macOS/Linux 使用 Qt 5.15.2 的 `QWindow::startSystemMove()` 和
   `QWindow::startSystemResize()` 接入平台原生拖动与缩放入口。
4. 三个平台都按 `minimumSize()`/`maximumSize()` 禁止无效方向缩放。
5. Ribbon 搜索框、快速访问栏、页签区域不作为标题栏拖动区域。

## 三系统标题栏和边框功能清单

| 系统 | 功能 | 期望行为 | 状态 |
| --- | --- | --- | --- |
| Windows | 标题栏空白区拖动 | 窗口跟随鼠标移动 | 命中区通过，待人工拖拽复测 |
| Windows | 拖到屏幕顶部 | 系统最大化或出现 Snap 提示 | 原生样式通过，待人工拖拽复测 |
| Windows | 最大化后按标题栏向下拖 | 系统还原并继续拖动 | 原生样式通过，待人工拖拽复测 |
| Windows | 拖到左右边缘 | 系统半屏停靠 | 原生样式通过，待人工拖拽复测 |
| Windows | 拖到四角 | 系统四分屏停靠 | 原生样式通过，待人工拖拽复测 |
| Windows | 双击标题栏空白区 | 最大化和还原切换 | 代码路径通过，待人工复测 |
| Windows | 标题栏右键 | 弹出系统菜单 | 代码路径通过，待人工复测 |
| Windows | Alt+Space | 弹出系统菜单 | 代码路径通过，待人工复测 |
| Windows | 左/右边框 | 水平方向原生缩放 | 命中区通过，待人工拖拽复测 |
| Windows | 上/下边框 | 垂直方向原生缩放 | 命中区通过，待人工拖拽复测 |
| Windows | 四个角 | 对角线方向原生缩放 | 命中区通过，待人工拖拽复测 |
| Windows | 固定宽度 | 禁止左右缩放 | 本机自动探测通过 |
| Windows | 固定高度 | 禁止上下缩放 | 本机自动探测通过 |
| Windows | 最大化边界 | 不覆盖任务栏 | `WM_GETMINMAXINFO` 代码路径通过 |
| macOS | 标题栏空白区拖动 | 通过平台窗口系统移动 | 待 macOS 复测 |
| macOS | 双击标题栏空白区 | 按系统设置缩放或最大化 | 待 macOS 复测 |
| macOS | 边框和角缩放 | 调用平台原生 resize | 待 macOS 复测 |
| macOS | 固定宽高约束 | 禁止对应方向缩放 | 待 macOS 复测 |
| Linux X11/Wayland | 标题栏空白区拖动 | 通过窗口管理器移动 | 待 Linux 复测 |
| Linux X11/Wayland | 边框和角缩放 | 调用窗口管理器 resize | 待 Linux 复测 |
| Linux X11/Wayland | 平铺/吸附 | 遵循当前桌面环境能力 | 待 Linux 复测 |
| Linux X11/Wayland | 固定宽高约束 | 禁止对应方向缩放 | 待 Linux 复测 |

## Windows 本机执行记录

测试环境：

- Windows
- Qt 5.15.2
- MinGW 8.1.0 64-bit
- 示例工程：`LqRibbonWin/Example/LqRibbonExample.pro`

执行项：

1. `qmake LqRibbonExample.pro`：通过。
2. `mingw32-make`：通过。
3. 启动示例程序：通过。
4. 截图检查 Ribbon、搜索框、快速访问栏和内容区：通过。
5. Win32 自动探测 `WM_NCHITTEST`、系统样式位、固定宽高约束：通过。
6. `WM_NCCALCSIZE` 和 `WM_GETMINMAXINFO`：代码路径审阅通过。
7. 桌面自动化插件当前不可用，未自动执行真实鼠标拖到屏幕边缘、
   拖下恢复和右键系统菜单；这些项保留为人工复测项。

macOS 和 Linux 需要在对应系统执行同一份文档中的清单后再改状态。
