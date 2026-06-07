#ifndef LQRIBBON_H
#define LQRIBBON_H

#include <QAction>
#include <QByteArray>
#include <QCompleter>
#include <QDebug>
#include <QFrame>
#include <QGridLayout>
#include <QHash>
#include <QIcon>
#include <QLabel>
#include <QLineEdit>
#include <QList>
#include <QMainWindow>
#include <QPaintEvent>
#include <QPointer>
#include <QPoint>
#include <QResizeEvent>
#include <QStatusBar>
#include <QStringList>
#include <QStringListModel>
#include <QTabWidget>
#include <QToolBar>
#include <QToolButton>
#include <QVBoxLayout>
#include <QWidget>

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

private:
    QToolButton *createButton(QAction *action, Qt::ToolButtonStyle buttonStyle);
    QGridLayout *smallButtonLayout();

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

signals:
    void pageChanged(int index);
    void searchTextChanged(const QString &strText);
    void searchAccepted(const QString &strText);
    void searchSuggestionActivated(const QString &strText);
    void searchActionTriggered(QAction *action);
    void recentSearchActionsChanged();

protected:
    void paintEvent(QPaintEvent *event) override;
    void resizeEvent(QResizeEvent *event) override;

private:
    void updateSearchGeometry();
    void updateQuickAccessGeometry();
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
    QToolBar *m_quickAccessBar;
    QStringList m_searchSuggestionList;
    QList<SearchCommand> m_searchCommandList;
    QHash<QString, QPointer<QAction>> m_searchActionIndex;
    QList<QPointer<QAction>> m_recentSearchActionList;
    QStringListModel *m_searchSuggestionModel;
    QCompleter *m_searchCompleter;
    bool m_searchActionTriggerEnabled;
    int m_recentSearchLimit;
    bool m_frameThemeEnabled;
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

protected:
    bool nativeEvent(const QByteArray &eventType, void *message, long *result) override;

private:
    bool isNativeCaptionPoint(const QPoint &globalPoint) const;
    int nativeHitTestResult(const QPoint &globalPoint) const;
    int effectiveNativeResizeBorderWidth() const;

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
