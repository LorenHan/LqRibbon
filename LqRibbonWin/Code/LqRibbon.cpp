#include "LqRibbon.h"

#include <QAbstractItemView>
#include <QApplication>
#include <QChildEvent>
#include <QComboBox>
#include <QCoreApplication>
#include <QFontMetrics>
#include <QGridLayout>
#include <QKeyEvent>
#include <QLayout>
#include <QListView>
#include <QLocale>
#include <QMdiArea>
#include <QMdiSubWindow>
#include <QMouseEvent>
#include <QPainter>
#include <QPaintEvent>
#include <QScreen>
#include <QSpinBox>
#include <QStackedWidget>
#include <QStandardItemModel>
#include <QStyle>
#include <QTabBar>
#include <QWindow>

#ifdef Q_OS_WIN
#include <qt_windows.h>
#ifndef SM_CXPADDEDBORDER
#define SM_CXPADDEDBORDER 92
#endif
#endif

namespace {

const int ribbonLargeButtonMinimumWidth = 40;
const int ribbonLargeButtonMaximumWidth = 82;
const int ribbonSmallButtonMinimumWidth = 56;
const int ribbonSmallButtonMaximumWidth = 240;
const int ribbonRowItemCount = 3;
const int ribbonGroupTopMargin = 5;
const int ribbonGroupRightMargin = 5;
const int ribbonGroupBottomMargin = 5;
const int ribbonGroupLeftMargin = 4;
const int ribbonSmallButtonColumnSpacing = 4;
const int ribbonCaptionHeight = 36;
const int ribbonCaptionTopMargin = 3;
const int ribbonTabHeight = 24;
const int ribbonDefaultBarHeight = 158;
const int ribbonWindowButtonWidth = 46;
const int ribbonWindowButtonHeight = 30;
const int ribbonCollapseButtonWidth = 32;
const int ribbonCollapseButtonHeight = 24;
const int ribbonMdiTitleHeight = 28;
const int ribbonMdiButtonWidth = 28;
const int ribbonMdiButtonHeight = 24;
const int ribbonSearchPopupMaxHeight = 260;
const int ribbonSearchPopupRowHeight = 24;
const int ribbonSearchPopupKindRole = Qt::UserRole + 1;
const int ribbonSearchPopupActionRole = Qt::UserRole + 2;

enum RibbonSearchPopupKind
{
    SearchPopupHeaderItem = 0,
    SearchPopupActionItem,
    SearchPopupHelpItem
};

struct RibbonTranslationEntry
{
    const char *sourceText;
    const char *zhCnText;
};

const RibbonTranslationEntry ribbonTranslationTable[] = {
    {"Search", "\xE6\x90\x9C\xE7\xB4\xA2"},
    {"Actions", "\xE6\x93\x8D\xE4\xBD\x9C"},
    {"Help", "\xE5\xB8\xAE\xE5\x8A\xA9"},
    {"Get Help with \"%1\"",
     "\xE8\x8E\xB7\xE5\x8F\x96\x20\x22\x25\x31\x22\x20"
     "\xE7\x9A\x84\xE5\xB8\xAE\xE5\x8A\xA9"},
    {"Minimize", "\xE6\x9C\x80\xE5\xB0\x8F\xE5\x8C\x96"},
    {"Maximize", "\xE6\x9C\x80\xE5\xA4\xA7\xE5\x8C\x96"},
    {"Restore", "\xE8\xBF\x98\xE5\x8E\x9F"},
    {"Close", "\xE5\x85\xB3\xE9\x97\xAD"},
    {"Collapse the Ribbon",
     "\xE6\x8A\x98\xE5\x8F\xA0\xE5\x8A\x9F\xE8\x83\xBD\xE5\x8C\xBA"},
    {"Expand the Ribbon",
     "\xE5\xB1\x95\xE5\xBC\x80\xE5\x8A\x9F\xE8\x83\xBD\xE5\x8C\xBA"}
};

///
/// \brief containsChineseCharacter
/// Checks whether a translated Qt string contains a CJK character.
/// \param strText Text returned by an installed application translator.
/// \return true when the string contains a Chinese/Japanese/Korean glyph.
///
bool containsChineseCharacter(const QString &strText)
{
    for (const QChar ch : strText) {
        const ushort unicode = ch.unicode();
        if ((unicode >= 0x3400 && unicode <= 0x9fff)
            || (unicode >= 0xf900 && unicode <= 0xfaff)) {
            return true;
        }
    }

    return false;
}

///
/// \brief hasChineseApplicationTranslation
/// Detects applications that switched to Chinese without changing QLocale.
/// \return true when installed translators already expose Chinese UI text.
///
bool hasChineseApplicationTranslation()
{
    const QString strDemoSearch = QCoreApplication::translate(
        "DemoRibbonWindow", "Search");
    if (containsChineseCharacter(strDemoSearch)) {
        return true;
    }

    const QString strPageHelp = QCoreApplication::translate(
        "PageHelp", "Help");
    return containsChineseCharacter(strPageHelp);
}

///
/// \brief builtInChineseRibbonText
/// Returns LqRibbon's built-in simplified Chinese text for core UI strings.
/// \param sourceText English source text used by the public LqRibbon API.
/// \return Built-in Chinese text, or an empty string when the key is unknown.
///
QString builtInChineseRibbonText(const char *sourceText)
{
    const QLatin1String strSourceText(sourceText);
    for (const RibbonTranslationEntry &entry : ribbonTranslationTable) {
        if (strSourceText == QLatin1String(entry.sourceText)) {
            return QString::fromUtf8(entry.zhCnText);
        }
    }

    return QString();
}

///
/// \brief ribbonText
/// Translates LqRibbon core strings without requiring host project TS files.
/// \param sourceText English source text.
/// \return Text translated by installed translators or LqRibbon's fallback.
///
QString ribbonText(const char *sourceText)
{
    const QString strSourceText = QString::fromLatin1(sourceText);
    const QString strRibbonText = QCoreApplication::translate(
        "LqRibbon::RibbonBar", sourceText);
    if (strRibbonText != strSourceText) {
        return strRibbonText;
    }

    const QString strGenericRibbonText = QCoreApplication::translate(
        "LqRibbon", sourceText);
    if (strGenericRibbonText != strSourceText) {
        return strGenericRibbonText;
    }

    const bool chineseLocale = QLocale().language() == QLocale::Chinese
        || QLocale::system().language() == QLocale::Chinese;
    if (chineseLocale || hasChineseApplicationTranslation()) {
        const QString strBuiltInText = builtInChineseRibbonText(sourceText);
        if (!strBuiltInText.isEmpty()) {
            return strBuiltInText;
        }
    }

    return strSourceText;
}

class RibbonWindowButton : public QToolButton
{
public:
    enum ButtonKind
    {
        MinimizeButton,
        MaximizeButton,
        CloseButton
    };

public:
    explicit RibbonWindowButton(ButtonKind buttonKind, QWidget *parent = nullptr);

    void setRestoreMode(bool restoreMode);

protected:
    void paintEvent(QPaintEvent *event) override;

private:
    ButtonKind m_buttonKind;
    bool m_restoreMode;
};

class RibbonCollapseButton : public QToolButton
{
public:
    explicit RibbonCollapseButton(QWidget *parent = nullptr);

    void setCollapsed(bool collapsed);

protected:
    void paintEvent(QPaintEvent *event) override;

private:
    bool m_collapsed;
};

class RibbonMdiButton : public QToolButton
{
public:
    enum ButtonKind
    {
        MinimizeButton,
        MaximizeButton,
        CloseButton
    };

public:
    explicit RibbonMdiButton(ButtonKind buttonKind, QWidget *parent = nullptr);

    void setRestoreMode(bool restoreMode);

protected:
    void paintEvent(QPaintEvent *event) override;

private:
    ButtonKind m_buttonKind;
    bool m_restoreMode;
};

class RibbonMdiTitleBar : public QWidget
{
public:
    explicit RibbonMdiTitleBar(QMdiSubWindow *subWindow);

    void syncWithSubWindow();
    void cancelDrag();

protected:
    void mouseDoubleClickEvent(QMouseEvent *event) override;
    void mouseMoveEvent(QMouseEvent *event) override;
    void mousePressEvent(QMouseEvent *event) override;
    void mouseReleaseEvent(QMouseEvent *event) override;
    void paintEvent(QPaintEvent *event) override;

private:
    void toggleMaximized();
    void updateButtonGeometry();

private:
    QMdiSubWindow *m_subWindow;
    RibbonMdiButton *m_minimizeButton;
    RibbonMdiButton *m_maximizeButton;
    RibbonMdiButton *m_closeButton;
    QPoint m_dragGlobalPos;
    QPoint m_dragWindowPos;
    bool m_dragging;
};

///
/// \brief RibbonWindowButton::RibbonWindowButton
/// Creates a title-bar button used by the themed Ribbon frame.
/// \param buttonKind Button role to paint and activate.
/// \param parent Parent widget that owns the button.
///
RibbonWindowButton::RibbonWindowButton(ButtonKind buttonKind, QWidget *parent)
    : QToolButton(parent)
    , m_buttonKind(buttonKind)
    , m_restoreMode(false)
{
    setAutoRaise(true);
    setCursor(Qt::ArrowCursor);
    setFixedSize(ribbonWindowButtonWidth, ribbonWindowButtonHeight);
    setFocusPolicy(Qt::NoFocus);
}

///
/// \brief RibbonWindowButton::setRestoreMode
/// Selects whether the maximize button paints the restore glyph.
/// \param restoreMode true to paint restore, false to paint maximize.
///
void RibbonWindowButton::setRestoreMode(bool restoreMode)
{
    if (m_restoreMode == restoreMode) {
        return;
    }

    m_restoreMode = restoreMode;
    update();
}

///
/// \brief paintRibbonWindowButton
/// Paints the glyph for a themed minimize, maximize, restore, or close button.
/// \param painter Painter used to draw the glyph.
/// \param buttonRect Button rectangle in painter coordinates.
/// \param buttonKind Button role to draw.
/// \param restoreMode true to draw the restore glyph for maximize buttons.
///
void paintRibbonWindowButton(QPainter *painter,
                             const QRect &buttonRect,
                             RibbonWindowButton::ButtonKind buttonKind,
                             bool restoreMode)
{
    painter->save();

    QPen pen(Qt::white);
    pen.setWidthF(1.3);
    painter->setPen(pen);
    painter->setRenderHint(QPainter::Antialiasing, false);

    const int centerX = buttonRect.x() + buttonRect.width() / 2;
    const int centerY = buttonRect.y() + buttonRect.height() / 2;

    switch (buttonKind) {
    case RibbonWindowButton::MinimizeButton:
        painter->drawLine(centerX - 6, centerY + 5, centerX + 6, centerY + 5);
        break;
    case RibbonWindowButton::MaximizeButton:
        if (restoreMode) {
            painter->drawRect(QRect(centerX - 2, centerY - 7, 10, 10));
            painter->drawRect(QRect(centerX - 6, centerY - 3, 10, 10));
        } else {
            painter->drawRect(QRect(centerX - 6, centerY - 6, 12, 12));
        }
        break;
    case RibbonWindowButton::CloseButton:
        painter->drawLine(centerX - 5, centerY - 5, centerX + 5, centerY + 5);
        painter->drawLine(centerX + 5, centerY - 5, centerX - 5, centerY + 5);
        break;
    }

    painter->restore();
}

///
/// \brief createSearchIcon
/// Builds the small trailing magnifier used by the title-bar search edit.
/// \return Icon painted in the neutral Office-style search color.
///
QIcon createSearchIcon()
{
    QPixmap pixmap(16, 16);
    pixmap.fill(Qt::transparent);

    QPainter painter(&pixmap);
    painter.setRenderHint(QPainter::Antialiasing, true);
    QPen pen(QColor(QStringLiteral("#6f6f6f")));
    pen.setWidthF(1.3);
    painter.setPen(pen);
    painter.drawEllipse(QRectF(3.5, 3.5, 7.0, 7.0));
    painter.drawLine(QPointF(9.5, 9.5), QPointF(12.8, 12.8));

    return QIcon(pixmap);
}

///
/// \brief visibleWidgetRight
/// Calculates the visible right edge of a widget on its current screen.
/// \param widget Widget to inspect.
/// \return Right edge in widget coordinates, clipped to the available screen.
///
int visibleWidgetRight(const QWidget *widget)
{
    if (!widget) {
        return 0;
    }

    int right = widget->width();
    QWindow *windowHandle = widget->windowHandle();
    if (!windowHandle || !windowHandle->screen()) {
        return right;
    }

    const QRect screenGeometry = windowHandle->screen()->availableGeometry();
    const QPoint screenRight = widget->mapFromGlobal(
        QPoint(screenGeometry.right(), screenGeometry.top()));
    return qMin(right, screenRight.x() + 1);
}

///
/// \brief RibbonWindowButton::paintEvent
/// Paints the hover, pressed, and glyph states for a frame button.
/// \param event Paint event supplied by Qt.
///
void RibbonWindowButton::paintEvent(QPaintEvent *event)
{
    Q_UNUSED(event)

    QPainter painter(this);
    if (isDown()) {
        painter.fillRect(rect(),
                         m_buttonKind == CloseButton
                             ? QColor(QStringLiteral("#8f1f15"))
                             : QColor(QStringLiteral("#244d80")));
    } else if (underMouse()) {
        painter.fillRect(rect(),
                         m_buttonKind == CloseButton
                             ? QColor(QStringLiteral("#c42b1c"))
                             : QColor(QStringLiteral("#386caf")));
    }

    paintRibbonWindowButton(&painter, rect(), m_buttonKind, m_restoreMode);
}

///
/// \brief RibbonCollapseButton::RibbonCollapseButton
/// Creates the caption-row button that collapses or expands the Ribbon page.
/// \param parent Parent widget that owns the button.
///
RibbonCollapseButton::RibbonCollapseButton(QWidget *parent)
    : QToolButton(parent)
    , m_collapsed(false)
{
    setAutoRaise(true);
    setCursor(Qt::ArrowCursor);
    setFixedSize(ribbonCollapseButtonWidth, ribbonCollapseButtonHeight);
    setFocusPolicy(Qt::NoFocus);
}

///
/// \brief RibbonCollapseButton::setCollapsed
/// Selects whether the button paints the expand or collapse chevron.
/// \param collapsed true to paint expand, false to paint collapse.
///
void RibbonCollapseButton::setCollapsed(bool collapsed)
{
    if (m_collapsed == collapsed) {
        return;
    }

    m_collapsed = collapsed;
    update();
}

///
/// \brief RibbonCollapseButton::paintEvent
/// Paints the Office-style Ribbon collapse chevron.
/// \param event Paint event supplied by Qt.
///
void RibbonCollapseButton::paintEvent(QPaintEvent *event)
{
    Q_UNUSED(event)

    QPainter painter(this);
    if (isDown()) {
        painter.fillRect(rect(), QColor(QStringLiteral("#244d80")));
    } else if (underMouse()) {
        painter.fillRect(rect(), QColor(QStringLiteral("#386caf")));
    }

    QPen pen(Qt::white);
    pen.setWidthF(1.7);
    painter.setPen(pen);
    painter.setRenderHint(QPainter::Antialiasing, true);

    const int centerX = width() / 2;
    const int centerY = height() / 2;
    if (m_collapsed) {
        painter.drawLine(centerX - 6, centerY - 3, centerX, centerY + 3);
        painter.drawLine(centerX, centerY + 3, centerX + 6, centerY - 3);
    } else {
        painter.drawLine(centerX - 6, centerY + 3, centerX, centerY - 3);
        painter.drawLine(centerX, centerY - 3, centerX + 6, centerY + 3);
    }
}

///
/// \brief RibbonMdiButton::RibbonMdiButton
/// Creates a flat MDI child-window caption button.
/// \param buttonKind Button role to paint and activate.
/// \param parent Parent widget that owns the button.
///
RibbonMdiButton::RibbonMdiButton(ButtonKind buttonKind, QWidget *parent)
    : QToolButton(parent)
    , m_buttonKind(buttonKind)
    , m_restoreMode(false)
{
    setAutoRaise(true);
    setCursor(Qt::ArrowCursor);
    setFixedSize(ribbonMdiButtonWidth, ribbonMdiButtonHeight);
    setFocusPolicy(Qt::NoFocus);
}

///
/// \brief RibbonMdiButton::setRestoreMode
/// Selects whether the MDI maximize button paints the restore glyph.
/// \param restoreMode true to paint restore, false to paint maximize.
///
void RibbonMdiButton::setRestoreMode(bool restoreMode)
{
    if (m_restoreMode == restoreMode) {
        return;
    }

    m_restoreMode = restoreMode;
    update();
}

///
/// \brief RibbonMdiButton::paintEvent
/// Paints a flat caption button for styled MDI subwindows.
/// \param event Paint event supplied by Qt.
///
void RibbonMdiButton::paintEvent(QPaintEvent *event)
{
    Q_UNUSED(event)

    QPainter painter(this);
    if (isDown()) {
        painter.fillRect(rect(),
                         m_buttonKind == CloseButton
                             ? QColor(QStringLiteral("#8f1f15"))
                             : QColor(QStringLiteral("#244d80")));
    } else if (underMouse()) {
        painter.fillRect(rect(),
                         m_buttonKind == CloseButton
                             ? QColor(QStringLiteral("#c42b1c"))
                             : QColor(QStringLiteral("#386caf")));
    }

    QPen pen(Qt::white);
    pen.setWidthF(1.2);
    painter.setPen(pen);
    painter.setRenderHint(QPainter::Antialiasing, false);

    const int centerX = width() / 2;
    const int centerY = height() / 2;

    switch (m_buttonKind) {
    case MinimizeButton:
        painter.drawLine(centerX - 5, centerY + 5, centerX + 5, centerY + 5);
        break;
    case MaximizeButton:
        if (m_restoreMode) {
            painter.drawRect(QRect(centerX - 1, centerY - 6, 8, 8));
            painter.drawRect(QRect(centerX - 5, centerY - 2, 8, 8));
        } else {
            painter.drawRect(QRect(centerX - 5, centerY - 5, 10, 10));
        }
        break;
    case CloseButton:
        painter.drawLine(centerX - 4, centerY - 4, centerX + 4, centerY + 4);
        painter.drawLine(centerX + 4, centerY - 4, centerX - 4, centerY + 4);
        break;
    }
}

///
/// \brief RibbonMdiTitleBar::RibbonMdiTitleBar
/// Creates a flat title bar for a QMdiSubWindow.
/// \param subWindow MDI subwindow controlled by this title bar.
///
RibbonMdiTitleBar::RibbonMdiTitleBar(QMdiSubWindow *subWindow)
    : QWidget(subWindow)
    , m_subWindow(subWindow)
    , m_minimizeButton(new RibbonMdiButton(
                           RibbonMdiButton::MinimizeButton, this))
    , m_maximizeButton(new RibbonMdiButton(
                           RibbonMdiButton::MaximizeButton, this))
    , m_closeButton(new RibbonMdiButton(RibbonMdiButton::CloseButton, this))
    , m_dragging(false)
{
    setObjectName(QStringLiteral("lqRibbonMdiTitleBar"));
    setMouseTracking(true);
    setFixedHeight(ribbonMdiTitleHeight);

    connect(m_minimizeButton, &QToolButton::clicked, this, [this]() {
        m_subWindow->showMinimized();
    });
    connect(m_maximizeButton, &QToolButton::clicked, this, [this]() {
        toggleMaximized();
    });
    connect(m_closeButton, &QToolButton::clicked, this, [this]() {
        m_subWindow->close();
    });
}

///
/// \brief RibbonMdiTitleBar::syncWithSubWindow
/// Synchronizes geometry, button state, and stacking with the subwindow.
///
void RibbonMdiTitleBar::syncWithSubWindow()
{
    if (!m_subWindow) {
        return;
    }

    setGeometry(0,
                0,
                qMax(0, m_subWindow->width()),
                ribbonMdiTitleHeight);
    updateButtonGeometry();
    m_maximizeButton->setRestoreMode(m_subWindow->isMaximized());
    raise();
    update();
}

///
/// \brief RibbonMdiTitleBar::cancelDrag
/// Clears an active title-bar drag before hiding or changing MDI view mode.
///
void RibbonMdiTitleBar::cancelDrag()
{
    m_dragging = false;
    releaseMouse();
}

///
/// \brief RibbonMdiTitleBar::mouseDoubleClickEvent
/// Toggles the MDI subwindow maximized state on double click.
/// \param event Mouse event supplied by Qt.
///
void RibbonMdiTitleBar::mouseDoubleClickEvent(QMouseEvent *event)
{
    if (event->button() == Qt::LeftButton) {
        toggleMaximized();
        event->accept();
        return;
    }

    QWidget::mouseDoubleClickEvent(event);
}

///
/// \brief RibbonMdiTitleBar::mouseMoveEvent
/// Moves the MDI subwindow while the title bar is being dragged.
/// \param event Mouse event supplied by Qt.
///
void RibbonMdiTitleBar::mouseMoveEvent(QMouseEvent *event)
{
    if (!(event->buttons() & Qt::LeftButton)) {
        m_dragging = false;
        releaseMouse();
    }

    if (!m_dragging || !m_subWindow || m_subWindow->isMaximized()) {
        QWidget::mouseMoveEvent(event);
        return;
    }

    const QPoint delta = event->globalPos() - m_dragGlobalPos;
    m_subWindow->move(m_dragWindowPos + delta);
    event->accept();
}

///
/// \brief RibbonMdiTitleBar::mousePressEvent
/// Starts an MDI title-bar drag operation.
/// \param event Mouse event supplied by Qt.
///
void RibbonMdiTitleBar::mousePressEvent(QMouseEvent *event)
{
    if (event->button() == Qt::LeftButton && m_subWindow) {
        if (m_subWindow->mdiArea()) {
            m_subWindow->mdiArea()->setActiveSubWindow(m_subWindow);
        }

        m_dragging = true;
        m_dragGlobalPos = event->globalPos();
        m_dragWindowPos = m_subWindow->pos();
        grabMouse();
        event->accept();
        return;
    }

    QWidget::mousePressEvent(event);
}

///
/// \brief RibbonMdiTitleBar::mouseReleaseEvent
/// Ends an MDI title-bar drag operation.
/// \param event Mouse event supplied by Qt.
///
void RibbonMdiTitleBar::mouseReleaseEvent(QMouseEvent *event)
{
    if (event->button() == Qt::LeftButton) {
        m_dragging = false;
        releaseMouse();
        event->accept();
        return;
    }

    QWidget::mouseReleaseEvent(event);
}

///
/// \brief RibbonMdiTitleBar::paintEvent
/// Paints the flat MDI title background, icon, and title text.
/// \param event Paint event supplied by Qt.
///
void RibbonMdiTitleBar::paintEvent(QPaintEvent *event)
{
    Q_UNUSED(event)

    QPainter painter(this);
    painter.fillRect(rect(), QColor(QStringLiteral("#2b579a")));

    if (!m_subWindow) {
        return;
    }

    const QIcon icon = m_subWindow->windowIcon();
    if (!icon.isNull()) {
        icon.paint(&painter, QRect(6, 6, 16, 16));
    }

    painter.setPen(Qt::white);
    const int textLeft = icon.isNull() ? 8 : 28;
    const int buttonGroupLeft = qMax(0, width() - (ribbonMdiButtonWidth * 3));
    const int textWidth = qMax(0, buttonGroupLeft - textLeft - 6);
    if (textWidth > 0) {
        painter.drawText(QRect(textLeft, 0, textWidth, height()),
                         Qt::AlignLeft | Qt::AlignVCenter,
                         m_subWindow->windowTitle());
    }
}

///
/// \brief RibbonMdiTitleBar::toggleMaximized
/// Switches the controlled MDI subwindow between normal and maximized states.
///
void RibbonMdiTitleBar::toggleMaximized()
{
    if (!m_subWindow) {
        return;
    }

    if (m_subWindow->isMaximized()) {
        m_subWindow->showNormal();
    } else {
        m_subWindow->showMaximized();
    }

    syncWithSubWindow();
}

///
/// \brief RibbonMdiTitleBar::updateButtonGeometry
/// Places minimize, maximize, and close buttons at the right edge.
///
void RibbonMdiTitleBar::updateButtonGeometry()
{
    int x = qMax(0, width() - (ribbonMdiButtonWidth * 3));
    const int y = qMax(0, (height() - ribbonMdiButtonHeight) / 2);
    m_minimizeButton->setGeometry(x, y, ribbonMdiButtonWidth, ribbonMdiButtonHeight);
    x += ribbonMdiButtonWidth;
    m_maximizeButton->setGeometry(x, y, ribbonMdiButtonWidth, ribbonMdiButtonHeight);
    x += ribbonMdiButtonWidth;
    m_closeButton->setGeometry(x, y, ribbonMdiButtonWidth, ribbonMdiButtonHeight);
}

const char ribbonStyleSheet[] =
    "LqRibbon--RibbonBar {"
    "    background: #f3f3f3;"
    "}"
    "QTabWidget::pane {"
    "    border: none;"
    "    background: #f3f3f3;"
    "}"
    "QTabBar {"
    "    background: transparent;"
    "}"
    "QTabBar::tab {"
    "    min-width: 46px;"
    "    min-height: 21px;"
    "    padding: 2px 10px 1px 10px;"
    "    color: #ffffff;"
    "    background: transparent;"
    "    border: none;"
    "}"
    "QTabBar::tab:selected {"
    "    background: #ffffff;"
    "    color: #1f1f1f;"
    "    border-left: 1px solid #c8c8c8;"
    "    border-right: 1px solid #c8c8c8;"
    "    border-top: 1px solid #c8c8c8;"
    "}"
    "QTabBar::tab:hover:!selected {"
    "    background: #386caf;"
    "}"
    "QLineEdit#lqRibbonSearchEdit {"
    "    min-height: 18px;"
    "    padding: 0px 22px 0px 6px;"
    "    border: 1px solid #b7cbe6;"
    "    border-radius: 1px;"
    "    background: #ffffff;"
    "    selection-background-color: #2b579a;"
    "}"
    "QLineEdit#lqRibbonSearchEdit:focus {"
    "    border-color: #5f95d0;"
    "}"
    "QAbstractItemView#lqRibbonSearchSuggestionPopup {"
    "    border: 1px solid #9eb6d8;"
    "    background: #ffffff;"
    "    selection-background-color: #dcecff;"
    "    selection-color: #202020;"
    "}"
    "QListView#lqRibbonSearchPopupView {"
    "    border: 1px solid #8c8c8c;"
    "    background: #f4f4f4;"
    "    outline: 0px;"
    "}"
    "QListView#lqRibbonSearchPopupView::item {"
    "    min-height: 22px;"
    "    padding: 1px 6px;"
    "    color: #202020;"
    "}"
    "QListView#lqRibbonSearchPopupView::item:selected {"
    "    background: #e8f2ff;"
    "    color: #202020;"
    "}"
    "QToolBar#lqRibbonQuickAccessBar {"
    "    background: transparent;"
    "    border: none;"
    "    spacing: 1px;"
    "}"
    "QToolBar#lqRibbonQuickAccessBar QToolButton {"
    "    border: 1px solid #6f9fd0;"
    "    border-radius: 2px;"
    "    padding: 2px;"
    "    background: #2f63a3;"
    "}"
    "QToolBar#lqRibbonQuickAccessBar QToolButton:hover {"
    "    background: #386caf;"
    "    border-color: #b7cbe6;"
    "}"
    "LqRibbon--RibbonGroup {"
    "    background: transparent;"
    "    border: none;"
    "    border-right: 1px solid #d6d6d6;"
    "    border-radius: 0px;"
    "    margin: 0px;"
    "}"
    "LqRibbon--RibbonGroup QLabel#lqRibbonGroupTitle {"
    "    color: #676767;"
    "    font-size: 11px;"
    "    padding: 0px 4px 3px 4px;"
    "}"
    "LqRibbon--RibbonGroup QToolButton {"
    "    border: 1px solid transparent;"
    "    border-radius: 1px;"
    "    padding: 1px 2px;"
    "    color: #202020;"
    "    background: transparent;"
    "}"
    "LqRibbon--RibbonGroup QToolButton:hover {"
    "    background: #dcecff;"
    "    border-color: #80a9dc;"
    "}"
    "LqRibbon--RibbonGroup QToolButton:pressed {"
    "    background: #c5ddfa;"
    "    border-color: #5f95d0;"
    "}"
    "LqRibbon--RibbonGroup QToolButton::menu-button {"
    "    border: none;"
    "    width: 14px;"
    "}"
    "LqRibbon--RibbonGroup QToolButton::menu-indicator {"
    "    width: 10px;"
    "    subcontrol-origin: padding;"
    "    subcontrol-position: center right;"
    "    right: 3px;"
    "}";

const char ribbonMdiAreaStyleSheet[] =
    "QMdiArea {"
    "    background: #cfcfcf;"
    "}"
    "QMdiSubWindow {"
    "    background: #ffffff;"
    "    border: 1px solid #8aaed7;"
    "}"
    "QMdiSubWindow::title {"
    "    background: #2b579a;"
    "    color: #ffffff;"
    "    padding-left: 6px;"
    "    height: 28px;"
    "}"
    "QMdiSubWindow::close-button,"
    "QMdiSubWindow::normal-button,"
    "QMdiSubWindow::minimize-button {"
    "    border: none;"
    "    width: 28px;"
    "    height: 22px;"
    "    background: transparent;"
    "}"
    "QMdiSubWindow::close-button:hover {"
    "    background: #c42b1c;"
    "}"
    "QMdiSubWindow::normal-button:hover,"
    "QMdiSubWindow::minimize-button:hover {"
    "    background: #386caf;"
    "}"
    "QTabBar {"
    "    background: #d7d7d7;"
    "}"
    "QTabBar::tab {"
    "    min-width: 0px;"
    "    padding: 4px 16px 4px 10px;"
    "    border: 1px solid #9eb6d8;"
    "    border-bottom: none;"
    "    background: #efefef;"
    "    color: #202020;"
    "}"
    "QTabBar::tab:selected {"
    "    background: #ffffff;"
    "    color: #202020;"
    "}"
    "QTabBar::tab:hover:!selected {"
    "    background: #e8f2ff;"
    "}";

///
/// \brief prepareMetricWidget
/// Applies the font and style polish needed for size-hint measurements.
/// \param widget Temporary widget used only for metric calculation.
/// \param font Font that should be measured.
///
void prepareMetricWidget(QWidget *widget, const QFont &font)
{
    widget->setAttribute(Qt::WA_MacSmallSize);
    widget->setFont(font);
    widget->ensurePolished();
}

///
/// \brief ribbonStyleIconSize
/// Reads a square icon size from the current Qt style.
/// \param widget Widget whose style should provide the metric.
/// \param pixelMetric Style pixel metric to read.
/// \return Square icon size in logical pixels.
///
QSize ribbonStyleIconSize(const QWidget *widget, QStyle::PixelMetric pixelMetric)
{
    const int iconSize = widget->style()->pixelMetric(pixelMetric, nullptr, widget);
    return QSize(iconSize, iconSize);
}

///
/// \brief ribbonLargeIconSize
/// Returns the style large-icon size used by major Ribbon commands.
/// \param widget Widget whose style should provide the metric.
/// \return Large icon size in logical pixels.
///
QSize ribbonLargeIconSize(const QWidget *widget)
{
    return ribbonStyleIconSize(widget, QStyle::PM_LargeIconSize);
}

///
/// \brief ribbonSmallIconSize
/// Returns the style small-icon size used by compact Ribbon commands.
/// \param widget Widget whose style should provide the metric.
/// \return Small icon size in logical pixels.
///
QSize ribbonSmallIconSize(const QWidget *widget)
{
    return ribbonStyleIconSize(widget, QStyle::PM_SmallIconSize);
}

///
/// \brief ribbonRowItemHeight
/// Calculates the height for one compact Ribbon row.
/// \param widget Widget whose font and style should be measured.
/// \return Row height in logical pixels.
///
int ribbonRowItemHeight(const QWidget *widget)
{
    const QFont widgetFont = widget->font();
    const QFontMetrics fontMetrics(widgetFont);
    int rowItemHeight = fontMetrics.height();

    QLineEdit lineEdit;
    prepareMetricWidget(&lineEdit, widgetFont);
    rowItemHeight = qMax(rowItemHeight, lineEdit.sizeHint().height());

    QComboBox comboBox;
    prepareMetricWidget(&comboBox, widgetFont);
    rowItemHeight = qMax(rowItemHeight, comboBox.sizeHint().height());

    QComboBox editableComboBox;
    editableComboBox.setEditable(true);
    prepareMetricWidget(&editableComboBox, widgetFont);
    rowItemHeight = qMax(rowItemHeight, editableComboBox.sizeHint().height());

    QSpinBox spinBox;
    prepareMetricWidget(&spinBox, widgetFont);
    rowItemHeight = qMax(rowItemHeight, spinBox.sizeHint().height());

    return rowItemHeight + (fontMetrics.height() / 4);
}

///
/// \brief ribbonLargeButtonHeight
/// Calculates the height for a large Ribbon command button.
/// \param widget Widget whose font and style should be measured.
/// \return Large button height in logical pixels.
///
int ribbonLargeButtonHeight(const QWidget *widget)
{
    return ribbonRowItemHeight(widget) * ribbonRowItemCount;
}

///
/// \brief ribbonGroupTitleHeight
/// Calculates the height reserved for a group title label.
/// \param widget Widget whose font should be measured.
/// \return Group title height in logical pixels.
///
int ribbonGroupTitleHeight(const QWidget *widget)
{
    const QFontMetrics fontMetrics(widget->font());
    return qRound(fontMetrics.height() * 1.2);
}

///
/// \brief ribbonGroupHeight
/// Calculates the content height of a Ribbon group.
/// \param widget Widget whose font and style should be measured.
/// \return Group height in logical pixels.
///
int ribbonGroupHeight(const QWidget *widget)
{
    return ribbonLargeButtonHeight(widget)
        + ribbonGroupTopMargin
        + ribbonGroupBottomMargin
        + ribbonGroupTitleHeight(widget);
}

///
/// \brief ribbonBarHeight
/// Calculates the full Ribbon bar height including caption and tabs.
/// \param widget Widget whose font and style should be measured.
/// \return Ribbon bar height in logical pixels.
///
int ribbonBarHeight(const QWidget *widget)
{
    const int calculatedHeight = ribbonCaptionHeight
        + ribbonTabHeight
        + ribbonGroupHeight(widget);

    return qMax(ribbonDefaultBarHeight, calculatedHeight);
}

///
/// \brief cleanRibbonButtonText
/// Removes Qt mnemonic markers and trims command text.
/// \param strText Original action or button text.
/// \return Text suitable for painting and search matching.
///
QString cleanRibbonButtonText(const QString &strText)
{
    QString strCleanText = strText;
    strCleanText.remove(QLatin1Char('&'));
    return strCleanText.trimmed();
}

///
/// \brief ribbonButtonTextWidth
/// Measures the widest line of a Ribbon button text.
/// \param widget Widget whose font should be measured.
/// \param strText Text that may contain line breaks.
/// \return Maximum text width in logical pixels.
///
int ribbonButtonTextWidth(const QWidget *widget, const QString &strText)
{
    const QFontMetrics fontMetrics(widget->font());
    const QStringList strLineList = strText.split(QLatin1Char('\n'));
    int textWidth = 0;

    for (const QString &strLine : strLineList) {
        textWidth = qMax(textWidth, fontMetrics.horizontalAdvance(strLine));
    }

    return textWidth;
}

///
/// \brief ribbonLargeButtonWidth
/// Calculates a Qtitan-like width for a large Ribbon command button.
/// \param button Button whose text, icon, menu, and style are measured.
/// \return Bounded large button width in logical pixels.
///
int ribbonLargeButtonWidth(const QToolButton *button)
{
    const QString strButtonText = cleanRibbonButtonText(button->text());
    const int textWidth = ribbonButtonTextWidth(button, strButtonText);
    const int styleWidth = button->sizeHint().width();
    const int iconWidth = button->icon().isNull()
        ? 0
        : ribbonLargeIconSize(button).width() + 4;
    const int menuIndicatorWidth = button->menu()
        ? button->style()->pixelMetric(QStyle::PM_MenuButtonIndicator, nullptr, button)
        : 0;
    const int menuWidth = button->menu() ? menuIndicatorWidth : 0;

    return qBound(ribbonLargeButtonMinimumWidth,
                  qMax(qMax(textWidth + menuWidth + 12, iconWidth), styleWidth),
                  ribbonLargeButtonMaximumWidth);
}

///
/// \brief ribbonSmallButtonWidth
/// Calculates a Qtitan-like width for a compact Ribbon command button.
/// \param button Button whose text, icon, menu, and style are measured.
/// \return Bounded compact button width in logical pixels.
///
int ribbonSmallButtonWidth(const QToolButton *button)
{
    const QString strButtonText = cleanRibbonButtonText(button->text());
    const int textWidth = ribbonButtonTextWidth(button, strButtonText);
    const int styleWidth = button->sizeHint().width();
    const int rowItemHeight = ribbonRowItemHeight(button);
    const int iconTextWidth = button->icon().isNull()
        ? 0
        : rowItemHeight;
    const int menuIndicatorWidth = button->menu()
        ? button->style()->pixelMetric(QStyle::PM_MenuButtonIndicator, nullptr, button)
        : 0;
    const int menuWidth = button->menu() ? menuIndicatorWidth : 0;

    return qBound(ribbonSmallButtonMinimumWidth,
                  qMax(iconTextWidth + textWidth + menuWidth + 10, styleWidth),
                  ribbonSmallButtonMaximumWidth);
}

///
/// \brief createSearchHeaderItem
/// Creates a non-selectable section header for the search popup.
/// \param strText Header text.
/// \return New model item owned by the caller after insertion.
///
QStandardItem *createSearchHeaderItem(const QString &strText)
{
    QStandardItem *item = new QStandardItem(strText);
    QFont itemFont = item->font();
    itemFont.setBold(true);
    item->setFont(itemFont);
    item->setFlags(Qt::NoItemFlags);
    item->setData(SearchPopupHeaderItem, ribbonSearchPopupKindRole);
    item->setData(QColor(QStringLiteral("#d0d0d0")), Qt::BackgroundRole);
    item->setData(QColor(QStringLiteral("#333333")), Qt::ForegroundRole);
    return item;
}

///
/// \brief createSearchActionItem
/// Creates a selectable search result row for an action.
/// \param action Action represented by the row.
/// \return New model item owned by the caller after insertion.
///
QStandardItem *createSearchActionItem(QAction *action)
{
    QStandardItem *item = new QStandardItem(action->icon(),
                                           cleanRibbonButtonText(action->text()));
    item->setFlags(Qt::ItemIsEnabled | Qt::ItemIsSelectable);
    item->setData(SearchPopupActionItem, ribbonSearchPopupKindRole);
    item->setData(static_cast<qlonglong>(reinterpret_cast<quintptr>(action)),
                  ribbonSearchPopupActionRole);
    return item;
}

///
/// \brief createSearchHelpItem
/// Creates a selectable helper row shown when no action matches.
/// \param strText Help text displayed in the popup.
/// \param icon Icon displayed before the help text.
/// \return New model item owned by the caller after insertion.
///
QStandardItem *createSearchHelpItem(const QString &strText, const QIcon &icon)
{
    QStandardItem *item = new QStandardItem(icon, strText);
    item->setFlags(Qt::ItemIsEnabled | Qt::ItemIsSelectable);
    item->setData(SearchPopupHelpItem, ribbonSearchPopupKindRole);
    return item;
}

} // namespace

namespace LqRibbon {

///
/// \brief RibbonGroup::RibbonGroup
/// Builds a titled Ribbon group and initializes its content layout.
/// \param strTitle Title displayed at the bottom of the group.
/// \param parent Parent widget that owns the group.
///
RibbonGroup::RibbonGroup(const QString &strTitle, QWidget *parent)
    : QFrame(parent)
    , m_titleLabel(new QLabel(strTitle, this))
    , m_contentLayout(new QHBoxLayout)
    , m_smallButtonLayout(nullptr)
    , m_smallButtonWidget(nullptr)
    , m_smallButtonRow(0)
    , m_smallButtonColumn(0)
{
    setObjectName(QStringLiteral("lqRibbonGroup"));
    setSizePolicy(QSizePolicy::Maximum, QSizePolicy::Preferred);
    setMinimumWidth(44);

    m_titleLabel->setObjectName(QStringLiteral("lqRibbonGroupTitle"));
    m_titleLabel->setAlignment(Qt::AlignCenter);

    m_contentLayout->setContentsMargins(ribbonGroupLeftMargin,
                                        ribbonGroupTopMargin,
                                        ribbonGroupRightMargin,
                                        ribbonGroupBottomMargin);
    m_contentLayout->setSpacing(2);
    m_contentLayout->setAlignment(Qt::AlignLeft | Qt::AlignTop);

    QVBoxLayout *mainLayout = new QVBoxLayout(this);
    mainLayout->setContentsMargins(0, 0, 0, 0);
    mainLayout->setSpacing(0);
    mainLayout->addLayout(m_contentLayout, 1);
    mainLayout->addWidget(m_titleLabel);
    updateMetrics();
}

///
/// \brief RibbonGroup::addAction
/// Creates an action and adds a matching command button to the group.
/// \param icon Icon displayed by the command button.
/// \param strText Text displayed by the command button.
/// \param buttonStyle Button style used by the created command button.
/// \return Newly created action owned by the group.
///
QAction *RibbonGroup::addAction(const QIcon &icon,
                                const QString &strText,
                                Qt::ToolButtonStyle buttonStyle)
{
    QAction *action = new QAction(icon, strText, this);
    addAction(action, buttonStyle);
    return action;
}

///
/// \brief RibbonGroup::addAction
/// Adds an existing action as a Ribbon command button.
/// \param action Existing action to expose in the group.
/// \param buttonStyle Button style used by the created command button.
///
void RibbonGroup::addAction(QAction *action, Qt::ToolButtonStyle buttonStyle)
{
    if (!action) {
        return;
    }

    QToolButton *button = createButton(action, buttonStyle);
    if (buttonStyle == Qt::ToolButtonTextBesideIcon) {
        addSmallButton(button);
        return;
    }

    m_contentLayout->addWidget(button);
}

///
/// \brief RibbonGroup::addWidget
/// Adds a custom widget into the group content area.
/// \param widget Widget inserted into the group layout.
///
void RibbonGroup::addWidget(QWidget *widget)
{
    if (!widget) {
        return;
    }

    widget->setParent(this);

    QToolButton *button = qobject_cast<QToolButton *>(widget);
    if (button) {
        setupSmallButton(button);
        addSmallButton(button);
        return;
    }

    m_contentLayout->addWidget(widget);
}

///
/// \brief RibbonGroup::title
/// Returns the group title text.
/// \return Current group title.
///
QString RibbonGroup::title() const
{
    return m_titleLabel->text();
}

///
/// \brief RibbonGroup::setTitle
/// Updates the group title text.
/// \param strTitle New group title.
///
void RibbonGroup::setTitle(const QString &strTitle)
{
    m_titleLabel->setText(strTitle);
}

///
/// \brief RibbonGroup::event
/// Refreshes metrics when the group receives style or font changes.
/// \param event Qt event delivered to the group.
/// \return true when the event is handled.
///
bool RibbonGroup::event(QEvent *event)
{
    const bool handled = QFrame::event(event);

    switch (event->type()) {
    case QEvent::FontChange:
    case QEvent::PolishRequest:
    case QEvent::StyleChange:
        updateMetrics();
        break;
    default:
        break;
    }

    return handled;
}

///
/// \brief RibbonGroup::createButton
/// Creates and configures a tool button for a Ribbon action.
/// \param action Action assigned to the button.
/// \param buttonStyle Qt tool button style used by the button.
/// \return Newly created button owned by the group.
///
QToolButton *RibbonGroup::createButton(QAction *action, Qt::ToolButtonStyle buttonStyle)
{
    QToolButton *button = new QToolButton(this);
    button->setDefaultAction(action);
    button->setAutoRaise(true);
    button->setToolButtonStyle(buttonStyle);
    button->setFocusPolicy(Qt::NoFocus);

    if (action->menu()) {
        button->setMenu(action->menu());
        button->setPopupMode(QToolButton::MenuButtonPopup);
    }

    if (buttonStyle != Qt::ToolButtonTextUnderIcon) {
        setupSmallButton(button);
        return button;
    }

    button->setIconSize(ribbonLargeIconSize(button));
    button->setPopupMode(action->menu()
                         ? QToolButton::MenuButtonPopup
                         : QToolButton::DelayedPopup);
    const int buttonWidth = ribbonLargeButtonWidth(button);
    const int buttonHeight = ribbonLargeButtonHeight(button);
    button->setMinimumSize(buttonWidth, buttonHeight);
    button->setMaximumSize(buttonWidth, buttonHeight);
    button->setSizePolicy(QSizePolicy::Fixed, QSizePolicy::Fixed);

    return button;
}

///
/// \brief RibbonGroup::addSmallButton
/// Adds a compact command widget to the three-row small-button grid.
/// \param widget Widget inserted into the compact command grid.
///
void RibbonGroup::addSmallButton(QWidget *widget)
{
    if (!widget) {
        return;
    }

    smallButtonLayout()->addWidget(widget, m_smallButtonRow, m_smallButtonColumn);
    ++m_smallButtonRow;

    if (m_smallButtonRow >= ribbonRowItemCount) {
        m_smallButtonRow = 0;
        ++m_smallButtonColumn;
    }
}

///
/// \brief RibbonGroup::setupSmallButton
/// Applies compact icon and geometry metrics to a small command button.
/// \param button Button to configure.
///
void RibbonGroup::setupSmallButton(QToolButton *button)
{
    if (!button) {
        return;
    }

    button->setAutoRaise(true);
    button->setFocusPolicy(Qt::NoFocus);
    button->setToolButtonStyle(Qt::ToolButtonTextBesideIcon);
    button->setIconSize(ribbonSmallIconSize(button));
    button->setStyleSheet(QString());
    button->setPopupMode(button->menu()
                         ? QToolButton::MenuButtonPopup
                         : QToolButton::DelayedPopup);

    const int buttonWidth = ribbonSmallButtonWidth(button);
    const int buttonHeight = ribbonRowItemHeight(button);
    button->setMinimumSize(buttonWidth, buttonHeight);
    button->setMaximumSize(buttonWidth, buttonHeight);
    button->setSizePolicy(QSizePolicy::Fixed, QSizePolicy::Fixed);
}

///
/// \brief RibbonGroup::smallButtonLayout
/// Lazily creates and returns the compact command grid layout.
/// \return Small-button grid layout owned by the group.
///
QGridLayout *RibbonGroup::smallButtonLayout()
{
    if (m_smallButtonLayout) {
        return m_smallButtonLayout;
    }

    m_smallButtonWidget = new QWidget(this);
    m_smallButtonWidget->setSizePolicy(QSizePolicy::Maximum, QSizePolicy::Fixed);
    m_smallButtonLayout = new QGridLayout(m_smallButtonWidget);
    m_smallButtonLayout->setContentsMargins(0, 0, 0, 0);
    m_smallButtonLayout->setHorizontalSpacing(ribbonSmallButtonColumnSpacing);
    m_smallButtonLayout->setVerticalSpacing(0);
    m_smallButtonLayout->setSizeConstraint(QLayout::SetFixedSize);
    const int rowItemHeight = ribbonRowItemHeight(this);
    for (int row = 0; row < ribbonRowItemCount; ++row) {
        m_smallButtonLayout->setRowMinimumHeight(row, rowItemHeight);
    }

    m_contentLayout->addWidget(m_smallButtonWidget, 0, Qt::AlignTop);
    return m_smallButtonLayout;
}

///
/// \brief RibbonGroup::updateMetrics
/// Recalculates group and title geometry from the current style.
///
void RibbonGroup::updateMetrics()
{
    setMinimumHeight(ribbonGroupHeight(this));
    m_titleLabel->setFixedHeight(ribbonGroupTitleHeight(this));

    if (m_smallButtonLayout) {
        const int rowItemHeight = ribbonRowItemHeight(this);
        for (int row = 0; row < ribbonRowItemCount; ++row) {
            m_smallButtonLayout->setRowMinimumHeight(row, rowItemHeight);
        }
    }

    const QList<QToolButton *> buttonList = findChildren<QToolButton *>();
    for (QToolButton *button : buttonList) {
        if (button->toolButtonStyle() == Qt::ToolButtonTextUnderIcon) {
            button->setIconSize(ribbonLargeIconSize(button));
            const int buttonWidth = ribbonLargeButtonWidth(button);
            const int buttonHeight = ribbonLargeButtonHeight(button);
            button->setMinimumSize(buttonWidth, buttonHeight);
            button->setMaximumSize(buttonWidth, buttonHeight);
        } else {
            setupSmallButton(button);
        }
    }
}

///
/// \brief RibbonPage::RibbonPage
/// Builds a Ribbon page that owns a horizontal group layout.
/// \param strTitle Title shown by the corresponding Ribbon tab.
/// \param parent Parent widget.
///
RibbonPage::RibbonPage(const QString &strTitle, QWidget *parent)
    : QWidget(parent)
    , m_strTitle(strTitle)
    , m_groupLayout(new QHBoxLayout)
{
    m_groupLayout->setContentsMargins(0, 0, 0, 0);
    m_groupLayout->setSpacing(0);
    m_groupLayout->addStretch(1);

    QVBoxLayout *mainLayout = new QVBoxLayout(this);
    mainLayout->setContentsMargins(0, 0, 0, 0);
    mainLayout->addLayout(m_groupLayout);
}

///
/// \brief RibbonPage::addGroup
/// Creates and appends a titled group to the page.
/// \param strTitle Title displayed by the new group.
/// \return Newly created group owned by the page.
///
RibbonGroup *RibbonPage::addGroup(const QString &strTitle)
{
    RibbonGroup *group = new RibbonGroup(strTitle, this);
    const int stretchIndex = m_groupLayout->count() - 1;
    m_groupLayout->insertWidget(stretchIndex, group);
    return group;
}

///
/// \brief RibbonPage::title
/// Returns the title mirrored to the Ribbon tab.
/// \return Current page title.
///
QString RibbonPage::title() const
{
    return m_strTitle;
}

///
/// \brief RibbonPage::setTitle
/// Updates the page title and emits titleChanged when needed.
/// \param strTitle New page title.
///
void RibbonPage::setTitle(const QString &strTitle)
{
    if (m_strTitle == strTitle) {
        return;
    }

    m_strTitle = strTitle;
    emit titleChanged(strTitle);
}

///
/// \brief RibbonBar::RibbonBar
/// Creates the Ribbon bar, search box, quick access bar, and frame buttons.
/// \param parent Parent widget.
///
RibbonBar::RibbonBar(QWidget *parent)
    : QTabWidget(parent)
    , m_searchEdit(new QLineEdit(this))
    , m_searchPopupView(new QListView(this))
    , m_searchPopupModel(new QStandardItemModel(this))
    , m_searchLineAction(nullptr)
    , m_quickAccessBar(new QToolBar(this))
    , m_minimizeButton(new RibbonWindowButton(
                           RibbonWindowButton::MinimizeButton, this))
    , m_maximizeButton(new RibbonWindowButton(
                           RibbonWindowButton::MaximizeButton, this))
    , m_closeButton(new RibbonWindowButton(
                        RibbonWindowButton::CloseButton, this))
    , m_collapseButton(new RibbonCollapseButton(this))
    , m_searchSuggestionModel(new QStringListModel(this))
    , m_searchCompleter(new QCompleter(m_searchSuggestionModel, this))
    , m_searchActionTriggerEnabled(true)
    , m_recentSearchLimit(8)
    , m_frameThemeEnabled(false)
    , m_ribbonMinimized(false)
    , m_searchVisibleExplicitlySet(false)
    , m_searchPlaceholderExplicitlySet(false)
{
    setDocumentMode(false);
    setMovable(false);
    setTabPosition(QTabWidget::North);
    updateRibbonMetrics();
    tabBar()->setExpanding(false);
    tabBar()->setUsesScrollButtons(true);

    m_searchEdit->setObjectName(QStringLiteral("lqRibbonSearchEdit"));
    m_searchEdit->setPlaceholderText(ribbonText("Search"));
    m_searchEdit->setClearButtonEnabled(false);
    m_searchEdit->hide();
    m_searchEdit->installEventFilter(this);
    m_searchLineAction = m_searchEdit->addAction(
        createSearchIcon(), QLineEdit::TrailingPosition);
    m_searchCompleter->setCaseSensitivity(Qt::CaseInsensitive);
    m_searchCompleter->setFilterMode(Qt::MatchContains);
    m_searchCompleter->setCompletionMode(QCompleter::PopupCompletion);
    m_searchCompleter->setMaxVisibleItems(8);
    m_searchCompleter->popup()->setObjectName(
        QStringLiteral("lqRibbonSearchSuggestionPopup"));

    m_searchPopupView->setObjectName(QStringLiteral("lqRibbonSearchPopupView"));
    m_searchPopupView->setModel(m_searchPopupModel);
    m_searchPopupView->setEditTriggers(QAbstractItemView::NoEditTriggers);
    m_searchPopupView->setHorizontalScrollBarPolicy(Qt::ScrollBarAlwaysOff);
    m_searchPopupView->setVerticalScrollBarPolicy(Qt::ScrollBarAlwaysOff);
    m_searchPopupView->setSelectionBehavior(QAbstractItemView::SelectRows);
    m_searchPopupView->setSelectionMode(QAbstractItemView::SingleSelection);
    m_searchPopupView->setUniformItemSizes(false);
    m_searchPopupView->installEventFilter(this);
    m_searchPopupView->hide();

    m_quickAccessBar->setObjectName(QStringLiteral("lqRibbonQuickAccessBar"));
    m_quickAccessBar->setMovable(false);
    m_quickAccessBar->setFloatable(false);
    m_quickAccessBar->setIconSize(ribbonSmallIconSize(m_quickAccessBar));
    m_quickAccessBar->setToolButtonStyle(Qt::ToolButtonIconOnly);
    m_quickAccessBar->hide();

    setupWindowControlButton(m_minimizeButton);
    setupWindowControlButton(m_maximizeButton);
    setupWindowControlButton(m_closeButton);
    setupWindowControlButton(m_collapseButton);
    updateLocalizedText();
    updateWindowControlVisibility();

    connect(this, &QTabWidget::currentChanged, this, &RibbonBar::pageChanged);
    connect(m_searchEdit, &QLineEdit::textChanged,
            this, &RibbonBar::searchTextChanged);
    connect(m_searchEdit, &QLineEdit::textEdited,
            this, &RibbonBar::updateSearchPopup);
    connect(m_searchPopupView, &QListView::clicked,
            this, &RibbonBar::activateSearchPopupIndex);
    connect(m_searchLineAction, &QAction::triggered, this, [this]() {
        m_searchEdit->setFocus();
        const QString strText = m_searchEdit->text().trimmed();
        if (strText.isEmpty()) {
            updateSearchPopup();
            return;
        }

        if (!triggerSearchAction(strText)) {
            emit searchAccepted(strText);
        }
        finishSearch();
    });
    connect(m_minimizeButton, &QToolButton::clicked, this, [this]() {
        if (QWidget *topLevelWidget = window()) {
            topLevelWidget->showMinimized();
        }
    });
    connect(m_maximizeButton, &QToolButton::clicked, this, [this]() {
        QWidget *topLevelWidget = window();
        if (!topLevelWidget) {
            return;
        }

        if (topLevelWidget->isMaximized()) {
            topLevelWidget->showNormal();
        } else {
            topLevelWidget->showMaximized();
        }

        updateWindowControlState();
    });
    connect(m_closeButton, &QToolButton::clicked, this, [this]() {
        if (QWidget *topLevelWidget = window()) {
            topLevelWidget->close();
        }
    });
    connect(m_collapseButton, &QToolButton::clicked, this, [this]() {
        setRibbonMinimized(!m_ribbonMinimized);
    });
    connect(m_searchEdit, &QLineEdit::returnPressed, this, [this]() {
        if (m_searchPopupView->isVisible()
            && m_searchPopupView->currentIndex().isValid()) {
            activateSearchPopupIndex(m_searchPopupView->currentIndex());
            return;
        }

        const QString strText = m_searchEdit->text().trimmed();
        if (strText.isEmpty()) {
            finishSearch();
            return;
        }

        if (!triggerSearchAction(strText)) {
            emit searchAccepted(strText);
        }
        finishSearch();
    });
    connect(m_searchCompleter,
            QOverload<const QString &>::of(&QCompleter::activated),
            this, [this](const QString &strText) {
                m_searchEdit->setText(strText);
                emit searchSuggestionActivated(strText);
                if (!triggerSearchAction(strText)) {
                    emit searchAccepted(strText);
                }
                finishSearch();
            });

    updateStyleSheet();
    updateRibbonTabGeometry();
    updateWindowControlGeometry();
    updateSearchGeometry();
    updateQuickAccessGeometry();
}

///
/// \brief RibbonBar::~RibbonBar
/// Hides transient search UI before Qt destroys the owned child widgets.
///
RibbonBar::~RibbonBar()
{
    for (const SearchCommand &command : m_searchCommandList) {
        if (!command.action.isNull()) {
            disconnect(command.action.data(), nullptr, this, nullptr);
        }
    }

    m_searchCommandList.clear();
    m_recentSearchActionList.clear();
    m_searchActionIndex.clear();
}

///
/// \brief RibbonBar::addPage
/// Creates a Ribbon page and connects its title to the matching tab text.
/// \param strTitle Text displayed by the new tab.
/// \return Newly created page owned by the Ribbon bar.
///
RibbonPage *RibbonBar::addPage(const QString &strTitle)
{
    RibbonPage *newPage = new RibbonPage(strTitle, this);
    const int index = addTab(newPage, strTitle);
    connect(newPage, &RibbonPage::titleChanged, this, [this, newPage](const QString &strNewTitle) {
        const int pageIndex = indexOf(newPage);
        if (pageIndex >= 0) {
            setTabText(pageIndex, strNewTitle);
        }
    });
    setCurrentIndex(index);
    updateRibbonTabGeometry();
    return newPage;
}

///
/// \brief RibbonBar::page
/// Returns the page at the requested index.
/// \param index Zero-based page index.
/// \return Page pointer or nullptr when the index is invalid.
///
RibbonPage *RibbonBar::page(int index) const
{
    return qobject_cast<RibbonPage *>(widget(index));
}

///
/// \brief RibbonBar::currentPage
/// Returns the currently selected Ribbon page.
/// \return Current page pointer or nullptr when no page exists.
///
RibbonPage *RibbonBar::currentPage() const
{
    return page(currentIndex());
}

///
/// \brief RibbonBar::searchLineEdit
/// Returns the title-bar search edit widget.
/// \return Search line edit owned by the Ribbon bar.
///
QLineEdit *RibbonBar::searchLineEdit() const
{
    return m_searchEdit;
}

///
/// \brief RibbonBar::searchCompleter
/// Returns the completer attached to the search edit.
/// \return Search completer owned by the Ribbon bar.
///
QCompleter *RibbonBar::searchCompleter() const
{
    return m_searchCompleter;
}

///
/// \brief RibbonBar::setSearchVisible
/// Shows or hides the title-bar search edit.
/// \param visible true to show search, false to hide it.
///
void RibbonBar::setSearchVisible(bool visible)
{
    m_searchVisibleExplicitlySet = true;
    m_searchEdit->setVisible(visible);
    if (!visible) {
        hideSearchPopup();
    }

    updateSearchGeometry();
    updateQuickAccessGeometry();
}

///
/// \brief RibbonBar::isSearchVisible
/// Checks whether the search edit is visible.
/// \return true when search is visible.
///
bool RibbonBar::isSearchVisible() const
{
    return m_searchEdit->isVisible();
}

///
/// \brief RibbonBar::setSearchPlaceholderText
/// Sets the placeholder text shown in the search edit.
/// \param strText Placeholder text.
///
void RibbonBar::setSearchPlaceholderText(const QString &strText)
{
    m_searchPlaceholderExplicitlySet = true;
    m_searchEdit->setPlaceholderText(strText);
}

///
/// \brief RibbonBar::searchText
/// Returns the current search edit text.
/// \return Current search text.
///
QString RibbonBar::searchText() const
{
    return m_searchEdit->text();
}

///
/// \brief RibbonBar::setSearchText
/// Replaces the current search edit text.
/// \param strText New search text.
///
void RibbonBar::setSearchText(const QString &strText)
{
    m_searchEdit->setText(strText);
    updateSearchPopup();
}

///
/// \brief RibbonBar::setSearchSuggestions
/// Replaces the plain text suggestion list used by search completion.
/// \param strList Suggestion strings.
///
void RibbonBar::setSearchSuggestions(const QStringList &strList)
{
    m_searchSuggestionList = strList;
    updateSearchSuggestions();
    updateSearchPopup();
}

///
/// \brief RibbonBar::searchSuggestions
/// Returns the configured plain text suggestions.
/// \return Suggestion strings.
///
QStringList RibbonBar::searchSuggestions() const
{
    return m_searchSuggestionModel->stringList();
}

///
/// \brief RibbonBar::clearSearchSuggestions
/// Clears all plain text search suggestions.
///
void RibbonBar::clearSearchSuggestions()
{
    m_searchSuggestionList.clear();
    updateSearchSuggestions();
    updateSearchPopup();
}

///
/// \brief RibbonBar::registerSearchAction
/// Adds an action to the searchable command index.
/// \param action Action that can be found and triggered by search.
/// \param strKeywords Extra keywords matched in addition to action text.
///
void RibbonBar::registerSearchAction(QAction *action, const QStringList &strKeywords)
{
    if (!action) {
        return;
    }

    unregisterSearchAction(action);

    SearchCommand command;
    command.action = action;
    command.strText = searchActionText(action);
    command.strKeywords = strKeywords;
    m_searchCommandList.append(command);

    connect(action, &QObject::destroyed,
            this, &RibbonBar::removeInvalidSearchActions,
            Qt::UniqueConnection);
    connect(action, &QAction::changed,
            this, &RibbonBar::updateChangedSearchAction,
            Qt::UniqueConnection);

    rebuildSearchActionIndex();
    updateSearchSuggestions();
    updateSearchPopup();
}

///
/// \brief RibbonBar::unregisterSearchAction
/// Removes an action from the searchable command index.
/// \param action Action to remove.
///
void RibbonBar::unregisterSearchAction(QAction *action)
{
    bool removed = false;
    for (int index = m_searchCommandList.count() - 1; index >= 0; --index) {
        if (m_searchCommandList.at(index).action.data() == action) {
            m_searchCommandList.removeAt(index);
            removed = true;
        }
    }

    bool recentRemoved = false;
    for (int index = m_recentSearchActionList.count() - 1; index >= 0; --index) {
        if (m_recentSearchActionList.at(index).data() == action) {
            m_recentSearchActionList.removeAt(index);
            recentRemoved = true;
        }
    }

    if (recentRemoved) {
        emit recentSearchActionsChanged();
    }

    if (!removed && !recentRemoved) {
        return;
    }

    rebuildSearchActionIndex();
    updateSearchSuggestions();
    updateSearchPopup();
}

///
/// \brief RibbonBar::searchActions
/// Returns all valid actions registered for search.
/// \return Searchable action list.
///
QList<QAction *> RibbonBar::searchActions() const
{
    QList<QAction *> actionList;
    for (const SearchCommand &command : m_searchCommandList) {
        if (!command.action.isNull()) {
            actionList.append(command.action.data());
        }
    }

    return actionList;
}

///
/// \brief RibbonBar::searchAction
/// Finds the best matching registered action.
/// \param strText Search text to normalize and match.
/// \return Matching action or nullptr when no action matches.
///
QAction *RibbonBar::searchAction(const QString &strText) const
{
    return m_searchActionIndex.value(normalizedSearchText(strText)).data();
}

///
/// \brief RibbonBar::triggerSearchAction
/// Finds and triggers the action that matches the search text.
/// \param strText Search text accepted by the user.
/// \return true when an action was found and triggered.
///
bool RibbonBar::triggerSearchAction(const QString &strText)
{
    if (!m_searchActionTriggerEnabled) {
        return false;
    }

    QAction *action = searchAction(strText);
    if (!action || !action->isEnabled()) {
        return false;
    }

    QPointer<QAction> actionPointer = action;
    recordRecentSearchAction(action);
    action->trigger();
    if (!actionPointer.isNull()) {
        emit searchActionTriggered(actionPointer.data());
    }
    return true;
}

///
/// \brief RibbonBar::setSearchActionTriggerEnabled
/// Enables or disables automatic action triggering from accepted search text.
/// \param enabled true to allow search to trigger actions.
///
void RibbonBar::setSearchActionTriggerEnabled(bool enabled)
{
    m_searchActionTriggerEnabled = enabled;
}

///
/// \brief RibbonBar::isSearchActionTriggerEnabled
/// Returns whether accepted search text can trigger actions.
/// \return true when triggering is enabled.
///
bool RibbonBar::isSearchActionTriggerEnabled() const
{
    return m_searchActionTriggerEnabled;
}

///
/// \brief RibbonBar::recentSearchActions
/// Returns the valid recent actions triggered from search.
/// \return Recent action list in newest-first order.
///
QList<QAction *> RibbonBar::recentSearchActions() const
{
    QList<QAction *> actionList;
    for (const QPointer<QAction> &action : m_recentSearchActionList) {
        if (!action.isNull()) {
            actionList.append(action.data());
        }
    }

    return actionList;
}

///
/// \brief RibbonBar::clearRecentSearchActions
/// Clears the search action history and notifies listeners.
///
void RibbonBar::clearRecentSearchActions()
{
    if (m_recentSearchActionList.isEmpty()) {
        return;
    }

    m_recentSearchActionList.clear();
    updateSearchSuggestions();
    emit recentSearchActionsChanged();
    updateSearchPopup();
}

///
/// \brief RibbonBar::setRecentSearchLimit
/// Sets the maximum number of recent search actions to keep.
/// \param count Maximum history length.
///
void RibbonBar::setRecentSearchLimit(int count)
{
    m_recentSearchLimit = qMax(0, count);
    while (m_recentSearchActionList.count() > m_recentSearchLimit) {
        m_recentSearchActionList.removeLast();
    }

    updateSearchSuggestions();
    emit recentSearchActionsChanged();
    updateSearchPopup();
}

///
/// \brief RibbonBar::recentSearchLimit
/// Returns the maximum search history length.
/// \return Recent search action limit.
///
int RibbonBar::recentSearchLimit() const
{
    return m_recentSearchLimit;
}

///
/// \brief RibbonBar::quickAccessBar
/// Returns the quick access toolbar placed in the caption area.
/// \return Quick access toolbar owned by the Ribbon bar.
///
QToolBar *RibbonBar::quickAccessBar() const
{
    return m_quickAccessBar;
}

///
/// \brief RibbonBar::addQuickAccessAction
/// Creates and adds an action to the quick access toolbar.
/// \param icon Icon shown by the toolbar action.
/// \param strText Text and tooltip source for the action.
/// \return Newly created action owned by the quick access toolbar.
///
QAction *RibbonBar::addQuickAccessAction(const QIcon &icon, const QString &strText)
{
    QAction *action = new QAction(icon, strText, this);
    addQuickAccessAction(action);
    return action;
}

///
/// \brief RibbonBar::addQuickAccessAction
/// Adds an existing action to the quick access toolbar.
/// \param action Action to add.
///
void RibbonBar::addQuickAccessAction(QAction *action)
{
    if (!action) {
        return;
    }

    if (!m_quickAccessBar->actions().contains(action)) {
        m_quickAccessBar->addAction(action);
    }

    m_quickAccessBar->show();
    updateQuickAccessGeometry();
    updateStyleSheet();
}

///
/// \brief RibbonBar::clearQuickAccessActions
/// Removes all actions from the quick access toolbar.
///
void RibbonBar::clearQuickAccessActions()
{
    m_quickAccessBar->clear();
    m_quickAccessBar->hide();
    updateQuickAccessGeometry();
    updateStyleSheet();
}

///
/// \brief RibbonBar::setCurrentPageIndex
/// Selects the active Ribbon page by index.
/// \param index Zero-based tab index.
///
void RibbonBar::setCurrentPageIndex(int index)
{
    setCurrentIndex(index);
}

///
/// \brief RibbonBar::setRibbonMinimized
/// Collapses or expands the command pages while keeping title and tabs visible.
/// \param minimized true to collapse the command area.
///
void RibbonBar::setRibbonMinimized(bool minimized)
{
    if (m_ribbonMinimized == minimized) {
        return;
    }

    m_ribbonMinimized = minimized;
    updateRibbonMetrics();
    updateRibbonTabGeometry();
    updateWindowControlState();
    updateWindowControlGeometry();
    updateSearchGeometry();
    updateQuickAccessGeometry();
    updateGeometry();
    emit ribbonMinimizedChanged(m_ribbonMinimized);
}

///
/// \brief RibbonBar::isRibbonMinimized
/// Checks whether the command pages are currently collapsed.
/// \return true when the command area is collapsed.
///
bool RibbonBar::isRibbonMinimized() const
{
    return m_ribbonMinimized;
}

///
/// \brief RibbonBar::setFrameThemeEnabled
/// Enables or disables Qtitan-style frame painting and controls.
/// \param enabled true to paint the Ribbon caption and buttons.
///
void RibbonBar::setFrameThemeEnabled(bool enabled)
{
    RibbonMainWindow *mainWindow = qobject_cast<RibbonMainWindow *>(window());
    if (mainWindow) {
        mainWindow->setNativeFrameEnabled(enabled);
    }

    if (m_frameThemeEnabled == enabled) {
        return;
    }

    m_frameThemeEnabled = enabled;
    if (enabled && !m_searchVisibleExplicitlySet) {
        m_searchEdit->show();
    }

    updateWindowControlVisibility();
    updateRibbonTabGeometry();
    updateWindowControlGeometry();
    updateSearchGeometry();
    updateQuickAccessGeometry();
    updateStyleSheet();
}

///
/// \brief RibbonBar::isFrameThemeEnabled
/// Returns whether themed frame painting is active.
/// \return true when themed frame painting is enabled.
///
bool RibbonBar::isFrameThemeEnabled() const
{
    return m_frameThemeEnabled;
}

///
/// \brief RibbonBar::event
/// Updates Ribbon metrics when font, style, or palette information changes.
/// \param event Qt event delivered to the Ribbon bar.
/// \return true when the event is handled.
///
bool RibbonBar::event(QEvent *event)
{
    const bool handled = QTabWidget::event(event);

    switch (event->type()) {
    case QEvent::FontChange:
    case QEvent::StyleChange:
        updateRibbonMetrics();
        updateRibbonTabGeometry();
        updateWindowControlGeometry();
        updateSearchGeometry();
        updateQuickAccessGeometry();
        break;
    case QEvent::LanguageChange:
    case QEvent::LocaleChange:
        updateLocalizedText();
        updateRibbonMetrics();
        updateRibbonTabGeometry();
        updateWindowControlGeometry();
        updateSearchGeometry();
        updateQuickAccessGeometry();
        break;
    case QEvent::LayoutRequest:
    case QEvent::PolishRequest:
    case QEvent::Show:
        updateRibbonTabGeometry();
        updateWindowControlGeometry();
        updateSearchGeometry();
        updateQuickAccessGeometry();
        break;
    default:
        break;
    }

    return handled;
}

///
/// \brief RibbonBar::eventFilter
/// Handles search keyboard navigation, action tracking, and popup events.
/// \param object Object that generated the filtered event.
/// \param event Event to filter.
/// \return true when the event is consumed.
///
bool RibbonBar::eventFilter(QObject *object, QEvent *event)
{
    if (object == m_searchEdit && event->type() == QEvent::KeyPress) {
        QKeyEvent *keyEvent = static_cast<QKeyEvent *>(event);
        if (keyEvent->key() == Qt::Key_Down) {
            updateSearchPopup();
            if (m_searchPopupView->isVisible()) {
                m_searchPopupView->setFocus();
                m_searchPopupView->setCurrentIndex(
                    m_searchPopupModel->index(1, 0));
                return true;
            }
        } else if (keyEvent->key() == Qt::Key_Escape) {
            finishSearch();
            return true;
        }
    }

    if (object == m_searchPopupView && event->type() == QEvent::KeyPress) {
        QKeyEvent *keyEvent = static_cast<QKeyEvent *>(event);
        if (keyEvent->key() == Qt::Key_Return
            || keyEvent->key() == Qt::Key_Enter) {
            activateSearchPopupIndex(m_searchPopupView->currentIndex());
            return true;
        }

        if (keyEvent->key() == Qt::Key_Escape) {
            finishSearch();
            return true;
        }
    }

    return QTabWidget::eventFilter(object, event);
}

///
/// \brief RibbonBar::paintEvent
/// Paints the tab widget and Qtitan-style caption area when enabled.
/// \param event Paint event supplied by Qt.
///
void RibbonBar::paintEvent(QPaintEvent *event)
{
    if (m_frameThemeEnabled) {
        updateWindowControlState();
        updateWindowControlGeometry();
    }

    updateRibbonTabGeometry();
    QTabWidget::paintEvent(event);

    if (!m_frameThemeEnabled) {
        return;
    }

    QPainter painter(this);
    const int titleHeight = ribbonCaptionHeight + ribbonTabHeight;
    painter.fillRect(0,
                     0,
                     width(),
                     titleHeight,
                     QColor(QStringLiteral("#2b579a")));

    QWidget *topLevelWidget = window();
    if (!topLevelWidget) {
        return;
    }

    const QIcon windowIcon = topLevelWidget->windowIcon();
    const int iconSize = 16;
    const int iconTop = ribbonCaptionTopMargin
        + ((ribbonWindowButtonHeight - iconSize) / 2);
    if (!windowIcon.isNull()) {
        windowIcon.paint(&painter, QRect(7, iconTop, iconSize, iconSize));
    }

    painter.setPen(Qt::white);
    painter.drawText(QRect(34,
                            ribbonCaptionTopMargin,
                            320,
                            ribbonWindowButtonHeight),
                     Qt::AlignLeft | Qt::AlignVCenter,
                     topLevelWidget->windowTitle());

}

///
/// \brief RibbonBar::resizeEvent
/// Repositions tabs, search, quick access actions, and window controls.
/// \param event Resize event supplied by Qt.
///
void RibbonBar::resizeEvent(QResizeEvent *event)
{
    QTabWidget::resizeEvent(event);
    updateWindowControlState();
    updateRibbonMetrics();
    updateRibbonTabGeometry();
    updateWindowControlGeometry();
    updateSearchGeometry();
    updateQuickAccessGeometry();
    updateStyleSheet();
}

///
/// \brief RibbonBar::isWindowControlPoint
/// Checks whether a point hits the themed minimize, maximize, or close area.
/// \param point Point in RibbonBar coordinates.
/// \return true when the point is inside the window-control rectangle.
///
bool RibbonBar::isWindowControlPoint(const QPoint &point) const
{
    if (!m_frameThemeEnabled) {
        return false;
    }

    const QWidget *controlParent = window();
    if (!controlParent) {
        controlParent = this;
    }

    const int ribbonRight = mapTo(
        controlParent, QPoint(width(), 0)).x();
    const int controlRight = qMin(visibleWidgetRight(controlParent),
                                  ribbonRight);
    const int controlLeft = controlRight - windowControlWidth();
    const QPoint topLeft = mapFrom(
        controlParent, QPoint(controlLeft, ribbonCaptionTopMargin));
    const QRect buttonRect(topLeft.x(),
                           topLeft.y(),
                           windowControlWidth(),
                           ribbonWindowButtonHeight);
    return buttonRect.contains(point);
}

///
/// \brief RibbonBar::updateRibbonTabGeometry
/// Places the tab bar below the caption area and sizes the page stack.
///
void RibbonBar::updateRibbonTabGeometry()
{
    QTabBar *ribbonTabBar = tabBar();
    if (!ribbonTabBar) {
        return;
    }

    const int titleHeight = m_frameThemeEnabled
        ? ribbonCaptionHeight
        : 0;
    const int tabHeight = m_frameThemeEnabled
        ? ribbonTabHeight
        : ribbonTabBar->sizeHint().height();
    const int stackTop = titleHeight + tabHeight;
    const int availableTabWidth = m_frameThemeEnabled
        ? qMax(0, width() - ribbonCollapseButtonWidth)
        : width();
    const int tabWidth = qMin(availableTabWidth,
                              ribbonTabBar->sizeHint().width());
    ribbonTabBar->setGeometry(0, titleHeight, tabWidth, tabHeight);
    ribbonTabBar->raise();

    QStackedWidget *stackedWidget = findChild<QStackedWidget *>();
    if (!stackedWidget) {
        return;
    }

    const int stackHeight = m_ribbonMinimized
        ? 0
        : qMax(0, height() - stackTop);
    stackedWidget->setGeometry(0, stackTop, width(), stackHeight);
    stackedWidget->setVisible(!m_ribbonMinimized);
}

///
/// \brief RibbonBar::updateSearchGeometry
/// Centers the title-bar search box while avoiding the frame buttons.
///
void RibbonBar::updateSearchGeometry()
{
    const int preferredSearchWidth = 416;
    const int searchHeight = 22;
    const int topMargin = ribbonCaptionTopMargin
        + ((ribbonWindowButtonHeight - searchHeight) / 2);
    const int controlWidth = windowControlWidth();
    const int availableWidth = qMax(0, width() - controlWidth - 48);
    const int searchWidth = qMin(preferredSearchWidth,
                                 qMax(160, availableWidth));
    const int controlLeft = width() - controlWidth;
    int x = controlWidth > 0
        ? (controlLeft - searchWidth) / 2
        : (width() - searchWidth) / 2;

    if (controlWidth > 0) {
        x = qMin(x, controlLeft - searchWidth - 10);
    }

    x = qMax(220, x);

    m_searchEdit->setGeometry(x, topMargin, searchWidth, searchHeight);
    m_searchEdit->raise();
    if (m_searchPopupView->isVisible()) {
        updateSearchPopup();
    }
}

///
/// \brief RibbonBar::updateQuickAccessGeometry
/// Places quick access commands between the title and search box.
///
void RibbonBar::updateQuickAccessGeometry()
{
    const int leftMargin = 340;
    const int rightMargin = 12;
    const int searchGap = 8;
    const int controlWidth = windowControlWidth();
    const int barHeight = 24;
    const int topMargin = ribbonCaptionTopMargin
        + ((ribbonWindowButtonHeight - barHeight) / 2);
    const int rightLimit = m_searchEdit->isVisible()
        ? m_searchEdit->x() - searchGap
        : width() - controlWidth - rightMargin;
    const int maxWidth = qMax(0, rightLimit - leftMargin);
    const int barWidth = qMin(m_quickAccessBar->sizeHint().width(), maxWidth);

    m_quickAccessBar->setGeometry(leftMargin, topMargin, barWidth, barHeight);
    m_quickAccessBar->raise();
}

///
/// \brief RibbonBar::updateRibbonMetrics
/// Applies the calculated fixed Ribbon height.
///
void RibbonBar::updateRibbonMetrics()
{
    const int barHeight = m_ribbonMinimized
        ? (m_frameThemeEnabled
               ? ribbonCaptionHeight + ribbonTabHeight
               : tabBar()->sizeHint().height())
        : ribbonBarHeight(this);
    if (height() != barHeight || minimumHeight() != barHeight) {
        setFixedHeight(barHeight);
    }
}

///
/// \brief RibbonBar::setupWindowControlButton
/// Initializes a frame-control button before it is reparented to the window.
/// \param button Button to initialize.
///
void RibbonBar::setupWindowControlButton(QToolButton *button)
{
    if (!button) {
        return;
    }

    button->hide();
    button->raise();
}

///
/// \brief RibbonBar::updateWindowControlGeometry
/// Positions the themed window-control widgets over the caption area.
///
void RibbonBar::updateWindowControlGeometry()
{
    const int buttonWidth = ribbonWindowButtonWidth;
    const int buttonHeight = ribbonWindowButtonHeight;
    QWidget *controlParent = window();
    if (!controlParent) {
        controlParent = this;
    }

    if (m_minimizeButton->parentWidget() != controlParent) {
        m_minimizeButton->setParent(controlParent);
        m_maximizeButton->setParent(controlParent);
        m_closeButton->setParent(controlParent);
    }
    if (m_collapseButton->parentWidget() != controlParent) {
        m_collapseButton->setParent(controlParent);
    }

    const QPoint topLeft = mapTo(controlParent, QPoint(0, 0));
    const int ribbonRight = mapTo(controlParent, QPoint(width(), 0)).x();
    const int controlRight = qMin(visibleWidgetRight(controlParent),
                                  ribbonRight);
    int x = controlRight - (buttonWidth * 3);
    const int top = topLeft.y() + ribbonCaptionTopMargin;

    m_minimizeButton->setGeometry(x, top, buttonWidth, buttonHeight);
    x += buttonWidth;
    m_maximizeButton->setGeometry(x, top, buttonWidth, buttonHeight);
    x += buttonWidth;
    m_closeButton->setGeometry(x, top, buttonWidth, buttonHeight);
    const int collapseTop = topLeft.y() + ribbonCaptionHeight
        + ((ribbonTabHeight - ribbonCollapseButtonHeight) / 2);
    m_collapseButton->setGeometry(controlRight - ribbonCollapseButtonWidth,
                                  collapseTop,
                                  ribbonCollapseButtonWidth,
                                  ribbonCollapseButtonHeight);

    m_minimizeButton->setVisible(m_frameThemeEnabled);
    m_maximizeButton->setVisible(m_frameThemeEnabled);
    m_closeButton->setVisible(m_frameThemeEnabled);
    m_collapseButton->setVisible(m_frameThemeEnabled);
    m_minimizeButton->raise();
    m_maximizeButton->raise();
    m_closeButton->raise();
    m_collapseButton->raise();
}

///
/// \brief RibbonBar::updateWindowControlState
/// Synchronizes maximize button glyph and enabled state with the top window.
///
void RibbonBar::updateWindowControlState()
{
    QWidget *topLevelWidget = window();
    const bool isMaximized = topLevelWidget && topLevelWidget->isMaximized();
    RibbonWindowButton *button =
        static_cast<RibbonWindowButton *>(m_maximizeButton);
    button->setRestoreMode(isMaximized);
    m_maximizeButton->setToolTip(isMaximized
        ? ribbonText("Restore")
        : ribbonText("Maximize"));
    RibbonCollapseButton *collapseButton =
        static_cast<RibbonCollapseButton *>(m_collapseButton);
    collapseButton->setCollapsed(m_ribbonMinimized);
    m_collapseButton->setToolTip(m_ribbonMinimized
        ? ribbonText("Expand the Ribbon")
        : ribbonText("Collapse the Ribbon"));

    const bool canMaximize = topLevelWidget
        && topLevelWidget->minimumWidth() < topLevelWidget->maximumWidth()
        && topLevelWidget->minimumHeight() < topLevelWidget->maximumHeight();
    m_maximizeButton->setEnabled(canMaximize);
}

///
/// \brief RibbonBar::updateWindowControlVisibility
/// Shows or hides themed frame buttons according to frame-theme state.
///
void RibbonBar::updateWindowControlVisibility()
{
    m_minimizeButton->setVisible(m_frameThemeEnabled);
    m_maximizeButton->setVisible(m_frameThemeEnabled);
    m_closeButton->setVisible(m_frameThemeEnabled);
    m_collapseButton->setVisible(m_frameThemeEnabled);
    updateWindowControlState();
}
///
/// rief RibbonBar::updateLocalizedText
/// Refreshes built-in LqRibbon text after locale or translator changes.
///
void RibbonBar::updateLocalizedText()
{
    if (!m_searchPlaceholderExplicitlySet) {
        m_searchEdit->setPlaceholderText(ribbonText("Search"));
    }

    if (m_searchLineAction) {
        m_searchLineAction->setToolTip(ribbonText("Search"));
    }

    m_minimizeButton->setToolTip(ribbonText("Minimize"));
    m_closeButton->setToolTip(ribbonText("Close"));
    updateWindowControlState();
    updateSearchPopup();
}

///
/// \brief RibbonBar::windowControlWidth
/// Returns the total width reserved for themed frame buttons.
/// \return Combined minimize, maximize, and close button width.
///
int RibbonBar::windowControlWidth() const
{
    if (!m_frameThemeEnabled) {
        return 0;
    }

    return ribbonWindowButtonWidth * 3;
}

///
/// \brief RibbonBar::updateSearchPopup
/// Rebuilds and positions the search suggestion popup.
///
void RibbonBar::updateSearchPopup()
{
    if (!m_searchEdit->isVisible()) {
        hideSearchPopup();
        return;
    }

    const QString strText = m_searchEdit->text().trimmed();
    const QList<QAction *> actionList = matchedSearchActions(strText);
    m_searchPopupModel->clear();

    if (!actionList.isEmpty()) {
        m_searchPopupModel->appendRow(createSearchHeaderItem(ribbonText("Actions")));
        for (QAction *action : actionList) {
            m_searchPopupModel->appendRow(createSearchActionItem(action));
        }
    }

    if (!strText.isEmpty()) {
        m_searchPopupModel->appendRow(createSearchHeaderItem(ribbonText("Help")));
        const QString strHelpText =
            ribbonText("Get Help with \"%1\"").arg(strText);
        const QIcon helpIcon = style()->standardIcon(QStyle::SP_MessageBoxQuestion);
        m_searchPopupModel->appendRow(createSearchHelpItem(strHelpText, helpIcon));
    }

    if (m_searchPopupModel->rowCount() == 0) {
        hideSearchPopup();
        return;
    }

    int popupHeight = 2;
    for (int row = 0; row < m_searchPopupModel->rowCount(); ++row) {
        popupHeight += qMax(ribbonSearchPopupRowHeight,
                            m_searchPopupView->sizeHintForRow(row));
    }

    const bool needsScrollBar = popupHeight > ribbonSearchPopupMaxHeight;
    popupHeight = qMin(ribbonSearchPopupMaxHeight, popupHeight);
    m_searchPopupView->setVerticalScrollBarPolicy(needsScrollBar
                                                  ? Qt::ScrollBarAsNeeded
                                                  : Qt::ScrollBarAlwaysOff);
    const QRect searchRect = m_searchEdit->geometry();
    m_searchPopupView->setGeometry(searchRect.left(),
                                   searchRect.bottom(),
                                   searchRect.width(),
                                   popupHeight);
    m_searchPopupView->show();
    m_searchPopupView->raise();

    for (int row = 0; row < m_searchPopupModel->rowCount(); ++row) {
        const QModelIndex index = m_searchPopupModel->index(row, 0);
        if (index.data(ribbonSearchPopupKindRole).toInt()
            == SearchPopupActionItem) {
            m_searchPopupView->setCurrentIndex(index);
            break;
        }
    }
}

///
/// \brief RibbonBar::hideSearchPopup
/// Hides the transient search popup.
///
void RibbonBar::hideSearchPopup()
{
    m_searchPopupView->hide();
}

///
/// \brief RibbonBar::finishSearch
/// Closes the search UI and clears accepted text after a completed search.
///
void RibbonBar::finishSearch()
{
    hideSearchPopup();
    if (!m_searchEdit->text().isEmpty()) {
        m_searchEdit->clear();
    }
    m_searchEdit->setFocus();
}

///
/// \brief RibbonBar::activateSearchPopupIndex
/// Activates the command or helper row selected in the search popup.
/// \param index Popup model index to activate.
///
void RibbonBar::activateSearchPopupIndex(const QModelIndex &index)
{
    if (!index.isValid()) {
        return;
    }

    const int itemKind = index.data(ribbonSearchPopupKindRole).toInt();
    if (itemKind == SearchPopupActionItem) {
        const qlonglong actionValue =
            index.data(ribbonSearchPopupActionRole).toLongLong();
        QAction *action =
            reinterpret_cast<QAction *>(static_cast<quintptr>(actionValue));
        if (!action || !action->isEnabled()) {
            return;
        }

        QPointer<QAction> actionPointer = action;
        recordRecentSearchAction(action);
        finishSearch();
        action->trigger();
        if (!actionPointer.isNull()) {
            emit searchActionTriggered(actionPointer.data());
        }
        return;
    }

    if (itemKind == SearchPopupHelpItem) {
        const QString strText = m_searchEdit->text().trimmed();
        emit searchAccepted(strText);
        finishSearch();
    }
}

///
/// \brief RibbonBar::matchedSearchActions
/// Finds all registered actions whose text or keywords match the search text.
/// \param strText Search text entered by the user.
/// \return Matching actions sorted by registration order.
///
QList<QAction *> RibbonBar::matchedSearchActions(const QString &strText) const
{
    QList<QAction *> actionList;
    const QString strNormalizedText = normalizedSearchText(strText);
    if (strNormalizedText.isEmpty()) {
        for (const QPointer<QAction> &action : m_recentSearchActionList) {
            if (!action.isNull() && !actionList.contains(action.data())) {
                actionList.append(action.data());
            }
        }
        return actionList;
    }

    for (const SearchCommand &command : m_searchCommandList) {
        if (command.action.isNull()) {
            continue;
        }

        QStringList strKeyList = command.strKeywords;
        strKeyList.prepend(command.strText);
        for (const QString &strKey : strKeyList) {
            if (normalizedSearchText(strKey).contains(strNormalizedText)) {
                actionList.append(command.action.data());
                break;
            }
        }
    }

    const QList<QToolButton *> buttonList = findChildren<QToolButton *>();
    for (QToolButton *button : buttonList) {
        if (button == m_minimizeButton
            || button == m_maximizeButton
            || button == m_closeButton
            || button == m_collapseButton) {
            continue;
        }

        QAction *action = button->defaultAction();
        if (!action || actionList.contains(action)) {
            continue;
        }

        const QString strActionText = searchActionText(action);
        const QString strToolTip = action->toolTip();
        const QString strObjectName = action->objectName();
        if (normalizedSearchText(strActionText).contains(strNormalizedText)
            || normalizedSearchText(strToolTip).contains(strNormalizedText)
            || normalizedSearchText(strObjectName).contains(strNormalizedText)) {
            actionList.append(action);
        }
    }

    while (actionList.count() > 40) {
        actionList.removeLast();
    }

    return actionList;
}

///
/// \brief RibbonBar::updateSearchSuggestions
/// Rebuilds the completer string list from suggestions and actions.
///
void RibbonBar::updateSearchSuggestions()
{
    QStringList strList;
    for (const QPointer<QAction> &action : m_recentSearchActionList) {
        if (action.isNull()) {
            continue;
        }

        const QString strText = searchActionText(action.data());
        if (!strText.isEmpty() && !strList.contains(strText)) {
            strList.append(strText);
        }
    }

    for (const QString &strText : m_searchSuggestionList) {
        if (!strText.isEmpty() && !strList.contains(strText)) {
            strList.append(strText);
        }
    }

    for (const SearchCommand &command : m_searchCommandList) {
        if (command.action.isNull() || command.strText.isEmpty()) {
            continue;
        }

        if (!strList.contains(command.strText)) {
            strList.append(command.strText);
        }
    }

    m_searchSuggestionModel->setStringList(strList);
}

///
/// \brief RibbonBar::recordRecentSearchAction
/// Adds an action to the recent-search list and enforces the history limit.
/// \param action Action that was triggered from search.
///
void RibbonBar::recordRecentSearchAction(QAction *action)
{
    if (!action || m_recentSearchLimit <= 0) {
        return;
    }

    for (int index = m_recentSearchActionList.count() - 1; index >= 0; --index) {
        if (m_recentSearchActionList.at(index).data() == action) {
            m_recentSearchActionList.removeAt(index);
        }
    }

    m_recentSearchActionList.prepend(action);
    while (m_recentSearchActionList.count() > m_recentSearchLimit) {
        m_recentSearchActionList.removeLast();
    }

    updateSearchSuggestions();
    emit recentSearchActionsChanged();
}

///
/// \brief RibbonBar::removeInvalidSearchActions
/// Removes deleted actions from search registration and history containers.
///
void RibbonBar::removeInvalidSearchActions()
{
    bool recentRemoved = false;
    for (int index = m_recentSearchActionList.count() - 1; index >= 0; --index) {
        if (m_recentSearchActionList.at(index).isNull()) {
            m_recentSearchActionList.removeAt(index);
            recentRemoved = true;
        }
    }

    for (int index = m_searchCommandList.count() - 1; index >= 0; --index) {
        if (m_searchCommandList.at(index).action.isNull()) {
            m_searchCommandList.removeAt(index);
        }
    }

    if (recentRemoved) {
        emit recentSearchActionsChanged();
    }

    rebuildSearchActionIndex();
    updateSearchSuggestions();
}

///
/// \brief RibbonBar::updateChangedSearchAction
/// Refreshes search indexes when a registered action changes text or icon.
///
void RibbonBar::updateChangedSearchAction()
{
    QAction *action = qobject_cast<QAction *>(sender());
    if (!action) {
        return;
    }

    for (SearchCommand &command : m_searchCommandList) {
        if (command.action.data() == action) {
            command.strText = searchActionText(action);
        }
    }

    rebuildSearchActionIndex();
    updateSearchSuggestions();
    updateSearchPopup();
}

///
/// \brief RibbonBar::rebuildSearchActionIndex
/// Rebuilds normalized text and keyword lookup entries for search actions.
///
void RibbonBar::rebuildSearchActionIndex()
{
    m_searchActionIndex.clear();
    for (const SearchCommand &command : m_searchCommandList) {
        if (command.action.isNull()) {
            continue;
        }

        QStringList strKeyList = command.strKeywords;
        strKeyList.prepend(command.strText);
        for (const QString &strKey : strKeyList) {
            const QString strNormalizedKey = normalizedSearchText(strKey);
            if (strNormalizedKey.isEmpty()
                || m_searchActionIndex.contains(strNormalizedKey)) {
                continue;
            }

            m_searchActionIndex.insert(strNormalizedKey, command.action);
        }
    }
}

///
/// \brief RibbonBar::normalizedSearchText
/// Normalizes search text for case-insensitive matching.
/// \param strText Text to normalize.
/// \return Trimmed lower-case search key.
///
QString RibbonBar::normalizedSearchText(const QString &strText) const
{
    QString strNormalizedText = strText.trimmed().toCaseFolded();
    strNormalizedText.remove(QLatin1Char('&'));
    return strNormalizedText;
}

///
/// \brief RibbonBar::searchActionText
/// Returns clean display text for a searchable action.
/// \param action Action whose text should be cleaned.
/// \return Text without mnemonic markers.
///
QString RibbonBar::searchActionText(QAction *action) const
{
    QString strText = action->text();
    strText.remove(QLatin1Char('&'));
    return strText.trimmed();
}

///
/// \brief RibbonBar::updateStyleSheet
/// Applies the Ribbon stylesheet that matches the current frame mode.
///
void RibbonBar::updateStyleSheet()
{
    setStyleSheet(QString::fromLatin1(ribbonStyleSheet));
}

///
/// \brief RibbonMainWindow::RibbonMainWindow
/// Creates a main window with a top Ribbon bar and central content area.
/// \param parent Parent widget.
///
RibbonMainWindow::RibbonMainWindow(QWidget *parent)
    : QMainWindow(parent)
    , m_rootWidget(new QWidget(this))
    , m_rootLayout(new QVBoxLayout(m_rootWidget))
    , m_ribbonBar(new RibbonBar(m_rootWidget))
    , m_nativeFrameEnabled(false)
    , m_nativeCaptionHeight(ribbonCaptionHeight)
    , m_nativeResizeBorderWidth(0)
{
    setMouseTracking(true);
    m_rootLayout->setContentsMargins(0, 0, 0, 0);
    m_rootLayout->setSpacing(0);
    m_rootLayout->addWidget(m_ribbonBar);
    QMainWindow::setCentralWidget(m_rootWidget);
    m_rootWidget->setMouseTracking(true);
    m_ribbonBar->setMouseTracking(true);

    if (QApplication::instance()) {
        QApplication::instance()->installEventFilter(this);
    }
}

///
/// \brief RibbonMainWindow::~RibbonMainWindow
/// Removes the event filter before Qt destroys child widgets.
///
RibbonMainWindow::~RibbonMainWindow()
{
    if (QApplication::instance()) {
        QApplication::instance()->removeEventFilter(this);
    }
}

///
/// \brief RibbonMainWindow::ribbonBar
/// Returns the embedded Ribbon bar.
/// \return Ribbon bar owned by this main window.
///
RibbonBar *RibbonMainWindow::ribbonBar() const
{
    return m_ribbonBar;
}

///
/// \brief RibbonMainWindow::setCentralWidget
/// Places a widget under the Ribbon bar and installs frame event filtering.
/// \param widget Widget to use as the main content area.
///
void RibbonMainWindow::setCentralWidget(QWidget *widget)
{
    if (!widget || widget == m_centralWidget) {
        return;
    }

    if (m_centralWidget) {
        m_rootLayout->removeWidget(m_centralWidget);
        m_centralWidget->deleteLater();
    }

    m_centralWidget = widget;
    widget->setParent(m_rootWidget);
    widget->setMouseTracking(true);
    m_rootLayout->addWidget(widget, 1);
    polishMdiObject(widget);
}

///
/// \brief RibbonMainWindow::setNativeFrameEnabled
/// Enables native move, resize, hit-test, and system-menu handling.
/// \param enabled true to let LqRibbon handle native frame gestures.
///
void RibbonMainWindow::setNativeFrameEnabled(bool enabled)
{
    if (m_nativeFrameEnabled == enabled) {
        return;
    }

    const bool wasVisible = isVisible();
    m_nativeFrameEnabled = enabled;

    Qt::WindowFlags flags = windowFlags();
    if (enabled) {
        flags |= Qt::FramelessWindowHint;
    } else {
        flags &= ~Qt::FramelessWindowHint;
    }

    setWindowFlags(flags);
    setAttribute(Qt::WA_NativeWindow, enabled);
    updateNativeWindowStyle();

    if (wasVisible) {
        show();
        updateNativeWindowStyle();
    }
}

///
/// \brief RibbonMainWindow::isNativeFrameEnabled
/// Returns whether native frame handling is active.
/// \return true when LqRibbon handles native frame gestures.
///
bool RibbonMainWindow::isNativeFrameEnabled() const
{
    return m_nativeFrameEnabled;
}

///
/// \brief RibbonMainWindow::setNativeCaptionHeight
/// Sets the height of the draggable caption region.
/// \param height Caption height in logical pixels.
///
void RibbonMainWindow::setNativeCaptionHeight(int height)
{
    m_nativeCaptionHeight = qMax(0, height);
}

///
/// \brief RibbonMainWindow::nativeCaptionHeight
/// Returns the draggable caption height.
/// \return Caption height in logical pixels.
///
int RibbonMainWindow::nativeCaptionHeight() const
{
    return m_nativeCaptionHeight;
}

///
/// \brief RibbonMainWindow::setNativeResizeBorderWidth
/// Sets the fallback resize hit-test border width.
/// \param width Border width in logical pixels.
///
void RibbonMainWindow::setNativeResizeBorderWidth(int width)
{
    m_nativeResizeBorderWidth = qMax(0, width);
}

///
/// \brief RibbonMainWindow::nativeResizeBorderWidth
/// Returns the fallback resize hit-test border width.
/// \return Border width in logical pixels.
///
int RibbonMainWindow::nativeResizeBorderWidth() const
{
    return m_nativeResizeBorderWidth;
}

///
/// \brief RibbonMainWindow::setFrameThemeEnabled
/// Enables Qtitan-style Ribbon frame painting on the embedded Ribbon bar.
/// \param enabled true to enable themed frame painting.
///
void RibbonMainWindow::setFrameThemeEnabled(bool enabled)
{
    m_ribbonBar->setFrameThemeEnabled(enabled);
    setNativeFrameEnabled(enabled);
}

///
/// \brief RibbonMainWindow::isFrameThemeEnabled
/// Returns whether themed frame painting is enabled.
/// \return true when frame painting is active.
///
bool RibbonMainWindow::isFrameThemeEnabled() const
{
    return m_ribbonBar->isFrameThemeEnabled();
}

///
/// \brief RibbonMainWindow::eventFilter
/// Routes native-frame and MDI polish events from child widgets.
/// \param object Object that generated the filtered event.
/// \param event Event to filter.
/// \return true when the event is consumed.
///
bool RibbonMainWindow::eventFilter(QObject *object, QEvent *event)
{
    if (handleNativeFrameEvent(object, event)) {
        return true;
    }

    if (event->type() == QEvent::ChildAdded) {
        QChildEvent *childEvent = static_cast<QChildEvent *>(event);
        polishMdiObject(childEvent->child());
        polishMdiObject(object);
    } else if (event->type() == QEvent::Show
               || event->type() == QEvent::Polish
               || event->type() == QEvent::LayoutRequest
               || event->type() == QEvent::Resize
               || event->type() == QEvent::WindowActivate
               || event->type() == QEvent::WindowDeactivate
               || event->type() == QEvent::WindowStateChange
               || event->type() == QEvent::WindowTitleChange
               || event->type() == QEvent::WindowIconChange) {
        polishMdiObject(object);
    }

    return false;
}

///
/// \brief RibbonMainWindow::polishMdiObject
/// Applies flat Ribbon-compatible styling to MDI-related objects.
/// \param object Object that may be a QMdiArea or QMdiSubWindow.
///
void RibbonMainWindow::polishMdiObject(QObject *object)
{
    if (!object) {
        return;
    }

    QMdiArea *mdiArea = qobject_cast<QMdiArea *>(object);
    if (mdiArea) {
        polishMdiArea(mdiArea);
        return;
    }

    QMdiSubWindow *subWindow = qobject_cast<QMdiSubWindow *>(object);
    if (subWindow) {
        polishMdiSubWindow(subWindow);
        return;
    }

    QWidget *widget = qobject_cast<QWidget *>(object);
    if (!widget) {
        return;
    }

    const QList<QMdiArea *> mdiAreaList = widget->findChildren<QMdiArea *>();
    for (QMdiArea *childMdiArea : mdiAreaList) {
        polishMdiArea(childMdiArea);
    }

    const QList<QMdiSubWindow *> subWindowList =
        widget->findChildren<QMdiSubWindow *>();
    for (QMdiSubWindow *childSubWindow : subWindowList) {
        polishMdiSubWindow(childSubWindow);
    }
}

///
/// \brief RibbonMainWindow::polishMdiArea
/// Applies Qtitan-like styling and event filtering to an MDI area.
/// \param mdiArea MDI area to polish.
///
void RibbonMainWindow::polishMdiArea(QMdiArea *mdiArea)
{
    if (!mdiArea) {
        return;
    }

    if (!mdiArea->property("lqRibbonMdiPolished").toBool()) {
        mdiArea->setProperty("lqRibbonMdiPolished", true);
        mdiArea->setStyleSheet(QString::fromLatin1(ribbonMdiAreaStyleSheet));
        mdiArea->setTabsClosable(true);
        mdiArea->setTabsMovable(true);
        mdiArea->setTabPosition(QTabWidget::North);
        mdiArea->installEventFilter(this);
    }

    updateMdiTabBars(mdiArea);

    const QList<QMdiSubWindow *> subWindowList = mdiArea->subWindowList();
    for (QMdiSubWindow *subWindow : subWindowList) {
        polishMdiSubWindow(subWindow);
    }
}

///
/// \brief RibbonMainWindow::polishMdiSubWindow
/// Replaces native-looking MDI chrome with a flat Ribbon title bar.
/// \param subWindow MDI subwindow to polish.
///
void RibbonMainWindow::polishMdiSubWindow(QMdiSubWindow *subWindow)
{
    if (!subWindow) {
        return;
    }

    if (!subWindow->property("lqRibbonMdiPolished").toBool()) {
        subWindow->setProperty("lqRibbonMdiPolished", true);
        subWindow->setOption(QMdiSubWindow::RubberBandMove, false);
        subWindow->setOption(QMdiSubWindow::RubberBandResize, false);
        subWindow->setAttribute(Qt::WA_StyledBackground, true);
        subWindow->installEventFilter(this);
    }

    QWidget *titleBarWidget = subWindow->findChild<QWidget *>(
        QStringLiteral("lqRibbonMdiTitleBar"), Qt::FindDirectChildrenOnly);
    RibbonMdiTitleBar *titleBar =
        static_cast<RibbonMdiTitleBar *>(titleBarWidget);
    QMdiArea *mdiArea = subWindow->mdiArea();
    const bool isTabbedView = mdiArea
        && mdiArea->viewMode() == QMdiArea::TabbedView;
    if (isTabbedView) {
        if (titleBar) {
            titleBar->cancelDrag();
            titleBar->hide();
        }
        return;
    }

    if (!titleBar) {
        if (subWindow->property("lqRibbonMdiTitleBarCreating").toBool()) {
            return;
        }

        subWindow->setProperty("lqRibbonMdiTitleBarCreating", true);
        titleBar = new RibbonMdiTitleBar(subWindow);
        subWindow->setProperty("lqRibbonMdiTitleBarCreating", false);
    }

    titleBar->show();
    titleBar->syncWithSubWindow();
}

///
/// \brief RibbonMainWindow::updateMdiTabBars
/// Applies flat close-button and tab metrics to tabbed MDI views.
/// \param mdiArea MDI area whose tab bars should be updated.
///
void RibbonMainWindow::updateMdiTabBars(QMdiArea *mdiArea)
{
    if (!mdiArea) {
        return;
    }

    const QList<QTabBar *> tabBarList = mdiArea->findChildren<QTabBar *>();
    for (QTabBar *tabBar : tabBarList) {
        tabBar->setDocumentMode(false);
        tabBar->setElideMode(Qt::ElideRight);
        tabBar->setExpanding(false);
        tabBar->setUsesScrollButtons(true);
    }
}

///
/// \brief RibbonMainWindow::nativeEvent
/// Handles platform-native messages for frameless window behavior.
/// \param eventType Native event type passed by Qt.
/// \param message Platform message pointer.
/// \param result Native result value returned to Qt.
/// \return true when the native message is fully handled.
///
bool RibbonMainWindow::nativeEvent(const QByteArray &eventType, void *message, long *result)
{
#ifdef Q_OS_WIN
    Q_UNUSED(eventType)

    if (!m_nativeFrameEnabled) {
        return QMainWindow::nativeEvent(eventType, message, result);
    }

    MSG *nativeMessage = reinterpret_cast<MSG *>(message);
    if (!nativeMessage) {
        return QMainWindow::nativeEvent(eventType, message, result);
    }

    switch (nativeMessage->message) {
    case WM_NCCALCSIZE:
        *result = 0;
        return true;
    case WM_NCHITTEST: {
        const int x = static_cast<short>(LOWORD(nativeMessage->lParam));
        const int y = static_cast<short>(HIWORD(nativeMessage->lParam));
        *result = nativeHitTestResult(QPoint(x, y));
        return true;
    }
    case WM_GETMINMAXINFO:
        updateNativeMinMaxInfo(reinterpret_cast<void *>(nativeMessage->lParam));
        *result = 0;
        return true;
    case WM_NCRBUTTONUP:
        if (nativeMessage->wParam == HTCAPTION) {
            const int x = static_cast<short>(LOWORD(nativeMessage->lParam));
            const int y = static_cast<short>(HIWORD(nativeMessage->lParam));
            showNativeSystemMenu(QPoint(x, y));
            *result = 0;
            return true;
        }
        break;
    case WM_SYSKEYDOWN:
        if (nativeMessage->wParam == VK_SPACE
            && (HIWORD(nativeMessage->lParam) & KF_ALTDOWN)) {
            showNativeSystemMenu(nativeSystemMenuPoint());
            *result = 0;
            return true;
        }
        break;
    default:
        break;
    }

    return QMainWindow::nativeEvent(eventType, message, result);
#else
    Q_UNUSED(eventType)
    Q_UNUSED(message)
    Q_UNUSED(result)
    return false;
#endif
}

///
/// \brief RibbonMainWindow::handleNativeFrameEvent
/// Converts Qt mouse events into native move, resize, and caption actions.
/// \param object Object that generated the event.
/// \param event Event to inspect.
/// \return true when the event is consumed.
///
bool RibbonMainWindow::handleNativeFrameEvent(QObject *object, QEvent *event)
{
    if (!m_nativeFrameEnabled) {
        return false;
    }

    QWidget *widget = qobject_cast<QWidget *>(object);
    if (!widget || widget->window() != this) {
        return false;
    }

    switch (event->type()) {
    case QEvent::MouseMove: {
        QMouseEvent *mouseEvent = static_cast<QMouseEvent *>(event);
        updateNativeFrameCursor(mouseEvent->globalPos());
        return false;
    }
    case QEvent::Leave:
        unsetCursor();
        return false;
    case QEvent::MouseButtonRelease: {
        QMouseEvent *mouseEvent = static_cast<QMouseEvent *>(event);
        if (widget == m_ribbonBar && mouseEvent->button() == Qt::LeftButton) {
            const QPoint ribbonPoint =
                m_ribbonBar->mapFromGlobal(mouseEvent->globalPos());
            if (m_ribbonBar->isWindowControlPoint(ribbonPoint)) {
                const int controlLeft = visibleWidgetRight(this)
                    - (ribbonWindowButtonWidth * 3);
                const int left = m_ribbonBar->mapFrom(this,
                                                      QPoint(controlLeft, 0)).x();
                const int buttonIndex =
                    (ribbonPoint.x() - left) / ribbonWindowButtonWidth;
                if (buttonIndex == 0) {
                    showMinimized();
                } else if (buttonIndex == 1 && canNativeMaximize()) {
                    isMaximized() ? showNormal() : showMaximized();
                } else if (buttonIndex == 2) {
                    close();
                }

                return true;
            }
        }

        break;
    }
    case QEvent::MouseButtonDblClick: {
        QMouseEvent *mouseEvent = static_cast<QMouseEvent *>(event);
        if (mouseEvent->button() == Qt::LeftButton
            && isNativeCaptionPoint(mouseEvent->globalPos())
            && canNativeMaximize()) {
            isMaximized() ? showNormal() : showMaximized();
            return true;
        }
        break;
    }
    case QEvent::MouseButtonPress: {
        QMouseEvent *mouseEvent = static_cast<QMouseEvent *>(event);
        const QPoint globalPoint = mouseEvent->globalPos();
        if (mouseEvent->button() == Qt::LeftButton) {
            if (nativeResizeEdges(globalPoint) != Qt::Edges()) {
                return startNativeSystemResize(globalPoint);
            }
            if (isNativeCaptionPoint(globalPoint)) {
                return startNativeSystemMove(globalPoint);
            }
        } else if (mouseEvent->button() == Qt::RightButton
                   && isNativeCaptionPoint(globalPoint)) {
            return showNativeSystemMenu(globalPoint);
        }
        break;
    }
    default:
        break;
    }

    return false;
}

///
/// \brief RibbonMainWindow::isNativeCaptionPoint
/// Checks whether a global point is inside the draggable caption area.
/// \param globalPoint Global screen point.
/// \return true when the point can start a window move or caption double-click.
///
bool RibbonMainWindow::isNativeCaptionPoint(const QPoint &globalPoint) const
{
    if (m_nativeCaptionHeight <= 0 || !m_ribbonBar->isVisible()) {
        return false;
    }

    const QPoint ribbonPoint = m_ribbonBar->mapFromGlobal(globalPoint);
    if (!m_ribbonBar->rect().contains(ribbonPoint)
        || ribbonPoint.y() >= m_nativeCaptionHeight) {
        return false;
    }

    if (m_ribbonBar->searchLineEdit()->isVisible()
        && m_ribbonBar->searchLineEdit()->geometry().contains(ribbonPoint)) {
        return false;
    }

    if (m_ribbonBar->quickAccessBar()->isVisible()
        && m_ribbonBar->quickAccessBar()->geometry().contains(ribbonPoint)) {
        return false;
    }

    if (m_ribbonBar->isWindowControlPoint(ribbonPoint)) {
        return false;
    }

    QTabBar *tabBar = m_ribbonBar->findChild<QTabBar *>();
    if (tabBar) {
        const QPoint tabPoint = tabBar->mapFrom(m_ribbonBar, ribbonPoint);
        for (int index = 0; index < tabBar->count(); ++index) {
            if (tabBar->tabRect(index).contains(tabPoint)) {
                return false;
            }
        }
    }

    return true;
}

///
/// \brief RibbonMainWindow::startNativeSystemMove
/// Starts a platform-native system move operation.
/// \param globalPoint Global point where dragging started.
/// \return true when the platform accepted the move operation.
///
bool RibbonMainWindow::startNativeSystemMove(const QPoint &globalPoint)
{
    Q_UNUSED(globalPoint)

    QWindow *nativeWindow = windowHandle();
    if (!nativeWindow) {
        return false;
    }

    return nativeWindow->startSystemMove();
}

///
/// \brief RibbonMainWindow::startNativeSystemResize
/// Starts a platform-native system resize operation.
/// \param globalPoint Global point where resizing started.
/// \return true when the platform accepted the resize operation.
///
bool RibbonMainWindow::startNativeSystemResize(const QPoint &globalPoint)
{
    const Qt::Edges edges = nativeResizeEdges(globalPoint);
    if (edges == Qt::Edges()) {
        return false;
    }

    QWindow *nativeWindow = windowHandle();
    if (!nativeWindow) {
        return false;
    }

    return nativeWindow->startSystemResize(edges);
}

///
/// \brief RibbonMainWindow::nativeResizeEdges
/// Determines which window edges should resize for a global point.
/// \param globalPoint Global screen point.
/// \return Resize edges under the point.
///
Qt::Edges RibbonMainWindow::nativeResizeEdges(const QPoint &globalPoint) const
{
    if (isMaximized() || isFullScreen()) {
        return Qt::Edges();
    }

    const int borderWidth = effectiveNativeResizeBorderWidth();
    if (borderWidth <= 0) {
        return Qt::Edges();
    }

    const QRect windowRect = frameGeometry();
    Qt::Edges edges;
    if (canNativeResizeHorizontally()
        && globalPoint.x() >= windowRect.left()
        && globalPoint.x() < windowRect.left() + borderWidth) {
        edges |= Qt::LeftEdge;
    }
    if (canNativeResizeHorizontally()
        && globalPoint.x() <= windowRect.right()
        && globalPoint.x() > windowRect.right() - borderWidth) {
        edges |= Qt::RightEdge;
    }
    if (canNativeResizeVertically()
        && globalPoint.y() >= windowRect.top()
        && globalPoint.y() < windowRect.top() + borderWidth) {
        edges |= Qt::TopEdge;
    }
    if (canNativeResizeVertically()
        && globalPoint.y() <= windowRect.bottom()
        && globalPoint.y() > windowRect.bottom() - borderWidth) {
        edges |= Qt::BottomEdge;
    }

    return edges;
}

///
/// \brief RibbonMainWindow::updateNativeFrameCursor
/// Updates the cursor shape for native resize hit-test zones.
/// \param globalPoint Global screen point under the cursor.
///
void RibbonMainWindow::updateNativeFrameCursor(const QPoint &globalPoint)
{
    const Qt::Edges edges = nativeResizeEdges(globalPoint);
    if (edges == Qt::Edges()) {
        unsetCursor();
        return;
    }

    const bool isLeftTop = edges.testFlag(Qt::LeftEdge)
        && edges.testFlag(Qt::TopEdge);
    const bool isRightBottom = edges.testFlag(Qt::RightEdge)
        && edges.testFlag(Qt::BottomEdge);
    const bool isRightTop = edges.testFlag(Qt::RightEdge)
        && edges.testFlag(Qt::TopEdge);
    const bool isLeftBottom = edges.testFlag(Qt::LeftEdge)
        && edges.testFlag(Qt::BottomEdge);

    if (isLeftTop || isRightBottom) {
        setCursor(Qt::SizeFDiagCursor);
    } else if (isRightTop || isLeftBottom) {
        setCursor(Qt::SizeBDiagCursor);
    } else if (edges.testFlag(Qt::LeftEdge)
               || edges.testFlag(Qt::RightEdge)) {
        setCursor(Qt::SizeHorCursor);
    } else {
        setCursor(Qt::SizeVerCursor);
    }
}

///
/// \brief RibbonMainWindow::nativeHitTestResult
/// Maps a global point to a Windows non-client hit-test result.
/// \param globalPoint Global screen point.
/// \return Windows hit-test code, or HTCLIENT outside native zones.
///
int RibbonMainWindow::nativeHitTestResult(const QPoint &globalPoint) const
{
#ifdef Q_OS_WIN
    HWND windowHandle = reinterpret_cast<HWND>(winId());
    RECT windowRect;
    if (!GetWindowRect(windowHandle, &windowRect)) {
        return HTCLIENT;
    }

    const bool isMaximized = IsZoomed(windowHandle);
    const int borderWidth = effectiveNativeResizeBorderWidth();
    const bool canResizeHorizontally = canNativeResizeHorizontally();
    const bool canResizeVertically = canNativeResizeVertically();
    if (!isMaximized
        && borderWidth > 0
        && (canResizeHorizontally || canResizeVertically)) {
        const bool onLeft = canResizeHorizontally
            && globalPoint.x() >= windowRect.left
            && globalPoint.x() < windowRect.left + borderWidth;
        const bool onRight = canResizeHorizontally
            && globalPoint.x() <= windowRect.right
            && globalPoint.x() > windowRect.right - borderWidth;
        const bool onTop = canResizeVertically
            && globalPoint.y() >= windowRect.top
            && globalPoint.y() < windowRect.top + borderWidth;
        const bool onBottom = canResizeVertically
            && globalPoint.y() <= windowRect.bottom
            && globalPoint.y() > windowRect.bottom - borderWidth;

        if (onTop && onLeft) {
            return HTTOPLEFT;
        }
        if (onTop && onRight) {
            return HTTOPRIGHT;
        }
        if (onBottom && onLeft) {
            return HTBOTTOMLEFT;
        }
        if (onBottom && onRight) {
            return HTBOTTOMRIGHT;
        }
        if (onLeft) {
            return HTLEFT;
        }
        if (onRight) {
            return HTRIGHT;
        }
        if (onTop) {
            return HTTOP;
        }
        if (onBottom) {
            return HTBOTTOM;
        }
    }

    if (isNativeCaptionPoint(globalPoint)) {
        return HTCAPTION;
    }

    return HTCLIENT;
#else
    Q_UNUSED(globalPoint)
    return 0;
#endif
}

///
/// \brief RibbonMainWindow::effectiveNativeResizeBorderWidth
/// Returns the configured or platform-default resize border width.
/// \return Resize border width in logical pixels.
///
int RibbonMainWindow::effectiveNativeResizeBorderWidth() const
{
#ifdef Q_OS_WIN
    if (m_nativeResizeBorderWidth > 0) {
        return m_nativeResizeBorderWidth;
    }

    const int frameWidth = GetSystemMetrics(SM_CXSIZEFRAME);
    const int paddedWidth = GetSystemMetrics(SM_CXPADDEDBORDER);
    return qMax(4, frameWidth + paddedWidth);
#else
    return m_nativeResizeBorderWidth > 0 ? m_nativeResizeBorderWidth : 6;
#endif
}

///
/// \brief RibbonMainWindow::showNativeSystemMenu
/// Displays the platform system menu at the requested point.
/// \param globalPoint Global point where the menu should appear.
/// \return true when the menu was shown.
///
bool RibbonMainWindow::showNativeSystemMenu(const QPoint &globalPoint)
{
#ifdef Q_OS_WIN
    HWND windowHandle = reinterpret_cast<HWND>(winId());
    HMENU systemMenu = GetSystemMenu(windowHandle, FALSE);
    if (!systemMenu) {
        return false;
    }

    updateNativeSystemMenu(systemMenu);
    SetForegroundWindow(windowHandle);

    const UINT popupFlags = TPM_RETURNCMD
        | TPM_RIGHTBUTTON
        | TPM_LEFTALIGN
        | TPM_TOPALIGN;
    const UINT command = TrackPopupMenu(systemMenu,
        popupFlags,
        globalPoint.x(),
        globalPoint.y(),
        0,
        windowHandle,
        nullptr);

    if (command != 0) {
        PostMessage(windowHandle, WM_SYSCOMMAND, command, 0);
    }

    PostMessage(windowHandle, WM_NULL, 0, 0);
    return true;
#else
    Q_UNUSED(globalPoint)
    return false;
#endif
}

///
/// \brief RibbonMainWindow::updateNativeSystemMenu
/// Enables or disables native system menu commands for the current state.
/// \param menuHandle Platform system menu handle.
///
void RibbonMainWindow::updateNativeSystemMenu(void *menuHandle) const
{
#ifdef Q_OS_WIN
    HMENU systemMenu = reinterpret_cast<HMENU>(menuHandle);
    if (!systemMenu) {
        return;
    }

    HWND windowHandle = reinterpret_cast<HWND>(winId());
    const bool isMaximized = IsZoomed(windowHandle);
    const bool isMinimized = IsIconic(windowHandle);
    const bool canResize = canNativeResizeHorizontally()
        || canNativeResizeVertically();
    const Qt::WindowFlags flags = windowFlags();
    const bool hasCustomButtons = flags.testFlag(Qt::CustomizeWindowHint);
    const bool canMinimize = !hasCustomButtons
        || flags.testFlag(Qt::WindowMinimizeButtonHint);
    const bool canClose = !hasCustomButtons
        || flags.testFlag(Qt::WindowCloseButtonHint);

    const UINT enabled = MF_BYCOMMAND | MF_ENABLED;
    const UINT disabled = MF_BYCOMMAND | MF_GRAYED;
    EnableMenuItem(systemMenu,
        SC_RESTORE,
        (isMaximized || isMinimized) ? enabled : disabled);
    EnableMenuItem(systemMenu,
        SC_MOVE,
        (!isMaximized && !isMinimized) ? enabled : disabled);
    EnableMenuItem(systemMenu,
        SC_SIZE,
        (canResize && !isMaximized && !isMinimized) ? enabled : disabled);
    EnableMenuItem(systemMenu,
        SC_MINIMIZE,
        (canMinimize && !isMinimized) ? enabled : disabled);
    EnableMenuItem(systemMenu,
        SC_MAXIMIZE,
        (canNativeMaximize() && !isMaximized) ? enabled : disabled);
    EnableMenuItem(systemMenu, SC_CLOSE, canClose ? enabled : disabled);
#else
    Q_UNUSED(menuHandle)
#endif
}

///
/// \brief RibbonMainWindow::nativeSystemMenuPoint
/// Calculates the default point for Alt+Space system-menu display.
/// \return Global point where the system menu should open.
///
QPoint RibbonMainWindow::nativeSystemMenuPoint() const
{
#ifdef Q_OS_WIN
    HWND windowHandle = reinterpret_cast<HWND>(winId());
    RECT windowRect;
    if (GetWindowRect(windowHandle, &windowRect)) {
        const int borderWidth = IsZoomed(windowHandle)
            ? 0
            : effectiveNativeResizeBorderWidth();
        return QPoint(windowRect.left + borderWidth,
            windowRect.top + borderWidth + m_nativeCaptionHeight);
    }
#endif

    return mapToGlobal(QPoint(0, m_nativeCaptionHeight));
}

///
/// \brief RibbonMainWindow::updateNativeMinMaxInfo
/// Writes Qt minimum and maximum sizes into native min/max tracking data.
/// \param minMaxInfo Platform min/max structure pointer.
///
void RibbonMainWindow::updateNativeMinMaxInfo(void *minMaxInfo) const
{
#ifdef Q_OS_WIN
    MINMAXINFO *info = reinterpret_cast<MINMAXINFO *>(minMaxInfo);
    if (!info) {
        return;
    }

    HWND windowHandle = reinterpret_cast<HWND>(winId());
    HMONITOR monitorHandle = MonitorFromWindow(windowHandle, MONITOR_DEFAULTTONEAREST);
    MONITORINFO monitorInfo;
    monitorInfo.cbSize = sizeof(MONITORINFO);

    if (GetMonitorInfo(monitorHandle, &monitorInfo)) {
        const RECT workRect = monitorInfo.rcWork;
        const RECT monitorRect = monitorInfo.rcMonitor;
        info->ptMaxPosition.x = workRect.left - monitorRect.left;
        info->ptMaxPosition.y = workRect.top - monitorRect.top;
        info->ptMaxSize.x = workRect.right - workRect.left;
        info->ptMaxSize.y = workRect.bottom - workRect.top;
    }

    const QSize minSize = minimumSize();
    if (minSize.width() > 0) {
        info->ptMinTrackSize.x = minSize.width();
    }
    if (minSize.height() > 0) {
        info->ptMinTrackSize.y = minSize.height();
    }

    const QSize maxSize = maximumSize();
    if (maxSize.width() < QWIDGETSIZE_MAX) {
        info->ptMaxTrackSize.x = maxSize.width();
    }
    if (maxSize.height() < QWIDGETSIZE_MAX) {
        info->ptMaxTrackSize.y = maxSize.height();
    }
#else
    Q_UNUSED(minMaxInfo)
#endif
}

///
/// \brief RibbonMainWindow::canNativeResizeHorizontally
/// Checks whether the window can be resized horizontally.
/// \return true when minimum and maximum widths allow horizontal resize.
///
bool RibbonMainWindow::canNativeResizeHorizontally() const
{
    return minimumWidth() < maximumWidth();
}

///
/// \brief RibbonMainWindow::canNativeResizeVertically
/// Checks whether the window can be resized vertically.
/// \return true when minimum and maximum heights allow vertical resize.
///
bool RibbonMainWindow::canNativeResizeVertically() const
{
    return minimumHeight() < maximumHeight();
}

///
/// \brief RibbonMainWindow::canNativeMaximize
/// Checks whether native maximize should be available.
/// \return true when maximize is allowed by flags and resize constraints.
///
bool RibbonMainWindow::canNativeMaximize() const
{
    const Qt::WindowFlags flags = windowFlags();
    const bool hasCustomButtons = flags.testFlag(Qt::CustomizeWindowHint);
    const bool hasMaximizeButton = !hasCustomButtons
        || flags.testFlag(Qt::WindowMaximizeButtonHint);
    return hasMaximizeButton
        && canNativeResizeHorizontally()
        && canNativeResizeVertically();
}

///
/// \brief RibbonMainWindow::updateNativeWindowStyle
/// Synchronizes Windows style bits with Qt window flags and resize rules.
///
void RibbonMainWindow::updateNativeWindowStyle()
{
#ifdef Q_OS_WIN
    if (!m_nativeFrameEnabled) {
        return;
    }

    HWND windowHandle = reinterpret_cast<HWND>(winId());
    LONG_PTR style = GetWindowLongPtr(windowHandle, GWL_STYLE);
    style |= WS_CAPTION | WS_SYSMENU | WS_THICKFRAME;

    const Qt::WindowFlags flags = windowFlags();
    const bool hasCustomButtons = flags.testFlag(Qt::CustomizeWindowHint);
    if (!hasCustomButtons || flags.testFlag(Qt::WindowMinimizeButtonHint)) {
        style |= WS_MINIMIZEBOX;
    } else {
        style &= ~WS_MINIMIZEBOX;
    }

    if (canNativeMaximize()) {
        style |= WS_MAXIMIZEBOX;
    } else {
        style &= ~WS_MAXIMIZEBOX;
    }

    SetWindowLongPtr(windowHandle, GWL_STYLE, style);
    SetWindowPos(windowHandle,
                 nullptr,
                 0,
                 0,
                 0,
                 0,
                 SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER | SWP_NOACTIVATE
                     | SWP_FRAMECHANGED);
#endif
}
} // namespace LqRibbon
