#include "LqRibbon.h"

#include <QAbstractItemView>
#include <QApplication>
#include <QChildEvent>
#include <QComboBox>
#include <QContextMenuEvent>
#include <QCoreApplication>
#include <QFontMetrics>
#include <QGridLayout>
#include <QKeyEvent>
#include <QLayout>
#include <QListView>
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
#include <QTimer>
#include <QWidgetAction>
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
const int ribbonSimplifiedBarHeight = ribbonCaptionHeight + ribbonTabHeight + 48;
const int ribbonWindowButtonWidth = 46;
const int ribbonWindowButtonHeight = 30;
const int ribbonCollapseButtonWidth = 32;
const int ribbonCollapseButtonHeight = 24;
const int ribbonQuickAccessBelowHeight = 28;
const int ribbonMaximizedContentMargin = 3;
const int ribbonMdiTitleHeight = 28;
const int ribbonMdiTitleBottomOverlap = 2;
const int ribbonMdiButtonWidth = 28;
const int ribbonMdiButtonHeight = 24;
const int ribbonSearchPopupScreenMargin = 8;
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
    {"Recently Used",
     "\xE6\x9C\x80\xE8\xBF\x91\xE4\xBD\xBF\xE7\x94\xA8"},
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

    if (hasChineseApplicationTranslation()) {
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
    void setThemeColors(const QColor &hoverColor,
                        const QColor &pressedColor,
                        const QColor &closeHoverColor,
                        const QColor &closePressedColor,
                        const QColor &glyphColor);

protected:
    void paintEvent(QPaintEvent *event) override;

private:
    ButtonKind m_buttonKind;
    bool m_restoreMode;
    QColor m_hoverColor;
    QColor m_pressedColor;
    QColor m_closeHoverColor;
    QColor m_closePressedColor;
    QColor m_glyphColor;
};

class RibbonCollapseButton : public QToolButton
{
public:
    explicit RibbonCollapseButton(QWidget *parent = nullptr);

    void setCollapsed(bool collapsed);
    void setThemeColors(const QColor &hoverColor,
                        const QColor &pressedColor,
                        const QColor &glyphColor);

protected:
    void paintEvent(QPaintEvent *event) override;

private:
    bool m_collapsed;
    QColor m_hoverColor;
    QColor m_pressedColor;
    QColor m_glyphColor;
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
    , m_hoverColor(QColor(QStringLiteral("#386caf")))
    , m_pressedColor(QColor(QStringLiteral("#244d80")))
    , m_closeHoverColor(QColor(QStringLiteral("#c42b1c")))
    , m_closePressedColor(QColor(QStringLiteral("#8f1f15")))
    , m_glyphColor(Qt::white)
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

void RibbonWindowButton::setThemeColors(const QColor &hoverColor,
                                        const QColor &pressedColor,
                                        const QColor &closeHoverColor,
                                        const QColor &closePressedColor,
                                        const QColor &glyphColor)
{
    m_hoverColor = hoverColor;
    m_pressedColor = pressedColor;
    m_closeHoverColor = closeHoverColor;
    m_closePressedColor = closePressedColor;
    m_glyphColor = glyphColor;
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
                             bool restoreMode,
                             const QColor &glyphColor)
{
    painter->save();

    QPen pen(glyphColor);
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
                             ? m_closePressedColor
                             : m_pressedColor);
    } else if (underMouse()) {
        painter.fillRect(rect(),
                         m_buttonKind == CloseButton
                             ? m_closeHoverColor
                             : m_hoverColor);
    }

    paintRibbonWindowButton(&painter,
                            rect(),
                            m_buttonKind,
                            m_restoreMode,
                            m_glyphColor);
}

///
/// \brief RibbonCollapseButton::RibbonCollapseButton
/// Creates the caption-row button that collapses or expands the Ribbon page.
/// \param parent Parent widget that owns the button.
///
RibbonCollapseButton::RibbonCollapseButton(QWidget *parent)
    : QToolButton(parent)
    , m_collapsed(false)
    , m_hoverColor(QColor(QStringLiteral("#e7e7e7")))
    , m_pressedColor(QColor(QStringLiteral("#d0d0d0")))
    , m_glyphColor(QColor(QStringLiteral("#333333")))
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

void RibbonCollapseButton::setThemeColors(const QColor &hoverColor,
                                          const QColor &pressedColor,
                                          const QColor &glyphColor)
{
    m_hoverColor = hoverColor;
    m_pressedColor = pressedColor;
    m_glyphColor = glyphColor;
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
        painter.fillRect(rect(), m_pressedColor);
    } else if (underMouse()) {
        painter.fillRect(rect(), m_hoverColor);
    }

    QPen pen(m_glyphColor);
    pen.setWidthF(1.5);
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
    setFixedHeight(ribbonMdiTitleHeight + ribbonMdiTitleBottomOverlap);

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
                ribbonMdiTitleHeight + ribbonMdiTitleBottomOverlap);
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

const char ribbonStyleSheetTemplate[] =
    "LqRibbon--RibbonBar {"
    "    background: $ribbonBg;"
    "}"
    "QTabWidget::pane {"
    "    border: none;"
    "    background: $ribbonBg;"
    "}"
    "QTabBar {"
    "    background: transparent;"
    "}"
    "QTabBar::tab {"
    "    min-width: 46px;"
    "    min-height: 21px;"
    "    padding: 2px 10px 1px 10px;"
    "    color: $captionText;"
    "    background: transparent;"
    "    border: none;"
    "}"
    "QTabBar::tab:selected {"
    "    background: $selectedTabBg;"
    "    color: $selectedTabText;"
    "    border-left: 1px solid $selectedTabBorder;"
    "    border-right: 1px solid $selectedTabBorder;"
    "    border-top: 1px solid $selectedTabBorder;"
    "    border-radius: $tabRadius;"
    "}"
    "QTabBar::tab:hover:!selected {"
    "    background: $captionHover;"
    "    border-radius: $tabRadius;"
    "}"
    "QLineEdit#lqRibbonSearchEdit {"
    "    min-height: 18px;"
    "    padding: 0px 22px 0px 6px;"
    "    border: 1px solid $controlBorder;"
    "    border-radius: 1px;"
    "    background: $fieldBg;"
    "    color: $text;"
    "    selection-background-color: $accent;"
    "}"
    "QLineEdit#lqRibbonSearchEdit:focus {"
    "    border-color: $focus;"
    "}"
    "QAbstractItemView#lqRibbonSearchSuggestionPopup {"
    "    border: 1px solid $controlBorder;"
    "    background: $fieldBg;"
    "    selection-background-color: $popupSelection;"
    "    selection-color: $text;"
    "}"
    "QListView#lqRibbonSearchPopupView {"
    "    border: 1px solid $controlBorder;"
    "    background: $popupBg;"
    "    outline: 0px;"
    "}"
    "QListView#lqRibbonSearchPopupView::item {"
    "    min-height: 22px;"
    "    padding: 1px 6px;"
    "    color: $text;"
    "}"
    "QListView#lqRibbonSearchPopupView::item:selected {"
    "    background: $popupSelection;"
    "    color: $text;"
    "}"
    "QToolBar#lqRibbonQuickAccessBar {"
    "    background: transparent;"
    "    border: none;"
    "    spacing: 1px;"
    "}"
    "QToolBar#lqRibbonQuickAccessBar QToolButton {"
    "    border: 1px solid $quickBorder;"
    "    border-radius: 2px;"
    "    padding: 2px;"
    "    background: $quickBg;"
    "}"
    "QToolBar#lqRibbonQuickAccessBar QToolButton:hover {"
    "    background: $captionHover;"
    "    border-color: $controlBorder;"
    "}"
    "QToolBar#lqRibbonTitleButtonBar {"
    "    background: transparent;"
    "    border: none;"
    "    spacing: 12px;"
    "}"
    "QToolBar#lqRibbonTitleButtonBar QToolButton {"
    "    min-width: 22px;"
    "    max-width: 22px;"
    "    min-height: 22px;"
    "    max-height: 22px;"
    "    border: 1px solid transparent;"
    "    border-radius: 2px;"
    "    padding: 0px;"
    "    background: transparent;"
    "}"
    "QToolBar#lqRibbonTitleButtonBar QToolButton:hover {"
    "    background: $captionHover;"
    "    border-color: $controlBorder;"
    "}"
    "LqRibbon--RibbonGroup {"
    "    background: transparent;"
    "    border: none;"
    "    border-radius: 0px;"
    "    margin: 0px;"
    "}"
    "LqRibbon--RibbonGroup QLabel#lqRibbonGroupTitle {"
    "    color: $text;"
    "    font-size: 11px;"
    "    padding: 0px 4px 3px 4px;"
    "}"
    "LqRibbon--RibbonGroup QToolButton {"
    "    border: 1px solid transparent;"
    "    border-radius: 1px;"
    "    padding: 1px 2px;"
    "    color: $text;"
    "    background: transparent;"
    "}"
    "LqRibbon--RibbonGroup QToolButton:hover {"
    "    background: $groupHover;"
    "    border-color: $commandHoverBorder;"
    "}"
    "LqRibbon--RibbonGroup QToolButton:pressed {"
    "    background: $groupPressed;"
    "    border-color: $commandPressedBorder;"
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
    "}"
    "QMenu::item:selected {"
    "    background: $groupHover;"
    "    color: $text;"
    "}";

struct RibbonStylePalette
{
    QString accent;
    QString captionBackground;
    QString captionHover;
    QString captionPressed;
    QString captionText;
    QString closeHover;
    QString closePressed;
    QString selectedTabBackground;
    QString selectedTabText;
    QString ribbonBackground;
    QString fieldBackground;
    QString popupBackground;
    QString text;
    QString focus;
    QString popupSelection;
    QString groupHover;
    QString groupPressed;
    QString quickBackground;
    QString quickBorder;
    QString tabRadius;
    QString selectedTabBorder;
    QString controlBorder;
    QString commandHoverBorder;
    QString commandPressedBorder;
};

RibbonStylePalette ribbonStylePalette(LqRibbon::RibbonBar::RibbonStyle style)
{
    switch (style) {
    case LqRibbon::RibbonBar::Office2019Colorful:
        return {
            QStringLiteral("#185abd"),
            QStringLiteral("#185abd"),
            QStringLiteral("#2f6fca"),
            QStringLiteral("#124078"),
            QStringLiteral("#ffffff"),
            QStringLiteral("#c42b1c"),
            QStringLiteral("#8f1f15"),
            QStringLiteral("#ffffff"),
            QStringLiteral("#124078"),
            QStringLiteral("#f3f2f1"),
            QStringLiteral("#ffffff"),
            QStringLiteral("#f7f7f7"),
            QStringLiteral("#202020"),
            QStringLiteral("#5f95d0"),
            QStringLiteral("#e8f2ff"),
            QStringLiteral("#deecf9"),
            QStringLiteral("#c7e0f4"),
            QStringLiteral("#2466b1"),
            QStringLiteral("#8fb9ec"),
            QStringLiteral("0px"),
            QStringLiteral("#c8c8c8"),
            QStringLiteral("#b7cbe6"),
            QStringLiteral("#deecf9"),
            QStringLiteral("#5f95d0")
        };
    case LqRibbon::RibbonBar::Microsoft365Light:
        return {
            QStringLiteral("#0f6cbd"),
            QStringLiteral("#f8f8f8"),
            QStringLiteral("#e5f1fb"),
            QStringLiteral("#cfe4fa"),
            QStringLiteral("#242424"),
            QStringLiteral("#c42b1c"),
            QStringLiteral("#8f1f15"),
            QStringLiteral("#ffffff"),
            QStringLiteral("#0f6cbd"),
            QStringLiteral("#fbfbfb"),
            QStringLiteral("#ffffff"),
            QStringLiteral("#ffffff"),
            QStringLiteral("#242424"),
            QStringLiteral("#0f6cbd"),
            QStringLiteral("#e5f1fb"),
            QStringLiteral("#e5f1fb"),
            QStringLiteral("#cfe4fa"),
            QStringLiteral("#ffffff"),
            QStringLiteral("#e5e5e5"),
            QStringLiteral("6px 6px 0px 0px"),
            QStringLiteral("#e5e5e5"),
            QStringLiteral("#e5e5e5"),
            QStringLiteral("#e5e5e5"),
            QStringLiteral("#c7c7c7")
        };
    case LqRibbon::RibbonBar::Microsoft365Dark:
        return {
            QStringLiteral("#60cdff"),
            QStringLiteral("#202020"),
            QStringLiteral("#3a3a3a"),
            QStringLiteral("#4a4a4a"),
            QStringLiteral("#f3f2f1"),
            QStringLiteral("#c42b1c"),
            QStringLiteral("#8f1f15"),
            QStringLiteral("#2d2d2d"),
            QStringLiteral("#ffffff"),
            QStringLiteral("#1f1f1f"),
            QStringLiteral("#2d2d2d"),
            QStringLiteral("#2d2d2d"),
            QStringLiteral("#f3f2f1"),
            QStringLiteral("#60cdff"),
            QStringLiteral("#3b3a39"),
            QStringLiteral("#3a3a3a"),
            QStringLiteral("#4a4a4a"),
            QStringLiteral("#2d2d2d"),
            QStringLiteral("#3a3a3a"),
            QStringLiteral("6px 6px 0px 0px"),
            QStringLiteral("#3a3a3a"),
            QStringLiteral("#3a3a3a"),
            QStringLiteral("#3a3a3a"),
            QStringLiteral("#5f5f5f")
        };
    case LqRibbon::RibbonBar::Office2016Blue:
    default:
        return {
            QStringLiteral("#2b579a"),
            QStringLiteral("#2b579a"),
            QStringLiteral("#386caf"),
            QStringLiteral("#244d80"),
            QStringLiteral("#ffffff"),
            QStringLiteral("#c42b1c"),
            QStringLiteral("#8f1f15"),
            QStringLiteral("#ffffff"),
            QStringLiteral("#124078"),
            QStringLiteral("#f3f3f3"),
            QStringLiteral("#ffffff"),
            QStringLiteral("#f4f4f4"),
            QStringLiteral("#202020"),
            QStringLiteral("#5f95d0"),
            QStringLiteral("#e8f2ff"),
            QStringLiteral("#8cc8f7"),
            QStringLiteral("#c5ddfa"),
            QStringLiteral("#2f63a3"),
            QStringLiteral("#6f9fd0"),
            QStringLiteral("0px"),
            QStringLiteral("#c8c8c8"),
            QStringLiteral("#b7cbe6"),
            QStringLiteral("#8cc8f7"),
            QStringLiteral("#5f95d0")
        };
    }
}

QString buildRibbonStyleSheet(const RibbonStylePalette &palette)
{
    QString styleSheet = QString::fromLatin1(ribbonStyleSheetTemplate);
    struct Replacement
    {
        const char *token;
        const QString *value;
    };

    const Replacement replacements[] = {
        {"$accent", &palette.accent},
        {"$captionText", &palette.captionText},
        {"$captionHover", &palette.captionHover},
        {"$selectedTabBg", &palette.selectedTabBackground},
        {"$selectedTabText", &palette.selectedTabText},
        {"$ribbonBg", &palette.ribbonBackground},
        {"$fieldBg", &palette.fieldBackground},
        {"$popupBg", &palette.popupBackground},
        {"$text", &palette.text},
        {"$focus", &palette.focus},
        {"$popupSelection", &palette.popupSelection},
        {"$groupHover", &palette.groupHover},
        {"$groupPressed", &palette.groupPressed},
        {"$quickBg", &palette.quickBackground},
        {"$quickBorder", &palette.quickBorder},
        {"$tabRadius", &palette.tabRadius},
        {"$selectedTabBorder", &palette.selectedTabBorder},
        {"$controlBorder", &palette.controlBorder},
        {"$commandHoverBorder", &palette.commandHoverBorder},
        {"$commandPressedBorder", &palette.commandPressedBorder},
    };

    for (const Replacement &replacement : replacements) {
        styleSheet.replace(QLatin1String(replacement.token),
                           *replacement.value);
    }

    return styleSheet;
}

const char ribbonMdiAreaStyleSheet[] =
    "QMdiArea {"
    "    background: #cfcfcf;"
    "}"
    "QMdiSubWindow {"
    "    background: #2b579a;"
    "    border: 1px solid #8aaed7;"
    "}"
    "QMdiSubWindow::title {"
    "    background: #2b579a;"
    "    color: #ffffff;"
    "    padding-left: 6px;"
    "    height: 30px;"
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
/// Calculates an Office-style width for a large Ribbon command button.
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
/// Calculates an Office-style width for a compact Ribbon command button.
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

QColor ribbonContextColor(LqRibbon::ContextColor color)
{
    switch (color) {
    case LqRibbon::ContextColorBlue:
        return QColor(QStringLiteral("#2b579a"));
    case LqRibbon::ContextColorYellow:
        return QColor(QStringLiteral("#f2c811"));
    case LqRibbon::ContextColorGreen:
        return QColor(QStringLiteral("#107c10"));
    case LqRibbon::ContextColorRed:
        return QColor(QStringLiteral("#d13438"));
    case LqRibbon::ContextColorPurple:
        return QColor(QStringLiteral("#5c2d91"));
    case LqRibbon::ContextColorCyan:
        return QColor(QStringLiteral("#008575"));
    case LqRibbon::ContextColorOrange:
        return QColor(QStringLiteral("#ca5010"));
    case LqRibbon::ContextColorNone:
    default:
        return QColor();
    }
}

} // namespace

namespace LqRibbon {

RibbonGroup::RibbonGroup(QWidget *parent)
    : RibbonGroup(QString(), parent)
{
}

RibbonGroup::RibbonGroup(RibbonPage *page, const QString &strTitle)
    : RibbonGroup(strTitle, page)
{
    if (page) {
        page->addGroup(this);
    }
}

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
    , m_optionButton(new QToolButton(this))
    , m_smallButtonRow(0)
    , m_smallButtonColumn(0)
    , m_titleFont(m_titleLabel->font())
    , m_titleColor(palette().text().color())
    , m_optionButtonAction(nullptr)
    , m_contentAlignment(Qt::AlignLeft | Qt::AlignTop)
    , m_controlsAlignment(Qt::AlignLeft | Qt::AlignTop)
    , m_titleElideMode(Qt::ElideRight)
    , m_sizeDefinition(RibbonControlSizeDefinition::GroupLarge
                       | RibbonControlSizeDefinition::GroupMedium
                       | RibbonControlSizeDefinition::GroupSmall
                       | RibbonControlSizeDefinition::GroupPopup)
    , m_controlsGrouping(false)
{
    setObjectName(QStringLiteral("lqRibbonGroup"));
    setSizePolicy(QSizePolicy::Maximum, QSizePolicy::Preferred);
    setMinimumWidth(44);

    m_titleLabel->setObjectName(QStringLiteral("lqRibbonGroupTitle"));
    m_titleLabel->setAlignment(Qt::AlignCenter);

    m_optionButton->setObjectName(QStringLiteral("lqRibbonGroupOptionButton"));
    m_optionButton->setAutoRaise(true);
    m_optionButton->setFixedSize(16, 16);
    m_optionButton->setToolButtonStyle(Qt::ToolButtonIconOnly);
    m_optionButton->hide();

    m_contentLayout->setContentsMargins(ribbonGroupLeftMargin,
                                        ribbonGroupTopMargin,
                                        ribbonGroupRightMargin,
                                        ribbonGroupBottomMargin);
    m_contentLayout->setSpacing(2);
    m_contentLayout->setAlignment(m_contentAlignment);

    QVBoxLayout *mainLayout = new QVBoxLayout(this);
    mainLayout->setContentsMargins(0, 0, 0, 0);
    mainLayout->setSpacing(0);
    mainLayout->addLayout(m_contentLayout, 1);

    QHBoxLayout *titleLayout = new QHBoxLayout;
    titleLayout->setContentsMargins(4, 0, 4, 0);
    titleLayout->setSpacing(2);
    titleLayout->addWidget(m_titleLabel, 1);
    titleLayout->addWidget(m_optionButton);
    mainLayout->addLayout(titleLayout);
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
                                Qt::ToolButtonStyle buttonStyle,
                                QMenu *menu,
                                QToolButton::ToolButtonPopupMode mode)
{
    QAction *action = new QAction(icon, strText, this);
    addAction(action, buttonStyle, menu, mode);
    return action;
}

///
/// \brief RibbonGroup::addAction
/// Adds an existing action as a Ribbon command button.
/// \param action Existing action to expose in the group.
/// \param buttonStyle Button style used by the created command button.
///
QAction *RibbonGroup::addAction(QAction *action,
                                Qt::ToolButtonStyle buttonStyle,
                                QMenu *menu,
                                QToolButton::ToolButtonPopupMode mode)
{
    if (!action) {
        return nullptr;
    }

    QToolButton *button = createButton(action, buttonStyle, menu, mode);
    if (buttonStyle == Qt::ToolButtonTextBesideIcon) {
        addSmallButton(button);
        rememberActionWidget(action, button);
        QWidget::addAction(action);
        return action;
    }

    m_contentLayout->addWidget(button);
    rememberActionWidget(action, button);
    QWidget::addAction(action);
    return action;
}

QAction *RibbonGroup::insertAction(QAction *before,
                                   QAction *action,
                                   Qt::ToolButtonStyle buttonStyle,
                                   QMenu *menu,
                                   QToolButton::ToolButtonPopupMode mode)
{
    if (!action) {
        return nullptr;
    }

    QToolButton *button = createButton(action, buttonStyle, menu, mode);
    const int beforeIndex = before && m_actionWidgetHash.contains(before)
        ? m_contentLayout->indexOf(m_actionWidgetHash.value(before))
        : -1;
    if (buttonStyle == Qt::ToolButtonTextBesideIcon) {
        addSmallButton(button);
    } else if (beforeIndex >= 0) {
        m_contentLayout->insertWidget(beforeIndex, button);
    } else {
        m_contentLayout->addWidget(button);
    }
    rememberActionWidget(action, button);
    QWidget::insertAction(before, action);
    return action;
}

///
/// \brief RibbonGroup::addWidget
/// Adds a custom widget into the group content area.
/// \param widget Widget inserted into the group layout.
///
QAction *RibbonGroup::addWidget(QWidget *widget)
{
    if (!widget) {
        return nullptr;
    }

    widget->setParent(this);
    QWidgetAction *action = new QWidgetAction(this);
    QWidget::addAction(action);

    QToolButton *button = qobject_cast<QToolButton *>(widget);
    if (button) {
        setupSmallButton(button);
        addSmallButton(button);
        rememberActionWidget(action, widget);
        return action;
    }

    m_contentLayout->addWidget(widget);
    rememberActionWidget(action, widget);
    return action;
}

QAction *RibbonGroup::addWidget(const QIcon &icon,
                                const QString &strText,
                                QWidget *widget)
{
    QAction *action = addWidget(widget);
    if (action) {
        action->setIcon(icon);
        action->setText(strText);
    }
    return action;
}

QAction *RibbonGroup::addWidget(const QIcon &icon,
                                const QString &strText,
                                bool stretch,
                                QWidget *widget)
{
    QAction *action = addWidget(icon, strText, widget);
    if (stretch && widget) {
        widget->setSizePolicy(QSizePolicy::Expanding,
                              widget->sizePolicy().verticalPolicy());
    }
    return action;
}

QMenu *RibbonGroup::addMenu(const QIcon &icon,
                            const QString &strText,
                            Qt::ToolButtonStyle buttonStyle)
{
    QMenu *menu = new QMenu(strText, this);
    menu->menuAction()->setIcon(icon);
    QAction *menuButtonAction = addAction(icon,
                                          strText,
                                          buttonStyle,
                                          menu,
                                          QToolButton::InstantPopup);
    connect(menu->menuAction(), &QAction::changed, menuButtonAction, [menu, menuButtonAction]() {
        menuButtonAction->setText(menu->title());
        menuButtonAction->setIcon(menu->menuAction()->icon());
        menuButtonAction->setEnabled(menu->menuAction()->isEnabled());
        menuButtonAction->setVisible(menu->menuAction()->isVisible());
    });
    return menu;
}

QAction *RibbonGroup::addSeparator()
{
    QAction *action = new QAction(this);
    action->setSeparator(true);
    QFrame *line = new QFrame(this);
    line->setFrameShape(QFrame::VLine);
    line->setFrameShadow(QFrame::Sunken);
    line->setFixedWidth(8);
    m_contentLayout->addWidget(line);
    QWidget::addAction(action);
    rememberActionWidget(action, line);
    return action;
}

void RibbonGroup::addControl(RibbonControl *control)
{
    if (!control || m_controlList.contains(control)) {
        return;
    }
    m_controlList.append(control);
    addWidget(control);
}

void RibbonGroup::removeControl(RibbonControl *control)
{
    if (!control) {
        return;
    }
    m_controlList.removeAll(control);
    remove(control);
}

void RibbonGroup::remove(QWidget *widget)
{
    if (!widget) {
        return;
    }
    QAction *action = m_widgetActionHash.take(widget);
    if (action) {
        m_actionWidgetHash.remove(action);
        QWidget::removeAction(action);
        action->deleteLater();
    }
    m_contentLayout->removeWidget(widget);
    if (m_smallButtonLayout) {
        m_smallButtonLayout->removeWidget(widget);
    }
    widget->deleteLater();
}

void RibbonGroup::clear()
{
    const QList<QWidget *> widgets = m_widgetActionHash.keys();
    for (QWidget *widget : widgets) {
        remove(widget);
    }
    m_controlList.clear();
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
    if (m_titleLabel->text() == strTitle) {
        return;
    }
    m_titleLabel->setText(strTitle);
    emit titleChanged(strTitle);
}

RibbonBar *RibbonGroup::ribbonBar() const
{
    const RibbonPage *page = qobject_cast<const RibbonPage *>(parentWidget());
    return page ? page->ribbonBar() : nullptr;
}

bool RibbonGroup::isReduced() const
{
    return false;
}

const QFont &RibbonGroup::titleFont() const
{
    return m_titleFont;
}

void RibbonGroup::setTitleFont(const QFont &font)
{
    if (m_titleFont == font) {
        return;
    }
    m_titleFont = font;
    m_titleLabel->setFont(font);
    emit titleFontChanged(font);
}

const QColor &RibbonGroup::titleColor() const
{
    return m_titleColor;
}

void RibbonGroup::setTitleColor(const QColor &color)
{
    m_titleColor = color;
    QPalette pal = m_titleLabel->palette();
    pal.setColor(QPalette::WindowText, color);
    m_titleLabel->setPalette(pal);
}

const QIcon &RibbonGroup::icon() const
{
    return m_icon;
}

void RibbonGroup::setIcon(const QIcon &icon)
{
    m_icon = icon;
}

bool RibbonGroup::isOptionButtonVisible() const
{
    return m_optionButton->isVisible();
}

void RibbonGroup::setOptionButtonVisible(bool visible)
{
    m_optionButton->setVisible(visible);
}

QAction *RibbonGroup::optionButtonAction() const
{
    return m_optionButtonAction;
}

void RibbonGroup::setOptionButtonAction(QAction *action)
{
    m_optionButtonAction = action;
    m_optionButton->setDefaultAction(action);
    setOptionButtonVisible(action != nullptr);
}

Qt::Alignment RibbonGroup::contentAlignment() const
{
    return m_contentAlignment;
}

void RibbonGroup::setContentAlignment(Qt::Alignment alignment)
{
    m_contentAlignment = alignment;
    m_contentLayout->setAlignment(alignment);
}

Qt::Alignment RibbonGroup::controlsAlignment() const
{
    return m_controlsAlignment;
}

void RibbonGroup::setControlsAlignment(Qt::Alignment alignment)
{
    m_controlsAlignment = alignment;
}

int RibbonGroup::spacing() const
{
    return m_contentLayout->spacing();
}

void RibbonGroup::setSpacing(int spacing)
{
    m_contentLayout->setSpacing(spacing);
    if (m_smallButtonLayout) {
        m_smallButtonLayout->setHorizontalSpacing(spacing);
    }
}

int RibbonGroup::controlCount() const
{
    return m_controlList.count();
}

RibbonControl *RibbonGroup::controlByIndex(int index) const
{
    return index >= 0 && index < m_controlList.count()
        ? m_controlList.at(index)
        : nullptr;
}

RibbonControl *RibbonGroup::controlByAction(QAction *action) const
{
    QWidget *widget = m_actionWidgetHash.value(action, nullptr);
    return qobject_cast<RibbonControl *>(widget);
}

RibbonWidgetControl *RibbonGroup::controlByWidget(QWidget *widget) const
{
    return qobject_cast<RibbonWidgetControl *>(widget);
}

Qt::TextElideMode RibbonGroup::titleElideMode() const
{
    return m_titleElideMode;
}

void RibbonGroup::setTitleElideMode(Qt::TextElideMode mode)
{
    m_titleElideMode = mode;
    update();
}

RibbonControlSizeDefinition::GroupSizes RibbonGroup::sizeDefinition() const
{
    return m_sizeDefinition;
}

void RibbonGroup::setSizeDefinition(
    const RibbonControlSizeDefinition::GroupSizes &sizeDefinition)
{
    m_sizeDefinition = sizeDefinition;
}

void RibbonGroup::setControlsCentering(bool enabled)
{
    setContentAlignment(enabled ? Qt::AlignCenter : Qt::AlignLeft);
}

bool RibbonGroup::isControlsCentering() const
{
    return m_contentAlignment.testFlag(Qt::AlignHCenter);
}

void RibbonGroup::setControlsGrouping(bool enabled)
{
    m_controlsGrouping = enabled;
}

bool RibbonGroup::isControlsGrouping() const
{
    return m_controlsGrouping;
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
QToolButton *RibbonGroup::createButton(QAction *action,
                                       Qt::ToolButtonStyle buttonStyle,
                                       QMenu *menu,
                                       QToolButton::ToolButtonPopupMode mode)
{
    QToolButton *button = new QToolButton(this);
    button->setDefaultAction(action);
    button->setAutoRaise(true);
    button->setToolButtonStyle(buttonStyle);
    button->setFocusPolicy(Qt::NoFocus);

    QMenu *buttonMenu = menu ? menu : action->menu();
    if (buttonMenu) {
        button->setMenu(buttonMenu);
        action->setMenu(buttonMenu);
        button->setPopupMode(mode);
    }

    if (buttonStyle != Qt::ToolButtonTextUnderIcon) {
        setupSmallButton(button);
        return button;
    }

    button->setIconSize(ribbonLargeIconSize(button));
    button->setPopupMode(buttonMenu
                         ? mode
                         : QToolButton::DelayedPopup);
    const int buttonWidth = ribbonLargeButtonWidth(button);
    const int buttonHeight = ribbonLargeButtonHeight(button);
    button->setMinimumSize(buttonWidth, buttonHeight);
    button->setMaximumSize(buttonWidth, buttonHeight);
    button->setSizePolicy(QSizePolicy::Fixed, QSizePolicy::Fixed);

    return button;
}

void RibbonGroup::rememberActionWidget(QAction *action, QWidget *widget)
{
    if (!action || !widget) {
        return;
    }
    m_actionWidgetHash.insert(action, widget);
    m_widgetActionHash.insert(widget, action);
    if (RibbonControl *control = qobject_cast<RibbonControl *>(widget)) {
        if (!m_controlList.contains(control)) {
            m_controlList.append(control);
        }
    }
    for (auto it = m_actionTriggeredActionList.begin();
         it != m_actionTriggeredActionList.end();) {
        if (it->isNull()) {
            it = m_actionTriggeredActionList.erase(it);
            continue;
        }
        if (it->data() == action) {
            return;
        }
        ++it;
    }

    connect(action, &QAction::triggered, this, [this, action]() {
        emit actionTriggered(action);
        if (RibbonBar *bar = ribbonBar()) {
            if (bar->isRibbonMinimized()) {
                QTimer::singleShot(0, bar, [bar]() {
                    if (bar->isRibbonMinimized()) {
                        bar->setRibbonMinimized(true);
                    }
                });
            }
        }
    });
    m_actionTriggeredActionList.append(action);
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
    const QToolButton::ToolButtonPopupMode popupMode = button->popupMode();
    button->setPopupMode(button->menu()
                         ? (popupMode == QToolButton::DelayedPopup
                                ? QToolButton::MenuButtonPopup
                                : popupMode)
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
RibbonPage::RibbonPage(QWidget *parent)
    : RibbonPage(QString::fromLatin1(QtnRibbonUntitledString), parent)
{
}

RibbonPage::RibbonPage(const QString &strTitle, QWidget *parent)
    : QWidget(parent)
    , m_strTitle(strTitle)
    , m_groupLayout(new QHBoxLayout)
    , m_defaultAction(new QAction(strTitle, this))
    , m_contextColor()
{
    m_groupLayout->setContentsMargins(0, 0, 0, 0);
    m_groupLayout->setSpacing(4);
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
    addGroup(group);
    return group;
}

void RibbonPage::addGroup(RibbonGroup *group)
{
    insertGroup(m_groupList.count(), group);
}

RibbonGroup *RibbonPage::addGroup(const QIcon &icon, const QString &strTitle)
{
    RibbonGroup *group = addGroup(strTitle);
    group->setIcon(icon);
    return group;
}

void RibbonPage::insertGroup(int index, RibbonGroup *group)
{
    if (!group) {
        return;
    }
    const int oldIndex = m_groupList.indexOf(group);
    if (oldIndex >= 0) {
        m_groupList.removeAt(oldIndex);
        m_groupLayout->removeWidget(group);
        if (oldIndex < index) {
            --index;
        }
    }

    const int normalizedIndex = index < 0
        ? m_groupList.count()
        : qMin(index, m_groupList.count());
    group->setParent(this);
    const int stretchIndex = qMax(0, m_groupLayout->count() - 1);
    m_groupLayout->insertWidget(qMin(normalizedIndex, stretchIndex), group);
    m_groupList.insert(normalizedIndex, group);
    group->show();
    updateLayout();
}

RibbonGroup *RibbonPage::insertGroup(int index, const QString &strTitle)
{
    RibbonGroup *group = new RibbonGroup(strTitle, this);
    insertGroup(index, group);
    return group;
}

RibbonGroup *RibbonPage::insertGroup(int index,
                                     const QIcon &icon,
                                     const QString &strTitle)
{
    RibbonGroup *group = insertGroup(index, strTitle);
    group->setIcon(icon);
    return group;
}

void RibbonPage::removeGroup(RibbonGroup *group)
{
    if (!group) {
        return;
    }
    detachGroup(group);
    group->deleteLater();
}

void RibbonPage::removeGroupByIndex(int index)
{
    removeGroup(group(index));
}

void RibbonPage::detachGroup(RibbonGroup *group)
{
    if (!group) {
        return;
    }
    m_groupList.removeAll(group);
    m_groupLayout->removeWidget(group);
    group->setParent(nullptr);
    updateLayout();
}

void RibbonPage::detachGroupByIndex(int index)
{
    detachGroup(group(index));
}

void RibbonPage::clearGroups()
{
    const RibbonGroupList groupList = m_groupList;
    for (RibbonGroup *group : groupList) {
        removeGroup(group);
    }
}

RibbonBar *RibbonPage::ribbonBar() const
{
    QWidget *widget = parentWidget();
    while (widget) {
        if (RibbonBar *bar = qobject_cast<RibbonBar *>(widget)) {
            return bar;
        }
        widget = widget->parentWidget();
    }
    return nullptr;
}

QAction *RibbonPage::defaultAction() const
{
    return m_defaultAction;
}

int RibbonPage::groupCount() const
{
    return m_groupList.count();
}

RibbonGroup *RibbonPage::group(int index) const
{
    return index >= 0 && index < m_groupList.count()
        ? m_groupList.at(index)
        : nullptr;
}

int RibbonPage::groupIndex(RibbonGroup *group) const
{
    return m_groupList.indexOf(group);
}

const RibbonGroupList &RibbonPage::groups() const
{
    return m_groupList;
}

void RibbonPage::paintEvent(QPaintEvent *event)
{
    QWidget::paintEvent(event);

    QPainter painter(this);
    painter.setRenderHint(QPainter::Antialiasing, false);

    const int top = 5;
    const int bottom = qMax(top, height() - 4);
    for (int index = 0; index < m_groupList.count(); ++index) {
        RibbonGroup *group = m_groupList.at(index);
        if (!group || !group->isVisible()) {
            continue;
        }

        const int x = group->geometry().right()
            + qMax(1, m_groupLayout->spacing() / 2);
        painter.setPen(QColor(QStringLiteral("#c2c2c2")));
        painter.drawLine(x, top, x, bottom);
        painter.setPen(QColor(QStringLiteral("#f4f4f4")));
        painter.drawLine(x + 1, top, x + 1, bottom);
    }
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
    m_defaultAction->setText(strTitle);
    emit titleChanged(strTitle);
}

const QColor &RibbonPage::contextColor() const
{
    return m_contextColor;
}

const QString &RibbonPage::contextTitle() const
{
    return m_contextTitle;
}

const QString &RibbonPage::contextGroupName() const
{
    return m_contextGroupName;
}

void RibbonPage::setContextColor(ContextColor color)
{
    setContextColor(ribbonContextColor(color));
}

void RibbonPage::setContextColor(const QColor &color)
{
    m_contextColor = color;
    update();
}

void RibbonPage::setContextTitle(const QString &strTitle)
{
    m_contextTitle = strTitle;
}

void RibbonPage::setContextGroupName(const QString &strGroupName)
{
    m_contextGroupName = strGroupName;
}

void RibbonPage::updateLayout()
{
    updateGeometry();
    update();
}

///
/// \brief RibbonBar::RibbonBar
/// Creates the Ribbon bar, search box, quick access bar, and frame buttons.
/// \param parent Parent widget.
///
RibbonBar::RibbonBar(QWidget *parent)
    : QTabWidget(parent)
    , m_searchEdit(new RibbonSearchBar(this))
    , m_searchPopupView(new QListView(this))
    , m_searchPopupModel(new QStandardItemModel(this))
    , m_searchLineAction(nullptr)
    , m_quickAccessBar(new RibbonQuickAccessBar(this))
    , m_titleButtonBar(new QToolBar(this))
    , m_progressBar(new RibbonProgressBar(this))
    , m_systemButton(nullptr)
    , m_simplifiedAction(new QAction(this))
    , m_customizeManager(nullptr)
    , m_customizeDialog(nullptr)
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
    , m_ribbonTemporaryExpanded(false)
    , m_ignoreNextTabRelease(false)
    , m_searchVisibleExplicitlySet(false)
    , m_searchPlaceholderExplicitlySet(false)
    , m_quickAccessBarPosition(TopPosition)
    , m_tabBarPosition(TopPosition)
    , m_searchBarAppearance(SearchBarCentral)
    , m_ribbonStyle(Office2016Blue)
    , m_logoAlignment(Qt::AlignLeft)
    , m_keyTipsEnabled(false)
    , m_keyTipsComplement(false)
    , m_keyTipsShowing(false)
    , m_minimizationEnabled(true)
    , m_simplifiedMode(false)
    , m_simplifiedModeEnabled(true)
    , m_acrylicEnabled(false)
    , m_contextualTabsVisible(true)
    , m_titleGroupsVisible(true)
    , m_expandDirection(Qt::LeftToRight)
    , m_updateLockCount(0)
{
    setDocumentMode(false);
    setMovable(false);
    setTabPosition(QTabWidget::North);
    updateRibbonMetrics();
    tabBar()->setExpanding(false);
    tabBar()->setUsesScrollButtons(true);
    if (qApp) {
        qApp->installEventFilter(this);
    }

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
    m_searchPopupView->setWindowFlags(Qt::Popup | Qt::FramelessWindowHint);
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

    m_progressBar->setObjectName(QStringLiteral("lqRibbonProgressBar"));
    m_progressBar->hide();

    m_titleButtonBar->setObjectName(QStringLiteral("lqRibbonTitleButtonBar"));
    m_titleButtonBar->setMovable(false);
    m_titleButtonBar->setFloatable(false);
    m_titleButtonBar->setIconSize(QSize(16, 16));
    m_titleButtonBar->setToolButtonStyle(Qt::ToolButtonIconOnly);
    m_titleButtonBar->hide();

    setupWindowControlButton(m_minimizeButton);
    setupWindowControlButton(m_maximizeButton);
    setupWindowControlButton(m_closeButton);
    setupWindowControlButton(m_collapseButton);
    m_simplifiedAction->setText(
        QString::fromLatin1(QtnRibbonSimplifiedRibbonActionString));
    m_simplifiedAction->setToolTip(
        QString::fromLatin1(QtnRibbonSimplifiedRibbonActionToolTipsString));
    m_simplifiedAction->setCheckable(true);
    connect(m_simplifiedAction, &QAction::toggled,
            this, &RibbonBar::setSimplifiedMode);
    updateLocalizedText();
    updateWindowControlVisibility();

    connect(this, &QTabWidget::currentChanged, this, [this](int index) {
        emit pageChanged(index);
        emit currentPageIndexChanged(index);
        emit currentPageChanged(page(index));
    });
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
    updateTitleButtonGeometry();
    updateQuickAccessGeometry();
}

///
/// \brief RibbonBar::~RibbonBar
/// Hides transient search UI before Qt destroys the owned child widgets.
///
RibbonBar::~RibbonBar()
{
    if (qApp) {
        qApp->removeEventFilter(this);
    }

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
    addPage(newPage);
    return newPage;
}

void RibbonBar::addPage(RibbonPage *page)
{
    insertPage(count(), page);
}

RibbonPage *RibbonBar::insertPage(int index, const QString &strTitle)
{
    RibbonPage *newPage = new RibbonPage(strTitle, this);
    insertPage(index, newPage);
    return newPage;
}

void RibbonBar::insertPage(int index, RibbonPage *page)
{
    if (!page) {
        return;
    }
    const int oldIndex = indexOf(page);
    if (oldIndex >= 0) {
        removeTab(oldIndex);
        if (oldIndex < index) {
            --index;
        }
    }
    const int normalizedIndex = index < 0 ? count() : qMin(index, count());
    const int insertedIndex = insertTab(normalizedIndex, page, page->title());
    connect(page, &RibbonPage::titleChanged, this,
            [this, page](const QString &strNewTitle) {
        const int pageIndex = indexOf(page);
        if (pageIndex >= 0) {
            setTabText(pageIndex, strNewTitle);
        }
    }, Qt::UniqueConnection);
    setCurrentIndex(insertedIndex);
    updateRibbonTabGeometry();
}

void RibbonBar::movePage(RibbonPage *page, int newIndex)
{
    movePage(pageIndex(page), newIndex);
}

void RibbonBar::movePage(int index, int newIndex)
{
    RibbonPage *movingPage = page(index);
    if (!movingPage || index == newIndex) {
        return;
    }
    const QString title = tabText(index);
    const QIcon icon = tabIcon(index);
    removeTab(index);
    const int normalizedIndex = newIndex < 0 ? count() : qMin(newIndex, count());
    insertTab(normalizedIndex, movingPage, icon, title);
    setCurrentIndex(normalizedIndex);
}

void RibbonBar::removePage(RibbonPage *page)
{
    if (!page) {
        return;
    }
    const int index = indexOf(page);
    if (index >= 0) {
        removeTab(index);
    }
    page->deleteLater();
}

void RibbonBar::removePage(int index)
{
    removePage(page(index));
}

void RibbonBar::detachPage(RibbonPage *page)
{
    if (!page) {
        return;
    }
    const int index = indexOf(page);
    if (index >= 0) {
        removeTab(index);
    }
    page->setParent(nullptr);
}

void RibbonBar::detachPage(int index)
{
    detachPage(page(index));
}

void RibbonBar::clearPages()
{
    while (count() > 0) {
        removePage(0);
    }
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

int RibbonBar::pageCount() const
{
    return count();
}

int RibbonBar::currentPageIndex() const
{
    return currentIndex();
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

RibbonPageList RibbonBar::pages() const
{
    RibbonPageList list;
    for (int index = 0; index < count(); ++index) {
        if (RibbonPage *ribbonPage = page(index)) {
            list.append(ribbonPage);
        }
    }
    return list;
}

int RibbonBar::pageIndex(RibbonPage *page) const
{
    return indexOf(page);
}

bool RibbonBar::isKeyTipsShowing() const
{
    return m_keyTipsShowing;
}

bool RibbonBar::keyTipsEnabled() const
{
    return m_keyTipsEnabled;
}

void RibbonBar::setKeyTipsEnable(bool enable)
{
    if (m_keyTipsEnabled == enable) {
        return;
    }
    m_keyTipsEnabled = enable;
    m_keyTipsShowing = enable && m_keyTipsShowing;
    emit keyTipsShowed(m_keyTipsShowing);
}

bool RibbonBar::isKeyTipsComplement() const
{
    return m_keyTipsComplement;
}

void RibbonBar::setKeyTipsComplement(bool complement)
{
    m_keyTipsComplement = complement;
}

void RibbonBar::setKeyTip(QAction *action, const QString &keyTip)
{
    if (action) {
        m_keyTipHash[action] = keyTip;
    }
}

bool RibbonBar::isMovableTabs() const
{
    return tabBar()->isMovable();
}

void RibbonBar::setMovableTabs(bool movable)
{
    tabBar()->setMovable(movable);
}

Qt::TextElideMode RibbonBar::tabsElideMode() const
{
    return tabBar()->elideMode();
}

void RibbonBar::setTabsElideMode(Qt::TextElideMode mode)
{
    tabBar()->setElideMode(mode);
}

void RibbonBar::setLogoPixmap(const QPixmap &pixmap,
                              Qt::AlignmentFlag alignment)
{
    m_logoPixmap = pixmap;
    m_logoAlignment = alignment;
    update();
}

QPixmap RibbonBar::logoPixmap() const
{
    return m_logoPixmap;
}

void RibbonBar::setTitleBackground(const QPixmap &pixmap)
{
    m_titleBackground = pixmap;
    update();
}

const QPixmap &RibbonBar::titleBackground() const
{
    return m_titleBackground;
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
    if (!action) {
        const QList<QAction *> actionList = matchedSearchActions(strText);
        if (!actionList.isEmpty()) {
            action = actionList.first();
        }
    }

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
RibbonQuickAccessBar *RibbonBar::quickAccessBar() const
{
    return m_quickAccessBar;
}

RibbonProgressBar *RibbonBar::progressBar() const
{
    return m_progressBar;
}

RibbonSearchBar *RibbonBar::searchBar() const
{
    return m_searchEdit;
}

void RibbonBar::setQuickAccessBarPosition(BarPosition position)
{
    m_quickAccessBarPosition = position;
    updateRibbonDisplayState();
}

RibbonBar::BarPosition RibbonBar::quickAccessBarPosition() const
{
    return m_quickAccessBarPosition;
}

void RibbonBar::setSearchBarAppearance(SearchBarAppearance appearance)
{
    m_searchBarAppearance = appearance;
    m_searchVisibleExplicitlySet = true;
    m_searchEdit->setCompact(appearance == SearchBarCompact);
    m_searchEdit->setVisible(appearance != SearchBarHidden);
    if (appearance == SearchBarHidden) {
        hideSearchPopup();
    }

    updateSearchGeometry();
    updateQuickAccessGeometry();
}

RibbonBar::SearchBarAppearance RibbonBar::searchBarAppearance() const
{
    return m_searchBarAppearance;
}

void RibbonBar::setTabBarPosition(BarPosition position)
{
    m_tabBarPosition = position;
    setTabPosition(position == TopPosition ? QTabWidget::North
                                           : QTabWidget::South);
}

RibbonBar::BarPosition RibbonBar::tabBarPosition() const
{
    return m_tabBarPosition;
}

void RibbonBar::setRibbonStyle(RibbonStyle style)
{
    if (m_ribbonStyle == style) {
        return;
    }

    m_ribbonStyle = style;
    updateStyleSheet();
    update();
    emit ribbonStyleChanged(m_ribbonStyle);
}

RibbonBar::RibbonStyle RibbonBar::ribbonStyle() const
{
    return m_ribbonStyle;
}

QString RibbonBar::ribbonStyleName(RibbonStyle style)
{
    switch (style) {
    case Office2019Colorful:
        return QStringLiteral("Office 2019 Colorful");
    case Microsoft365Light:
        return QStringLiteral("Microsoft 365 Light");
    case Microsoft365Dark:
        return QStringLiteral("Microsoft 365 Dark");
    case Office2016Blue:
    default:
        return QStringLiteral("Office 2016 Blue");
    }
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
/// \brief RibbonBar::addTitleButton
/// Creates a caption button and returns its action.
/// \param icon Icon shown by the title button.
/// \param strText Text and tooltip source for the button.
/// \return Newly created action owned by the Ribbon bar.
///
QAction *RibbonBar::addTitleButton(const QIcon &icon, const QString &strText)
{
    QAction *action = new QAction(icon, strText, this);
    action->setToolTip(strText);
    m_titleButtonBar->addAction(action);
    m_titleButtonBar->show();

    connect(action, &QAction::changed, this, [this]() {
        updateTitleButtonGeometry();
        updateStyleSheet();
    });

    updateTitleButtonGeometry();
    updateQuickAccessGeometry();
    updateStyleSheet();
    return action;
}

///
/// \brief RibbonBar::clearQuickAccessActions
/// Removes all actions from the quick access toolbar.
///
void RibbonBar::clearQuickAccessActions()
{
    m_quickAccessBar->clear();
    m_quickAccessBar->addAction(m_quickAccessBar->actionCustomizeButton());
    m_quickAccessBar->hide();
    updateQuickAccessGeometry();
    updateStyleSheet();
}

void RibbonBar::removeTitleButton(QAction *action)
{
    if (!action) {
        return;
    }
    m_titleButtonBar->removeAction(action);
    action->deleteLater();
    if (m_titleButtonBar->actions().isEmpty()) {
        m_titleButtonBar->hide();
    }
    updateTitleButtonGeometry();
    updateQuickAccessGeometry();
}

///
/// \brief RibbonBar::setCurrentPageIndex
/// Selects the active Ribbon page by index.
/// \param index Zero-based tab index.
///
void RibbonBar::setCurrentPageIndex(int index)
{
    bool changed = true;
    emit pageAboutToBeChanged(page(index), changed);
    if (!changed) {
        return;
    }
    setCurrentIndex(index);
}

int RibbonBar::rowItemHeight() const
{
    return ribbonRowItemHeight(this);
}

int RibbonBar::rowItemCount() const
{
    return ribbonRowItemCount;
}

///
/// \brief RibbonBar::setRibbonMinimized
/// Collapses or expands the command pages while keeping title and tabs visible.
/// \param minimized true to collapse the command area.
///
void RibbonBar::setRibbonMinimized(bool minimized)
{
    if (!m_minimizationEnabled && minimized) {
        return;
    }
    if (m_ribbonMinimized == minimized) {
        if (minimized) {
            hideTemporaryRibbon();
        }
        return;
    }

    const bool temporaryWasExpanded = m_ribbonTemporaryExpanded;
    m_ribbonMinimized = minimized;
    m_ribbonTemporaryExpanded = false;
    updateRibbonDisplayState();
    emit ribbonMinimizedChanged(m_ribbonMinimized);
    emit minimizationChanged(m_ribbonMinimized);
    if (temporaryWasExpanded) {
        emit ribbonTemporaryExpandedChanged(false);
    }
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

bool RibbonBar::isRibbonTemporaryExpanded() const
{
    return m_ribbonTemporaryExpanded;
}

void RibbonBar::minimize()
{
    setRibbonMinimized(true);
}

bool RibbonBar::isMinimized() const
{
    return isRibbonMinimized();
}

void RibbonBar::setMinimized(bool minimized)
{
    setRibbonMinimized(minimized);
}

void RibbonBar::maximize()
{
    setRibbonMinimized(false);
}

bool RibbonBar::isMaximized() const
{
    return !isRibbonMinimized();
}

void RibbonBar::setMaximized(bool maximized)
{
    setRibbonMinimized(!maximized);
}

void RibbonBar::setMinimizationEnabled(bool enabled)
{
    m_minimizationEnabled = enabled;
    if (!enabled) {
        setRibbonMinimized(false);
    }
}

bool RibbonBar::isMinimizationEnabled() const
{
    return m_minimizationEnabled;
}

QAction *RibbonBar::simplifiedAction() const
{
    return m_simplifiedAction;
}

bool RibbonBar::simplifiedMode() const
{
    return m_simplifiedMode;
}

void RibbonBar::setSimplifiedMode(bool enabled)
{
    if (!m_simplifiedModeEnabled && enabled) {
        return;
    }
    if (m_simplifiedMode == enabled) {
        return;
    }
    m_simplifiedMode = enabled;
    m_simplifiedAction->setChecked(enabled);
    if (enabled) {
        setRibbonMinimized(false);
    }
    updateRibbonDisplayState();
    emit simplifiedModeChanged(enabled);
}

bool RibbonBar::simplifiedModeEnabled() const
{
    return m_simplifiedModeEnabled;
}

void RibbonBar::setSimplifiedModeEnabled(bool enabled)
{
    m_simplifiedModeEnabled = enabled;
    m_simplifiedAction->setEnabled(enabled);
    if (!enabled) {
        setSimplifiedMode(false);
    }
}

Qt::LayoutDirection RibbonBar::expandDirection() const
{
    return m_expandDirection;
}

void RibbonBar::setExpandDirection(Qt::LayoutDirection direction)
{
    m_expandDirection = direction;
    setLayoutDirection(direction);
}

RibbonCustomizeManager *RibbonBar::customizeManager()
{
    if (!m_customizeManager) {
        m_customizeManager = new RibbonCustomizeManager(this);
        m_customizeManager->addToolBar(m_quickAccessBar);
    }
    return m_customizeManager;
}

RibbonCustomizeDialog *RibbonBar::customizeDialog()
{
    if (!m_customizeDialog) {
        m_customizeDialog = new RibbonCustomizeDialog(this);
        RibbonQuickAccessBarCustomizePage *quickAccessPage =
            new RibbonQuickAccessBarCustomizePage(this);
        quickAccessPage->setWindowTitle(
            QString::fromLatin1(QtnRibbonCustomizeQuickAccessToolBarString));
        RibbonBarCustomizePage *ribbonPage =
            new RibbonBarCustomizePage(this);
        ribbonPage->setWindowTitle(
            QString::fromLatin1(QtnRibbonCustomizeActionString));
        m_customizeDialog->addPage(quickAccessPage);
        m_customizeDialog->addPage(ribbonPage);
    }
    return m_customizeDialog;
}

void RibbonBar::showCustomizeDialog()
{
    customizeDialog()->show();
    customizeDialog()->raise();
    customizeDialog()->activateWindow();
}

QMenu *RibbonBar::addMenu(const QString &strText)
{
    QMenu *menu = new QMenu(strText, this);
    m_ownedMenuList.append(menu);
    return menu;
}

QAction *RibbonBar::addAction(const QIcon &icon,
                              const QString &strText,
                              Qt::ToolButtonStyle buttonStyle,
                              QMenu *menu)
{
    QAction *action = new QAction(icon, strText, this);
    if (menu) {
        action->setMenu(menu);
    }
    addAction(action, buttonStyle);
    return action;
}

QAction *RibbonBar::addAction(QAction *action, Qt::ToolButtonStyle buttonStyle)
{
    Q_UNUSED(buttonStyle)
    if (!action) {
        return nullptr;
    }
    addQuickAccessAction(action);
    return action;
}

QAction *RibbonBar::addSystemButton(const QString &strText)
{
    return addSystemButton(QIcon(), strText);
}

QAction *RibbonBar::addSystemButton(const QIcon &icon, const QString &strText)
{
    if (!m_systemButton) {
        m_systemButton = new RibbonSystemButton(this);
        m_systemButton->setObjectName(QStringLiteral("lqRibbonSystemButton"));
        m_systemButton->hide();
    }
    QAction *action = new QAction(icon, strText, this);
    m_systemButton->setDefaultAction(action);
    m_systemButton->show();
    updateQuickAccessGeometry();
    return action;
}

RibbonSystemButton *RibbonBar::systemButton() const
{
    return m_systemButton;
}

void RibbonBar::setAcrylicEnabled(bool enabled)
{
    m_acrylicEnabled = enabled;
    update();
}

bool RibbonBar::isAcrylicEnabled() const
{
    return m_acrylicEnabled;
}

void RibbonBar::setContextualTabsVisible(bool visible)
{
    m_contextualTabsVisible = visible;
    update();
}

bool RibbonBar::isContextualTabsVisible() const
{
    return m_contextualTabsVisible;
}

void RibbonBar::setTitleGroupsVisible(bool visible)
{
    m_titleGroupsVisible = visible;
    update();
}

bool RibbonBar::isTitleGroupsVisible() const
{
    return m_titleGroupsVisible;
}

bool RibbonBar::isBackstageVisible() const
{
    return m_systemButton && m_systemButton->backstage()
        && m_systemButton->backstage()->isVisible();
}

void RibbonBar::updateLayout()
{
    updateRibbonTabGeometry();
    updateWindowControlGeometry();
    updateSearchGeometry();
    updateTitleButtonGeometry();
    updateQuickAccessGeometry();
    updateGeometry();
}

void RibbonBar::beginUpdate()
{
    ++m_updateLockCount;
    setUpdatesEnabled(false);
}

void RibbonBar::endUpdate()
{
    if (m_updateLockCount > 0) {
        --m_updateLockCount;
    }
    if (m_updateLockCount == 0) {
        setUpdatesEnabled(true);
        updateLayout();
    }
}

bool RibbonBar::loadTranslation(const QString &strCountry)
{
    Q_UNUSED(strCountry)
    return true;
}

QString RibbonBar::tr_compatible(const char *text, const char *context)
{
    Q_UNUSED(context)
    return QString::fromUtf8(text);
}

///
/// \brief RibbonBar::setFrameThemeEnabled
/// Enables or disables themed frame painting and controls.
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
    if (!m_searchVisibleExplicitlySet) {
        m_searchEdit->setVisible(enabled);
        if (!enabled) {
            hideSearchPopup();
        }
    }

    updateWindowControlVisibility();
    updateRibbonTabGeometry();
    updateWindowControlGeometry();
    updateSearchGeometry();
    updateTitleButtonGeometry();
    updateQuickAccessGeometry();
    updateStyleSheet();
    emit frameThemeChanged(enabled);
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
        updateTitleButtonGeometry();
        updateQuickAccessGeometry();
        break;
    case QEvent::LanguageChange:
    case QEvent::LocaleChange:
        updateLocalizedText();
        updateRibbonMetrics();
        updateRibbonTabGeometry();
        updateWindowControlGeometry();
        updateSearchGeometry();
        updateTitleButtonGeometry();
        updateQuickAccessGeometry();
        break;
    case QEvent::LayoutRequest:
    case QEvent::PolishRequest:
    case QEvent::Show:
        updateRibbonTabGeometry();
        updateWindowControlGeometry();
        updateSearchGeometry();
        updateTitleButtonGeometry();
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
    if (object == tabBar()
        && event->type() == QEvent::MouseButtonDblClick) {
        QMouseEvent *mouseEvent = static_cast<QMouseEvent *>(event);
        if (mouseEvent->button() == Qt::LeftButton
            && tabBar()->tabAt(mouseEvent->pos()) >= 0) {
            m_ignoreNextTabRelease = true;
            setRibbonMinimized(!m_ribbonMinimized);
            return true;
        }
    }

    if (object == tabBar()
        && event->type() == QEvent::MouseButtonRelease) {
        QMouseEvent *mouseEvent = static_cast<QMouseEvent *>(event);
        if (m_ignoreNextTabRelease) {
            m_ignoreNextTabRelease = false;
        } else if (mouseEvent->button() == Qt::LeftButton
            && m_ribbonMinimized
            && tabBar()->tabAt(mouseEvent->pos()) >= 0) {
            showTemporaryRibbon();
        }
    }

    if (m_ribbonTemporaryExpanded) {
        switch (event->type()) {
        case QEvent::MouseButtonRelease:
            if (!isRibbonRelatedObject(object)) {
                scheduleHideTemporaryRibbon();
            }
            break;
        case QEvent::FocusIn:
            if (object && !isRibbonRelatedObject(object)) {
                scheduleHideTemporaryRibbon();
            }
            break;
        case QEvent::WindowDeactivate:
        case QEvent::ApplicationDeactivate:
            hideTemporaryRibbon();
            break;
        default:
            break;
        }
    }

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

    if (object == m_searchEdit && event->type() == QEvent::FocusIn) {
        updateSearchPopup();
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
/// Paints the tab widget and themed caption area when enabled.
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

    const RibbonStylePalette palette = ribbonStylePalette(m_ribbonStyle);
    QPainter painter(this);
    const int titleHeight = ribbonCaptionHeight + ribbonTabHeight;
    painter.fillRect(0,
                     0,
                     width(),
                     titleHeight,
                     QColor(palette.captionBackground));

    QWidget *topLevelWidget = window();
    if (!topLevelWidget) {
        return;
    }

    const QIcon windowIcon = topLevelWidget->windowIcon();
    const bool captionTitleVisible = !m_searchEdit->isVisible();
    const int iconLeft = 7;
    const int iconSize = 16;
    const int titleIconGap = 20;
    const int iconTop = ribbonCaptionTopMargin
        + ((ribbonWindowButtonHeight - iconSize) / 2);
    if (captionTitleVisible && !windowIcon.isNull()) {
        windowIcon.paint(&painter, QRect(iconLeft, iconTop, iconSize, iconSize));
    }

    const int titleLeft = windowIcon.isNull()
        ? 12
        : iconLeft + iconSize + titleIconGap;
    const int titleRight = m_searchEdit->isVisible()
        ? m_searchEdit->x() - 12
        : width() - windowControlWidth() - 12;
    const int titleWidth = qMax(0, titleRight - titleLeft);
    if (captionTitleVisible && titleWidth > 0) {
        painter.setPen(QColor(palette.captionText));
        painter.drawText(QRect(titleLeft,
                               ribbonCaptionTopMargin,
                               titleWidth,
                               ribbonWindowButtonHeight),
                         Qt::AlignLeft | Qt::AlignVCenter,
                         fontMetrics().elidedText(topLevelWidget->windowTitle(),
                                                  Qt::ElideRight,
                                                  titleWidth));
    }
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
    updateTitleButtonGeometry();
    updateQuickAccessGeometry();
    updateStyleSheet();
}

void RibbonBar::contextMenuEvent(QContextMenuEvent *event)
{
    QMenu menu(this);
    QAction *minimizeAction = menu.addAction(
        QString::fromLatin1(QtnRibbonMinimizeActionString));
    minimizeAction->setCheckable(true);
    minimizeAction->setChecked(isRibbonMinimized());
    connect(minimizeAction, &QAction::toggled,
            this, &RibbonBar::setRibbonMinimized);
    menu.addAction(m_simplifiedAction);
    emit showRibbonContextMenu(&menu, event);
    if (!menu.isEmpty()) {
        menu.exec(event->globalPos());
    }
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
    const int availableTabWidth = width();
    const int tabWidth = qMin(availableTabWidth,
                              ribbonTabBar->sizeHint().width());
    ribbonTabBar->setGeometry(0, titleHeight, tabWidth, tabHeight);
    ribbonTabBar->raise();

    QStackedWidget *stackedWidget = findChild<QStackedWidget *>();
    if (!stackedWidget) {
        return;
    }

    const bool commandAreaVisible = isRibbonCommandAreaVisible();
    const int quickAccessReserve =
        commandAreaVisible
            && m_quickAccessBarPosition == BottomPosition
            && !m_quickAccessBar->isHidden()
        ? ribbonQuickAccessBelowHeight
        : 0;
    const int stackHeight = commandAreaVisible
        ? qMax(0, height() - stackTop - quickAccessReserve)
        : 0;
    stackedWidget->setGeometry(0, stackTop, width(), stackHeight);
    stackedWidget->setVisible(commandAreaVisible);
}

///
/// \brief RibbonBar::updateSearchGeometry
/// Centers the title-bar search box while avoiding the right-side controls.
///
void RibbonBar::updateSearchGeometry()
{
    const bool compactSearch =
        m_searchBarAppearance == RibbonBar::SearchBarCompact;
    const int preferredSearchWidth = compactSearch ? 36 : 524;
    const int minimumUsefulSearchWidth = compactSearch ? 36 : 120;
    const int searchHeight = 22;
    const int topMargin = ribbonCaptionTopMargin
        + ((ribbonWindowButtonHeight - searchHeight) / 2);
    const int controlWidth = windowControlWidth();
    const int titleButtonReserve = m_titleButtonBar->isVisible()
        ? m_titleButtonBar->sizeHint().width() + 48
        : 0;
    const int rightLimit = controlWidth > 0
        ? width() - controlWidth - titleButtonReserve - 24
        : width() - 10;
    const int availableWidth = qMax(0, rightLimit);
    int searchWidth = qMin(preferredSearchWidth, availableWidth);
    int x = qMax(0, (width() - searchWidth) / 2);

    if (x + searchWidth > rightLimit) {
        const int centerX = width() / 2;
        const int centeredWidth =
            qMin(preferredSearchWidth, qMax(0, rightLimit - centerX) * 2);
        if (centeredWidth >= minimumUsefulSearchWidth) {
            searchWidth = centeredWidth;
            x = qMax(0, (width() - searchWidth) / 2);
        } else {
            x = qMin(x, qMax(0, rightLimit - searchWidth));
        }
    }

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
    const int rightMargin = 12;
    const int barHeight = 24;
    if (m_quickAccessBarPosition == BottomPosition
        && isRibbonCommandAreaVisible()) {
        const int leftMargin = 8;
        const int rightLimit =
            width() - ribbonCollapseButtonWidth - rightMargin;
        const int maxWidth = qMax(0, rightLimit - leftMargin);
        const int barWidth =
            qMin(m_quickAccessBar->sizeHint().width(), maxWidth);
        const int topMargin = qMax(
            0,
            height() - ribbonQuickAccessBelowHeight
                + ((ribbonQuickAccessBelowHeight - barHeight) / 2));
        m_quickAccessBar->setGeometry(leftMargin,
                                      topMargin,
                                      barWidth,
                                      barHeight);
        m_quickAccessBar->raise();
        return;
    }

    const int preferredLeftMargin = 340;
    const int itemGap = 8;
    const int controlWidth = windowControlWidth();
    const int topMargin = ribbonCaptionTopMargin
        + ((ribbonWindowButtonHeight - barHeight) / 2);
    const int rightLimit = m_searchEdit->isVisible()
        ? (m_titleButtonBar->isVisible()
               ? m_titleButtonBar->x() - itemGap
               : m_searchEdit->x() - itemGap)
        : width() - controlWidth - rightMargin;
    const int searchRight = m_searchEdit->isVisible()
        ? m_searchEdit->geometry().right() + 1 + itemGap
        : 0;
    const int leftLimit = qMax(preferredLeftMargin, searchRight);
    const int leftMargin = qMin(leftLimit, qMax(0, rightLimit));
    const int maxWidth = qMax(0, rightLimit - leftMargin);
    const int barWidth = qMin(m_quickAccessBar->sizeHint().width(), maxWidth);

    if (m_systemButton && m_systemButton->isVisible()) {
        const int systemWidth = qMax(64, m_systemButton->sizeHint().width());
        m_systemButton->setGeometry(6, topMargin, systemWidth, barHeight);
        m_systemButton->raise();
    }

    m_quickAccessBar->setGeometry(leftMargin, topMargin, barWidth, barHeight);
    m_quickAccessBar->raise();
}

///
/// \brief RibbonBar::updateTitleButtonGeometry
/// Places icon-only title buttons near the right caption controls.
///
void RibbonBar::updateTitleButtonGeometry()
{
    const int controlGap = 28;
    const int controlWidth = windowControlWidth();
    const int barHeight = 24;
    const int topMargin = ribbonCaptionTopMargin
        + ((ribbonWindowButtonHeight - barHeight) / 2);
    const int rightLimit = width() - controlWidth - controlGap;
    const int maxWidth = qMax(0, rightLimit);
    const int barWidth = qMin(m_titleButtonBar->sizeHint().width(), maxWidth);
    const int leftMargin = qMax(0, rightLimit - barWidth);

    m_titleButtonBar->setGeometry(leftMargin, topMargin, barWidth, barHeight);
    m_titleButtonBar->raise();
}

///
/// \brief RibbonBar::updateRibbonMetrics
/// Applies the calculated fixed Ribbon height.
///
void RibbonBar::updateRibbonMetrics()
{
    const int barHeight = isRibbonCommandAreaVisible()
        ? (m_simplifiedMode ? ribbonSimplifiedBarHeight
                            : ribbonBarHeight(this))
        : (m_frameThemeEnabled
               ? ribbonCaptionHeight + ribbonTabHeight
               : tabBar()->sizeHint().height());
    const int quickAccessReserve =
        isRibbonCommandAreaVisible()
            && m_quickAccessBarPosition == BottomPosition
            && !m_quickAccessBar->isHidden()
        ? ribbonQuickAccessBelowHeight
        : 0;
    const int adjustedBarHeight = barHeight + quickAccessReserve;
    if (height() != adjustedBarHeight
        || minimumHeight() != adjustedBarHeight) {
        setFixedHeight(adjustedBarHeight);
    }
}

void RibbonBar::updateRibbonDisplayState()
{
    updateRibbonMetrics();
    updateRibbonTabGeometry();
    updateWindowControlState();
    updateWindowControlGeometry();
    updateSearchGeometry();
    updateTitleButtonGeometry();
    updateQuickAccessGeometry();
    updateGeometry();
}

bool RibbonBar::isRibbonCommandAreaVisible() const
{
    return !m_ribbonMinimized || m_ribbonTemporaryExpanded;
}

void RibbonBar::showTemporaryRibbon()
{
    if (!m_ribbonMinimized
        || m_ribbonTemporaryExpanded
        || !m_minimizationEnabled) {
        return;
    }

    m_ribbonTemporaryExpanded = true;
    updateRibbonDisplayState();
    emit ribbonTemporaryExpandedChanged(true);
}

void RibbonBar::hideTemporaryRibbon()
{
    if (!m_ribbonTemporaryExpanded) {
        return;
    }

    m_ribbonTemporaryExpanded = false;
    updateRibbonDisplayState();
    emit ribbonTemporaryExpandedChanged(false);
}

void RibbonBar::scheduleHideTemporaryRibbon()
{
    if (!m_ribbonTemporaryExpanded) {
        return;
    }

    QTimer::singleShot(0, this, [this]() {
        hideTemporaryRibbon();
    });
}

bool RibbonBar::isRibbonRelatedObject(QObject *object) const
{
    for (QObject *current = object; current; current = current->parent()) {
        if (current == this) {
            return true;
        }
    }

    QWidget *widget = qobject_cast<QWidget *>(object);
    while (widget) {
        if (widget == this) {
            return true;
        }
        widget = widget->parentWidget();
    }

    return false;
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
    int x = qMax(topLeft.x(), controlRight - (buttonWidth * 3));
    const int top = topLeft.y() + ribbonCaptionTopMargin;

    m_minimizeButton->setGeometry(x, top, buttonWidth, buttonHeight);
    x += buttonWidth;
    m_maximizeButton->setGeometry(x, top, buttonWidth, buttonHeight);
    x += buttonWidth;
    m_closeButton->setGeometry(x, top, buttonWidth, buttonHeight);
    const int collapseTop = topLeft.y() + height()
        - ribbonCollapseButtonHeight - 2;
    m_collapseButton->setGeometry(qMax(topLeft.x(),
                                      controlRight - ribbonCollapseButtonWidth),
                                  collapseTop,
                                  ribbonCollapseButtonWidth,
                                  ribbonCollapseButtonHeight);

    m_minimizeButton->setVisible(m_frameThemeEnabled);
    m_maximizeButton->setVisible(m_frameThemeEnabled);
    m_closeButton->setVisible(m_frameThemeEnabled);
    m_collapseButton->setVisible(m_frameThemeEnabled && !m_ribbonMinimized);
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
    m_collapseButton->setVisible(m_frameThemeEnabled && !m_ribbonMinimized);
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

    if (!actionList.isEmpty() && strText.isEmpty()) {
        QList<QAction *> recentActionList;
        for (const QPointer<QAction> &action : m_recentSearchActionList) {
            QAction *recentAction = action.data();
            if (actionList.contains(recentAction)
                && !recentActionList.contains(recentAction)) {
                recentActionList.append(recentAction);
            }
        }

        QList<QAction *> defaultActionList = actionList;
        for (QAction *action : recentActionList) {
            defaultActionList.removeAll(action);
        }

        if (!recentActionList.isEmpty()) {
            m_searchPopupModel->appendRow(
                createSearchHeaderItem(ribbonText("Recently Used")));
            for (QAction *action : recentActionList) {
                m_searchPopupModel->appendRow(createSearchActionItem(action));
            }
        }

        if (!defaultActionList.isEmpty()) {
            m_searchPopupModel->appendRow(createSearchHeaderItem(ribbonText("Actions")));
            for (QAction *action : defaultActionList) {
                m_searchPopupModel->appendRow(createSearchActionItem(action));
            }
        }
    } else if (!actionList.isEmpty()) {
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

    const int desiredPopupHeight = popupHeight;
    QPoint popupTopLeft = m_searchEdit->mapToGlobal(
        QPoint(0, m_searchEdit->height()));
    const QPoint searchTopLeft = m_searchEdit->mapToGlobal(QPoint(0, 0));
    const int popupWidth = m_searchEdit->width();

    if (QScreen *screen = QApplication::screenAt(popupTopLeft)) {
        const QRect screenRect = screen->availableGeometry();
        const int belowHeight = qMax(0,
                                     screenRect.bottom() - popupTopLeft.y() + 1
                                     - ribbonSearchPopupScreenMargin);
        const int aboveHeight = qMax(0,
                                     searchTopLeft.y() - screenRect.top()
                                     - ribbonSearchPopupScreenMargin);
        const bool showAbove = belowHeight < desiredPopupHeight
            && aboveHeight > belowHeight;
        const int availableHeight = showAbove ? aboveHeight : belowHeight;
        if (availableHeight > 0) {
            popupHeight = qMin(desiredPopupHeight, availableHeight);
        }
        if (showAbove) {
            popupTopLeft = QPoint(searchTopLeft.x(),
                                  searchTopLeft.y() - popupHeight);
        }
    }

    const bool needsScrollBar = desiredPopupHeight > popupHeight;
    m_searchPopupView->setVerticalScrollBarPolicy(needsScrollBar
                                                  ? Qt::ScrollBarAsNeeded
                                                  : Qt::ScrollBarAlwaysOff);
    m_searchPopupView->setGeometry(popupTopLeft.x(),
                                   popupTopLeft.y(),
                                   popupWidth,
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
        const int maxActionCount = qMax(1, m_searchCompleter->maxVisibleItems());
        auto appendDefaultAction = [&](QAction *action) {
            if (!actionList.contains(action) && isSearchableAction(action)) {
                actionList.append(action);
            }
        };

        for (const QPointer<QAction> &action : m_recentSearchActionList) {
            appendDefaultAction(action.data());
            if (actionList.count() >= maxActionCount) {
                return actionList;
            }
        }

        for (const QString &strSuggestion : m_searchSuggestionList) {
            appendDefaultAction(searchAction(strSuggestion));
            if (actionList.count() >= maxActionCount) {
                return actionList;
            }
        }

        for (const SearchCommand &command : m_searchCommandList) {
            appendDefaultAction(command.action.data());
            if (actionList.count() >= maxActionCount) {
                return actionList;
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
        appendSearchActionIfMatches(actionList, action, strNormalizedText);
        appendMenuSearchActions(actionList, button->menu(), strNormalizedText);
        if (action) {
            appendMenuSearchActions(actionList, action->menu(), strNormalizedText);
        }
    }

    while (actionList.count() > 40) {
        actionList.removeLast();
    }

    return actionList;
}

///
/// \brief RibbonBar::isSearchableAction
/// Returns whether an action should appear in search results.
/// \param action Action to test.
/// \return true when the action is a visible command with display text.
///
bool RibbonBar::isSearchableAction(QAction *action) const
{
    if (!action || action->isSeparator() || !action->isVisible()) {
        return false;
    }

    return !searchActionText(action).isEmpty();
}

///
/// \brief RibbonBar::searchActionMatches
/// Tests whether one visible command matches normalized search text.
/// \param action Action to test.
/// \param strNormalizedText Already normalized search text.
/// \return true when current display text contains the query.
///
bool RibbonBar::searchActionMatches(QAction *action, const QString &strNormalizedText) const
{
    if (!isSearchableAction(action)) {
        return false;
    }

    const QString strActionText = searchActionText(action);
    return normalizedSearchText(strActionText).contains(strNormalizedText);
}

///
/// \brief RibbonBar::appendSearchActionIfMatches
/// Appends a matching action once.
/// \param actionList Destination result list.
/// \param action Candidate action.
/// \param strNormalizedText Already normalized search text.
///
void RibbonBar::appendSearchActionIfMatches(QList<QAction *> &actionList,
                                            QAction *action,
                                            const QString &strNormalizedText) const
{
    if (!actionList.contains(action) && searchActionMatches(action, strNormalizedText)) {
        actionList.append(action);
    }
}

///
/// \brief RibbonBar::appendMenuSearchActions
/// Recursively appends matching actions from a menu and its submenus.
/// \param actionList Destination result list.
/// \param menu Menu to scan.
/// \param strNormalizedText Already normalized search text.
///
void RibbonBar::appendMenuSearchActions(QList<QAction *> &actionList,
                                        QMenu *menu,
                                        const QString &strNormalizedText) const
{
    if (!menu) {
        return;
    }

    const QList<QAction *> menuActions = menu->actions();
    for (QAction *action : menuActions) {
        if (!action || action->isSeparator()) {
            continue;
        }

        appendSearchActionIfMatches(actionList, action, strNormalizedText);
        appendMenuSearchActions(actionList, action->menu(), strNormalizedText);
    }
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
    updateSearchPopup();
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
    const RibbonStylePalette palette = ribbonStylePalette(m_ribbonStyle);
    setStyleSheet(buildRibbonStyleSheet(palette));
    static_cast<RibbonWindowButton *>(m_minimizeButton)
        ->setThemeColors(QColor(palette.captionHover),
                         QColor(palette.captionPressed),
                         QColor(palette.closeHover),
                         QColor(palette.closePressed),
                         QColor(palette.captionText));
    static_cast<RibbonWindowButton *>(m_maximizeButton)
        ->setThemeColors(QColor(palette.captionHover),
                         QColor(palette.captionPressed),
                         QColor(palette.closeHover),
                         QColor(palette.closePressed),
                         QColor(palette.captionText));
    static_cast<RibbonWindowButton *>(m_closeButton)
        ->setThemeColors(QColor(palette.captionHover),
                         QColor(palette.captionPressed),
                         QColor(palette.closeHover),
                         QColor(palette.closePressed),
                         QColor(palette.captionText));
    static_cast<RibbonCollapseButton *>(m_collapseButton)
        ->setThemeColors(QColor(palette.groupHover),
                         QColor(palette.groupPressed),
                         QColor(palette.text));
}

///
/// \brief RibbonMainWindow::RibbonMainWindow
/// Creates a main window with a top Ribbon bar and central content area.
/// \param parent Parent widget.
///
RibbonMainWindow::RibbonMainWindow(QWidget *parent, Qt::WindowFlags flags)
    : QMainWindow(parent, flags)
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
    updateNativeContentMargins();
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

void RibbonMainWindow::setRibbonBar(RibbonBar *ribbonBar)
{
    if (!ribbonBar || ribbonBar == m_ribbonBar) {
        return;
    }
    const int oldIndex = m_rootLayout->indexOf(m_ribbonBar);
    if (m_ribbonBar) {
        m_rootLayout->removeWidget(m_ribbonBar);
        m_ribbonBar->deleteLater();
    }
    m_ribbonBar = ribbonBar;
    m_ribbonBar->setParent(m_rootWidget);
    m_rootLayout->insertWidget(qMax(0, oldIndex), m_ribbonBar);
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

void RibbonMainWindow::setCentralWidget(QStyle *style)
{
    QWidget *widget = new QWidget;
    if (style) {
        widget->setStyle(style);
    }
    setCentralWidget(widget);
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
    updateNativeContentMargins();

    if (wasVisible) {
        show();
        updateNativeWindowStyle();
        updateNativeContentMargins();
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
/// Enables themed Ribbon frame painting on the embedded Ribbon bar.
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

void RibbonMainWindow::setRibbonStyle(RibbonBar::RibbonStyle style)
{
    m_ribbonBar->setRibbonStyle(style);
}

RibbonBar::RibbonStyle RibbonMainWindow::ribbonStyle() const
{
    return m_ribbonBar->ribbonStyle();
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
    if (object == this
        && (event->type() == QEvent::Show
            || event->type() == QEvent::Resize
            || event->type() == QEvent::WindowStateChange)) {
        updateNativeContentMargins();
    }

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
/// Applies Ribbon styling and event filtering to an MDI area.
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
#if QT_VERSION >= QT_VERSION_CHECK(6, 0, 0)
bool RibbonMainWindow::nativeEvent(const QByteArray &eventType, void *message, qintptr *result)
#else
bool RibbonMainWindow::nativeEvent(const QByteArray &eventType, void *message, long *result)
#endif
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

    QToolBar *titleButtonBar = m_ribbonBar->findChild<QToolBar *>(
        QStringLiteral("lqRibbonTitleButtonBar"));
    if (titleButtonBar && titleButtonBar->isVisible()
        && titleButtonBar->geometry().contains(ribbonPoint)) {
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
/// \brief RibbonMainWindow::updateNativeContentMargins
/// Keeps custom-framed maximized content away from screen edges.
///
void RibbonMainWindow::updateNativeContentMargins()
{
    const bool needsSafeMargin = m_nativeFrameEnabled
        && isMaximized()
        && !windowState().testFlag(Qt::WindowFullScreen);
    const int topMargin = needsSafeMargin ? ribbonMaximizedContentMargin : 0;
    const int bottomMargin = needsSafeMargin ? ribbonMaximizedContentMargin * 2 : 0;
    const QMargins targetMargins(0, topMargin, 0, bottomMargin);
    if (contentsMargins() == targetMargins) {
        return;
    }

    QMainWindow::setContentsMargins(targetMargins);
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
