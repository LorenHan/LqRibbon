#include "LqRibbon.h"

#include <QAbstractItemView>
#include <QGridLayout>
#include <QPainter>
#include <QPaintEvent>
#include <QTabBar>

#ifdef Q_OS_WIN
#include <qt_windows.h>
#ifndef SM_CXPADDEDBORDER
#define SM_CXPADDEDBORDER 92
#endif
#endif

namespace {

const char ribbonStyleSheet[] =
    "LqRibbon--RibbonBar {"
    "    background: #f5f7fb;"
    "}"
    "QTabWidget::pane {"
    "    border-top: 1px solid #9eb6d8;"
    "    background: #f5f7fb;"
    "}"
    "QTabBar::tab {"
    "    min-width: 76px;"
    "    min-height: 24px;"
    "    padding: 3px 12px;"
    "    color: #ffffff;"
    "    border: 1px solid transparent;"
    "    border-bottom: none;"
    "}"
    "QTabBar::tab:selected {"
    "    background: #ffffff;"
    "    color: #1f1f1f;"
    "    border-color: #9eb6d8;"
    "}"
    "QTabBar::tab:hover:!selected {"
    "    background: #386caf;"
    "    border-color: #b7cbe6;"
    "}"
    "QLineEdit#lqRibbonSearchEdit {"
    "    min-height: 22px;"
    "    padding: 1px 8px;"
    "    border: 1px solid #b7cbe6;"
    "    border-radius: 2px;"
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
    "    background: #ffffff;"
    "    border: 1px solid #c8d5e5;"
    "    border-radius: 2px;"
    "    margin: 4px 2px 3px 2px;"
    "}"
    "LqRibbon--RibbonGroup QLabel#lqRibbonGroupTitle {"
    "    color: #4b4b4b;"
    "    font-size: 11px;"
    "    padding: 1px 4px 3px 4px;"
    "}"
    "LqRibbon--RibbonGroup QToolButton {"
    "    border: 1px solid transparent;"
    "    border-radius: 2px;"
    "    padding: 3px;"
    "    color: #202020;"
    "}"
    "LqRibbon--RibbonGroup QToolButton:hover {"
    "    background: #dcecff;"
    "    border-color: #80a9dc;"
    "}"
    "LqRibbon--RibbonGroup QToolButton:pressed {"
    "    background: #c5ddfa;"
    "    border-color: #5f95d0;"
    "}";

} // namespace

namespace LqRibbon {

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
    setMinimumHeight(92);
    setMinimumWidth(80);

    m_titleLabel->setObjectName(QStringLiteral("lqRibbonGroupTitle"));
    m_titleLabel->setAlignment(Qt::AlignCenter);

    m_contentLayout->setContentsMargins(5, 4, 5, 1);
    m_contentLayout->setSpacing(2);
    m_contentLayout->setAlignment(Qt::AlignLeft | Qt::AlignTop);

    QVBoxLayout *mainLayout = new QVBoxLayout(this);
    mainLayout->setContentsMargins(0, 0, 0, 0);
    mainLayout->setSpacing(0);
    mainLayout->addLayout(m_contentLayout, 1);
    mainLayout->addWidget(m_titleLabel);
}

QAction *RibbonGroup::addAction(const QIcon &icon,
                                const QString &strText,
                                Qt::ToolButtonStyle buttonStyle)
{
    QAction *action = new QAction(icon, strText, this);
    addAction(action, buttonStyle);
    return action;
}

void RibbonGroup::addAction(QAction *action, Qt::ToolButtonStyle buttonStyle)
{
    if (!action) {
        return;
    }

    QToolButton *button = createButton(action, buttonStyle);
    if (buttonStyle == Qt::ToolButtonTextBesideIcon) {
        smallButtonLayout()->addWidget(button, m_smallButtonRow, m_smallButtonColumn);
        ++m_smallButtonRow;
        if (m_smallButtonRow >= 3) {
            m_smallButtonRow = 0;
            ++m_smallButtonColumn;
        }
        return;
    }

    m_contentLayout->addWidget(button);
}

void RibbonGroup::addWidget(QWidget *widget)
{
    if (!widget) {
        return;
    }

    widget->setParent(this);
    m_contentLayout->addWidget(widget);
}

QString RibbonGroup::title() const
{
    return m_titleLabel->text();
}

void RibbonGroup::setTitle(const QString &strTitle)
{
    m_titleLabel->setText(strTitle);
}

QToolButton *RibbonGroup::createButton(QAction *action, Qt::ToolButtonStyle buttonStyle)
{
    QToolButton *button = new QToolButton(this);
    button->setDefaultAction(action);
    button->setAutoRaise(true);
    button->setToolButtonStyle(buttonStyle);
    button->setFocusPolicy(Qt::NoFocus);
    button->setIconSize(buttonStyle == Qt::ToolButtonTextUnderIcon ? QSize(28, 28) : QSize(18, 18));

    if (buttonStyle == Qt::ToolButtonTextUnderIcon) {
        button->setMinimumSize(66, 62);
        button->setSizePolicy(QSizePolicy::Preferred, QSizePolicy::Expanding);
    } else {
        button->setMinimumSize(92, 24);
        button->setSizePolicy(QSizePolicy::Preferred, QSizePolicy::Fixed);
    }

    return button;
}

QGridLayout *RibbonGroup::smallButtonLayout()
{
    if (m_smallButtonLayout) {
        return m_smallButtonLayout;
    }

    m_smallButtonWidget = new QWidget(this);
    m_smallButtonLayout = new QGridLayout(m_smallButtonWidget);
    m_smallButtonLayout->setContentsMargins(0, 0, 0, 0);
    m_smallButtonLayout->setSpacing(1);
    m_contentLayout->addWidget(m_smallButtonWidget);
    return m_smallButtonLayout;
}

RibbonPage::RibbonPage(const QString &strTitle, QWidget *parent)
    : QWidget(parent)
    , m_strTitle(strTitle)
    , m_groupLayout(new QHBoxLayout)
{
    m_groupLayout->setContentsMargins(3, 2, 3, 2);
    m_groupLayout->setSpacing(1);
    m_groupLayout->addStretch(1);

    QVBoxLayout *mainLayout = new QVBoxLayout(this);
    mainLayout->setContentsMargins(0, 0, 0, 0);
    mainLayout->addLayout(m_groupLayout);
}

RibbonGroup *RibbonPage::addGroup(const QString &strTitle)
{
    RibbonGroup *group = new RibbonGroup(strTitle, this);
    const int stretchIndex = m_groupLayout->count() - 1;
    m_groupLayout->insertWidget(stretchIndex, group);
    return group;
}

QString RibbonPage::title() const
{
    return m_strTitle;
}

void RibbonPage::setTitle(const QString &strTitle)
{
    if (m_strTitle == strTitle) {
        return;
    }

    m_strTitle = strTitle;
    emit titleChanged(strTitle);
}

RibbonBar::RibbonBar(QWidget *parent)
    : QTabWidget(parent)
    , m_searchEdit(new QLineEdit(this))
    , m_quickAccessBar(new QToolBar(this))
    , m_searchSuggestionModel(new QStringListModel(this))
    , m_searchCompleter(new QCompleter(m_searchSuggestionModel, this))
    , m_searchActionTriggerEnabled(true)
    , m_recentSearchLimit(8)
    , m_frameThemeEnabled(false)
{
    setDocumentMode(false);
    setMovable(false);
    setTabPosition(QTabWidget::North);
    setFixedHeight(120);

    m_searchEdit->setObjectName(QStringLiteral("lqRibbonSearchEdit"));
    m_searchEdit->setPlaceholderText(tr("Search"));
    m_searchEdit->setClearButtonEnabled(true);
    m_searchEdit->hide();
    m_searchCompleter->setCaseSensitivity(Qt::CaseInsensitive);
    m_searchCompleter->setFilterMode(Qt::MatchContains);
    m_searchCompleter->setCompletionMode(QCompleter::PopupCompletion);
    m_searchCompleter->setMaxVisibleItems(8);
    m_searchCompleter->popup()->setObjectName(
        QStringLiteral("lqRibbonSearchSuggestionPopup"));
    m_searchEdit->setCompleter(m_searchCompleter);

    m_quickAccessBar->setObjectName(QStringLiteral("lqRibbonQuickAccessBar"));
    m_quickAccessBar->setMovable(false);
    m_quickAccessBar->setFloatable(false);
    m_quickAccessBar->setIconSize(QSize(16, 16));
    m_quickAccessBar->setToolButtonStyle(Qt::ToolButtonIconOnly);
    m_quickAccessBar->hide();

    connect(this, &QTabWidget::currentChanged, this, &RibbonBar::pageChanged);
    connect(m_searchEdit, &QLineEdit::textChanged,
            this, &RibbonBar::searchTextChanged);
    connect(m_searchEdit, &QLineEdit::returnPressed, this, [this]() {
        const QString strText = m_searchEdit->text();
        if (!triggerSearchAction(strText)) {
            emit searchAccepted(strText);
        }
    });
    connect(m_searchCompleter,
            QOverload<const QString &>::of(&QCompleter::activated),
            this, [this](const QString &strText) {
                m_searchEdit->setText(strText);
                emit searchSuggestionActivated(strText);
                if (!triggerSearchAction(strText)) {
                    emit searchAccepted(strText);
                }
            });

    updateStyleSheet();
    updateQuickAccessGeometry();
    updateSearchGeometry();
}

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
    return newPage;
}

RibbonPage *RibbonBar::page(int index) const
{
    return qobject_cast<RibbonPage *>(widget(index));
}

RibbonPage *RibbonBar::currentPage() const
{
    return page(currentIndex());
}

QLineEdit *RibbonBar::searchLineEdit() const
{
    return m_searchEdit;
}

QCompleter *RibbonBar::searchCompleter() const
{
    return m_searchCompleter;
}

void RibbonBar::setSearchVisible(bool visible)
{
    m_searchEdit->setVisible(visible);
    updateSearchGeometry();
}

bool RibbonBar::isSearchVisible() const
{
    return m_searchEdit->isVisible();
}

void RibbonBar::setSearchPlaceholderText(const QString &strText)
{
    m_searchEdit->setPlaceholderText(strText);
}

QString RibbonBar::searchText() const
{
    return m_searchEdit->text();
}

void RibbonBar::setSearchText(const QString &strText)
{
    m_searchEdit->setText(strText);
}

void RibbonBar::setSearchSuggestions(const QStringList &strList)
{
    m_searchSuggestionList = strList;
    updateSearchSuggestions();
}

QStringList RibbonBar::searchSuggestions() const
{
    return m_searchSuggestionModel->stringList();
}

void RibbonBar::clearSearchSuggestions()
{
    m_searchSuggestionList.clear();
    updateSearchSuggestions();
}

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
}

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
}

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

QAction *RibbonBar::searchAction(const QString &strText) const
{
    return m_searchActionIndex.value(normalizedSearchText(strText)).data();
}

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

void RibbonBar::setSearchActionTriggerEnabled(bool enabled)
{
    m_searchActionTriggerEnabled = enabled;
}

bool RibbonBar::isSearchActionTriggerEnabled() const
{
    return m_searchActionTriggerEnabled;
}

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

void RibbonBar::clearRecentSearchActions()
{
    if (m_recentSearchActionList.isEmpty()) {
        return;
    }

    m_recentSearchActionList.clear();
    updateSearchSuggestions();
    emit recentSearchActionsChanged();
}

void RibbonBar::setRecentSearchLimit(int count)
{
    m_recentSearchLimit = qMax(0, count);
    while (m_recentSearchActionList.count() > m_recentSearchLimit) {
        m_recentSearchActionList.removeLast();
    }

    updateSearchSuggestions();
    emit recentSearchActionsChanged();
}

int RibbonBar::recentSearchLimit() const
{
    return m_recentSearchLimit;
}

QToolBar *RibbonBar::quickAccessBar() const
{
    return m_quickAccessBar;
}

QAction *RibbonBar::addQuickAccessAction(const QIcon &icon, const QString &strText)
{
    QAction *action = new QAction(icon, strText, this);
    addQuickAccessAction(action);
    return action;
}

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

void RibbonBar::clearQuickAccessActions()
{
    m_quickAccessBar->clear();
    m_quickAccessBar->hide();
    updateQuickAccessGeometry();
    updateStyleSheet();
}

void RibbonBar::setCurrentPageIndex(int index)
{
    setCurrentIndex(index);
}

void RibbonBar::setFrameThemeEnabled(bool enabled)
{
    if (m_frameThemeEnabled == enabled) {
        return;
    }

    m_frameThemeEnabled = enabled;
    updateStyleSheet();
}

bool RibbonBar::isFrameThemeEnabled() const
{
    return m_frameThemeEnabled;
}

void RibbonBar::paintEvent(QPaintEvent *event)
{
    QTabWidget::paintEvent(event);

    if (!m_frameThemeEnabled) {
        return;
    }

    QPainter painter(this);
    painter.fillRect(0, 0, width(), 30, QColor(QStringLiteral("#2b579a")));
}

void RibbonBar::resizeEvent(QResizeEvent *event)
{
    QTabWidget::resizeEvent(event);
    updateQuickAccessGeometry();
    updateSearchGeometry();
    updateStyleSheet();
}

void RibbonBar::updateSearchGeometry()
{
    const int searchWidth = 240;
    const int searchHeight = 24;
    const int rightMargin = 10;
    const int topMargin = 3;
    const int x = qMax(rightMargin, width() - searchWidth - rightMargin);

    m_searchEdit->setGeometry(x, topMargin, searchWidth, searchHeight);
    m_searchEdit->raise();
}

void RibbonBar::updateQuickAccessGeometry()
{
    const int topMargin = 3;
    const int rightMargin = 10;
    const int searchGap = 8;
    const int searchWidth = m_searchEdit->isHidden() ? 0 : 240;
    const int barHeight = 24;
    const int maxWidth = qMax(0, width() / 3);
    const int barWidth = qMin(m_quickAccessBar->sizeHint().width(), maxWidth);
    const int rightReservedWidth = rightMargin + searchWidth + searchGap;
    const int x = qMax(rightMargin, width() - rightReservedWidth - barWidth);

    m_quickAccessBar->setGeometry(x, topMargin, barWidth, barHeight);
    m_quickAccessBar->raise();
}

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
}

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

QString RibbonBar::normalizedSearchText(const QString &strText) const
{
    QString strNormalizedText = strText.trimmed().toCaseFolded();
    strNormalizedText.remove(QLatin1Char('&'));
    return strNormalizedText;
}

QString RibbonBar::searchActionText(QAction *action) const
{
    QString strText = action->text();
    strText.remove(QLatin1Char('&'));
    return strText.trimmed();
}

void RibbonBar::updateStyleSheet()
{
    setStyleSheet(QString::fromLatin1(ribbonStyleSheet));
}

RibbonMainWindow::RibbonMainWindow(QWidget *parent)
    : QMainWindow(parent)
    , m_rootWidget(new QWidget(this))
    , m_rootLayout(new QVBoxLayout(m_rootWidget))
    , m_ribbonBar(new RibbonBar(m_rootWidget))
    , m_nativeFrameEnabled(false)
    , m_nativeCaptionHeight(30)
    , m_nativeResizeBorderWidth(0)
{
    m_rootLayout->setContentsMargins(0, 0, 0, 0);
    m_rootLayout->setSpacing(0);
    m_rootLayout->addWidget(m_ribbonBar);
    QMainWindow::setCentralWidget(m_rootWidget);
}

RibbonMainWindow::~RibbonMainWindow()
{
}

RibbonBar *RibbonMainWindow::ribbonBar() const
{
    return m_ribbonBar;
}

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
    m_rootLayout->addWidget(widget, 1);
}

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

    if (wasVisible) {
        show();
    }
}

bool RibbonMainWindow::isNativeFrameEnabled() const
{
    return m_nativeFrameEnabled;
}

void RibbonMainWindow::setNativeCaptionHeight(int height)
{
    m_nativeCaptionHeight = qMax(0, height);
}

int RibbonMainWindow::nativeCaptionHeight() const
{
    return m_nativeCaptionHeight;
}

void RibbonMainWindow::setNativeResizeBorderWidth(int width)
{
    m_nativeResizeBorderWidth = qMax(0, width);
}

int RibbonMainWindow::nativeResizeBorderWidth() const
{
    return m_nativeResizeBorderWidth;
}

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
#endif

    return HTCLIENT;
}

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
    return m_nativeResizeBorderWidth;
#endif
}

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
    const bool canMaximize = (!hasCustomButtons
        || flags.testFlag(Qt::WindowMaximizeButtonHint)) && canResize;
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
        (canMaximize && !isMaximized) ? enabled : disabled);
    EnableMenuItem(systemMenu, SC_CLOSE, canClose ? enabled : disabled);
#else
    Q_UNUSED(menuHandle)
#endif
}

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

bool RibbonMainWindow::canNativeResizeHorizontally() const
{
    return minimumWidth() < maximumWidth();
}

bool RibbonMainWindow::canNativeResizeVertically() const
{
    return minimumHeight() < maximumHeight();
}
} // namespace LqRibbon
