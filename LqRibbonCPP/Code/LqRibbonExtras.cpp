#include "LqRibbon.h"

#include <QActionEvent>
#include <QApplication>
#include <QChildEvent>
#include <QColorDialog>
#include <QDialogButtonBox>
#include <QGuiApplication>
#include <QHBoxLayout>
#include <QIODevice>
#include <QKeyEvent>
#include <QLabel>
#include <QListWidget>
#include <QMouseEvent>
#include <QPainter>
#include <QPainterPath>
#include <QScreen>
#include <QStackedWidget>
#include <QStyle>
#include <QStyleOption>
#include <QTabBar>
#include <QTimer>
#include <QVBoxLayout>
#include <QWidgetAction>

namespace {

const int backstageMenuWidth = 190;
const int backstageButtonHeight = 36;
const int recentFileRowHeight = 26;

QColor contextColorToColor(LqRibbon::ContextColor color)
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

QAction *actionAtIndex(const QList<QAction *> &actions, int index)
{
    if (index < 0 || index >= actions.count()) {
        return nullptr;
    }
    return actions.at(index);
}

QString cleanActionText(const QString &text)
{
    QString result = text;
    result.remove(QLatin1Char('&'));
    return result.trimmed();
}

} // namespace

namespace LqRibbon {

const char *QtnRibbonCustomizeQuickAccessToolBarDotString =
    "Customize Quick Access Toolbar...";
const char *QtnRibbonCustomizeQuickAccessToolBarString =
    "Customize Quick Access Toolbar";
const char *QtnRibbonShowQuickAccessToolBarBelowString =
    "Show Quick Access Toolbar Below the Ribbon";
const char *QtnRibbonShowQuickAccessToolBarAboveString =
    "Show Quick Access Toolbar Above the Ribbon";
const char *QtnRibbonCustomizeActionString = "Customize the Ribbon...";
const char *QtnRibbonMinimizeActionString = "Minimize the Ribbon";
const char *QtnRibbonCustomizeDialogOptionsString = "Options";
const char *QtnRibbonSimplifiedRibbonActionString = "Simplified Ribbon";
const char *QtnRibbonSimplifiedRibbonActionToolTipsString =
    "Turn on/off Ribbon Simplified Mode";
const char *QtnRibbonRecentDocumentsString = "Recent Documents";
const char *QtnRibbonUntitledString = "Untitled";
const char *QtnRibbonSeparatorString = "Separator";
const char *QtnRibbonNewPageString = "New Page";
const char *QtnRibbonNewGroupString = "New Group";
const char *QtnRibbonAddCommandWarningString =
    "Only commands can be added to custom groups.";
const char *QtnRibbonSearchBarSearchString = "Search";
const char *QtnRibbonSearchBarGetHelpString = "Get Help";
const char *QtnRibbonSearchBarHelpString = "Help";
const char *QtnRibbonSearchBarActionsString = "Actions";
const char *QtnRibbonSearchBarSuggestedActionsString = "Suggested Actions";
const QSize QtnRibbonGalleryItemSize(72, 56);
const char *QtnRibbonGalleryItemString = "Gallery Item";

const char *getRibbonVersion()
{
    return "6.8.0-compatible";
}

RibbonButton::RibbonButton(QWidget *parent)
    : QToolButton(parent)
    , m_wordWrap(false)
    , m_largeIcon(false)
    , m_simplifiedMode(false)
{
    setAutoRaise(true);
    setToolButtonStyle(Qt::ToolButtonTextBesideIcon);
    updateIconSize();
}

RibbonButton::~RibbonButton() = default;

bool RibbonButton::wordWrap() const
{
    return m_wordWrap;
}

void RibbonButton::setWordWrap(bool on)
{
    if (m_wordWrap == on) {
        return;
    }
    m_wordWrap = on;
    updateGeometry();
    update();
}

bool RibbonButton::isLargeIcon() const
{
    return m_largeIcon;
}

void RibbonButton::setLargeIcon(bool large)
{
    if (m_largeIcon == large) {
        return;
    }
    m_largeIcon = large;
    updateIconSize();
    updateGeometry();
}

bool RibbonButton::simplifiedMode() const
{
    return m_simplifiedMode;
}

void RibbonButton::setSimplifiedMode(bool enabled)
{
    if (m_simplifiedMode == enabled) {
        return;
    }
    m_simplifiedMode = enabled;
    setToolButtonStyle(enabled ? Qt::ToolButtonIconOnly : toolButtonStyle());
    updateGeometry();
}

QSize RibbonButton::sizeHint() const
{
    QSize hint = QToolButton::sizeHint();
    if (m_largeIcon) {
        hint.setHeight(qMax(hint.height(), 72));
        hint.setWidth(qMax(hint.width(), 48));
    }
    if (m_wordWrap) {
        hint.setWidth(qMin(qMax(hint.width(), 64), 96));
    }
    return hint;
}

void RibbonButton::changed()
{
    updateIconSize();
    updateGeometry();
    update();
}

void RibbonButton::updateIconSize()
{
    setIconSize(m_largeIcon ? QSize(32, 32) : QSize(16, 16));
}

bool RibbonButton::event(QEvent *event)
{
    if (event->type() == QEvent::FontChange
        || event->type() == QEvent::StyleChange) {
        changed();
    }
    return QToolButton::event(event);
}

void RibbonButton::paintEvent(QPaintEvent *event)
{
    QToolButton::paintEvent(event);
}

void RibbonButton::actionEvent(QActionEvent *event)
{
    QToolButton::actionEvent(event);
    changed();
}

void RibbonButton::changeEvent(QEvent *event)
{
    QToolButton::changeEvent(event);
    changed();
}

RibbonQuickAccessBar::RibbonQuickAccessBar(QWidget *parent)
    : QToolBar(parent)
    , m_customizeAction(new QAction(this))
{
    setMovable(false);
    setFloatable(false);
    setIconSize(QSize(16, 16));
    setToolButtonStyle(Qt::ToolButtonIconOnly);
    m_customizeAction->setText(
        QString::fromLatin1(QtnRibbonCustomizeQuickAccessToolBarString));
    m_customizeAction->setToolTip(m_customizeAction->text());
    QToolBar::addAction(m_customizeAction);
    connect(m_customizeAction, &QAction::triggered, this, [this]() {
        QMenu menu(this);
        emit showCustomizeMenu(&menu);
        if (!menu.isEmpty()) {
            menu.exec(mapToGlobal(QPoint(0, height())));
        }
    });
}

RibbonQuickAccessBar::~RibbonQuickAccessBar() = default;

QAction *RibbonQuickAccessBar::actionCustomizeButton() const
{
    return m_customizeAction;
}

bool RibbonQuickAccessBar::isActionVisible(QAction *action) const
{
    return action && !m_hiddenActions.contains(action) && action->isVisible();
}

void RibbonQuickAccessBar::setActionVisible(QAction *action, bool visible)
{
    if (!action || action == m_customizeAction) {
        return;
    }
    if (visible) {
        m_hiddenActions.remove(action);
    } else {
        m_hiddenActions.insert(action);
    }
    action->setVisible(visible);
    if (QWidget *widget = widgetForAction(action)) {
        widget->setVisible(visible);
    }
    updateGeometry();
}

int RibbonQuickAccessBar::visibleCount() const
{
    int count = 0;
    for (QAction *action : actions()) {
        if (action != m_customizeAction && isActionVisible(action)) {
            ++count;
        }
    }
    return count;
}

void RibbonQuickAccessBar::paintContent(QPainter *painter)
{
    Q_UNUSED(painter)
}

QSize RibbonQuickAccessBar::sizeHint() const
{
    QSize hint = QToolBar::sizeHint();
    hint.setHeight(qMax(hint.height(), 24));
    return hint;
}

bool RibbonQuickAccessBar::event(QEvent *event)
{
    return QToolBar::event(event);
}

void RibbonQuickAccessBar::actionEvent(QActionEvent *event)
{
    QToolBar::actionEvent(event);
    if (event->type() == QEvent::ActionAdded
        && event->action() != m_customizeAction) {
        removeAction(m_customizeAction);
        QToolBar::addAction(m_customizeAction);
    }
}

void RibbonQuickAccessBar::paintEvent(QPaintEvent *event)
{
    QToolBar::paintEvent(event);
    QPainter painter(this);
    paintContent(&painter);
}

void RibbonQuickAccessBar::resizeEvent(QResizeEvent *event)
{
    QToolBar::resizeEvent(event);
}

RibbonSearchBar::RibbonSearchBar(RibbonBar *ribbonBar)
    : QLineEdit(ribbonBar)
    , m_ribbonBar(ribbonBar)
    , m_popupMenu(new QMenu(this))
    , m_compact(false)
    , m_helpEnabled(true)
    , m_maxSearchItemCount(8)
{
    m_icon = style()->standardIcon(QStyle::SP_FileDialogContentsView);
    setClearButtonEnabled(false);
    setPlaceholderText(QString::fromLatin1(QtnRibbonSearchBarSearchString));
}

RibbonSearchBar::~RibbonSearchBar() = default;

QSize RibbonSearchBar::minimumSizeHint() const
{
    QSize hint = QLineEdit::minimumSizeHint();
    hint.setWidth(m_compact ? 36 : 180);
    return hint;
}

void RibbonSearchBar::setCompact(bool compact)
{
    if (m_compact == compact) {
        return;
    }
    m_compact = compact;
    setTextMargins(m_compact ? 48 : 0, 0, 0, 0);
    updateGeometry();
    update();
}

bool RibbonSearchBar::isCompact() const
{
    return m_compact;
}

const QIcon &RibbonSearchBar::icon() const
{
    return m_icon;
}

bool RibbonSearchBar::isHelpEnabled() const
{
    return m_helpEnabled;
}

void RibbonSearchBar::setHelpEnabled(bool enabled)
{
    m_helpEnabled = enabled;
}

const QList<QAction *> &RibbonSearchBar::suggestedActions() const
{
    return m_suggestedActions;
}

void RibbonSearchBar::addSuggestedAction(QAction *action)
{
    if (!action || m_suggestedActions.contains(action)) {
        return;
    }
    m_suggestedActions.append(action);
    connect(action, &QObject::destroyed, this, [this, action]() {
        m_suggestedActions.removeAll(action);
    });
}

void RibbonSearchBar::removeSuggestedAction(QAction *action)
{
    m_suggestedActions.removeAll(action);
}

int RibbonSearchBar::maxSearchItemCount() const
{
    return m_maxSearchItemCount;
}

void RibbonSearchBar::setMaxSearchItemCount(int count)
{
    m_maxSearchItemCount = qMax(0, count);
}

void RibbonSearchBar::showPopup(const QString &text)
{
    m_popupMenu->clear();
    const QString normalized = text.trimmed();
    int count = 0;
    for (QAction *action : m_suggestedActions) {
        if (!action || !action->isVisible()) {
            continue;
        }
        const QString actionText = cleanActionText(action->text());
        if (!normalized.isEmpty()
            && !actionText.contains(normalized, Qt::CaseInsensitive)) {
            continue;
        }
        m_popupMenu->addAction(action);
        ++count;
        if (m_maxSearchItemCount > 0 && count >= m_maxSearchItemCount) {
            break;
        }
    }

    if (m_helpEnabled && !normalized.isEmpty()) {
        if (!m_popupMenu->isEmpty()) {
            m_popupMenu->addSeparator();
        }
        QAction *helpAction = m_popupMenu->addAction(
            QString::fromLatin1(QtnRibbonSearchBarGetHelpString)
            + QStringLiteral(" \"") + normalized + QStringLiteral("\""));
        connect(helpAction, &QAction::triggered, this, [this, normalized]() {
            emit showHelp(normalized);
        });
    }

    if (!m_popupMenu->isEmpty()) {
        m_popupMenu->popup(mapToGlobal(QPoint(0, height())));
    }
}

void RibbonSearchBar::closePopup()
{
    m_popupMenu->hide();
}

void RibbonSearchBar::animationFinished()
{
}

void RibbonSearchBar::animationValueChanged(const QVariant &value)
{
    Q_UNUSED(value)
}

void RibbonSearchBar::helpClicked()
{
    emit showHelp(text());
}

void RibbonSearchBar::mousePressEvent(QMouseEvent *event)
{
    QLineEdit::mousePressEvent(event);
}

void RibbonSearchBar::keyPressEvent(QKeyEvent *event)
{
    if (event->key() == Qt::Key_Escape) {
        closePopup();
    }
    QLineEdit::keyPressEvent(event);
}

void RibbonSearchBar::paintEvent(QPaintEvent *event)
{
    QLineEdit::paintEvent(event);
    if (!m_compact) {
        return;
    }

    QPainter painter(this);
    const int iconSize = qMin(16, qMin(width(), height()) - 6);
    if (iconSize <= 0) {
        return;
    }

    const QRect iconRect((width() - iconSize) / 2,
                         (height() - iconSize) / 2,
                         iconSize,
                         iconSize);
    m_icon.paint(&painter,
                 iconRect,
                 Qt::AlignCenter,
                 isEnabled() ? QIcon::Normal : QIcon::Disabled);
}

void RibbonSearchBar::focusInEvent(QFocusEvent *event)
{
    QLineEdit::focusInEvent(event);
}

void RibbonSearchBar::focusOutEvent(QFocusEvent *event)
{
    QLineEdit::focusOutEvent(event);
    closePopup();
}

void RibbonSearchBar::resizeEvent(QResizeEvent *event)
{
    QLineEdit::resizeEvent(event);
    if (m_compact) {
        setTextMargins(width() + 12, 0, 0, 0);
    }
}

RibbonBackstageSeparator::RibbonBackstageSeparator(QWidget *parent)
    : QFrame(parent)
    , m_orientation(Qt::Horizontal)
{
    setFrameShape(QFrame::HLine);
    setFrameShadow(QFrame::Sunken);
}

RibbonBackstageSeparator::~RibbonBackstageSeparator() = default;

void RibbonBackstageSeparator::setOrientation(Qt::Orientation orient)
{
    m_orientation = orient;
    setFrameShape(orient == Qt::Horizontal ? QFrame::HLine : QFrame::VLine);
}

Qt::Orientation RibbonBackstageSeparator::orientation() const
{
    return m_orientation;
}

RibbonBackstageButton::RibbonBackstageButton(QWidget *parent)
    : QToolButton(parent)
    , m_tabStyle(false)
{
    setAutoRaise(true);
    setToolButtonStyle(Qt::ToolButtonTextBesideIcon);
    setIconSize(QSize(20, 20));
}

RibbonBackstageButton::~RibbonBackstageButton() = default;

bool RibbonBackstageButton::tabStyle() const
{
    return m_tabStyle;
}

void RibbonBackstageButton::setTabStyle(bool style)
{
    if (m_tabStyle == style) {
        return;
    }
    m_tabStyle = style;
    setCheckable(style);
    update();
}

QSize RibbonBackstageButton::minimumSizeHint() const
{
    return QSize(80, backstageButtonHeight);
}

QSize RibbonBackstageButton::sizeHint() const
{
    QSize hint = QToolButton::sizeHint();
    hint.setHeight(qMax(hint.height(), backstageButtonHeight));
    hint.setWidth(qMax(hint.width(), 120));
    return hint;
}

bool RibbonBackstageButton::event(QEvent *event)
{
    return QToolButton::event(event);
}

void RibbonBackstageButton::paintEvent(QPaintEvent *event)
{
    QToolButton::paintEvent(event);
}

RibbonBackstagePage::RibbonBackstagePage(QWidget *parent)
    : QWidget(parent)
{
    setAutoFillBackground(false);
}

RibbonBackstagePage::~RibbonBackstagePage() = default;

void RibbonBackstagePage::paintEvent(QPaintEvent *event)
{
    QPainter painter(this);
    painter.fillRect(rect(), palette().base());
    QWidget::paintEvent(event);
}

RibbonBackstageView::RibbonBackstageView(QWidget *parent)
    : QWidget(parent)
    , m_menuWidget(new QWidget(this))
    , m_menuLayout(new QVBoxLayout(m_menuWidget))
    , m_pageStack(new QStackedWidget(this))
    , m_closePrevented(false)
{
    setObjectName(QStringLiteral("lqRibbonBackstageView"));
    setAutoFillBackground(false);
    setFocusPolicy(Qt::StrongFocus);

    m_menuWidget->setObjectName(QStringLiteral("lqRibbonBackstageMenu"));
    m_menuWidget->setFixedWidth(backstageMenuWidth);
    m_menuLayout->setContentsMargins(8, 12, 8, 12);
    m_menuLayout->setSpacing(2);
    m_menuLayout->addStretch(1);

    QHBoxLayout *layout = new QHBoxLayout(this);
    layout->setContentsMargins(0, 0, 0, 0);
    layout->setSpacing(0);
    layout->addWidget(m_menuWidget);
    layout->addWidget(m_pageStack, 1);
    hide();
}

RibbonBackstageView::~RibbonBackstageView() = default;

bool RibbonBackstageView::isClosePrevented() const
{
    return m_closePrevented;
}

void RibbonBackstageView::setClosePrevented(bool prevent)
{
    m_closePrevented = prevent;
}

QAction *RibbonBackstageView::addAction(const QIcon &icon, const QString &text)
{
    QAction *action = new QAction(icon, text, this);
    QWidget::addAction(action);
    return action;
}

QAction *RibbonBackstageView::addSeparator()
{
    QAction *action = new QAction(this);
    action->setSeparator(true);
    QWidget::addAction(action);
    return action;
}

QAction *RibbonBackstageView::addPage(QWidget *widget)
{
    if (!widget) {
        return nullptr;
    }
    const QString title = widget->windowTitle().isEmpty()
        ? widget->objectName()
        : widget->windowTitle();
    QAction *action = new QAction(widget->windowIcon(), title, this);
    action->setCheckable(true);
    m_actionPages.insert(action, widget);
    QWidget::addAction(action);
    QObject::connect(action,
                     &QAction::triggered,
                     this,
                     [this, widget]() { setActivePage(widget); });
    widget->setParent(m_pageStack);
    m_pageStack->addWidget(widget);
    if (!activePage()) {
        setActivePage(widget);
    }
    return action;
}

QWidget *RibbonBackstageView::activePage() const
{
    return m_pageStack->currentWidget();
}

void RibbonBackstageView::setActivePage(QWidget *widget)
{
    if (!widget) {
        return;
    }
    const int index = m_pageStack->indexOf(widget);
    if (index < 0) {
        return;
    }
    m_pageStack->setCurrentIndex(index);
    for (auto it = m_actionPages.constBegin(); it != m_actionPages.constEnd(); ++it) {
        it.key()->setChecked(it.value() == widget);
    }
}

QRect RibbonBackstageView::actionGeometry(QAction *action) const
{
    RibbonBackstageButton *button = m_actionButtons.value(action, nullptr);
    return button ? button->geometry() : QRect();
}

QRect RibbonBackstageView::menuGeometry() const
{
    return m_menuWidget->geometry();
}

void RibbonBackstageView::open()
{
    if (QWidget *parent = parentWidget()) {
        setGeometry(parent->rect());
    }
    raise();
    show();
    setFocus();
}

bool RibbonBackstageView::event(QEvent *event)
{
    if (event->type() == QEvent::KeyPress) {
        QKeyEvent *keyEvent = static_cast<QKeyEvent *>(event);
        if (keyEvent->key() == Qt::Key_Escape && !m_closePrevented) {
            hide();
            return true;
        }
    }
    return QWidget::event(event);
}

void RibbonBackstageView::paintEvent(QPaintEvent *event)
{
    Q_UNUSED(event)
    QPainter painter(this);
    painter.fillRect(rect(), palette().window());
    painter.fillRect(m_menuWidget->geometry(), QColor(QStringLiteral("#f3f2f1")));
}

void RibbonBackstageView::resizeEvent(QResizeEvent *event)
{
    QWidget::resizeEvent(event);
}

bool RibbonBackstageView::eventFilter(QObject *object, QEvent *event)
{
    return QWidget::eventFilter(object, event);
}

void RibbonBackstageView::actionEvent(QActionEvent *event)
{
    QWidget::actionEvent(event);
    QAction *action = event->action();
    if (!action) {
        return;
    }

    if (event->type() == QEvent::ActionAdded) {
        addActionButton(action);
    } else if (event->type() == QEvent::ActionRemoved) {
        if (RibbonBackstageButton *button = m_actionButtons.take(action)) {
            m_menuLayout->removeWidget(button);
            button->deleteLater();
        }
        m_actionPages.remove(action);
    }
}

void RibbonBackstageView::showEvent(QShowEvent *event)
{
    emit aboutToShow();
    QWidget::showEvent(event);
}

void RibbonBackstageView::hideEvent(QHideEvent *event)
{
    emit aboutToHide();
    QWidget::hideEvent(event);
}

void RibbonBackstageView::wheelEvent(QWheelEvent *event)
{
    QWidget::wheelEvent(event);
}

void RibbonBackstageView::rebuildMenu()
{
    for (QAction *action : actions()) {
        if (!m_actionButtons.contains(action)) {
            addActionButton(action);
        }
    }
}

void RibbonBackstageView::addActionButton(QAction *action)
{
    if (!action || m_actionButtons.contains(action)) {
        return;
    }

    QWidget *insertBefore = nullptr;
    const int stretchIndex = m_menuLayout->count() - 1;
    if (stretchIndex >= 0) {
        insertBefore = m_menuLayout->itemAt(stretchIndex)->widget();
    }

    if (action->isSeparator()) {
        RibbonBackstageSeparator *separator =
            new RibbonBackstageSeparator(m_menuWidget);
        separator->setFixedHeight(12);
        m_menuLayout->insertWidget(stretchIndex, separator);
        Q_UNUSED(insertBefore)
        return;
    }

    RibbonBackstageButton *button = new RibbonBackstageButton(m_menuWidget);
    button->setDefaultAction(action);
    button->setTabStyle(m_actionPages.contains(action));
    button->setSizePolicy(QSizePolicy::Expanding, QSizePolicy::Fixed);
    button->setMinimumHeight(backstageButtonHeight);
    connect(button, &QToolButton::clicked, this, [this, action]() {
        QWidget *page = m_actionPages.value(action, nullptr);
        if (page) {
            setActivePage(page);
        } else if (!m_closePrevented) {
            hide();
        }
    });
    m_actionButtons.insert(action, button);
    m_menuLayout->insertWidget(stretchIndex, button);
}

RibbonSystemButton::RibbonSystemButton(RibbonBar *ribbonBar)
    : QToolButton(ribbonBar)
    , m_ribbonBar(ribbonBar)
    , m_backgroundColor(QColor(QStringLiteral("#2b579a")))
{
    setAutoRaise(true);
    setToolButtonStyle(Qt::ToolButtonTextBesideIcon);
}

RibbonSystemButton::RibbonSystemButton(QWidget *parent)
    : QToolButton(parent)
    , m_ribbonBar(qobject_cast<RibbonBar *>(parent))
    , m_backgroundColor(QColor(QStringLiteral("#2b579a")))
{
    setAutoRaise(true);
    setToolButtonStyle(Qt::ToolButtonTextBesideIcon);
}

RibbonSystemButton::~RibbonSystemButton() = default;

RibbonBar *RibbonSystemButton::ribbonBar() const
{
    return m_ribbonBar;
}

RibbonBackstageView *RibbonSystemButton::backstage() const
{
    return m_backstage.data();
}

void RibbonSystemButton::setBackstage(RibbonBackstageView *backstage)
{
    m_backstage = backstage;
}

QColor RibbonSystemButton::backgroundColor() const
{
    return m_backgroundColor;
}

void RibbonSystemButton::setBackgroundColor(const QColor &color)
{
    m_backgroundColor = color;
    update();
}

RibbonSystemMenu *RibbonSystemButton::systemMenu() const
{
    return m_systemMenu.data();
}

void RibbonSystemButton::setSystemMenu(RibbonSystemMenu *menu)
{
    m_systemMenu = menu;
    setMenu(menu);
    setPopupMode(menu ? QToolButton::InstantPopup : QToolButton::DelayedPopup);
}

QSize RibbonSystemButton::sizeHint() const
{
    QSize hint = QToolButton::sizeHint();
    hint.setHeight(qMax(hint.height(), 28));
    return hint;
}

bool RibbonSystemButton::event(QEvent *event)
{
    return QToolButton::event(event);
}

bool RibbonSystemButton::eventFilter(QObject *watched, QEvent *event)
{
    return QToolButton::eventFilter(watched, event);
}

void RibbonSystemButton::paintEvent(QPaintEvent *event)
{
    QToolButton::paintEvent(event);
}

void RibbonSystemButton::mousePressEvent(QMouseEvent *event)
{
    if (event->button() == Qt::LeftButton && m_backstage) {
        m_backstage->open();
        event->accept();
        return;
    }
    QToolButton::mousePressEvent(event);
}

RibbonSystemMenu::RibbonSystemMenu(RibbonBar *ribbonBar)
    : QMenu(ribbonBar)
    , m_ribbonBar(ribbonBar)
    , m_popupBar(new QToolBar(this))
{
    m_popupBar->setMovable(false);
    m_popupBar->setFloatable(false);
    m_popupBar->setToolButtonStyle(Qt::ToolButtonTextOnly);
    QWidgetAction *barAction = new QWidgetAction(this);
    barAction->setDefaultWidget(m_popupBar);
    QMenu::addAction(barAction);
}

RibbonSystemMenu::~RibbonSystemMenu() = default;

RibbonBar *RibbonSystemMenu::ribbonBar() const
{
    return m_ribbonBar;
}

QAction *RibbonSystemMenu::addPopupBarAction(const QString &text)
{
    QAction *action = new QAction(text, this);
    addPopupBarAction(action);
    return action;
}

void RibbonSystemMenu::addPopupBarAction(QAction *action,
                                         Qt::ToolButtonStyle style)
{
    if (!action) {
        return;
    }
    m_popupBar->setToolButtonStyle(style);
    m_popupBar->addAction(action);
}

RibbonPageSystemRecentFileList *RibbonSystemMenu::addPageRecentFile(
    const QString &caption)
{
    RibbonPageSystemRecentFileList *list =
        new RibbonPageSystemRecentFileList(caption);
    QWidgetAction *action = new QWidgetAction(this);
    action->setDefaultWidget(list);
    QMenu::addAction(action);
    return list;
}

RibbonPageSystemPopup *RibbonSystemMenu::addPageSystemPopup(
    const QString &caption,
    QAction *defaultAction,
    bool splitAction)
{
    Q_UNUSED(splitAction)
    RibbonPageSystemPopup *popup = new RibbonPageSystemPopup(caption, this);
    if (defaultAction) {
        popup->addAction(defaultAction);
    }
    QMenu::addMenu(popup);
    return popup;
}

void RibbonSystemMenu::setVisible(bool visible)
{
    QMenu::setVisible(visible);
}

QSize RibbonSystemMenu::sizeHint() const
{
    QSize hint = QMenu::sizeHint();
    hint.setWidth(qMax(hint.width(), 280));
    return hint;
}

void RibbonSystemMenu::updateLayout()
{
    updateGeometry();
}

void RibbonSystemMenu::paintEvent(QPaintEvent *event)
{
    QMenu::paintEvent(event);
}

void RibbonSystemMenu::mousePressEvent(QMouseEvent *event)
{
    QMenu::mousePressEvent(event);
}

void RibbonSystemMenu::mouseReleaseEvent(QMouseEvent *event)
{
    QMenu::mouseReleaseEvent(event);
}

void RibbonSystemMenu::keyPressEvent(QKeyEvent *event)
{
    QMenu::keyPressEvent(event);
}

void RibbonSystemMenu::changeEvent(QEvent *event)
{
    QMenu::changeEvent(event);
}

RibbonPageSystemRecentFileList::RibbonPageSystemRecentFileList(
    const QString &caption)
    : QWidget(nullptr)
    , m_caption(caption)
    , m_size(9)
    , m_currentIndex(-1)
    , m_pressedIndex(-1)
{
    setMouseTracking(true);
    setMinimumWidth(260);
}

RibbonPageSystemRecentFileList::~RibbonPageSystemRecentFileList()
{
    qDeleteAll(m_actions);
}

QSize RibbonPageSystemRecentFileList::sizeHint() const
{
    return QSize(300, 32 + qMin(m_size, qMax(1, m_actions.count()))
                       * recentFileRowHeight);
}

void RibbonPageSystemRecentFileList::setSize(int size)
{
    m_size = qMax(0, size);
    updateGeometry();
}

int RibbonPageSystemRecentFileList::getSize() const
{
    return m_size;
}

QAction *RibbonPageSystemRecentFileList::getCurrentAction() const
{
    return actionAtIndex(m_actions, m_currentIndex);
}

void RibbonPageSystemRecentFileList::updateRecentFileActions(
    const QStringList &files)
{
    qDeleteAll(m_actions);
    m_actions.clear();
    for (const QString &file : files.mid(0, m_size)) {
        QAction *action = new QAction(file, this);
        action->setData(file);
        m_actions.append(action);
    }
    m_currentIndex = -1;
    updateGeometry();
    update();
}

void RibbonPageSystemRecentFileList::paintEvent(QPaintEvent *event)
{
    Q_UNUSED(event)
    QPainter painter(this);
    painter.fillRect(rect(), palette().base());
    painter.setPen(palette().text().color());
    painter.drawText(QRect(12, 6, width() - 24, 22),
                     Qt::AlignLeft | Qt::AlignVCenter,
                     m_caption);
    for (int i = 0; i < m_actions.count(); ++i) {
        const QRect rowRect(8, 32 + i * recentFileRowHeight,
                            width() - 16, recentFileRowHeight);
        if (i == m_currentIndex) {
            painter.fillRect(rowRect, palette().highlight());
            painter.setPen(palette().highlightedText().color());
        } else {
            painter.setPen(palette().text().color());
        }
        painter.drawText(rowRect.adjusted(8, 0, -8, 0),
                         Qt::AlignLeft | Qt::AlignVCenter,
                         m_actions.at(i)->text());
    }
}

void RibbonPageSystemRecentFileList::mousePressEvent(QMouseEvent *event)
{
    m_pressedIndex = hitAction(event->pos());
    QWidget::mousePressEvent(event);
}

void RibbonPageSystemRecentFileList::mouseMoveEvent(QMouseEvent *event)
{
    const int index = hitAction(event->pos());
    if (m_currentIndex != index) {
        m_currentIndex = index;
        update();
    }
    QWidget::mouseMoveEvent(event);
}

void RibbonPageSystemRecentFileList::mouseReleaseEvent(QMouseEvent *event)
{
    const int index = hitAction(event->pos());
    if (index >= 0 && index == m_pressedIndex) {
        QAction *action = m_actions.at(index);
        emit openRecentFile(action->data().toString());
        action->trigger();
    }
    m_pressedIndex = -1;
    QWidget::mouseReleaseEvent(event);
}

#if (QT_VERSION >= QT_VERSION_CHECK(6, 0, 0))
void RibbonPageSystemRecentFileList::enterEvent(QEnterEvent *event)
#else
void RibbonPageSystemRecentFileList::enterEvent(QEvent *event)
#endif
{
    QWidget::enterEvent(event);
}

void RibbonPageSystemRecentFileList::leaveEvent(QEvent *event)
{
    m_currentIndex = -1;
    update();
    QWidget::leaveEvent(event);
}

void RibbonPageSystemRecentFileList::keyPressEvent(QKeyEvent *event)
{
    if (event->key() == Qt::Key_Return || event->key() == Qt::Key_Enter) {
        if (QAction *action = getCurrentAction()) {
            emit openRecentFile(action->data().toString());
            action->trigger();
        }
        return;
    }
    QWidget::keyPressEvent(event);
}

void RibbonPageSystemRecentFileList::resizeEvent(QResizeEvent *event)
{
    QWidget::resizeEvent(event);
}

int RibbonPageSystemRecentFileList::hitAction(const QPoint &point) const
{
    const int index = (point.y() - 32) / recentFileRowHeight;
    if (index < 0 || index >= m_actions.count()) {
        return -1;
    }
    return index;
}

RibbonPageSystemPopup::RibbonPageSystemPopup(const QString &caption,
                                             QWidget *parent)
    : QMenu(caption, parent)
{
}

RibbonPageSystemPopup::~RibbonPageSystemPopup() = default;

QSize RibbonPageSystemPopup::sizeHint() const
{
    QSize hint = QMenu::sizeHint();
    hint.setWidth(qMax(hint.width(), 220));
    return hint;
}

bool RibbonPageSystemPopup::event(QEvent *event)
{
    return QMenu::event(event);
}

void RibbonPageSystemPopup::paintEvent(QPaintEvent *event)
{
    QMenu::paintEvent(event);
}

OfficePopupMenu::OfficePopupMenu(QWidget *parent)
    : QMenu(parent)
    , m_widgetAction(nullptr)
    , m_gripVisible(false)
    , m_dragging(false)
{
}

OfficePopupMenu::~OfficePopupMenu() = default;

OfficePopupMenu *OfficePopupMenu::createPopupMenu(QWidget *parent)
{
    return new OfficePopupMenu(parent);
}

QAction *OfficePopupMenu::addWidget(QWidget *widget)
{
    if (!widget) {
        return nullptr;
    }
    QWidgetAction *action = new QWidgetAction(this);
    action->setDefaultWidget(widget);
    QMenu::addAction(action);
    return action;
}

void OfficePopupMenu::setGripVisible(bool visible)
{
    m_gripVisible = visible;
    update();
}

bool OfficePopupMenu::isGripVisible() const
{
    return m_gripVisible;
}

void OfficePopupMenu::setWidgetBar(QWidget *widget)
{
    if (!m_widgetAction) {
        m_widgetAction = new QWidgetAction(this);
        QMenu::insertAction(actions().isEmpty() ? nullptr : actions().first(),
                            m_widgetAction);
    }
    m_widgetAction->setDefaultWidget(widget);
}

bool OfficePopupMenu::event(QEvent *event)
{
    return QMenu::event(event);
}

void OfficePopupMenu::paintEvent(QPaintEvent *event)
{
    QMenu::paintEvent(event);
    if (!m_gripVisible) {
        return;
    }
    QPainter painter(this);
    painter.setPen(palette().mid().color());
    const QRect gripRect(width() - 18, height() - 18, 12, 12);
    for (int i = 0; i < 3; ++i) {
        painter.drawLine(gripRect.left() + i * 4,
                         gripRect.bottom(),
                         gripRect.right(),
                         gripRect.top() + i * 4);
    }
}

void OfficePopupMenu::mousePressEvent(QMouseEvent *event)
{
    if (m_gripVisible && event->button() == Qt::LeftButton) {
        m_dragging = true;
        m_dragStartPos = event->globalPos() - pos();
    }
    QMenu::mousePressEvent(event);
}

void OfficePopupMenu::mouseMoveEvent(QMouseEvent *event)
{
    if (m_dragging) {
        move(event->globalPos() - m_dragStartPos);
        event->accept();
        return;
    }
    QMenu::mouseMoveEvent(event);
}

void OfficePopupMenu::mouseReleaseEvent(QMouseEvent *event)
{
    m_dragging = false;
    QMenu::mouseReleaseEvent(event);
}

void OfficePopupMenu::moveEvent(QMoveEvent *event)
{
    QMenu::moveEvent(event);
}

void OfficePopupMenu::showEvent(QShowEvent *event)
{
    QMenu::showEvent(event);
}

void OfficePopupMenu::hideEvent(QHideEvent *event)
{
    m_dragging = false;
    QMenu::hideEvent(event);
}

PopupColorButton::PopupColorButton(QWidget *parent)
    : QToolButton(parent)
    , m_color(Qt::black)
{
    setAutoRaise(true);
}

PopupColorButton::~PopupColorButton() = default;

const QColor &PopupColorButton::color() const
{
    return m_color;
}

void PopupColorButton::setColor(const QColor &color)
{
    if (m_color == color) {
        return;
    }
    m_color = color;
    emit colorChanged(m_color);
    update();
}

QSize PopupColorButton::sizeHint() const
{
    QSize hint = QToolButton::sizeHint();
    hint.setWidth(qMax(hint.width(), 36));
    return hint;
}

void PopupColorButton::paintEvent(QPaintEvent *event)
{
    QToolButton::paintEvent(event);
    QPainter painter(this);
    const QRect colorRect = rect().adjusted(6, height() - 8, -6, -4);
    painter.fillRect(colorRect, m_color);
    painter.setPen(palette().mid().color());
    painter.drawRect(colorRect.adjusted(0, 0, -1, -1));
}

void PopupColorButton::mousePressEvent(QMouseEvent *event)
{
    QToolButton::mousePressEvent(event);
    if (event->button() != Qt::LeftButton) {
        return;
    }
    const QColor color = QColorDialog::getColor(m_color, this);
    if (color.isValid()) {
        setColor(color);
    }
}

OfficePopupWindow::OfficePopupWindow(QWidget *parent)
    : QWidget(parent, Qt::ToolTip | Qt::FramelessWindowHint)
    , m_centralWidget(nullptr)
    , m_iconLabel(new QLabel(this))
    , m_titleLabel(new QLabel(this))
    , m_bodyLabel(new QLabel(this))
    , m_closeButton(new QToolButton(this))
    , m_displayTimer(new QTimer(this))
    , m_animation(PopupAnimationFade)
    , m_location(PopupLocationBottomRight)
    , m_transparency(1.0)
    , m_displayTime(4000)
    , m_animationSpeed(120)
    , m_dragDropEnabled(false)
{
    setAttribute(Qt::WA_DeleteOnClose, false);
    setWindowOpacity(m_transparency);
    m_titleLabel->setObjectName(QStringLiteral("lqOfficePopupTitle"));
    m_titleLabel->setSizePolicy(QSizePolicy::Expanding, QSizePolicy::Preferred);
    m_bodyLabel->setWordWrap(true);
    m_closeButton->setAutoRaise(true);
    m_closeButton->setText(QStringLiteral("x"));
    connect(m_closeButton, &QToolButton::clicked,
            this, &OfficePopupWindow::closePopup);
    connect(m_displayTimer, &QTimer::timeout,
            this, &OfficePopupWindow::closePopup);
    rebuildLayout();
}

OfficePopupWindow::~OfficePopupWindow() = default;

void OfficePopupWindow::showPopup(QWidget *parent,
                                  const QIcon &titleIcon,
                                  const QString &titleText,
                                  const QString &bodyText,
                                  bool closeButtonVisible)
{
    OfficePopupWindow *popup = new OfficePopupWindow(parent);
    popup->setAttribute(Qt::WA_DeleteOnClose);
    popup->setTitleIcon(titleIcon);
    popup->setTitleText(titleText);
    popup->setBodyText(bodyText);
    popup->setTitleCloseButtonVisible(closeButtonVisible);
    popup->showPopup();
}

bool OfficePopupWindow::showPopup()
{
    return showPopup(defaultPopupPosition());
}

bool OfficePopupWindow::showPopup(const QPoint &pos)
{
    m_position = pos;
    move(pos);
    emit aboutToShow();
    show();
    raise();
    if (m_displayTime > 0) {
        m_displayTimer->start(m_displayTime);
    }
    return true;
}

void OfficePopupWindow::setCentralWidget(QWidget *widget)
{
    if (m_centralWidget == widget) {
        return;
    }
    if (m_centralWidget) {
        m_centralWidget->setParent(nullptr);
    }
    m_centralWidget = widget;
    if (m_centralWidget) {
        m_centralWidget->setParent(this);
    }
    rebuildLayout();
}

QWidget *OfficePopupWindow::centralWidget() const
{
    return m_centralWidget;
}

void OfficePopupWindow::setBodyText(const QString &text)
{
    m_bodyText = text;
    m_bodyLabel->setText(text);
}

const QString &OfficePopupWindow::bodyText() const
{
    return m_bodyText;
}

void OfficePopupWindow::setTitleIcon(const QIcon &icon)
{
    m_titleIcon = icon;
    m_iconLabel->setPixmap(icon.pixmap(24, 24));
}

const QIcon &OfficePopupWindow::titleIcon() const
{
    return m_titleIcon;
}

void OfficePopupWindow::setTitleText(const QString &text)
{
    m_titleText = text;
    m_titleLabel->setText(text);
}

const QString &OfficePopupWindow::titleText() const
{
    return m_titleText;
}

void OfficePopupWindow::setCloseButtonPixmap(const QPixmap &pm)
{
    m_closePixmap = pm;
    m_closeButton->setIcon(QIcon(pm));
}

const QPixmap &OfficePopupWindow::closeButtonPixmap() const
{
    return m_closePixmap;
}

void OfficePopupWindow::setTitleCloseButtonVisible(bool visible)
{
    m_closeButton->setVisible(visible);
}

bool OfficePopupWindow::isTitleCloseButtonVisible() const
{
    return m_closeButton->isVisible();
}

QPoint OfficePopupWindow::getPosition() const
{
    return m_position;
}

void OfficePopupWindow::setPosition(const QPoint &pos)
{
    m_position = pos;
    move(pos);
}

void OfficePopupWindow::setAnimation(OfficePopupWindow::PopupAnimation popupAnimation)
{
    m_animation = popupAnimation;
}

OfficePopupWindow::PopupAnimation OfficePopupWindow::animation() const
{
    return m_animation;
}

void OfficePopupWindow::setTransparency(qreal transparency)
{
    m_transparency = qBound<qreal>(0.0, transparency, 1.0);
    setWindowOpacity(m_transparency);
}

qreal OfficePopupWindow::transparency() const
{
    return m_transparency;
}

void OfficePopupWindow::setDisplayTime(int time)
{
    m_displayTime = qMax(0, time);
}

int OfficePopupWindow::displayTime() const
{
    return m_displayTime;
}

void OfficePopupWindow::setAnimationSpeed(int time)
{
    m_animationSpeed = qMax(0, time);
}

int OfficePopupWindow::animationSpeed() const
{
    return m_animationSpeed;
}

void OfficePopupWindow::setDragDropEnabled(bool enabled)
{
    m_dragDropEnabled = enabled;
}

bool OfficePopupWindow::dragDropEnabled() const
{
    return m_dragDropEnabled;
}

void OfficePopupWindow::setLocation(OfficePopupWindow::PopupLocation location)
{
    m_location = location;
}

OfficePopupWindow::PopupLocation OfficePopupWindow::location() const
{
    return m_location;
}

QSize OfficePopupWindow::sizeHint() const
{
    return QSize(320, m_centralWidget ? 180 : 120);
}

void OfficePopupWindow::closePopup()
{
    if (!isVisible()) {
        return;
    }
    emit aboutToHide();
    hide();
    if (testAttribute(Qt::WA_DeleteOnClose)) {
        deleteLater();
    }
}

void OfficePopupWindow::showDelayTimer()
{
    showPopup();
}

void OfficePopupWindow::collapsingTimer()
{
    closePopup();
}

void OfficePopupWindow::expandingTimer()
{
    showPopup();
}

bool OfficePopupWindow::event(QEvent *event)
{
    return QWidget::event(event);
}

void OfficePopupWindow::paintEvent(QPaintEvent *event)
{
    Q_UNUSED(event)
    QPainter painter(this);
    painter.setRenderHint(QPainter::Antialiasing);
    QPainterPath path;
    path.addRoundedRect(rect().adjusted(0, 0, -1, -1), 4, 4);
    painter.fillPath(path, palette().window());
    painter.setPen(palette().mid().color());
    painter.drawPath(path);
}

#if (QT_VERSION >= QT_VERSION_CHECK(6, 0, 0))
void OfficePopupWindow::enterEvent(QEnterEvent *event)
#else
void OfficePopupWindow::enterEvent(QEvent *event)
#endif
{
    m_displayTimer->stop();
    QWidget::enterEvent(event);
}

void OfficePopupWindow::leaveEvent(QEvent *event)
{
    if (m_displayTime > 0) {
        m_displayTimer->start(m_displayTime);
    }
    QWidget::leaveEvent(event);
}

QPoint OfficePopupWindow::defaultPopupPosition() const
{
    QRect area;
    if (QWidget *parent = parentWidget()) {
        area = parent->screen()
            ? parent->screen()->availableGeometry()
            : QRect(parent->mapToGlobal(QPoint()), parent->size());
    } else if (QScreen *screen = QGuiApplication::primaryScreen()) {
        area = screen->availableGeometry();
    }

    const QSize hint = sizeHint();
    switch (m_location) {
    case PopupLocationCenter:
        return area.center() - QPoint(hint.width() / 2, hint.height() / 2);
    case PopupLocationNearTaskBar:
    case PopupLocationBottomRight:
    default:
        return QPoint(area.right() - hint.width() - 12,
                      area.bottom() - hint.height() - 12);
    }
}

void OfficePopupWindow::rebuildLayout()
{
    delete layout();
    QVBoxLayout *mainLayout = new QVBoxLayout(this);
    mainLayout->setContentsMargins(12, 10, 12, 12);
    mainLayout->setSpacing(8);

    QHBoxLayout *titleLayout = new QHBoxLayout;
    titleLayout->setContentsMargins(0, 0, 0, 0);
    titleLayout->addWidget(m_iconLabel);
    titleLayout->addWidget(m_titleLabel, 1);
    titleLayout->addWidget(m_closeButton);
    mainLayout->addLayout(titleLayout);
    mainLayout->addWidget(m_bodyLabel);
    if (m_centralWidget) {
        mainLayout->addWidget(m_centralWidget, 1);
    }
}

RibbonScrollArea::RibbonScrollArea(QWidget *parent)
    : QScrollArea(parent)
{
    setWidgetResizable(true);
    viewport()->setAutoFillBackground(false);
}

RibbonScrollArea::~RibbonScrollArea() = default;

QSize RibbonScrollArea::viewportSizeHint() const
{
    return viewport()->sizeHint();
}

void RibbonScrollArea::paintEvent(QPaintEvent *event)
{
    QScrollArea::paintEvent(event);
}

bool RibbonScrollArea::event(QEvent *event)
{
    if (event->type() == QEvent::LayoutRequest
        || event->type() == QEvent::Resize) {
        updateScrollBars();
    }
    return QScrollArea::event(event);
}

void RibbonScrollArea::updateScrollBars()
{
    updateGeometry();
}

RibbonWorkspace::RibbonWorkspace(QWidget *parent)
    : RibbonScrollArea(parent)
{
}

void RibbonWorkspace::paintEvent(QPaintEvent *event)
{
    QPainter painter(viewport());
    painter.fillRect(viewport()->rect(), palette().base());
    RibbonScrollArea::paintEvent(event);
}

RibbonMdiArea::RibbonMdiArea(QWidget *parent)
    : QMdiArea(parent)
{
    setDocumentMode(false);
    setTabsClosable(true);
    setTabsMovable(true);
    setViewMode(QMdiArea::TabbedView);
    fixupTabBar(this);
}

void RibbonMdiArea::fixupTabBar(RibbonMdiArea *area)
{
    if (!area) {
        return;
    }
    if (QTabBar *tabBar = area->findChild<QTabBar *>()) {
        tabBar->setExpanding(false);
        tabBar->setUsesScrollButtons(true);
    }
}

bool RibbonMdiArea::event(QEvent *event)
{
    const bool handled = QMdiArea::event(event);
    if (event->type() == QEvent::ChildAdded
        || event->type() == QEvent::LayoutRequest
        || event->type() == QEvent::Show) {
        fixupTabBar(this);
    }
    return handled;
}

RibbonCustomizeManager::RibbonCustomizeManager(RibbonBar *ribbonBar)
    : QObject(ribbonBar)
    , m_ribbonBar(ribbonBar)
    , m_editMode(false)
{
}

RibbonCustomizeManager::~RibbonCustomizeManager() = default;

QStringList RibbonCustomizeManager::categories() const
{
    QSet<QString> categorySet;
    for (const QString &category : m_actionsByCategory.keys()) {
        categorySet.insert(category);
    }
    for (const QString &category : m_toolBarsByCategory.keys()) {
        categorySet.insert(category);
    }
    for (const QString &category : m_pagesByCategory.keys()) {
        categorySet.insert(category);
    }
    for (const QString &category : m_groupsByCategory.keys()) {
        categorySet.insert(category);
    }
    return categorySet.values();
}

QList<QAction *> RibbonCustomizeManager::actionsAll() const
{
    QList<QAction *> result;
    for (QToolBar *toolBar : m_toolBars) {
        if (toolBar) {
            for (QAction *action : toolBar->actions()) {
                if (action && !result.contains(action)) {
                    result.append(action);
                }
            }
        }
    }
    for (const QList<QAction *> &actions : m_actionsByCategory) {
        for (QAction *action : actions) {
            if (action && !result.contains(action)) {
                result.append(action);
            }
        }
    }
    return result;
}

void RibbonCustomizeManager::addToolBar(QToolBar *toolBar)
{
    if (toolBar && !m_toolBars.contains(toolBar)) {
        m_toolBars.append(toolBar);
    }
}

void RibbonCustomizeManager::addAllActionsCategory(const QString &category)
{
    m_actionsByCategory[category] = actionsAll();
}

QList<QAction *> RibbonCustomizeManager::actionsByCategory(
    const QString &category) const
{
    return m_actionsByCategory.value(category);
}

void RibbonCustomizeManager::addToCategory(const QString &category,
                                           QAction *act)
{
    if (act && !m_actionsByCategory[category].contains(act)) {
        m_actionsByCategory[category].append(act);
    }
}

void RibbonCustomizeManager::removeFromCategory(const QString &category,
                                                QAction *act)
{
    m_actionsByCategory[category].removeAll(act);
}

QList<QToolBar *> RibbonCustomizeManager::toolBarsByCategory(
    const QString &category) const
{
    return m_toolBarsByCategory.value(category);
}

void RibbonCustomizeManager::addToCategory(const QString &category,
                                           QToolBar *toolBar)
{
    if (toolBar && !m_toolBarsByCategory[category].contains(toolBar)) {
        m_toolBarsByCategory[category].append(toolBar);
        addToolBar(toolBar);
    }
}

QList<RibbonPage *> RibbonCustomizeManager::pagesByCategory(
    const QString &category) const
{
    return m_pagesByCategory.value(category);
}

void RibbonCustomizeManager::addToCategory(const QString &category,
                                           RibbonPage *page)
{
    if (page && !m_pagesByCategory[category].contains(page)) {
        m_pagesByCategory[category].append(page);
    }
}

QList<RibbonGroup *> RibbonCustomizeManager::groupsByCategory(
    const QString &category) const
{
    return m_groupsByCategory.value(category);
}

void RibbonCustomizeManager::addToCategory(const QString &category,
                                           RibbonGroup *group)
{
    if (group && !m_groupsByCategory[category].contains(group)) {
        m_groupsByCategory[category].append(group);
    }
}

QString RibbonCustomizeManager::actionId(QAction *action) const
{
    return m_actionIds.value(action);
}

void RibbonCustomizeManager::setActionId(QAction *action, const QString &id)
{
    if (action) {
        m_actionIds[action] = id;
    }
}

QString RibbonCustomizeManager::pageId(RibbonPage *page) const
{
    return m_pageIds.value(page);
}

void RibbonCustomizeManager::setPageId(RibbonPage *page, const QString &id)
{
    if (page) {
        m_pageIds[page] = id;
    }
}

QString RibbonCustomizeManager::groupId(RibbonGroup *group) const
{
    return m_groupIds.value(group);
}

void RibbonCustomizeManager::setGroupId(RibbonGroup *group, const QString &id)
{
    if (group) {
        m_groupIds[group] = id;
    }
}

void RibbonCustomizeManager::setEditMode(bool set)
{
    m_editMode = set;
}

bool RibbonCustomizeManager::isEditMode() const
{
    return m_editMode;
}

void RibbonCustomizeManager::reset(QToolBar *toolBar)
{
    if (toolBar) {
        toolBar->clear();
    }
}

void RibbonCustomizeManager::commit()
{
    m_editMode = false;
}

void RibbonCustomizeManager::cancel()
{
    m_editMode = false;
}

QList<QAction *> RibbonCustomizeManager::actions(QToolBar *toolBar) const
{
    return toolBar ? toolBar->actions() : QList<QAction *>();
}

void RibbonCustomizeManager::insertAction(QToolBar *toolBar,
                                          QAction *action,
                                          int index)
{
    if (!toolBar || !action) {
        return;
    }
    QAction *before = actionAtIndex(toolBar->actions(), index);
    toolBar->insertAction(before, action);
}

void RibbonCustomizeManager::removeActionAt(QToolBar *toolBar, int index)
{
    if (!toolBar) {
        return;
    }
    if (QAction *action = actionAtIndex(toolBar->actions(), index)) {
        toolBar->removeAction(action);
    }
}

bool RibbonCustomizeManager::containsAction(QToolBar *toolBar,
                                            QAction *action) const
{
    return toolBar && action && toolBar->actions().contains(action);
}

RibbonPageList RibbonCustomizeManager::pages() const
{
    return m_ribbonBar ? m_ribbonBar->pages() : RibbonPageList();
}

RibbonPage *RibbonCustomizeManager::createPage(const QString &pageName,
                                               int index)
{
    return m_ribbonBar ? m_ribbonBar->insertPage(index, pageName) : nullptr;
}

void RibbonCustomizeManager::deletePage(RibbonPage *page)
{
    if (m_ribbonBar) {
        m_ribbonBar->removePage(page);
    }
}

int RibbonCustomizeManager::pageIndex(RibbonPage *page) const
{
    return m_ribbonBar ? m_ribbonBar->pageIndex(page) : -1;
}

void RibbonCustomizeManager::movePage(int oldIndex, int newIndex)
{
    if (m_ribbonBar) {
        m_ribbonBar->movePage(oldIndex, newIndex);
    }
}

RibbonGroupList RibbonCustomizeManager::pageGroups(RibbonPage *page) const
{
    return page ? page->groups() : RibbonGroupList();
}

RibbonGroup *RibbonCustomizeManager::createGroup(RibbonPage *page,
                                                 const QString &groupName,
                                                 int index)
{
    return page ? page->insertGroup(index, groupName) : nullptr;
}

void RibbonCustomizeManager::deleteGroup(RibbonPage *page, int index)
{
    if (page) {
        page->removeGroupByIndex(index);
    }
}

void RibbonCustomizeManager::moveGroup(RibbonPage *page,
                                       int oldIndex,
                                       int newIndex)
{
    if (!page) {
        return;
    }
    RibbonGroup *group = page->group(oldIndex);
    if (!group) {
        return;
    }
    page->detachGroup(group);
    page->insertGroup(newIndex, group);
}

void RibbonCustomizeManager::insertAction(RibbonGroup *group,
                                          QAction *action,
                                          int index)
{
    if (!group || !action) {
        return;
    }
    QAction *before = actionAtIndex(group->actions(), index);
    group->insertAction(before, action, Qt::ToolButtonTextBesideIcon);
}

void RibbonCustomizeManager::appendActions(RibbonGroup *group,
                                           const QList<QAction *> &actions)
{
    if (!group) {
        return;
    }
    for (QAction *action : actions) {
        group->addAction(action, Qt::ToolButtonTextBesideIcon);
    }
}

void RibbonCustomizeManager::clearActions(RibbonGroup *group)
{
    if (group) {
        group->clear();
    }
}

void RibbonCustomizeManager::removeActionAt(RibbonGroup *group, int index)
{
    if (!group) {
        return;
    }
    if (QAction *action = actionAtIndex(group->actions(), index)) {
        group->removeAction(action);
    }
}

bool RibbonCustomizeManager::containsAction(RibbonGroup *group,
                                            QAction *action) const
{
    return group && action && group->actions().contains(action);
}

QList<QAction *> RibbonCustomizeManager::actionsGroup(RibbonGroup *group) const
{
    return group ? group->actions() : QList<QAction *>();
}

bool RibbonCustomizeManager::isPageHidden(RibbonPage *page) const
{
    return page && page->property("lqRibbonPageHidden").toBool();
}

void RibbonCustomizeManager::setPageHidden(RibbonPage *page, bool hide)
{
    if (page) {
        page->setProperty("lqRibbonPageHidden", hide);
        page->setVisible(!hide);
    }
}

bool RibbonCustomizeManager::isPageVisible(RibbonPage *page) const
{
    return page && page->isVisible();
}

void RibbonCustomizeManager::setPageVisible(RibbonPage *page, bool visible)
{
    if (page) {
        page->setVisible(visible);
    }
}

QString RibbonCustomizeManager::pageName(RibbonPage *page) const
{
    return page ? page->title() : QString();
}

void RibbonCustomizeManager::setPageName(RibbonPage *page,
                                         const QString &pageName)
{
    if (page) {
        page->setTitle(pageName);
    }
}

QString RibbonCustomizeManager::groupName(RibbonGroup *group) const
{
    return group ? group->title() : QString();
}

void RibbonCustomizeManager::setGroupName(RibbonGroup *group,
                                          const QString &groupName)
{
    if (group) {
        group->setTitle(groupName);
    }
}

bool RibbonCustomizeManager::saveStateToDevice(QIODevice *device,
                                               bool autoFormatting)
{
    if (!device || !device->isWritable()) {
        return false;
    }
    QXmlStreamWriter writer(device);
    writer.setAutoFormatting(autoFormatting);
    return saveStateToXML(&writer);
}

bool RibbonCustomizeManager::saveStateToXML(IXmlStreamWriter *xmlwriter)
{
    if (!xmlwriter) {
        return false;
    }
    xmlwriter->writeStartDocument();
    xmlwriter->writeStartElement(QStringLiteral("LqRibbonState"));
    if (m_ribbonBar) {
        for (RibbonPage *page : m_ribbonBar->pages()) {
            xmlwriter->writeStartElement(QStringLiteral("Page"));
            xmlwriter->writeAttribute(QStringLiteral("id"), pageId(page));
            xmlwriter->writeAttribute(QStringLiteral("title"), page->title());
            xmlwriter->writeAttribute(QStringLiteral("visible"),
                                      page->isVisible() ? QStringLiteral("1")
                                                        : QStringLiteral("0"));
            for (RibbonGroup *group : page->groups()) {
                xmlwriter->writeStartElement(QStringLiteral("Group"));
                xmlwriter->writeAttribute(QStringLiteral("id"), groupId(group));
                xmlwriter->writeAttribute(QStringLiteral("title"),
                                          group->title());
                xmlwriter->writeEndElement();
            }
            xmlwriter->writeEndElement();
        }
    }
    xmlwriter->writeEndElement();
    xmlwriter->writeEndDocument();
    return !xmlwriter->hasError();
}

bool RibbonCustomizeManager::loadStateFromDevice(QIODevice *device)
{
    if (!device || !device->isReadable()) {
        return false;
    }
    QXmlStreamReader reader(device);
    return loadStateFromXML(&reader);
}

bool RibbonCustomizeManager::loadStateFromXML(IXmlStreamReader *xmlreader)
{
    if (!xmlreader || !m_ribbonBar) {
        return false;
    }
    QStringList existingPageTitles;
    for (RibbonPage *page : m_ribbonBar->pages()) {
        existingPageTitles.append(page->title());
    }
    while (!xmlreader->atEnd()) {
        xmlreader->readNext();
        if (!xmlreader->isStartElement()) {
            continue;
        }
        if (xmlreader->name() == QStringLiteral("Page")) {
            const QString title =
                xmlreader->attributes().value(QStringLiteral("title")).toString();
            const QString visible =
                xmlreader->attributes().value(QStringLiteral("visible")).toString();
            if (!title.isEmpty() && !existingPageTitles.contains(title)) {
                RibbonPage *page = m_ribbonBar->addPage(title);
                page->setVisible(visible != QStringLiteral("0"));
                existingPageTitles.append(title);
            }
        }
    }
    return !xmlreader->hasError();
}

void RibbonCustomizeManager::setDefaultState()
{
}

RibbonCustomizeDialog::RibbonCustomizeDialog(QWidget *parent)
    : QDialog(parent)
    , m_pageList(new QListWidget(this))
    , m_pageStack(new QStackedWidget(this))
{
    QHBoxLayout *contentLayout = new QHBoxLayout;
    contentLayout->addWidget(m_pageList);
    contentLayout->addWidget(m_pageStack, 1);

    QDialogButtonBox *buttonBox =
        new QDialogButtonBox(QDialogButtonBox::Ok | QDialogButtonBox::Cancel,
                             this);
    connect(buttonBox, &QDialogButtonBox::accepted, this,
            &RibbonCustomizeDialog::accept);
    connect(buttonBox, &QDialogButtonBox::rejected, this,
            &RibbonCustomizeDialog::reject);
    connect(m_pageList, &QListWidget::currentRowChanged,
            m_pageStack, &QStackedWidget::setCurrentIndex);

    QVBoxLayout *layout = new QVBoxLayout(this);
    layout->addLayout(contentLayout, 1);
    layout->addWidget(buttonBox);
}

RibbonCustomizeDialog::~RibbonCustomizeDialog() = default;

void RibbonCustomizeDialog::addPage(QWidget *page)
{
    insertPage(m_pageStack->count(), page);
}

void RibbonCustomizeDialog::insertPage(int index, QWidget *page)
{
    if (!page) {
        return;
    }
    const int normalizedIndex = index < 0
        ? m_pageStack->count()
        : qMin(index, m_pageStack->count());
    m_pageStack->insertWidget(normalizedIndex, page);
    const QString title = page->windowTitle().isEmpty()
        ? page->objectName()
        : page->windowTitle();
    m_pageList->insertItem(normalizedIndex, title);
    if (m_pageList->currentRow() < 0) {
        m_pageList->setCurrentRow(0);
    }
}

int RibbonCustomizeDialog::indexOf(QWidget *page) const
{
    return m_pageStack->indexOf(page);
}

QWidget *RibbonCustomizeDialog::currentPage() const
{
    return m_pageStack->currentWidget();
}

void RibbonCustomizeDialog::setCurrentPage(QWidget *page)
{
    setCurrentPageIndex(indexOf(page));
}

int RibbonCustomizeDialog::currentPageIndex() const
{
    return m_pageStack->currentIndex();
}

void RibbonCustomizeDialog::setCurrentPageIndex(int index)
{
    if (index >= 0 && index < m_pageStack->count()) {
        m_pageList->setCurrentRow(index);
        m_pageStack->setCurrentIndex(index);
    }
}

int RibbonCustomizeDialog::pageCount() const
{
    return m_pageStack->count();
}

QWidget *RibbonCustomizeDialog::pageByIndex(int index) const
{
    return m_pageStack->widget(index);
}

void RibbonCustomizeDialog::accept()
{
    QDialog::accept();
}

void RibbonCustomizeDialog::reject()
{
    QDialog::reject();
}

void RibbonCustomizeDialog::showEvent(QShowEvent *event)
{
    QDialog::showEvent(event);
}

void RibbonCustomizeDialog::hideEvent(QHideEvent *event)
{
    QDialog::hideEvent(event);
}

RibbonQuickAccessBarCustomizePage::RibbonQuickAccessBarCustomizePage(
    RibbonBar *ribbonBar)
    : QWidget(ribbonBar)
    , m_ribbonBar(ribbonBar)
{
}

RibbonQuickAccessBarCustomizePage::~RibbonQuickAccessBarCustomizePage() =
    default;

RibbonBar *RibbonQuickAccessBarCustomizePage::ribbonBar() const
{
    return m_ribbonBar;
}

void RibbonQuickAccessBarCustomizePage::addCustomCategory(
    const QString &strCategory)
{
    if (!m_categories.contains(strCategory)) {
        m_categories.append(strCategory);
    }
}

void RibbonQuickAccessBarCustomizePage::addSeparatorCategory(
    const QString &strCategory)
{
    addCustomCategory(strCategory);
}

void RibbonQuickAccessBarCustomizePage::accepted()
{
}

void RibbonQuickAccessBarCustomizePage::showEvent(QShowEvent *event)
{
    QWidget::showEvent(event);
}

RibbonBarCustomizePage::RibbonBarCustomizePage(RibbonBar *ribbonBar)
    : QWidget(ribbonBar)
    , m_ribbonBar(ribbonBar)
{
}

RibbonBarCustomizePage::~RibbonBarCustomizePage() = default;

RibbonBar *RibbonBarCustomizePage::ribbonBar() const
{
    return m_ribbonBar;
}

void RibbonBarCustomizePage::addCustomCategory(const QString &strCategory)
{
    if (!m_categories.contains(strCategory)) {
        m_categories.append(strCategory);
    }
}

void RibbonBarCustomizePage::addSeparatorCategory(const QString &strCategory)
{
    addCustomCategory(strCategory);
}

void RibbonBarCustomizePage::accepted()
{
}

void RibbonBarCustomizePage::rejected()
{
}

void RibbonBarCustomizePage::showEvent(QShowEvent *event)
{
    QWidget::showEvent(event);
}

void RibbonBarCustomizePage::hideEvent(QHideEvent *event)
{
    QWidget::hideEvent(event);
}

QColor contextColor(ContextColor color)
{
    return contextColorToColor(color);
}

} // namespace LqRibbon
