#include <QApplication>
#include <QActionGroup>
#include <QBuffer>
#include <QComboBox>
#include <QDate>
#include <QDebug>
#include <QEventLoop>
#include <QFormLayout>
#include <QFontDatabase>
#include <QFrame>
#include <QHBoxLayout>
#include <QLabel>
#include <QMouseEvent>
#include <QPalette>
#include <QMdiArea>
#include <QMdiSubWindow>
#include <QMenu>
#include <QMessageBox>
#include <QPlainTextEdit>
#include <QSettings>
#include <QStyle>
#include <QStackedWidget>
#include <QTabBar>
#include <QTableWidget>
#include <QTemporaryDir>
#include <QTimer>
#include <QToolButton>
#include <QToolBar>
#include <QVBoxLayout>

#include "LqRibbon.h"

namespace {

constexpr int systemRibbonStyleComboValue = -1;
const char ribbonStyleSettingsKey[] = "Ribbon/Style";

struct RibbonStylePreviewPalette
{
    QString accent;
    QString ribbon;
    QString field;
    QString text;
    QString border;
};

struct RibbonStateTiming
{
    int hoverDurationMs;
    int pressedHoldMs;
};

struct RibbonStyleStatePalette
{
    QString normal;
    QString hover;
    QString pressed;
    QString text;
    QString border;
};

enum class FluentPreviewPhase
{
    Normal,
    Hover,
    Pressed
};

void processCollapseTestEvents()
{
    qApp->processEvents(QEventLoop::AllEvents, 50);
}

QTabBar *collapseTestTabBar(LqRibbon::RibbonBar *ribbonBar)
{
    return ribbonBar->findChild<QTabBar *>();
}

QStackedWidget *collapseTestStack(LqRibbon::RibbonBar *ribbonBar)
{
    return ribbonBar->findChild<QStackedWidget *>();
}

bool collapseTestCommandAreaVisible(LqRibbon::RibbonBar *ribbonBar)
{
    QStackedWidget *stack = collapseTestStack(ribbonBar);
    return stack && stack->isVisible() && stack->height() > 0;
}

void sendCollapseTestMouse(QWidget *widget,
                           QEvent::Type type,
                           const QPoint &pos,
                           Qt::MouseButton button,
                           Qt::MouseButtons buttons)
{
    QMouseEvent event(type,
                      pos,
                      widget->mapToGlobal(pos),
                      button,
                      buttons,
                      Qt::NoModifier);
    QApplication::sendEvent(widget, &event);
    processCollapseTestEvents();
}

void clickCollapseTestWidget(QWidget *widget, const QPoint &pos)
{
    sendCollapseTestMouse(widget,
                          QEvent::MouseButtonPress,
                          pos,
                          Qt::LeftButton,
                          Qt::LeftButton);
    sendCollapseTestMouse(widget,
                          QEvent::MouseButtonRelease,
                          pos,
                          Qt::LeftButton,
                          Qt::NoButton);
}

void clickCollapseTestTab(LqRibbon::RibbonBar *ribbonBar, int index)
{
    QTabBar *tabBar = collapseTestTabBar(ribbonBar);
    clickCollapseTestWidget(tabBar, tabBar->tabRect(index).center());
}

void doubleClickCollapseTestTab(LqRibbon::RibbonBar *ribbonBar, int index)
{
    QTabBar *tabBar = collapseTestTabBar(ribbonBar);
    const QPoint pos = tabBar->tabRect(index).center();
    clickCollapseTestWidget(tabBar, pos);
    sendCollapseTestMouse(tabBar,
                          QEvent::MouseButtonDblClick,
                          pos,
                          Qt::LeftButton,
                          Qt::LeftButton);
    sendCollapseTestMouse(tabBar,
                          QEvent::MouseButtonRelease,
                          pos,
                          Qt::LeftButton,
                          Qt::NoButton);
}

QToolButton *collapseTestActionButton(LqRibbon::RibbonBar *ribbonBar,
                                      QAction *action)
{
    const QList<QToolButton *> buttons = ribbonBar->findChildren<QToolButton *>();
    for (QToolButton *button : buttons) {
        if (button->defaultAction() == action) {
            return button;
        }
    }
    return nullptr;
}

int runCollapseTests(LqRibbon::RibbonMainWindow &mainWindow,
                     QAction *classicRibbonAction,
                     QAction *pinRibbonAction,
                     QAction *unpinRibbonAction,
                     QAction *displayOptionsTitleAction,
                     QAction *showTabsAndCommandsAction,
                     QAction *showTabsOnlyAction,
                     QAction *alwaysShowRibbonAction,
                     QAction *autoHideRibbonAction,
                     QLabel *collapseStatePreview)
{
    LqRibbon::RibbonBar *ribbonBar = mainWindow.ribbonBar();
    ribbonBar->setMinimizationEnabled(true);
    mainWindow.setFrameThemeEnabled(true);

    LqRibbon::RibbonPage *firstPage =
        ribbonBar->addPage(QStringLiteral("Collapse Test A"));
    LqRibbon::RibbonGroup *firstGroup =
        firstPage->addGroup(QStringLiteral("Actions"));
    QAction *firstAction = firstGroup->addAction(
        mainWindow.style()->standardIcon(QStyle::SP_DialogApplyButton),
        QStringLiteral("Apply"),
        Qt::ToolButtonTextUnderIcon);

    LqRibbon::RibbonPage *secondPage =
        ribbonBar->addPage(QStringLiteral("Collapse Test B"));
    LqRibbon::RibbonGroup *secondGroup =
        secondPage->addGroup(QStringLiteral("Actions"));
    QAction *secondAction = secondGroup->addAction(
        mainWindow.style()->standardIcon(QStyle::SP_DialogApplyButton),
        QStringLiteral("Connect"),
        Qt::ToolButtonTextUnderIcon);

    QStringList hits;
    bool firstActionSawCommandArea = false;
    bool secondActionSawCommandArea = false;
    QObject::connect(firstAction, &QAction::triggered, [&hits]() {
        hits << QStringLiteral("apply");
    });
    QObject::connect(firstAction,
                     &QAction::triggered,
                     [&firstActionSawCommandArea, ribbonBar]() {
                         firstActionSawCommandArea =
                             collapseTestCommandAreaVisible(ribbonBar);
                     });
    QObject::connect(secondAction, &QAction::triggered, [&hits]() {
        hits << QStringLiteral("connect");
    });
    QObject::connect(secondAction,
                     &QAction::triggered,
                     [&secondActionSawCommandArea, ribbonBar]() {
                         secondActionSawCommandArea =
                             collapseTestCommandAreaVisible(ribbonBar);
                     });

    const int firstIndex = ribbonBar->pageIndex(firstPage);
    const int secondIndex = ribbonBar->pageIndex(secondPage);
    QLabel *content = new QLabel(QStringLiteral("collapse test content"));
    content->setAlignment(Qt::AlignCenter);
    mainWindow.setCentralWidget(content);
    mainWindow.show();
    processCollapseTestEvents();

    auto reset = [&]() {
        hits.clear();
        firstActionSawCommandArea = false;
        secondActionSawCommandArea = false;
        ribbonBar->setMinimizationEnabled(true);
        ribbonBar->setCurrentPageIndex(firstIndex);
        ribbonBar->setSimplifiedMode(false);
        ribbonBar->setRibbonMinimized(false);
        processCollapseTestEvents();
    };

    auto require = [](bool condition, const QString &name) {
        if (!condition) {
            qWarning().noquote() << "FAIL" << name;
            return false;
        }
        qInfo().noquote() << "PASS" << name;
        return true;
    };

    reset();
    doubleClickCollapseTestTab(ribbonBar, firstIndex);
    if (!require(ribbonBar->isRibbonMinimized()
                     && !collapseTestCommandAreaVisible(ribbonBar),
                 QStringLiteral("double click expanded tab collapses"))) {
        return 1;
    }

    reset();
    ribbonBar->setRibbonMinimized(true);
    doubleClickCollapseTestTab(ribbonBar, firstIndex);
    if (!require(!ribbonBar->isRibbonMinimized()
                     && collapseTestCommandAreaVisible(ribbonBar),
                 QStringLiteral("double click collapsed tab restores"))) {
        return 1;
    }

    reset();
    ribbonBar->setRibbonMinimized(true);
    if (!require(ribbonBar->isRibbonMinimized()
                     && !collapseTestCommandAreaVisible(ribbonBar),
                 QStringLiteral("programmatic collapse hides command area"))) {
        return 1;
    }

    reset();
    const int fullRibbonHeight = ribbonBar->height();
    ribbonBar->setSimplifiedMode(true);
    processCollapseTestEvents();
    if (!require(ribbonBar->simplifiedMode()
                     && ribbonBar->simplifiedAction()->isChecked()
                     && !ribbonBar->isRibbonMinimized()
                     && collapseTestCommandAreaVisible(ribbonBar)
                     && ribbonBar->height() < fullRibbonHeight,
                 QStringLiteral("simplified mode keeps one-line command area"))) {
        return 1;
    }
    ribbonBar->setSimplifiedMode(false);
    processCollapseTestEvents();
    if (!require(!ribbonBar->simplifiedMode()
                     && !ribbonBar->simplifiedAction()->isChecked()
                     && ribbonBar->height() >= fullRibbonHeight,
                 QStringLiteral("classic mode restores full command area"))) {
        return 1;
    }

    reset();
    ribbonBar->setSimplifiedMode(true);
    ribbonBar->setRibbonMinimized(true);
    classicRibbonAction->trigger();
    processCollapseTestEvents();
    if (!require(!ribbonBar->simplifiedMode()
                     && !ribbonBar->isRibbonMinimized()
                     && collapseTestCommandAreaVisible(ribbonBar)
                     && ribbonBar->height() >= fullRibbonHeight,
                 QStringLiteral("classic command restores multi-line ribbon"))) {
        return 1;
    }

    reset();
    ribbonBar->setRibbonMinimized(true);
    pinRibbonAction->trigger();
    processCollapseTestEvents();
    if (!require(!ribbonBar->isMinimizationEnabled()
                     && !ribbonBar->isRibbonMinimized()
                     && collapseTestCommandAreaVisible(ribbonBar),
                 QStringLiteral("pin command keeps ribbon open"))) {
        return 1;
    }
    doubleClickCollapseTestTab(ribbonBar, firstIndex);
    if (!require(!ribbonBar->isRibbonMinimized()
                     && collapseTestCommandAreaVisible(ribbonBar),
                 QStringLiteral("pinned ribbon ignores collapse gesture"))) {
        return 1;
    }
    unpinRibbonAction->trigger();
    processCollapseTestEvents();
    if (!require(ribbonBar->isMinimizationEnabled()
                     && ribbonBar->isRibbonMinimized()
                     && !collapseTestCommandAreaVisible(ribbonBar),
                 QStringLiteral("unpin command allows ribbon collapse"))) {
        return 1;
    }
    clickCollapseTestTab(ribbonBar, firstIndex);
    if (!require(ribbonBar->isRibbonMinimized()
                     && collapseTestCommandAreaVisible(ribbonBar),
                 QStringLiteral("unpinned ribbon temporarily expands"))) {
        return 1;
    }

    reset();
    if (!require(displayOptionsTitleAction->menu()
                     && displayOptionsTitleAction->menu()->actions().size() >= 4,
                 QStringLiteral("display options menu exposes ribbon modes"))) {
        return 1;
    }
    showTabsOnlyAction->trigger();
    processCollapseTestEvents();
    if (!require(ribbonBar->isMinimizationEnabled()
                     && ribbonBar->isRibbonMinimized()
                     && !collapseTestCommandAreaVisible(ribbonBar),
                 QStringLiteral("display menu switches to tabs only"))) {
        return 1;
    }
    showTabsAndCommandsAction->trigger();
    processCollapseTestEvents();
    if (!require(ribbonBar->isMinimizationEnabled()
                     && !ribbonBar->simplifiedMode()
                     && !ribbonBar->isRibbonMinimized()
                     && collapseTestCommandAreaVisible(ribbonBar),
                 QStringLiteral("display menu shows tabs and commands"))) {
        return 1;
    }
    alwaysShowRibbonAction->trigger();
    processCollapseTestEvents();
    if (!require(!ribbonBar->isMinimizationEnabled()
                     && !ribbonBar->isRibbonMinimized()
                     && collapseTestCommandAreaVisible(ribbonBar),
                 QStringLiteral("display menu always shows ribbon"))) {
        return 1;
    }
    autoHideRibbonAction->trigger();
    processCollapseTestEvents();
    if (!require(ribbonBar->isMinimizationEnabled()
                     && ribbonBar->isRibbonMinimized()
                     && !collapseTestCommandAreaVisible(ribbonBar),
                 QStringLiteral("display menu auto hides ribbon"))) {
        return 1;
    }

    reset();
    if (!require(collapseStatePreview->text().contains(QStringLiteral("Expanded")),
                 QStringLiteral("collapse state preview starts expanded"))) {
        return 1;
    }
    ribbonBar->setRibbonMinimized(true);
    processCollapseTestEvents();
    if (!require(collapseStatePreview->text().contains(QStringLiteral("Collapsed")),
                 QStringLiteral("collapse state preview tracks collapsed"))) {
        return 1;
    }
    ribbonBar->setRibbonMinimized(false);
    ribbonBar->setSimplifiedMode(true);
    processCollapseTestEvents();
    if (!require(collapseStatePreview->text().contains(QStringLiteral("Simplified")),
                 QStringLiteral("collapse state preview tracks simplified"))) {
        return 1;
    }
    pinRibbonAction->trigger();
    processCollapseTestEvents();
    if (!require(collapseStatePreview->text().contains(QStringLiteral("Pinned")),
                 QStringLiteral("collapse state preview tracks pinned"))) {
        return 1;
    }
    autoHideRibbonAction->trigger();
    processCollapseTestEvents();
    if (!require(collapseStatePreview->text().contains(QStringLiteral("Collapsed")),
                 QStringLiteral("collapse state preview tracks auto hide"))) {
        return 1;
    }
    clickCollapseTestTab(ribbonBar, firstIndex);
    if (!require(ribbonBar->isRibbonTemporaryExpanded()
                     && collapseStatePreview->text().contains(
                         QStringLiteral("Temporary")),
                 QStringLiteral("collapse state preview tracks temporary expansion"))) {
        return 1;
    }

    reset();
    ribbonBar->setRibbonMinimized(true);
    clickCollapseTestTab(ribbonBar, firstIndex);
    if (!require(ribbonBar->isRibbonMinimized()
                     && collapseTestCommandAreaVisible(ribbonBar),
                 QStringLiteral("single click collapsed tab temporarily expands"))) {
        return 1;
    }

    QToolButton *firstButton = collapseTestActionButton(ribbonBar, firstAction);
    if (!require(firstButton != nullptr,
                 QStringLiteral("first action button exists"))) {
        return 1;
    }
    hits.clear();
    clickCollapseTestWidget(firstButton, firstButton->rect().center());
    if (!require(hits == QStringList{QStringLiteral("apply")},
                 QStringLiteral("action triggers while temporarily expanded"))) {
        return 1;
    }
    if (!require(firstActionSawCommandArea,
                 QStringLiteral("action callback sees command area"))) {
        return 1;
    }
    if (!require(ribbonBar->isRibbonMinimized()
                     && !collapseTestCommandAreaVisible(ribbonBar),
                 QStringLiteral("action hides temporary expansion"))) {
        return 1;
    }

    reset();
    ribbonBar->setRibbonMinimized(true);
    clickCollapseTestTab(ribbonBar, firstIndex);
    clickCollapseTestWidget(content, content->rect().center());
    if (!require(ribbonBar->isRibbonMinimized()
                     && !collapseTestCommandAreaVisible(ribbonBar),
                 QStringLiteral("outside click hides temporary expansion"))) {
        return 1;
    }

    reset();
    ribbonBar->setRibbonMinimized(true);
    clickCollapseTestTab(ribbonBar, firstIndex);
    doubleClickCollapseTestTab(ribbonBar, firstIndex);
    if (!require(!ribbonBar->isRibbonMinimized()
                     && collapseTestCommandAreaVisible(ribbonBar),
                 QStringLiteral("double click temporary tab restores permanently"))) {
        return 1;
    }

    reset();
    ribbonBar->setRibbonMinimized(true);
    clickCollapseTestTab(ribbonBar, secondIndex);
    if (!require(ribbonBar->currentIndex() == secondIndex
                     && ribbonBar->isRibbonMinimized()
                     && collapseTestCommandAreaVisible(ribbonBar),
                 QStringLiteral("collapsed click other page selects and expands"))) {
        return 1;
    }
    QToolButton *secondButton = collapseTestActionButton(ribbonBar, secondAction);
    if (!require(secondButton != nullptr,
                 QStringLiteral("second action button exists"))) {
        return 1;
    }
    hits.clear();
    clickCollapseTestWidget(secondButton, secondButton->rect().center());
    if (!require(hits == QStringList{QStringLiteral("connect")},
                 QStringLiteral("other page action triggers while expanded"))) {
        return 1;
    }
    if (!require(secondActionSawCommandArea,
                 QStringLiteral("other page action callback sees command area"))) {
        return 1;
    }

    reset();
    ribbonBar->setMinimizationEnabled(false);
    doubleClickCollapseTestTab(ribbonBar, firstIndex);
    if (!require(!ribbonBar->isRibbonMinimized()
                     && collapseTestCommandAreaVisible(ribbonBar),
                 QStringLiteral("minimization disabled blocks collapse"))) {
        return 1;
    }

    return 0;
}

LqRibbon::RibbonBar::RibbonStyle ribbonStyleFromText(
    const QString &strText,
    LqRibbon::RibbonBar::RibbonStyle fallback =
        LqRibbon::RibbonBar::Office2016Blue)
{
    const QString key = strText.trimmed().toLower().remove(QLatin1Char('-'))
        .remove(QLatin1Char('_')).remove(QLatin1Char(' '));
    if (key == QStringLiteral("office2019colorful")
        || key == QStringLiteral("colorful")) {
        return LqRibbon::RibbonBar::Office2019Colorful;
    }
    if (key == QStringLiteral("microsoft365light")
        || key == QStringLiteral("m365light")
        || key == QStringLiteral("light")) {
        return LqRibbon::RibbonBar::Microsoft365Light;
    }
    if (key == QStringLiteral("microsoft365dark")
        || key == QStringLiteral("m365dark")
        || key == QStringLiteral("dark")) {
        return LqRibbon::RibbonBar::Microsoft365Dark;
    }
    if (key == QStringLiteral("office2016blue")
        || key == QStringLiteral("blue")) {
        return LqRibbon::RibbonBar::Office2016Blue;
    }
    return fallback;
}

LqRibbon::RibbonBar::RibbonStyle systemRibbonStyle()
{
    const QColor windowColor = qApp->palette().color(QPalette::Window);
    return windowColor.lightness() < 128
        ? LqRibbon::RibbonBar::Microsoft365Dark
        : LqRibbon::RibbonBar::Microsoft365Light;
}

bool isSystemRibbonStyleText(const QString &strText)
{
    const QString key = strText.trimmed().toLower().remove(QLatin1Char('-'))
        .remove(QLatin1Char('_')).remove(QLatin1Char(' '));
    return key == QStringLiteral("system")
        || key == QStringLiteral("systemdefault");
}

QString ribbonStyleSettingsValue(LqRibbon::RibbonBar::RibbonStyle style)
{
    switch (style) {
    case LqRibbon::RibbonBar::Office2019Colorful:
        return QStringLiteral("office2019colorful");
    case LqRibbon::RibbonBar::Microsoft365Light:
        return QStringLiteral("microsoft365light");
    case LqRibbon::RibbonBar::Microsoft365Dark:
        return QStringLiteral("microsoft365dark");
    case LqRibbon::RibbonBar::Office2016Blue:
    default:
        return QStringLiteral("office2016blue");
    }
}

QString ribbonStyleChoiceFromComboIndex(const QComboBox *combo, int index)
{
    const int value = combo->itemData(index).toInt();
    if (value == systemRibbonStyleComboValue) {
        return QStringLiteral("system");
    }
    return ribbonStyleSettingsValue(
        static_cast<LqRibbon::RibbonBar::RibbonStyle>(value));
}

QString savedRibbonStyleChoice(const QSettings &settings)
{
    return settings.value(QString::fromLatin1(ribbonStyleSettingsKey))
        .toString().trimmed();
}

void saveRibbonStyleChoice(QSettings &settings, const QString &choice)
{
    settings.setValue(QString::fromLatin1(ribbonStyleSettingsKey), choice);
    settings.sync();
}

QString fluentPreviewPhaseName(FluentPreviewPhase phase)
{
    switch (phase) {
    case FluentPreviewPhase::Hover:
        return QStringLiteral("hover");
    case FluentPreviewPhase::Pressed:
        return QStringLiteral("pressed");
    case FluentPreviewPhase::Normal:
    default:
        return QStringLiteral("normal");
    }
}

RibbonStateTiming ribbonStateTiming(LqRibbon::RibbonBar::RibbonStyle style)
{
    switch (style) {
    case LqRibbon::RibbonBar::Microsoft365Light:
    case LqRibbon::RibbonBar::Microsoft365Dark:
        return {120, 80};
    case LqRibbon::RibbonBar::Office2019Colorful:
    case LqRibbon::RibbonBar::Office2016Blue:
    default:
        return {0, 0};
    }
}

RibbonStyleStatePalette ribbonStyleStatePalette(
    LqRibbon::RibbonBar::RibbonStyle style)
{
    switch (style) {
    case LqRibbon::RibbonBar::Office2019Colorful:
        return {
            QStringLiteral("#ffffff"),
            QStringLiteral("#deecf9"),
            QStringLiteral("#c7e0f4"),
            QStringLiteral("#202020"),
            QStringLiteral("#c8c8c8")
        };
    case LqRibbon::RibbonBar::Microsoft365Light:
        return {
            QStringLiteral("#ffffff"),
            QStringLiteral("#e5f1fb"),
            QStringLiteral("#cfe4fa"),
            QStringLiteral("#242424"),
            QStringLiteral("#e5e5e5")
        };
    case LqRibbon::RibbonBar::Microsoft365Dark:
        return {
            QStringLiteral("#2d2d2d"),
            QStringLiteral("#3a3a3a"),
            QStringLiteral("#4a4a4a"),
            QStringLiteral("#f3f2f1"),
            QStringLiteral("#3a3a3a")
        };
    case LqRibbon::RibbonBar::Office2016Blue:
    default:
        return {
            QStringLiteral("#ffffff"),
            QStringLiteral("#8cc8f7"),
            QStringLiteral("#c5ddfa"),
            QStringLiteral("#202020"),
            QStringLiteral("#c8c8c8")
        };
    }
}

RibbonStylePreviewPalette ribbonStylePreviewPalette(
    LqRibbon::RibbonBar::RibbonStyle style)
{
    switch (style) {
    case LqRibbon::RibbonBar::Office2019Colorful:
        return {
            QStringLiteral("#185abd"),
            QStringLiteral("#f3f2f1"),
            QStringLiteral("#ffffff"),
            QStringLiteral("#202020"),
            QStringLiteral("#c8c8c8")
        };
    case LqRibbon::RibbonBar::Microsoft365Light:
        return {
            QStringLiteral("#0f6cbd"),
            QStringLiteral("#fbfbfb"),
            QStringLiteral("#ffffff"),
            QStringLiteral("#242424"),
            QStringLiteral("#e5e5e5")
        };
    case LqRibbon::RibbonBar::Microsoft365Dark:
        return {
            QStringLiteral("#60cdff"),
            QStringLiteral("#1f1f1f"),
            QStringLiteral("#2d2d2d"),
            QStringLiteral("#f3f2f1"),
            QStringLiteral("#3a3a3a")
        };
    case LqRibbon::RibbonBar::Office2016Blue:
    default:
        return {
            QStringLiteral("#2b579a"),
            QStringLiteral("#f3f3f3"),
            QStringLiteral("#ffffff"),
            QStringLiteral("#202020"),
            QStringLiteral("#c8c8c8")
        };
    }
}

class FluentStateTimingPreview : public QToolButton
{
public:
    explicit FluentStateTimingPreview(QWidget *parent = nullptr)
        : QToolButton(parent)
    {
        setObjectName(QStringLiteral("lqRibbonStateTimingPreview"));
        setFixedSize(30, 24);
        setFocusPolicy(Qt::NoFocus);
        setIconSize(QSize(14, 14));
        setToolTip(QObject::tr("Hover and press timing preview"));
        m_hoverTimer.setSingleShot(true);
        m_pressedResetTimer.setSingleShot(true);
        QObject::connect(&m_hoverTimer, &QTimer::timeout, this, [this]() {
            setPreviewPhase(FluentPreviewPhase::Hover);
        });
        QObject::connect(&m_pressedResetTimer, &QTimer::timeout, this, [this]() {
            restoreAfterPressed();
        });
        applyRibbonStyle(LqRibbon::RibbonBar::Office2016Blue);
    }

    void applyRibbonStyle(LqRibbon::RibbonBar::RibbonStyle style)
    {
        m_style = style;
        m_timing = ribbonStateTiming(style);
        setProperty("previewStyle", static_cast<int>(style));
        setProperty("hoverDurationMs", m_timing.hoverDurationMs);
        setProperty("pressedHoldMs", m_timing.pressedHoldMs);
        updatePreviewStyleSheet();
    }

    int hoverDurationMs() const
    {
        return m_timing.hoverDurationMs;
    }

    int pressedHoldMs() const
    {
        return m_timing.pressedHoldMs;
    }

    QString stateName() const
    {
        return fluentPreviewPhaseName(m_phase);
    }

    void beginHoverPreview()
    {
        m_hovered = true;
        m_pressedResetTimer.stop();
        if (m_phase == FluentPreviewPhase::Pressed) {
            return;
        }
        if (m_timing.hoverDurationMs > 0) {
            m_hoverTimer.start(m_timing.hoverDurationMs);
        } else {
            setPreviewPhase(FluentPreviewPhase::Hover);
        }
    }

    void leavePreview()
    {
        m_hovered = false;
        m_hoverTimer.stop();
        m_pressedResetTimer.stop();
        setPreviewPhase(FluentPreviewPhase::Normal);
    }

    void beginPressedPreview()
    {
        m_hoverTimer.stop();
        m_pressedResetTimer.stop();
        setPreviewPhase(FluentPreviewPhase::Pressed);
    }

    void endPressedPreview()
    {
        if (m_phase != FluentPreviewPhase::Pressed) {
            return;
        }
        if (m_timing.pressedHoldMs > 0) {
            m_pressedResetTimer.start(m_timing.pressedHoldMs);
        } else {
            restoreAfterPressed();
        }
    }

protected:
#if QT_VERSION >= QT_VERSION_CHECK(6, 0, 0)
    void enterEvent(QEnterEvent *event) override
#else
    void enterEvent(QEvent *event) override
#endif
    {
        beginHoverPreview();
        QToolButton::enterEvent(event);
    }

    void leaveEvent(QEvent *event) override
    {
        leavePreview();
        QToolButton::leaveEvent(event);
    }

    void mousePressEvent(QMouseEvent *event) override
    {
        beginPressedPreview();
        QToolButton::mousePressEvent(event);
    }

    void mouseReleaseEvent(QMouseEvent *event) override
    {
        QToolButton::mouseReleaseEvent(event);
        endPressedPreview();
    }

private:
    void restoreAfterPressed()
    {
        setPreviewPhase(m_hovered ? FluentPreviewPhase::Hover
                                  : FluentPreviewPhase::Normal);
    }

    void setPreviewPhase(FluentPreviewPhase phase)
    {
        if (m_phase == phase) {
            return;
        }
        m_phase = phase;
        setProperty("statePhase", fluentPreviewPhaseName(m_phase));
        updatePreviewStyleSheet();
    }

    void updatePreviewStyleSheet()
    {
        const RibbonStyleStatePalette palette = ribbonStyleStatePalette(m_style);
        const QString strBackground =
            m_phase == FluentPreviewPhase::Pressed
                ? palette.pressed
                : m_phase == FluentPreviewPhase::Hover
                    ? palette.hover
                    : palette.normal;
        setProperty("statePhase", fluentPreviewPhaseName(m_phase));
        setStyleSheet(
            QStringLiteral(
                "QToolButton#lqRibbonStateTimingPreview {"
                "background: %1;"
                "border: 1px solid %2;"
                "border-radius: 3px;"
                "padding: 0px;"
                "color: %3;"
                "}")
                .arg(strBackground, palette.border, palette.text));
    }

    LqRibbon::RibbonBar::RibbonStyle m_style =
        LqRibbon::RibbonBar::Office2016Blue;
    RibbonStateTiming m_timing = {0, 0};
    FluentPreviewPhase m_phase = FluentPreviewPhase::Normal;
    bool m_hovered = false;
    QTimer m_hoverTimer;
    QTimer m_pressedResetTimer;
};

QString ribbonStylePreviewSwatchSheet(const QString &color,
                                      const QString &border)
{
    return QStringLiteral(
               "QFrame { background: %1; border: 1px solid %2; }")
        .arg(color, border);
}

QFrame *ribbonStylePreviewSwatch(QWidget *parent, const QString &name)
{
    QFrame *swatch = new QFrame(parent);
    swatch->setObjectName(name);
    swatch->setFixedSize(24, 18);
    swatch->setFrameShape(QFrame::NoFrame);
    swatch->setSizePolicy(QSizePolicy::Fixed, QSizePolicy::Fixed);
    return swatch;
}

QWidget *createRibbonStylePreview(QWidget *parent)
{
    QWidget *preview = new QWidget(parent);
    preview->setObjectName(QStringLiteral("lqRibbonStylePreview"));
    preview->setFixedSize(128, 24);
    preview->setSizePolicy(QSizePolicy::Fixed, QSizePolicy::Fixed);

    QHBoxLayout *layout = new QHBoxLayout(preview);
    layout->setContentsMargins(0, 2, 0, 2);
    layout->setSpacing(4);
    layout->addWidget(ribbonStylePreviewSwatch(
        preview, QStringLiteral("lqRibbonStylePreviewAccent")));
    layout->addWidget(ribbonStylePreviewSwatch(
        preview, QStringLiteral("lqRibbonStylePreviewRibbon")));
    layout->addWidget(ribbonStylePreviewSwatch(
        preview, QStringLiteral("lqRibbonStylePreviewField")));
    layout->addWidget(ribbonStylePreviewSwatch(
        preview, QStringLiteral("lqRibbonStylePreviewText")));
    return preview;
}

void setRibbonStylePreviewColor(QWidget *preview,
                                const QString &name,
                                const QString &color,
                                const QString &border)
{
    QFrame *swatch = preview->findChild<QFrame *>(name);
    if (!swatch) {
        return;
    }
    swatch->setProperty("previewColor", color);
    swatch->setStyleSheet(ribbonStylePreviewSwatchSheet(color, border));
}

void updateRibbonStylePreview(QWidget *preview,
                              LqRibbon::RibbonBar::RibbonStyle style)
{
    if (!preview) {
        return;
    }

    const RibbonStylePreviewPalette palette =
        ribbonStylePreviewPalette(style);
    preview->setProperty("previewStyle", static_cast<int>(style));
    preview->setToolTip(LqRibbon::RibbonBar::ribbonStyleName(style));
    setRibbonStylePreviewColor(preview,
                               QStringLiteral("lqRibbonStylePreviewAccent"),
                               palette.accent,
                               palette.border);
    setRibbonStylePreviewColor(preview,
                               QStringLiteral("lqRibbonStylePreviewRibbon"),
                               palette.ribbon,
                               palette.border);
    setRibbonStylePreviewColor(preview,
                               QStringLiteral("lqRibbonStylePreviewField"),
                               palette.field,
                               palette.border);
    setRibbonStylePreviewColor(preview,
                               QStringLiteral("lqRibbonStylePreviewText"),
                               palette.text,
                               palette.border);
}

void updateFluentStateTimingPreview(FluentStateTimingPreview *preview,
                                    LqRibbon::RibbonBar::RibbonStyle style)
{
    if (!preview) {
        return;
    }
    preview->applyRibbonStyle(style);
}

LqRibbon::RibbonBar::RibbonStyle ribbonStyleFromComboIndex(
    const QComboBox *combo,
    int index)
{
    const int value = combo->itemData(index).toInt();
    return value == systemRibbonStyleComboValue
        ? systemRibbonStyle()
        : static_cast<LqRibbon::RibbonBar::RibbonStyle>(value);
}

void waitForStylePreviewTimer(int durationMs)
{
    QEventLoop loop;
    QTimer::singleShot(durationMs, &loop, &QEventLoop::quit);
    loop.exec();
}

int runStyleTests(LqRibbon::RibbonMainWindow &mainWindow,
                  QComboBox *styleCombo,
                  QWidget *stylePreview,
                  FluentStateTimingPreview *stateTimingPreview)
{
    LqRibbon::RibbonBar *ribbonBar = mainWindow.ribbonBar();
    auto require = [](bool condition, const QString &name) {
        if (!condition) {
            qWarning().noquote() << "FAIL" << name;
            return false;
        }
        qInfo().noquote() << "PASS" << name;
        return true;
    };

    if (!require(ribbonBar->ribbonStyle()
                     == LqRibbon::RibbonBar::Office2016Blue,
                 QStringLiteral("default style is Office 2016 Blue"))) {
        return 1;
    }
    if (!require(stylePreview != nullptr,
                 QStringLiteral("example exposes style preview"))) {
        return 1;
    }
    if (!require(stylePreview->property("previewStyle").toInt()
                     == static_cast<int>(LqRibbon::RibbonBar::Office2016Blue),
                 QStringLiteral("style preview defaults to Office 2016 Blue"))) {
        return 1;
    }
    if (!require(stateTimingPreview != nullptr,
                 QStringLiteral("example exposes state timing preview"))) {
        return 1;
    }
    if (!require(stateTimingPreview->hoverDurationMs() == 0
                     && stateTimingPreview->pressedHoldMs() == 0,
                 QStringLiteral("legacy themes use immediate state timing"))) {
        return 1;
    }

    QTemporaryDir settingsDir;
    if (!require(settingsDir.isValid(),
                 QStringLiteral("style settings temp directory exists"))) {
        return 1;
    }
    const QString strSettingsPath =
        settingsDir.filePath(QStringLiteral("style.ini"));
    {
        QSettings settings(strSettingsPath, QSettings::IniFormat);
        saveRibbonStyleChoice(
            settings,
            ribbonStyleSettingsValue(LqRibbon::RibbonBar::Microsoft365Dark));
    }
    QSettings savedSettings(strSettingsPath, QSettings::IniFormat);
    if (!require(savedRibbonStyleChoice(savedSettings)
                     == QStringLiteral("microsoft365dark"),
                 QStringLiteral("style choice persists to settings"))) {
        return 1;
    }
    savedSettings.remove(QString::fromLatin1(ribbonStyleSettingsKey));
    if (!require(savedRibbonStyleChoice(savedSettings).isEmpty(),
                 QStringLiteral("empty settings keep default style path"))) {
        return 1;
    }

    const LqRibbon::RibbonBar::RibbonStyle styles[] = {
        LqRibbon::RibbonBar::Office2016Blue,
        LqRibbon::RibbonBar::Office2019Colorful,
        LqRibbon::RibbonBar::Microsoft365Light,
        LqRibbon::RibbonBar::Microsoft365Dark
    };

    for (LqRibbon::RibbonBar::RibbonStyle style : styles) {
        mainWindow.setRibbonStyle(style);
        if (!require(ribbonBar->ribbonStyle() == style,
                     QStringLiteral("set style %1")
                         .arg(LqRibbon::RibbonBar::ribbonStyleName(style)))) {
            return 1;
        }
        updateRibbonStylePreview(stylePreview, style);
        updateFluentStateTimingPreview(stateTimingPreview, style);
        if (!require(stylePreview->property("previewStyle").toInt()
                         == static_cast<int>(style),
                     QStringLiteral("preview swatch updates for %1")
                         .arg(LqRibbon::RibbonBar::ribbonStyleName(style)))) {
            return 1;
        }
        if (!require(ribbonBar->styleSheet().contains(
                         style == LqRibbon::RibbonBar::Office2016Blue
                             ? QStringLiteral("#2b579a")
                             : QStringLiteral("#")),
                     QStringLiteral("stylesheet generated for %1")
                         .arg(LqRibbon::RibbonBar::ribbonStyleName(style)))) {
            return 1;
        }
        const QString strExpectedTabRadius =
            (style == LqRibbon::RibbonBar::Microsoft365Light
             || style == LqRibbon::RibbonBar::Microsoft365Dark)
                ? QStringLiteral("border-radius: 6px 6px 0px 0px;")
                : QStringLiteral("border-radius: 0px;");
        if (!require(ribbonBar->styleSheet().contains(strExpectedTabRadius),
                     QStringLiteral("tab radius generated for %1")
                         .arg(LqRibbon::RibbonBar::ribbonStyleName(style)))) {
            return 1;
        }
        const bool isMicrosoft365 =
            style == LqRibbon::RibbonBar::Microsoft365Light
            || style == LqRibbon::RibbonBar::Microsoft365Dark;
        const QString strExpectedTabBorder =
            isMicrosoft365
                ? (style == LqRibbon::RibbonBar::Microsoft365Dark
                       ? QStringLiteral("#3a3a3a")
                       : QStringLiteral("#e5e5e5"))
                : QStringLiteral("#c8c8c8");
        if (!require(ribbonBar->styleSheet().contains(
                         QStringLiteral("border-left: 1px solid %1;")
                             .arg(strExpectedTabBorder)),
                     QStringLiteral("soft tab border generated for %1")
                         .arg(LqRibbon::RibbonBar::ribbonStyleName(style)))) {
            return 1;
        }
        const QString strExpectedCommandBorder =
            isMicrosoft365
                ? strExpectedTabBorder
                : (style == LqRibbon::RibbonBar::Office2019Colorful
                       ? QStringLiteral("#deecf9")
                       : QStringLiteral("#8cc8f7"));
        if (!require(ribbonBar->styleSheet().contains(
                         QStringLiteral("border-color: %1;")
                             .arg(strExpectedCommandBorder)),
                     QStringLiteral("soft command border generated for %1")
                         .arg(LqRibbon::RibbonBar::ribbonStyleName(style)))) {
            return 1;
        }
        const RibbonStateTiming expectedTiming = ribbonStateTiming(style);
        if (!require(stateTimingPreview->property("hoverDurationMs").toInt()
                         == expectedTiming.hoverDurationMs
                     && stateTimingPreview->property("pressedHoldMs").toInt()
                         == expectedTiming.pressedHoldMs,
                     QStringLiteral("state timing tokens generated for %1")
                         .arg(LqRibbon::RibbonBar::ribbonStyleName(style)))) {
            return 1;
        }
    }

    updateFluentStateTimingPreview(stateTimingPreview,
                                   LqRibbon::RibbonBar::Microsoft365Light);
    stateTimingPreview->leavePreview();
    stateTimingPreview->beginHoverPreview();
    if (!require(stateTimingPreview->stateName() == QStringLiteral("normal"),
                 QStringLiteral("Fluent hover waits before activation"))) {
        return 1;
    }
    waitForStylePreviewTimer(stateTimingPreview->hoverDurationMs() + 30);
    if (!require(stateTimingPreview->stateName() == QStringLiteral("hover"),
                 QStringLiteral("Fluent hover activates after timing"))) {
        return 1;
    }
    stateTimingPreview->beginPressedPreview();
    stateTimingPreview->endPressedPreview();
    if (!require(stateTimingPreview->stateName() == QStringLiteral("pressed"),
                 QStringLiteral("Fluent pressed state holds after release"))) {
        return 1;
    }
    waitForStylePreviewTimer(stateTimingPreview->pressedHoldMs() + 30);
    if (!require(stateTimingPreview->stateName() == QStringLiteral("hover"),
                 QStringLiteral("Fluent pressed state restores after timing"))) {
        return 1;
    }
    stateTimingPreview->leavePreview();

    int changedCount = 0;
    QObject::connect(ribbonBar,
                     &LqRibbon::RibbonBar::ribbonStyleChanged,
                     ribbonBar,
                     [&changedCount](LqRibbon::RibbonBar::RibbonStyle) {
                         ++changedCount;
                     });
    mainWindow.setRibbonStyle(LqRibbon::RibbonBar::Office2016Blue);
    const int afterChange = changedCount;
    mainWindow.setRibbonStyle(LqRibbon::RibbonBar::Office2016Blue);
    if (!require(changedCount == afterChange,
                 QStringLiteral("reapplying same style emits no duplicate"))) {
        return 1;
    }

    if (styleCombo) {
        const int darkIndex = styleCombo->findData(
            static_cast<int>(LqRibbon::RibbonBar::Microsoft365Dark));
        styleCombo->setCurrentIndex(darkIndex);
        if (!require(ribbonBar->ribbonStyle()
                         == LqRibbon::RibbonBar::Microsoft365Dark,
                     QStringLiteral("example combo switches style"))) {
            return 1;
        }
        if (!require(stylePreview->property("previewStyle").toInt()
                         == static_cast<int>(
                             LqRibbon::RibbonBar::Microsoft365Dark),
                     QStringLiteral("style preview tracks combo selection"))) {
            return 1;
        }

        const int systemIndex = styleCombo->findData(systemRibbonStyleComboValue);
        if (!require(systemIndex >= 0,
                     QStringLiteral("example combo exposes system style"))) {
            return 1;
        }
        styleCombo->setCurrentIndex(systemIndex);
        if (!require(styleCombo->currentText() == QStringLiteral("System"),
                     QStringLiteral("system style remains visible in combo"))) {
            return 1;
        }
        if (!require(ribbonBar->ribbonStyle() == systemRibbonStyle(),
                     QStringLiteral("system style follows application palette"))) {
            return 1;
        }
        if (!require(stylePreview->property("previewStyle").toInt()
                         == static_cast<int>(systemRibbonStyle()),
                     QStringLiteral("style preview tracks system style"))) {
            return 1;
        }
    }

    return 0;
}

} // namespace

int main(int argc, char *argv[])
{
    QStringList rawArgumentList;
    rawArgumentList.reserve(argc);
    for (int index = 0; index < argc; ++index) {
        rawArgumentList.append(QString::fromLocal8Bit(argv[index]));
    }

    QApplication application(argc, argv);
    application.setApplicationName(QStringLiteral("LqRibbon Example"));
    application.setOrganizationName(QStringLiteral("LqRibbon"));
    for (const QString &fontPath : {
             QStringLiteral("C:/Windows/Fonts/segoeui.ttf"),
             QStringLiteral("C:/Windows/Fonts/arial.ttf"),
         }) {
        const int fontId = QFontDatabase::addApplicationFont(fontPath);
        const QStringList families =
            QFontDatabase::applicationFontFamilies(fontId);
        if (!families.isEmpty()) {
            application.setFont(QFont(families.constFirst(), 9));
            break;
        }
    }

    const QStringList argumentList = rawArgumentList;
    const int previewIndex = argumentList.indexOf(QStringLiteral("--grab-preview"));
    const bool previewRequested = previewIndex >= 0
        && previewIndex + 1 < argumentList.count();
    const QString strPreviewPath = previewRequested
        ? argumentList.at(previewIndex + 1)
        : QString();
    const bool searchPreviewRequested =
        argumentList.contains(QStringLiteral("--grab-search-preview"));
    const bool collapsedPreviewRequested =
        argumentList.contains(QStringLiteral("--grab-collapsed-preview"));
    const bool simplifiedPreviewRequested =
        argumentList.contains(QStringLiteral("--grab-simplified-preview"));
    const bool temporaryPreviewRequested =
        argumentList.contains(QStringLiteral("--grab-temporary-preview"));
    const bool mdiPreviewRequested =
        argumentList.contains(QStringLiteral("--grab-mdi-preview"));
    const bool tabPreviewRequested =
        argumentList.contains(QStringLiteral("--grab-tab-preview"));
    const bool controlsPreviewRequested =
        argumentList.contains(QStringLiteral("--grab-controls-preview"));
    const bool galleryPreviewRequested =
        argumentList.contains(QStringLiteral("--grab-gallery-preview"));
    const bool shellPreviewRequested =
        argumentList.contains(QStringLiteral("--grab-shell-preview"));
    const bool stylePreviewRequested =
        argumentList.contains(QStringLiteral("--grab-style-preview"));
    const bool collapseTestsRequested =
        argumentList.contains(QStringLiteral("--run-collapse-tests"));
    const bool styleTestsRequested =
        argumentList.contains(QStringLiteral("--run-style-tests"));
    const bool deterministicStyleRequested =
        previewRequested || collapseTestsRequested || styleTestsRequested;
    QSettings settings;
    const int styleArgumentIndex = argumentList.indexOf(QStringLiteral("--style"));
    const bool hasStyleArgument =
        styleArgumentIndex >= 0 && styleArgumentIndex + 1 < argumentList.count();
    const QString strRequestedStyleChoice =
        hasStyleArgument
            ? argumentList.at(styleArgumentIndex + 1)
            : (deterministicStyleRequested ? QString() : savedRibbonStyleChoice(settings));
    const LqRibbon::RibbonBar::RibbonStyle previewRibbonStyle =
        strRequestedStyleChoice.isEmpty()
            ? (stylePreviewRequested
                   ? LqRibbon::RibbonBar::Microsoft365Light
                   : LqRibbon::RibbonBar::Office2016Blue)
            : (isSystemRibbonStyleText(strRequestedStyleChoice)
                   ? systemRibbonStyle()
                   : ribbonStyleFromText(
                         strRequestedStyleChoice,
                         stylePreviewRequested
                             ? LqRibbon::RibbonBar::Microsoft365Light
                             : LqRibbon::RibbonBar::Office2016Blue));
    const bool systemStyleRequested =
        isSystemRibbonStyleText(strRequestedStyleChoice);
    const bool persistStyleChoice = !deterministicStyleRequested;

    LqRibbon::RibbonMainWindow mainWindow;
    mainWindow.setWindowTitle(QObject::tr("LqRibbon Example"));
    mainWindow.resize(920, 560);
    if (controlsPreviewRequested || galleryPreviewRequested
        || shellPreviewRequested || simplifiedPreviewRequested
        || temporaryPreviewRequested || stylePreviewRequested) {
        mainWindow.resize(1180, 560);
    }

    LqRibbon::RibbonPage *generalPage = mainWindow.ribbonBar()->addPage(QObject::tr("General"));
    LqRibbon::RibbonGroup *viewGroup = generalPage->addGroup(QObject::tr("View"));

    QAction *fullScreenAction = viewGroup->addAction(
        mainWindow.style()->standardIcon(QStyle::SP_TitleBarMaxButton),
        QObject::tr("Full Screen"),
        Qt::ToolButtonTextUnderIcon);

    QAction *mdiAction = viewGroup->addAction(
        mainWindow.style()->standardIcon(QStyle::SP_FileDialogDetailedView),
        QObject::tr("Mdi Mode"),
        Qt::ToolButtonTextBesideIcon);

    QAction *tabAction = viewGroup->addAction(
        mainWindow.style()->standardIcon(QStyle::SP_FileDialogListView),
        QObject::tr("Tab Mode"),
        Qt::ToolButtonTextBesideIcon);

    LqRibbon::RibbonGroup *styleSwitchGroup =
        generalPage->addGroup(QObject::tr("Style"));
    LqRibbon::RibbonComboBoxControl *styleComboControl =
        new LqRibbon::RibbonComboBoxControl(styleSwitchGroup);
    QComboBox *styleCombo = styleComboControl->widget();
    styleCombo->setObjectName(QStringLiteral("lqRibbonStyleCombo"));
    styleCombo->setMinimumWidth(220);
    const LqRibbon::RibbonBar::RibbonStyle styleItems[] = {
        LqRibbon::RibbonBar::Office2016Blue,
        LqRibbon::RibbonBar::Office2019Colorful,
        LqRibbon::RibbonBar::Microsoft365Light,
        LqRibbon::RibbonBar::Microsoft365Dark
    };
    for (LqRibbon::RibbonBar::RibbonStyle style : styleItems) {
        const QString strComboText =
            style == LqRibbon::RibbonBar::Microsoft365Light
                ? QStringLiteral("M365 Light")
                : style == LqRibbon::RibbonBar::Microsoft365Dark
                    ? QStringLiteral("M365 Dark")
                    : LqRibbon::RibbonBar::ribbonStyleName(style);
        styleCombo->addItem(strComboText, static_cast<int>(style));
        styleCombo->setItemData(styleCombo->count() - 1,
                                LqRibbon::RibbonBar::ribbonStyleName(style),
                                Qt::ToolTipRole);
    }
    styleCombo->addItem(QStringLiteral("System"), systemRibbonStyleComboValue);
    styleCombo->setItemData(styleCombo->count() - 1,
                            QObject::tr("Follow current system light/dark palette"),
                            Qt::ToolTipRole);
    styleSwitchGroup->addWidget(styleComboControl);
    QWidget *stylePreviewRow = new QWidget(styleSwitchGroup);
    stylePreviewRow->setObjectName(QStringLiteral("lqRibbonStylePreviewRow"));
    stylePreviewRow->setFixedSize(164, 24);
    stylePreviewRow->setSizePolicy(QSizePolicy::Fixed, QSizePolicy::Fixed);
    QHBoxLayout *stylePreviewRowLayout = new QHBoxLayout(stylePreviewRow);
    stylePreviewRowLayout->setContentsMargins(0, 0, 0, 0);
    stylePreviewRowLayout->setSpacing(4);
    QWidget *stylePreview = createRibbonStylePreview(stylePreviewRow);
    FluentStateTimingPreview *stateTimingPreview =
        new FluentStateTimingPreview(stylePreviewRow);
    stateTimingPreview->setIcon(
        mainWindow.style()->standardIcon(QStyle::SP_DialogApplyButton));
    updateRibbonStylePreview(stylePreview, LqRibbon::RibbonBar::Office2016Blue);
    updateFluentStateTimingPreview(stateTimingPreview,
                                   LqRibbon::RibbonBar::Office2016Blue);
    stylePreviewRowLayout->addWidget(stylePreview);
    stylePreviewRowLayout->addWidget(stateTimingPreview);
    styleSwitchGroup->addWidget(stylePreviewRow);
    QObject::connect(styleCombo,
                     QOverload<int>::of(&QComboBox::highlighted),
                     [styleCombo, stylePreview, stateTimingPreview](int index) {
                         const LqRibbon::RibbonBar::RibbonStyle style =
                             ribbonStyleFromComboIndex(styleCombo, index);
                         updateRibbonStylePreview(stylePreview, style);
                         updateFluentStateTimingPreview(stateTimingPreview,
                                                        style);
                     });
    QObject::connect(styleCombo,
                     QOverload<int>::of(&QComboBox::currentIndexChanged),
                     [&mainWindow,
                      styleCombo,
                      stylePreview,
                      stateTimingPreview,
                      &settings,
                      persistStyleChoice](int index) {
                         const LqRibbon::RibbonBar::RibbonStyle style =
                             ribbonStyleFromComboIndex(styleCombo, index);
                         updateRibbonStylePreview(stylePreview, style);
                         updateFluentStateTimingPreview(stateTimingPreview,
                                                        style);
                         mainWindow.setRibbonStyle(style);
                         if (persistStyleChoice) {
                             saveRibbonStyleChoice(
                                 settings,
                                 ribbonStyleChoiceFromComboIndex(styleCombo, index));
                         }
                     });

    LqRibbon::RibbonPage *driverPage = mainWindow.ribbonBar()->addPage(QObject::tr("Driver"));
    LqRibbon::RibbonGroup *communicationGroup = driverPage->addGroup(QObject::tr("Communication"));
    QAction *settingsAction = communicationGroup->addAction(
        mainWindow.style()->standardIcon(QStyle::SP_ComputerIcon),
        QObject::tr("Settings"),
        Qt::ToolButtonTextUnderIcon);
    QAction *connectAction = communicationGroup->addAction(
        mainWindow.style()->standardIcon(QStyle::SP_DialogApplyButton),
        QObject::tr("Connect"),
        Qt::ToolButtonTextUnderIcon);

    LqRibbon::RibbonGroup *specialistGroup = driverPage->addGroup(QObject::tr("Specialist"));
    QAction *basicAction = specialistGroup->addAction(
        mainWindow.style()->standardIcon(QStyle::SP_FileDialogContentsView),
        QObject::tr("Basic Operation"),
        Qt::ToolButtonTextBesideIcon);
    QAction *driverAction = specialistGroup->addAction(
        mainWindow.style()->standardIcon(QStyle::SP_DriveHDIcon),
        QObject::tr("Driver Configuration"),
        Qt::ToolButtonTextBesideIcon);

    QToolButton *toolButtonControl = new QToolButton(&mainWindow);
    toolButtonControl->setText(QObject::tr("Control Modes"));
    toolButtonControl->setIcon(
        mainWindow.style()->standardIcon(QStyle::SP_FileDialogListView));
    toolButtonControl->setToolButtonStyle(Qt::ToolButtonTextBesideIcon);
    toolButtonControl->setPopupMode(QToolButton::MenuButtonPopup);
    toolButtonControl->setMenu(new QMenu(toolButtonControl));
    toolButtonControl->menu()->addAction(QObject::tr("Pulse Mode"));
    toolButtonControl->menu()->addAction(QObject::tr("Analog Velocity Mode"));
    specialistGroup->addWidget(toolButtonControl);

    LqRibbon::RibbonPage *controlsPage =
        mainWindow.ribbonBar()->addPage(QObject::tr("Controls"));
    LqRibbon::RibbonGroup *selectorGroup =
        controlsPage->addGroup(QObject::tr("Selectors"));
    LqRibbon::RibbonComboBoxControl *modeCombo =
        new LqRibbon::RibbonComboBoxControl(selectorGroup);
    modeCombo->widget()->addItems(QStringList()
                                  << QObject::tr("Position")
                                  << QObject::tr("Velocity")
                                  << QObject::tr("Torque"));
    selectorGroup->addWidget(modeCombo);

    LqRibbon::RibbonFontComboBoxControl *fontCombo =
        new LqRibbon::RibbonFontComboBoxControl(selectorGroup);
    selectorGroup->addWidget(fontCombo);

    LqRibbon::RibbonCheckBoxControl *enabledCheck =
        new LqRibbon::RibbonCheckBoxControl(QObject::tr("Enabled"),
                                            selectorGroup);
    enabledCheck->widget()->setChecked(true);
    selectorGroup->addWidget(enabledCheck);

    LqRibbon::RibbonRadioButtonControl *autoRadio =
        new LqRibbon::RibbonRadioButtonControl(QObject::tr("Auto"),
                                               selectorGroup);
    autoRadio->widget()->setChecked(true);
    selectorGroup->addWidget(autoRadio);

    LqRibbon::RibbonGroup *valueGroup =
        controlsPage->addGroup(QObject::tr("Values"));
    LqRibbon::RibbonLineEditControl *nameEdit =
        new LqRibbon::RibbonLineEditControl(valueGroup);
    nameEdit->widget()->setPlaceholderText(QObject::tr("Axis name"));
    valueGroup->addWidget(nameEdit);

    LqRibbon::RibbonSpinBoxControl *speedSpin =
        new LqRibbon::RibbonSpinBoxControl(valueGroup);
    speedSpin->widget()->setRange(0, 6000);
    speedSpin->widget()->setValue(1500);
    valueGroup->addWidget(speedSpin);

    LqRibbon::RibbonDoubleSpinBoxControl *gainSpin =
        new LqRibbon::RibbonDoubleSpinBoxControl(valueGroup);
    gainSpin->widget()->setRange(0.0, 10.0);
    gainSpin->widget()->setSingleStep(0.1);
    gainSpin->widget()->setValue(1.5);
    valueGroup->addWidget(gainSpin);

    LqRibbon::RibbonDateEditControl *dateEdit =
        new LqRibbon::RibbonDateEditControl(valueGroup);
    dateEdit->setCalendarPopup(true);
    dateEdit->widget()->setDate(QDate::currentDate());
    valueGroup->addWidget(dateEdit);

    LqRibbon::RibbonGroup *rangeGroup =
        controlsPage->addGroup(QObject::tr("Range"));
    LqRibbon::RibbonSliderControl *limitSlider =
        new LqRibbon::RibbonSliderControl(Qt::Horizontal, rangeGroup);
    limitSlider->widget()->setRange(0, 100);
    limitSlider->widget()->setValue(35);
    rangeGroup->addWidget(limitSlider);

    LqRibbon::RibbonSliderPaneControl *fineSlider =
        new LqRibbon::RibbonSliderPaneControl(rangeGroup);
    fineSlider->widget()->setValue(65);
    rangeGroup->addWidget(fineSlider);

    LqRibbon::RibbonButtonControl *applyButton =
        new LqRibbon::RibbonButtonControl(rangeGroup);
    applyButton->setSmallIcon(
        mainWindow.style()->standardIcon(QStyle::SP_DialogApplyButton));
    applyButton->setLargeIcon(
        mainWindow.style()->standardIcon(QStyle::SP_DialogApplyButton));
    applyButton->setLabel(QObject::tr("Apply"));
    rangeGroup->addWidget(applyButton);

    LqRibbon::RibbonPage *galleryPage =
        mainWindow.ribbonBar()->addPage(QObject::tr("Gallery"));
    LqRibbon::RibbonGroup *styleGroup =
        galleryPage->addGroup(QObject::tr("Styles"));
    LqRibbon::RibbonGalleryGroup *styleGalleryGroup =
        new LqRibbon::RibbonGalleryGroup(&mainWindow);
    styleGalleryGroup->setSize(QSize(72, 42));
    styleGalleryGroup->addItem(
        QObject::tr("Normal"),
        mainWindow.style()->standardIcon(QStyle::SP_FileDialogDetailedView));
    styleGalleryGroup->addItem(
        QObject::tr("Compact"),
        mainWindow.style()->standardIcon(QStyle::SP_FileDialogListView));
    styleGalleryGroup->addItem(
        QObject::tr("Drive"),
        mainWindow.style()->standardIcon(QStyle::SP_DriveHDIcon));
    styleGalleryGroup->addItem(
        QObject::tr("Network"),
        mainWindow.style()->standardIcon(QStyle::SP_ComputerIcon));
    styleGalleryGroup->addItem(
        QObject::tr("Apply"),
        mainWindow.style()->standardIcon(QStyle::SP_DialogApplyButton));
    styleGalleryGroup->addItem(
        QObject::tr("Help"),
        mainWindow.style()->standardIcon(QStyle::SP_MessageBoxQuestion));

    LqRibbon::RibbonGallery *styleGallery =
        new LqRibbon::RibbonGallery(styleGroup);
    styleGallery->setGalleryGroup(styleGalleryGroup);
    styleGallery->setColumnCount(3);
    styleGallery->setRowCount(2);
    styleGallery->setCheckedIndex(1);

    QMenu *galleryMenu = new QMenu(styleGallery);
    galleryMenu->addAction(QObject::tr("More styles"));
    galleryMenu->addAction(QObject::tr("Reset style"));
    styleGallery->setPopupMenu(galleryMenu);

    LqRibbon::RibbonGalleryControl *styleGalleryControl =
        new LqRibbon::RibbonGalleryControl(styleGroup, styleGallery);
    styleGroup->addWidget(styleGalleryControl);

    LqRibbon::RibbonGroup *galleryActionGroup =
        galleryPage->addGroup(QObject::tr("Actions"));
    LqRibbon::RibbonToolBarControl *galleryToolBar =
        new LqRibbon::RibbonToolBarControl(galleryActionGroup);
    galleryToolBar->addAction(
        mainWindow.style()->standardIcon(QStyle::SP_DialogOpenButton),
        QObject::tr("Open"));
    galleryToolBar->addAction(
        mainWindow.style()->standardIcon(QStyle::SP_DialogSaveButton),
        QObject::tr("Save"));
    galleryToolBar->addSeparator();
    galleryToolBar->addMenu(
        mainWindow.style()->standardIcon(QStyle::SP_ArrowDown),
        QObject::tr("More"),
        galleryMenu);
    galleryActionGroup->addWidget(galleryToolBar);

    LqRibbon::RibbonPage *shellPage =
        mainWindow.ribbonBar()->addPage(QObject::tr("Shell"));
    LqRibbon::RibbonGroup *windowGroup =
        shellPage->addGroup(QObject::tr("Window"));
    QAction *minimizeRibbonAction = windowGroup->addAction(
        mainWindow.style()->standardIcon(QStyle::SP_TitleBarShadeButton),
        QObject::tr("Minimize"),
        Qt::ToolButtonTextUnderIcon);
    QAction *restoreRibbonAction = windowGroup->addAction(
        mainWindow.style()->standardIcon(QStyle::SP_TitleBarUnshadeButton),
        QObject::tr("Restore"),
        Qt::ToolButtonTextBesideIcon);
    QAction *toggleFrameAction = windowGroup->addAction(
        mainWindow.style()->standardIcon(QStyle::SP_TitleBarNormalButton),
        QObject::tr("Frame Theme"),
        Qt::ToolButtonTextBesideIcon);
    toggleFrameAction->setCheckable(true);
    toggleFrameAction->setChecked(true);
    QAction *simplifiedRibbonAction = mainWindow.ribbonBar()->simplifiedAction();
    simplifiedRibbonAction->setIcon(
        mainWindow.style()->standardIcon(QStyle::SP_ArrowUp));
    windowGroup->addAction(simplifiedRibbonAction,
                           Qt::ToolButtonTextBesideIcon);
    QAction *classicRibbonAction = windowGroup->addAction(
        mainWindow.style()->standardIcon(QStyle::SP_ArrowDown),
        QObject::tr("Classic Ribbon"),
        Qt::ToolButtonTextBesideIcon);
    QAction *pinRibbonAction = windowGroup->addAction(
        mainWindow.style()->standardIcon(QStyle::SP_DialogApplyButton),
        QObject::tr("Pin Ribbon"),
        Qt::ToolButtonTextBesideIcon);
    QAction *unpinRibbonAction = windowGroup->addAction(
        mainWindow.style()->standardIcon(QStyle::SP_DialogCancelButton),
        QObject::tr("Unpin Ribbon"),
        Qt::ToolButtonTextBesideIcon);
    QLabel *collapseStatePreview = new QLabel(&mainWindow);
    collapseStatePreview->setObjectName(QStringLiteral("collapseStatePreview"));
    collapseStatePreview->setMinimumWidth(112);
    collapseStatePreview->setAlignment(Qt::AlignCenter);
    collapseStatePreview->setFrameShape(QFrame::StyledPanel);
    collapseStatePreview->setToolTip(QObject::tr("Collapse button state preview"));
    windowGroup->addWidget(collapseStatePreview);

    LqRibbon::RibbonGroup *runtimeGroup =
        shellPage->addGroup(QObject::tr("Runtime"));
    QAction *addPageAction = runtimeGroup->addAction(
        mainWindow.style()->standardIcon(QStyle::SP_FileDialogNewFolder),
        QObject::tr("Add Page"),
        Qt::ToolButtonTextUnderIcon);
    QAction *renamePageAction = runtimeGroup->addAction(
        mainWindow.style()->standardIcon(QStyle::SP_FileDialogInfoView),
        QObject::tr("Rename Driver"),
        Qt::ToolButtonTextBesideIcon);
    QAction *moveGalleryAction = runtimeGroup->addAction(
        mainWindow.style()->standardIcon(QStyle::SP_ArrowRight),
        QObject::tr("Move Gallery"),
        Qt::ToolButtonTextBesideIcon);
    QAction *toggleGroupAction = runtimeGroup->addAction(
        mainWindow.style()->standardIcon(QStyle::SP_DialogResetButton),
        QObject::tr("Toggle Specialist"),
        Qt::ToolButtonTextBesideIcon);

    LqRibbon::RibbonGroup *popupGroup =
        shellPage->addGroup(QObject::tr("Popups"));
    QAction *officePopupAction = popupGroup->addAction(
        mainWindow.style()->standardIcon(QStyle::SP_MessageBoxInformation),
        QObject::tr("Popup"),
        Qt::ToolButtonTextUnderIcon);
    QAction *officeMenuAction = popupGroup->addAction(
        mainWindow.style()->standardIcon(QStyle::SP_DirOpenIcon),
        QObject::tr("Popup Menu"),
        Qt::ToolButtonTextBesideIcon);
    LqRibbon::PopupColorButton *colorButton =
        new LqRibbon::PopupColorButton(popupGroup);
    colorButton->setText(QObject::tr("Color"));
    colorButton->setToolButtonStyle(Qt::ToolButtonTextBesideIcon);
    colorButton->setColor(QColor(QStringLiteral("#2b579a")));
    colorButton->setToolTip(QObject::tr("Popup Color Button"));
    popupGroup->addWidget(colorButton);

    LqRibbon::RibbonGroup *customizeGroup =
        shellPage->addGroup(QObject::tr("Customize"));
    QAction *showCustomizeAction = customizeGroup->addAction(
        mainWindow.style()->standardIcon(QStyle::SP_FileDialogDetailedView),
        QObject::tr("Customize"),
        Qt::ToolButtonTextUnderIcon);
    QAction *saveStateAction = customizeGroup->addAction(
        mainWindow.style()->standardIcon(QStyle::SP_DialogSaveButton),
        QObject::tr("Save Layout"),
        Qt::ToolButtonTextBesideIcon);
    QAction *loadStateAction = customizeGroup->addAction(
        mainWindow.style()->standardIcon(QStyle::SP_DialogOpenButton),
        QObject::tr("Load Layout"),
        Qt::ToolButtonTextBesideIcon);

    QAction *specialistOptionsAction = new QAction(
        mainWindow.style()->standardIcon(QStyle::SP_FileDialogInfoView),
        QObject::tr("Specialist Options"),
        specialistGroup);
    specialistGroup->setOptionButtonAction(specialistOptionsAction);
    specialistGroup->setOptionButtonVisible(true);

    QAction *systemButtonAction = mainWindow.ribbonBar()->addSystemButton(
        mainWindow.style()->standardIcon(QStyle::SP_DriveFDIcon),
        QObject::tr("File"));
    Q_UNUSED(systemButtonAction)
    LqRibbon::RibbonBackstageView *backstage =
        new LqRibbon::RibbonBackstageView(&mainWindow);
    backstage->addAction(mainWindow.style()->standardIcon(QStyle::SP_DialogOpenButton),
                         QObject::tr("Open"));
    backstage->addAction(mainWindow.style()->standardIcon(QStyle::SP_DialogSaveButton),
                         QObject::tr("Save"));
    backstage->addSeparator();
    QWidget *backstagePage = new QWidget(backstage);
    QFormLayout *backstageLayout = new QFormLayout(backstagePage);
    backstageLayout->addRow(QObject::tr("Product"),
                            new QLabel(QObject::tr("LqRibbon Demo"), backstagePage));
    backstageLayout->addRow(QObject::tr("Mode"),
                            new QLabel(QObject::tr("Backstage page"), backstagePage));
    backstage->addPage(backstagePage);

    LqRibbon::RibbonSystemMenu *systemMenu =
        new LqRibbon::RibbonSystemMenu(mainWindow.ribbonBar());
    systemMenu->addPopupBarAction(QObject::tr("New"));
    systemMenu->addPopupBarAction(QObject::tr("Open"));
    LqRibbon::RibbonPageSystemRecentFileList *recentFiles =
        systemMenu->addPageRecentFile(QObject::tr("Recent Files"));
    recentFiles->updateRecentFileActions(QStringList()
                                         << QObject::tr("axis-profile.lqr")
                                         << QObject::tr("drive-layout.lqr"));
    QAction *exportAction = new QAction(
        mainWindow.style()->standardIcon(QStyle::SP_DialogSaveButton),
        QObject::tr("Export"), systemMenu);
    systemMenu->addPageSystemPopup(QObject::tr("Export"), exportAction, true);
    if (mainWindow.ribbonBar()->systemButton()) {
        mainWindow.ribbonBar()->systemButton()->setBackstage(backstage);
        mainWindow.ribbonBar()->systemButton()->setSystemMenu(systemMenu);
    }

    LqRibbon::OfficePopupMenu *officeMenu =
        LqRibbon::OfficePopupMenu::createPopupMenu(&mainWindow);
    officeMenu->setGripVisible(true);
    QPlainTextEdit *popupEditor = new QPlainTextEdit(officeMenu);
    popupEditor->setPlainText(QObject::tr("OfficePopupMenu widget host"));
    popupEditor->setFixedSize(260, 120);
    officeMenu->addWidget(popupEditor);

    LqRibbon::RibbonCustomizeManager *customizeManager =
        mainWindow.ribbonBar()->customizeManager();
    customizeManager->addToCategory(QObject::tr("Pages"), generalPage);
    customizeManager->addToCategory(QObject::tr("Pages"), driverPage);
    customizeManager->addToCategory(QObject::tr("Pages"), controlsPage);
    customizeManager->addToCategory(QObject::tr("Pages"), galleryPage);
    customizeManager->addToCategory(QObject::tr("Pages"), shellPage);
    customizeManager->addToCategory(QObject::tr("Actions"), fullScreenAction);
    customizeManager->addToCategory(QObject::tr("Actions"), connectAction);
    customizeManager->addToCategory(QObject::tr("Actions"), classicRibbonAction);
    customizeManager->addToCategory(QObject::tr("Actions"), pinRibbonAction);
    customizeManager->addToCategory(QObject::tr("Actions"), unpinRibbonAction);
    customizeManager->addToCategory(QObject::tr("Actions"), officePopupAction);
    customizeManager->addToCategory(QObject::tr("Actions"), showCustomizeAction);
    customizeManager->setPageId(shellPage, QStringLiteral("shell"));
    customizeManager->setGroupId(runtimeGroup, QStringLiteral("runtime"));
    QByteArray savedRibbonState;

    auto updateCollapseStatePreview = [&mainWindow, collapseStatePreview]() {
        LqRibbon::RibbonBar *bar = mainWindow.ribbonBar();
        QString stateText;
        if (!bar->isMinimizationEnabled()) {
            stateText = QObject::tr("Pinned");
        } else if (bar->isRibbonTemporaryExpanded()) {
            stateText = QObject::tr("Temporary");
        } else if (bar->simplifiedMode()) {
            stateText = QObject::tr("Simplified");
        } else if (bar->isRibbonMinimized()) {
            stateText = QObject::tr("Collapsed");
        } else {
            stateText = QObject::tr("Expanded");
        }
        collapseStatePreview->setText(QObject::tr("State: %1").arg(stateText));
    };
    QObject::connect(mainWindow.ribbonBar(),
                     &LqRibbon::RibbonBar::ribbonMinimizedChanged,
                     collapseStatePreview,
                     [updateCollapseStatePreview](bool) {
                         updateCollapseStatePreview();
                     });
    QObject::connect(mainWindow.ribbonBar(),
                     &LqRibbon::RibbonBar::ribbonTemporaryExpandedChanged,
                     collapseStatePreview,
                     [updateCollapseStatePreview](bool) {
                         updateCollapseStatePreview();
                     });
    QObject::connect(mainWindow.ribbonBar(),
                     &LqRibbon::RibbonBar::simplifiedModeChanged,
                     collapseStatePreview,
                     [updateCollapseStatePreview](bool) {
                         updateCollapseStatePreview();
                     });
    updateCollapseStatePreview();

    QObject::connect(fullScreenAction, &QAction::triggered, [&mainWindow]() {
        mainWindow.setWindowState(mainWindow.windowState() ^ Qt::WindowFullScreen);
    });

    QObject::connect(mdiAction, &QAction::triggered, [&mainWindow]() {
        QMessageBox::information(&mainWindow,
                                 QObject::tr("LqRibbon"),
                                 QObject::tr("Mdi Mode"));
    });

    QObject::connect(tabAction, &QAction::triggered, [&mainWindow]() {
        QMessageBox::information(&mainWindow,
                                 QObject::tr("LqRibbon"),
                                 QObject::tr("Tab Mode"));
    });

    QObject::connect(settingsAction, &QAction::triggered, [&mainWindow]() {
        QMessageBox::information(&mainWindow,
                                 QObject::tr("LqRibbon"),
                                 QObject::tr("Settings"));
    });

    QObject::connect(connectAction, &QAction::triggered, [&mainWindow]() {
        QMessageBox::information(&mainWindow,
                                 QObject::tr("LqRibbon"),
                                 QObject::tr("Connect"));
    });
    QObject::connect(specialistOptionsAction, &QAction::triggered,
                     [&mainWindow]() {
                         mainWindow.statusBar()->showMessage(
                             QObject::tr("Specialist option button clicked"),
                             2500);
                     });
    QObject::connect(minimizeRibbonAction, &QAction::triggered,
                     [&mainWindow, updateCollapseStatePreview]() {
                         mainWindow.ribbonBar()->setRibbonMinimized(true);
                         updateCollapseStatePreview();
                     });
    QObject::connect(restoreRibbonAction, &QAction::triggered,
                     [&mainWindow, updateCollapseStatePreview]() {
                         mainWindow.ribbonBar()->setRibbonMinimized(false);
                         updateCollapseStatePreview();
                     });
    QObject::connect(classicRibbonAction, &QAction::triggered,
                     [&mainWindow, updateCollapseStatePreview]() {
                         mainWindow.ribbonBar()->setRibbonMinimized(false);
                         mainWindow.ribbonBar()->setSimplifiedMode(false);
                         updateCollapseStatePreview();
                     });
    QObject::connect(pinRibbonAction, &QAction::triggered,
                     [&mainWindow, updateCollapseStatePreview]() {
                         mainWindow.ribbonBar()->setRibbonMinimized(false);
                         mainWindow.ribbonBar()->setMinimizationEnabled(false);
                         updateCollapseStatePreview();
                     });
    QObject::connect(unpinRibbonAction, &QAction::triggered,
                     [&mainWindow, updateCollapseStatePreview]() {
                         mainWindow.ribbonBar()->setMinimizationEnabled(true);
                         mainWindow.ribbonBar()->setRibbonMinimized(true);
                         updateCollapseStatePreview();
                     });
    QObject::connect(toggleFrameAction, &QAction::toggled,
                     [&mainWindow](bool checked) {
                         mainWindow.setFrameThemeEnabled(checked);
                     });
    QObject::connect(addPageAction, &QAction::triggered,
                     [&mainWindow]() {
                         static int runtimePageCounter = 1;
                         LqRibbon::RibbonPage *runtimePage =
                             mainWindow.ribbonBar()->addPage(
                                 QObject::tr("Runtime %1")
                                     .arg(runtimePageCounter++));
                         LqRibbon::RibbonGroup *runtimeGroup =
                             runtimePage->addGroup(QObject::tr("Generated"));
                         runtimeGroup->addAction(
                             mainWindow.style()->standardIcon(
                                 QStyle::SP_DialogApplyButton),
                             QObject::tr("Generated Action"),
                             Qt::ToolButtonTextUnderIcon);
                         mainWindow.ribbonBar()->setCurrentWidget(runtimePage);
                     });
    QObject::connect(renamePageAction, &QAction::triggered,
                     [driverPage]() {
                         driverPage->setTitle(
                             driverPage->title() == QObject::tr("Driver")
                                 ? QObject::tr("Drive")
                                 : QObject::tr("Driver"));
                     });
    QObject::connect(moveGalleryAction, &QAction::triggered,
                     [&mainWindow, galleryPage]() {
                         const int currentIndex =
                             mainWindow.ribbonBar()->pageIndex(galleryPage);
                         const int targetIndex = currentIndex == 1
                             ? mainWindow.ribbonBar()->pageCount() - 1
                             : 1;
                         mainWindow.ribbonBar()->movePage(galleryPage,
                                                          targetIndex);
                     });
    QObject::connect(toggleGroupAction, &QAction::triggered,
                     [driverPage, specialistGroup]() {
                         specialistGroup->setVisible(
                             !specialistGroup->isVisible());
                         driverPage->updateLayout();
                     });
    QObject::connect(officePopupAction, &QAction::triggered,
                     [&mainWindow]() {
                         LqRibbon::OfficePopupWindow::showPopup(
                             &mainWindow,
                             mainWindow.style()->standardIcon(
                                 QStyle::SP_MessageBoxInformation),
        QObject::tr("LqRibbon"),
                             QObject::tr("Popup window sample"));
                     });
    QObject::connect(officeMenuAction, &QAction::triggered,
                     [&mainWindow, officeMenu]() {
                         officeMenu->exec(mainWindow.mapToGlobal(
                             QPoint(40, 90)));
                     });
    QObject::connect(colorButton, &LqRibbon::PopupColorButton::colorChanged,
                     [&mainWindow](const QColor &color) {
                         mainWindow.statusBar()->showMessage(
                             QObject::tr("Color changed: %1")
                                 .arg(color.name()),
                             2500);
                     });
    QObject::connect(showCustomizeAction, &QAction::triggered,
                     [&mainWindow]() {
                         mainWindow.ribbonBar()->showCustomizeDialog();
                     });
    QObject::connect(saveStateAction, &QAction::triggered,
                     [&mainWindow, customizeManager, &savedRibbonState]() {
                         savedRibbonState.clear();
                         QBuffer buffer(&savedRibbonState);
                         buffer.open(QIODevice::WriteOnly);
                         customizeManager->saveStateToDevice(&buffer);
                         mainWindow.statusBar()->showMessage(
                             QObject::tr("Ribbon layout saved"), 2500);
                     });
    QObject::connect(loadStateAction, &QAction::triggered,
                     [&mainWindow, customizeManager, &savedRibbonState]() {
                         if (savedRibbonState.isEmpty()) {
                             mainWindow.statusBar()->showMessage(
                                 QObject::tr("No saved Ribbon layout"), 2500);
                             return;
                         }
                         QBuffer buffer(&savedRibbonState);
                         buffer.open(QIODevice::ReadOnly);
                         customizeManager->loadStateFromDevice(&buffer);
                         mainWindow.statusBar()->showMessage(
                             QObject::tr("Ribbon layout loaded"), 2500);
                     });

    if (mdiPreviewRequested || tabPreviewRequested) {
        QMdiArea *mdiArea = new QMdiArea(&mainWindow);
        mdiArea->setViewMode(tabPreviewRequested
                             ? QMdiArea::TabbedView
                             : QMdiArea::SubWindowView);

        for (int index = 0; index < 2; ++index) {
            QTableWidget *tableWidget = new QTableWidget(8, 4, mdiArea);
            tableWidget->setWindowTitle(index == 0
                                        ? QObject::tr("Write Settings")
                                        : QObject::tr("Control Loop Specialist"));
            QMdiSubWindow *subWindow = mdiArea->addSubWindow(tableWidget);
            subWindow->setWindowTitle(tableWidget->windowTitle());
            subWindow->resize(index == 0 ? 360 : 300, 220);
            subWindow->move(index == 0 ? 40 : 460, index == 0 ? 60 : 80);
            subWindow->show();
        }

        mainWindow.setCentralWidget(mdiArea);
    } else {
        QLabel *contentLabel = new QLabel(
            QObject::tr("LqRibbon Qt 5.15.2 C++ example"));
        contentLabel->setAlignment(Qt::AlignCenter);
        mainWindow.setCentralWidget(contentLabel);
    }

    LqRibbon::RibbonStatusBar *ribbonStatusBar =
        new LqRibbon::RibbonStatusBar(&mainWindow);
    ribbonStatusBar->addAction(QObject::tr("Ready"));
    ribbonStatusBar->addSeparator();
    ribbonStatusBar->addAction(QObject::tr("Online"));

    LqRibbon::RibbonStatusBarSwitchGroup *switchGroup =
        new LqRibbon::RibbonStatusBarSwitchGroup(ribbonStatusBar);
    QActionGroup *viewActionGroup = new QActionGroup(switchGroup);
    viewActionGroup->setExclusive(true);
    QAction *normalViewAction = viewActionGroup->addAction(
        mainWindow.style()->standardIcon(QStyle::SP_FileDialogDetailedView),
        QObject::tr("Normal View"));
    QAction *compactViewAction = viewActionGroup->addAction(
        mainWindow.style()->standardIcon(QStyle::SP_FileDialogListView),
        QObject::tr("Compact View"));
    normalViewAction->setCheckable(true);
    compactViewAction->setCheckable(true);
    normalViewAction->setChecked(true);
    switchGroup->addAction(normalViewAction);
    switchGroup->addAction(compactViewAction);

    LqRibbon::RibbonSliderPane *zoomSlider =
        new LqRibbon::RibbonSliderPane(ribbonStatusBar);
    zoomSlider->setRange(10, 200);
    zoomSlider->setSingleStep(10);
    zoomSlider->setValue(100);

    LqRibbon::RibbonProgressBar *progressBar =
        new LqRibbon::RibbonProgressBar(ribbonStatusBar);
    progressBar->setValue(42);

    QAction *syncAction = new QAction(
        mainWindow.style()->standardIcon(QStyle::SP_BrowserReload),
        QObject::tr("Sync"),
        ribbonStatusBar);
    ribbonStatusBar->addPermanentAction(syncAction);
    ribbonStatusBar->addPermanentWidget(switchGroup);
    ribbonStatusBar->addPermanentWidget(zoomSlider);
    ribbonStatusBar->addPermanentWidget(progressBar);
    mainWindow.setStatusBar(ribbonStatusBar);

    QObject::connect(zoomSlider, &LqRibbon::RibbonSliderPane::valueChanged,
                     progressBar, &LqRibbon::RibbonProgressBar::setValueSafe);

    const int generalPageIndex = mainWindow.ribbonBar()->indexOf(generalPage);
    const int controlsPageIndex = mainWindow.ribbonBar()->indexOf(controlsPage);
    const int galleryPageIndex = mainWindow.ribbonBar()->indexOf(galleryPage);
    const int shellPageIndex = mainWindow.ribbonBar()->indexOf(shellPage);
    if (stylePreviewRequested) {
        mainWindow.ribbonBar()->setCurrentPageIndex(generalPageIndex);
    } else if (shellPreviewRequested
               || simplifiedPreviewRequested
               || temporaryPreviewRequested) {
        mainWindow.ribbonBar()->setCurrentPageIndex(shellPageIndex);
    } else if (galleryPreviewRequested) {
        mainWindow.ribbonBar()->setCurrentPageIndex(galleryPageIndex);
    } else if (controlsPreviewRequested) {
        mainWindow.ribbonBar()->setCurrentPageIndex(controlsPageIndex);
    } else {
        mainWindow.ribbonBar()->setCurrentPageIndex(1);
    }
    mainWindow.setFrameThemeEnabled(true);
    const int styleComboIndex =
        styleCombo->findData(systemStyleRequested
                                 ? systemRibbonStyleComboValue
                                 : static_cast<int>(previewRibbonStyle));
    if (styleComboIndex >= 0) {
        styleCombo->setCurrentIndex(styleComboIndex);
    }
    mainWindow.setRibbonStyle(previewRibbonStyle);
    if (systemStyleRequested && styleComboIndex >= 0) {
        styleCombo->setCurrentIndex(styleComboIndex);
    }
    mainWindow.ribbonBar()->setSearchVisible(true);
    mainWindow.ribbonBar()->setSearchPlaceholderText(QObject::tr("Search commands"));
    mainWindow.ribbonBar()->setRecentSearchLimit(5);
    mainWindow.ribbonBar()->registerSearchAction(fullScreenAction);
    mainWindow.ribbonBar()->registerSearchAction(mdiAction);
    mainWindow.ribbonBar()->registerSearchAction(tabAction);
    mainWindow.ribbonBar()->registerSearchAction(settingsAction);
    mainWindow.ribbonBar()->registerSearchAction(connectAction);
    mainWindow.ribbonBar()->registerSearchAction(basicAction);
    mainWindow.ribbonBar()->registerSearchAction(driverAction);
    mainWindow.ribbonBar()->registerSearchAction(minimizeRibbonAction);
    mainWindow.ribbonBar()->registerSearchAction(restoreRibbonAction);
    mainWindow.ribbonBar()->registerSearchAction(classicRibbonAction);
    mainWindow.ribbonBar()->registerSearchAction(pinRibbonAction);
    mainWindow.ribbonBar()->registerSearchAction(unpinRibbonAction);
    mainWindow.ribbonBar()->registerSearchAction(addPageAction);
    mainWindow.ribbonBar()->registerSearchAction(renamePageAction);
    mainWindow.ribbonBar()->registerSearchAction(moveGalleryAction);
    mainWindow.ribbonBar()->registerSearchAction(toggleGroupAction);
    mainWindow.ribbonBar()->registerSearchAction(officePopupAction);
    mainWindow.ribbonBar()->registerSearchAction(officeMenuAction);
    mainWindow.ribbonBar()->registerSearchAction(showCustomizeAction);
    mainWindow.ribbonBar()->addQuickAccessAction(fullScreenAction);
    mainWindow.ribbonBar()->addQuickAccessAction(connectAction);
    mainWindow.ribbonBar()->addQuickAccessAction(minimizeRibbonAction);

    QMenu *displayOptionsMenu =
        new QMenu(QObject::tr("Ribbon Display Options"), &mainWindow);
    QAction *showTabsAndCommandsAction = displayOptionsMenu->addAction(
        mainWindow.style()->standardIcon(QStyle::SP_TitleBarUnshadeButton),
        QObject::tr("Show Tabs and Commands"));
    QAction *showTabsOnlyAction = displayOptionsMenu->addAction(
        mainWindow.style()->standardIcon(QStyle::SP_TitleBarShadeButton),
        QObject::tr("Show Tabs Only"));
    QAction *alwaysShowRibbonAction = displayOptionsMenu->addAction(
        mainWindow.style()->standardIcon(QStyle::SP_DialogApplyButton),
        QObject::tr("Always Show Ribbon"));
    QAction *autoHideRibbonAction = displayOptionsMenu->addAction(
        mainWindow.style()->standardIcon(QStyle::SP_DialogCancelButton),
        QObject::tr("Auto-Hide Ribbon"));
    QAction *displayOptionsTitleAction = mainWindow.ribbonBar()->addTitleButton(
        mainWindow.style()->standardIcon(QStyle::SP_TitleBarMenuButton),
        QObject::tr("Ribbon Display Options"));
    displayOptionsTitleAction->setMenu(displayOptionsMenu);
    if (QToolBar *titleButtonBar = mainWindow.ribbonBar()->findChild<QToolBar *>(
            QStringLiteral("lqRibbonTitleButtonBar"))) {
        if (QToolButton *displayButton =
                qobject_cast<QToolButton *>(
                    titleButtonBar->widgetForAction(displayOptionsTitleAction))) {
            displayButton->setPopupMode(QToolButton::InstantPopup);
        }
    }

    QAction *helpTitleAction = mainWindow.ribbonBar()->addTitleButton(
        mainWindow.style()->standardIcon(QStyle::SP_MessageBoxQuestion),
        QObject::tr("Help"));
    QAction *accountTitleAction = mainWindow.ribbonBar()->addTitleButton(
        mainWindow.style()->standardIcon(QStyle::SP_DirHomeIcon),
        QObject::tr("Account"));
    QObject::connect(helpTitleAction, &QAction::triggered, [&mainWindow]() {
        QMessageBox::information(&mainWindow,
                                 QObject::tr("LqRibbon"),
                                 QObject::tr("Help"));
    });
    QObject::connect(accountTitleAction, &QAction::triggered, [&mainWindow]() {
        QMessageBox::information(&mainWindow,
                                 QObject::tr("LqRibbon"),
                                 QObject::tr("Account"));
    });
    QObject::connect(showTabsAndCommandsAction, &QAction::triggered,
                     [&mainWindow, updateCollapseStatePreview]() {
                         mainWindow.ribbonBar()->setMinimizationEnabled(true);
                         mainWindow.ribbonBar()->setSimplifiedMode(false);
                         mainWindow.ribbonBar()->setRibbonMinimized(false);
                         updateCollapseStatePreview();
                     });
    QObject::connect(showTabsOnlyAction, &QAction::triggered,
                     [&mainWindow, updateCollapseStatePreview]() {
                         mainWindow.ribbonBar()->setMinimizationEnabled(true);
                         mainWindow.ribbonBar()->setSimplifiedMode(false);
                         mainWindow.ribbonBar()->setRibbonMinimized(true);
                         updateCollapseStatePreview();
                     });
    QObject::connect(alwaysShowRibbonAction, &QAction::triggered,
                     [&mainWindow, updateCollapseStatePreview]() {
                         mainWindow.ribbonBar()->setSimplifiedMode(false);
                         mainWindow.ribbonBar()->setRibbonMinimized(false);
                         mainWindow.ribbonBar()->setMinimizationEnabled(false);
                         updateCollapseStatePreview();
                     });
    QObject::connect(autoHideRibbonAction, &QAction::triggered,
                     [&mainWindow, updateCollapseStatePreview]() {
                         mainWindow.ribbonBar()->setMinimizationEnabled(true);
                         mainWindow.ribbonBar()->setSimplifiedMode(false);
                         mainWindow.ribbonBar()->setRibbonMinimized(true);
                         updateCollapseStatePreview();
                     });

    QObject::connect(mainWindow.ribbonBar(), &LqRibbon::RibbonBar::searchAccepted,
                     [&mainWindow](const QString &strText) {
                         QMessageBox::information(&mainWindow,
                                                  QObject::tr("Search"),
                                                  QObject::tr("No command: %1").arg(strText));
                     });

    mainWindow.show();

    if (collapseTestsRequested) {
        QTimer::singleShot(0,
                           &mainWindow,
                           [&mainWindow,
                            classicRibbonAction,
                            pinRibbonAction,
                            unpinRibbonAction,
                            displayOptionsTitleAction,
                            showTabsAndCommandsAction,
                            showTabsOnlyAction,
                            alwaysShowRibbonAction,
                            autoHideRibbonAction,
                            collapseStatePreview]() {
            qApp->exit(runCollapseTests(mainWindow,
                                        classicRibbonAction,
                                        pinRibbonAction,
                                        unpinRibbonAction,
                                        displayOptionsTitleAction,
                                        showTabsAndCommandsAction,
                                        showTabsOnlyAction,
                                        alwaysShowRibbonAction,
                                        autoHideRibbonAction,
                                        collapseStatePreview));
        });
        return application.exec();
    }

    if (styleTestsRequested) {
        QTimer::singleShot(0,
                           &mainWindow,
                           [&mainWindow,
                            styleCombo,
                            stylePreview,
                            stateTimingPreview]() {
            qApp->exit(runStyleTests(mainWindow,
                                     styleCombo,
                                     stylePreview,
                                     stateTimingPreview));
        });
        return application.exec();
    }

    if (!strPreviewPath.isEmpty()) {
        QTimer::singleShot(300, &mainWindow, [&mainWindow, strPreviewPath]() {
            mainWindow.grab().save(strPreviewPath);
            qApp->quit();
        });
    }

    if (searchPreviewRequested) {
        QTimer::singleShot(120, &mainWindow, [&mainWindow]() {
            mainWindow.ribbonBar()->searchLineEdit()->setFocus();
            mainWindow.ribbonBar()->setSearchText(QStringLiteral("ba"));
        });
    }

    if (collapsedPreviewRequested) {
        QTimer::singleShot(120, &mainWindow, [&mainWindow]() {
            mainWindow.ribbonBar()->setRibbonMinimized(true);
        });
    }

    if (simplifiedPreviewRequested) {
        QTimer::singleShot(120, &mainWindow, [&mainWindow]() {
            mainWindow.ribbonBar()->setSimplifiedMode(true);
        });
    }

    if (temporaryPreviewRequested) {
        QTimer::singleShot(120, &mainWindow, [&mainWindow]() {
            mainWindow.ribbonBar()->setRibbonMinimized(true);
            clickCollapseTestTab(mainWindow.ribbonBar(),
                                 mainWindow.ribbonBar()->currentIndex());
        });
    }

    return application.exec();
}
