#ifndef LQRIBBON_H
#define LQRIBBON_H

#include <QAction>
#include <QByteArray>
#include <QCompleter>
#include <QDebug>
#include <QEvent>
#include <QFrame>
#include <QGridLayout>
#include <QHash>
#include <QIcon>
#include <QLabel>
#include <QLineEdit>
#include <QList>
#include <QListView>
#include <QMainWindow>
#include <QPaintEvent>
#include <QPointer>
#include <QPoint>
#include <QResizeEvent>
#include <QStatusBar>
#include <QStringList>
#include <QStringListModel>
#include <QStandardItemModel>
#include <QTabWidget>
#include <QToolBar>
#include <QToolButton>
#include <QVBoxLayout>
#include <QWidget>

QT_BEGIN_NAMESPACE
class QMdiArea;
class QMdiSubWindow;
QT_END_NAMESPACE

namespace LqRibbon {

class RibbonGroup : public QFrame
{
    Q_OBJECT

public:
    explicit RibbonGroup(const QString &strTitle, QWidget *parent = nullptr);

    QAction *addAction(const QIcon &icon,
                       const QString &strText,
                       Qt::ToolButtonStyle buttonStyle);
    void addAction(QAction *action, Qt::ToolButtonStyle buttonStyle);
    void addWidget(QWidget *widget);

    QString title() const;
    void setTitle(const QString &strTitle);

protected:
    bool event(QEvent *event) override;

private:
    QToolButton *createButton(QAction *action, Qt::ToolButtonStyle buttonStyle);
    void addSmallButton(QWidget *widget);
    void setupSmallButton(QToolButton *button);
    QGridLayout *smallButtonLayout();
    void updateMetrics();

private:
    QLabel *m_titleLabel;
    QHBoxLayout *m_contentLayout;
    QGridLayout *m_smallButtonLayout;
    QWidget *m_smallButtonWidget;
    int m_smallButtonRow;
    int m_smallButtonColumn;
};

class RibbonPage : public QWidget
{
    Q_OBJECT

public:
    explicit RibbonPage(const QString &strTitle, QWidget *parent = nullptr);

    RibbonGroup *addGroup(const QString &strTitle);
    QString title() const;
    void setTitle(const QString &strTitle);

signals:
    void titleChanged(const QString &strTitle);

private:
    QString m_strTitle;
    QHBoxLayout *m_groupLayout;
};

class RibbonBar : public QTabWidget
{
    Q_OBJECT

public:
    explicit RibbonBar(QWidget *parent = nullptr);
    ~RibbonBar() override;

    RibbonPage *addPage(const QString &strTitle);
    RibbonPage *page(int index) const;
    RibbonPage *currentPage() const;
    QLineEdit *searchLineEdit() const;
    QCompleter *searchCompleter() const;
    void setSearchVisible(bool visible);
    bool isSearchVisible() const;
    void setSearchPlaceholderText(const QString &strText);
    QString searchText() const;
    void setSearchText(const QString &strText);
    void setSearchSuggestions(const QStringList &strList);
    QStringList searchSuggestions() const;
    void clearSearchSuggestions();
    void registerSearchAction(QAction *action,
                              const QStringList &strKeywords = QStringList());
    void unregisterSearchAction(QAction *action);
    QList<QAction *> searchActions() const;
    QAction *searchAction(const QString &strText) const;
    bool triggerSearchAction(const QString &strText);
    void setSearchActionTriggerEnabled(bool enabled);
    bool isSearchActionTriggerEnabled() const;
    QList<QAction *> recentSearchActions() const;
    void clearRecentSearchActions();
    void setRecentSearchLimit(int count);
    int recentSearchLimit() const;
    QToolBar *quickAccessBar() const;
    QAction *addQuickAccessAction(const QIcon &icon, const QString &strText);
    void addQuickAccessAction(QAction *action);
    void clearQuickAccessActions();
    void setCurrentPageIndex(int index);
    void setFrameThemeEnabled(bool enabled);
    bool isFrameThemeEnabled() const;
    bool isWindowControlPoint(const QPoint &point) const;

signals:
    void pageChanged(int index);
    void searchTextChanged(const QString &strText);
    void searchAccepted(const QString &strText);
    void searchSuggestionActivated(const QString &strText);
    void searchActionTriggered(QAction *action);
    void recentSearchActionsChanged();

protected:
    bool event(QEvent *event) override;
    bool eventFilter(QObject *object, QEvent *event) override;
    void paintEvent(QPaintEvent *event) override;
    void resizeEvent(QResizeEvent *event) override;

private:
    void updateRibbonTabGeometry();
    void updateSearchGeometry();
    void updateQuickAccessGeometry();
    void updateRibbonMetrics();
    void setupWindowControlButton(QToolButton *button);
    void updateWindowControlGeometry();
    void updateWindowControlState();
    void updateWindowControlVisibility();
    int windowControlWidth() const;
    void updateSearchPopup();
    void hideSearchPopup();
    void activateSearchPopupIndex(const QModelIndex &index);
    QList<QAction *> matchedSearchActions(const QString &strText) const;
    void updateSearchSuggestions();
    void recordRecentSearchAction(QAction *action);
    void removeInvalidSearchActions();
    void updateChangedSearchAction();
    void rebuildSearchActionIndex();
    QString normalizedSearchText(const QString &strText) const;
    QString searchActionText(QAction *action) const;
    void updateStyleSheet();

private:
    struct SearchCommand
    {
        QPointer<QAction> action;
        QString strText;
        QStringList strKeywords;
    };

private:
    QLineEdit *m_searchEdit;
    QListView *m_searchPopupView;
    QStandardItemModel *m_searchPopupModel;
    QToolBar *m_quickAccessBar;
    QToolButton *m_minimizeButton;
    QToolButton *m_maximizeButton;
    QToolButton *m_closeButton;
    QStringList m_searchSuggestionList;
    QList<SearchCommand> m_searchCommandList;
    QHash<QString, QPointer<QAction>> m_searchActionIndex;
    QList<QPointer<QAction>> m_recentSearchActionList;
    QStringListModel *m_searchSuggestionModel;
    QCompleter *m_searchCompleter;
    bool m_searchActionTriggerEnabled;
    int m_recentSearchLimit;
    bool m_frameThemeEnabled;
    bool m_searchVisibleExplicitlySet;
};

class RibbonMainWindow : public QMainWindow
{
    Q_OBJECT

public:
    explicit RibbonMainWindow(QWidget *parent = nullptr);
    ~RibbonMainWindow() override;

    RibbonBar *ribbonBar() const;
    void setCentralWidget(QWidget *widget);
    void setNativeFrameEnabled(bool enabled);
    bool isNativeFrameEnabled() const;
    void setNativeCaptionHeight(int height);
    int nativeCaptionHeight() const;
    void setNativeResizeBorderWidth(int width);
    int nativeResizeBorderWidth() const;
    void setFrameThemeEnabled(bool enabled);
    bool isFrameThemeEnabled() const;

protected:
    bool eventFilter(QObject *object, QEvent *event) override;
    bool nativeEvent(const QByteArray &eventType, void *message, long *result) override;

private:
    bool handleNativeFrameEvent(QObject *object, QEvent *event);
    bool isNativeCaptionPoint(const QPoint &globalPoint) const;
    bool startNativeSystemMove(const QPoint &globalPoint);
    bool startNativeSystemResize(const QPoint &globalPoint);
    Qt::Edges nativeResizeEdges(const QPoint &globalPoint) const;
    void updateNativeFrameCursor(const QPoint &globalPoint);
    int nativeHitTestResult(const QPoint &globalPoint) const;
    int effectiveNativeResizeBorderWidth() const;
    bool showNativeSystemMenu(const QPoint &globalPoint);
    void updateNativeSystemMenu(void *menuHandle) const;
    QPoint nativeSystemMenuPoint() const;
    void updateNativeMinMaxInfo(void *minMaxInfo) const;
    bool canNativeResizeHorizontally() const;
    bool canNativeResizeVertically() const;
    bool canNativeMaximize() const;
    void updateNativeWindowStyle();
    void polishMdiObject(QObject *object);
    void polishMdiArea(QMdiArea *mdiArea);
    void polishMdiSubWindow(QMdiSubWindow *subWindow);
    void updateMdiTabBars(QMdiArea *mdiArea);

private:
    QWidget *m_rootWidget;
    QVBoxLayout *m_rootLayout;
    RibbonBar *m_ribbonBar;
    QPointer<QWidget> m_centralWidget;
    bool m_nativeFrameEnabled;
    int m_nativeCaptionHeight;
    int m_nativeResizeBorderWidth;
};

using LqRibbonGroup = RibbonGroup;
using LqRibbonPage = RibbonPage;
using LqRibbonBar = RibbonBar;
using LqRibbonMainWindow = RibbonMainWindow;

} // namespace LqRibbon

using RibbonBar = LqRibbon::RibbonBar;
using RibbonPage = LqRibbon::RibbonPage;
using RibbonGroup = LqRibbon::RibbonGroup;
using RibbonMainWindow = LqRibbon::RibbonMainWindow;

#endif // LQRIBBON_H
