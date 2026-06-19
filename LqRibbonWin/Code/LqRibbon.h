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

///
/// \brief The RibbonGroup class displays one titled group of Ribbon commands.
///
/// A group arranges large buttons, small command rows, and custom widgets under
/// one title. The layout keeps existing Ribbon pages readable while switching
/// to LqRibbon.
///
class RibbonGroup : public QFrame
{
    Q_OBJECT

public:
    ///
    /// \brief RibbonGroup::RibbonGroup
    /// Creates a Ribbon command group with a visible title.
    /// \param strTitle Group title shown at the bottom of the group.
    /// \param parent Parent widget that owns the group.
    ///
    explicit RibbonGroup(const QString &strTitle, QWidget *parent = nullptr);

    ///
    /// \brief RibbonGroup::addAction
    /// Creates an action, adds a matching button to the group, and returns it.
    /// \param icon Icon displayed by the generated button.
    /// \param strText Button text and action text.
    /// \param buttonStyle Qt tool button style used by the generated button.
    /// \return Newly created action owned by the group.
    ///
    QAction *addAction(const QIcon &icon,
                       const QString &strText,
                       Qt::ToolButtonStyle buttonStyle);
    ///
    /// \brief RibbonGroup::addAction
    /// Adds an existing action to the group with the requested button style.
    /// \param action Existing action to expose in the Ribbon group.
    /// \param buttonStyle Qt tool button style used by the generated button.
    ///
    void addAction(QAction *action, Qt::ToolButtonStyle buttonStyle);
    ///
    /// \brief RibbonGroup::addWidget
    /// Adds a custom widget to the group content area.
    /// \param widget Widget that becomes owned by the group layout.
    ///
    void addWidget(QWidget *widget);

    ///
    /// \brief RibbonGroup::title
    /// Returns the current group title text.
    /// \return Title shown at the bottom of the group.
    ///
    QString title() const;
    ///
    /// \brief RibbonGroup::setTitle
    /// Changes the visible title text.
    /// \param strTitle New group title.
    ///
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

///
/// \brief The RibbonPage class is one tab page inside a Ribbon bar.
///
/// Pages contain Ribbon groups from left to right. A page title is mirrored to
/// the Ribbon tab text and emits titleChanged when renamed.
///
class RibbonPage : public QWidget
{
    Q_OBJECT

public:
    ///
    /// \brief RibbonPage::RibbonPage
    /// Creates a page that can hold Ribbon groups.
    /// \param strTitle Page title shown by the corresponding tab.
    /// \param parent Parent widget that owns the page.
    ///
    explicit RibbonPage(const QString &strTitle, QWidget *parent = nullptr);

    ///
    /// \brief RibbonPage::addGroup
    /// Creates and appends a titled command group.
    /// \param strTitle Title shown by the new group.
    /// \return Newly created group owned by the page.
    ///
    RibbonGroup *addGroup(const QString &strTitle);
    ///
    /// \brief RibbonPage::title
    /// Returns the current page title.
    /// \return Text shown by the Ribbon tab.
    ///
    QString title() const;
    ///
    /// \brief RibbonPage::setTitle
    /// Updates the page title and notifies the Ribbon bar.
    /// \param strTitle New page title.
    ///
    void setTitle(const QString &strTitle);

signals:
    ///
    /// \brief RibbonPage::titleChanged
    /// Emitted when setTitle changes the visible page title.
    /// \param strTitle New page title.
    ///
    void titleChanged(const QString &strTitle);

private:
    QString m_strTitle;
    QHBoxLayout *m_groupLayout;
};

///
/// \brief The RibbonBar class implements the tabbed Ribbon command surface.
///
/// RibbonBar owns pages, search, quick access commands, and optional themed
/// frame chrome. It is designed to be embedded at the top of RibbonMainWindow
/// but can also be used as a standalone widget.
///
class RibbonBar : public QTabWidget
{
    Q_OBJECT

public:
    ///
    /// \brief RibbonBar::RibbonBar
    /// Creates an empty Ribbon bar with search and quick access support.
    /// \param parent Parent widget.
    ///
    explicit RibbonBar(QWidget *parent = nullptr);
    ///
    /// \brief RibbonBar::~RibbonBar
    /// Releases popup, search, and frame-control resources.
    ///
    ~RibbonBar() override;

    ///
    /// \brief RibbonBar::addPage
    /// Creates and appends a Ribbon page.
    /// \param strTitle Text displayed by the new tab.
    /// \return Newly created page owned by the Ribbon bar.
    ///
    RibbonPage *addPage(const QString &strTitle);
    ///
    /// \brief RibbonBar::page
    /// Returns the page at the requested tab index.
    /// \param index Zero-based page index.
    /// \return Page pointer or nullptr when index is invalid.
    ///
    RibbonPage *page(int index) const;
    ///
    /// \brief RibbonBar::currentPage
    /// Returns the currently selected page.
    /// \return Current page pointer or nullptr when no page exists.
    ///
    RibbonPage *currentPage() const;
    ///
    /// \brief RibbonBar::searchLineEdit
    /// Returns the editable search box widget.
    /// \return Search line edit owned by the Ribbon bar.
    ///
    QLineEdit *searchLineEdit() const;
    ///
    /// \brief RibbonBar::searchCompleter
    /// Returns the completer used by the search box.
    /// \return Search completer owned by the Ribbon bar.
    ///
    QCompleter *searchCompleter() const;
    ///
    /// \brief RibbonBar::setSearchVisible
    /// Shows or hides the title-bar search box.
    /// \param visible true to show the search box, false to hide it.
    ///
    void setSearchVisible(bool visible);
    ///
    /// \brief RibbonBar::isSearchVisible
    /// Checks whether the search box is currently visible.
    /// \return true when search is visible.
    ///
    bool isSearchVisible() const;
    ///
    /// \brief RibbonBar::setSearchPlaceholderText
    /// Sets the placeholder text shown by the search box.
    /// \param strText Placeholder text.
    ///
    void setSearchPlaceholderText(const QString &strText);
    ///
    /// \brief RibbonBar::searchText
    /// Returns the current search text.
    /// \return Text currently entered by the user.
    ///
    QString searchText() const;
    ///
    /// \brief RibbonBar::setSearchText
    /// Replaces the current search text.
    /// \param strText New search text.
    ///
    void setSearchText(const QString &strText);
    ///
    /// \brief RibbonBar::setSearchSuggestions
    /// Replaces the plain text suggestion list used by the completer.
    /// \param strList Search suggestion strings.
    ///
    void setSearchSuggestions(const QStringList &strList);
    ///
    /// \brief RibbonBar::searchSuggestions
    /// Returns the configured plain text suggestions.
    /// \return Search suggestion strings.
    ///
    QStringList searchSuggestions() const;
    ///
    /// \brief RibbonBar::clearSearchSuggestions
    /// Removes all plain text search suggestions.
    ///
    void clearSearchSuggestions();
    ///
    /// \brief RibbonBar::registerSearchAction
    /// Registers an action so it can be found and triggered by search.
    /// \param action Action to include in Ribbon search results.
    /// \param strKeywords Additional keywords matched with the action text.
    ///
    void registerSearchAction(QAction *action,
                              const QStringList &strKeywords = QStringList());
    ///
    /// \brief RibbonBar::unregisterSearchAction
    /// Removes an action from the searchable command list.
    /// \param action Action to remove.
    ///
    void unregisterSearchAction(QAction *action);
    ///
    /// \brief RibbonBar::searchActions
    /// Returns all valid searchable actions.
    /// \return List of registered actions.
    ///
    QList<QAction *> searchActions() const;
    ///
    /// \brief RibbonBar::searchAction
    /// Finds the best matching searchable action for the text.
    /// \param strText Text typed in the search box.
    /// \return Matching action or nullptr when nothing matches.
    ///
    QAction *searchAction(const QString &strText) const;
    ///
    /// \brief RibbonBar::triggerSearchAction
    /// Triggers the best matching action for the text.
    /// \param strText Text typed in the search box.
    /// \return true when an action was found and triggered.
    ///
    bool triggerSearchAction(const QString &strText);
    ///
    /// \brief RibbonBar::setSearchActionTriggerEnabled
    /// Enables or disables automatic action triggering from search.
    /// \param enabled true to trigger registered actions from search.
    ///
    void setSearchActionTriggerEnabled(bool enabled);
    ///
    /// \brief RibbonBar::isSearchActionTriggerEnabled
    /// Returns whether search can trigger registered actions.
    /// \return true when action triggering is enabled.
    ///
    bool isSearchActionTriggerEnabled() const;
    ///
    /// \brief RibbonBar::recentSearchActions
    /// Returns recently triggered searchable actions.
    /// \return Recent action list in newest-first order.
    ///
    QList<QAction *> recentSearchActions() const;
    ///
    /// \brief RibbonBar::clearRecentSearchActions
    /// Clears the recent search action history.
    ///
    void clearRecentSearchActions();
    ///
    /// \brief RibbonBar::setRecentSearchLimit
    /// Sets the maximum number of recent search actions to keep.
    /// \param count Maximum history length.
    ///
    void setRecentSearchLimit(int count);
    ///
    /// \brief RibbonBar::recentSearchLimit
    /// Returns the maximum number of recent search actions.
    /// \return Recent search history limit.
    ///
    int recentSearchLimit() const;
    ///
    /// \brief RibbonBar::quickAccessBar
    /// Returns the title-bar quick access toolbar.
    /// \return Quick access toolbar owned by the Ribbon bar.
    ///
    QToolBar *quickAccessBar() const;
    ///
    /// \brief RibbonBar::addQuickAccessAction
    /// Creates and adds an action to the quick access toolbar.
    /// \param icon Icon displayed by the toolbar button.
    /// \param strText Action text and tooltip source.
    /// \return Newly created action owned by the toolbar.
    ///
    QAction *addQuickAccessAction(const QIcon &icon, const QString &strText);
    ///
    /// \brief RibbonBar::addQuickAccessAction
    /// Adds an existing action to the quick access toolbar.
    /// \param action Action to expose in the quick access toolbar.
    ///
    void addQuickAccessAction(QAction *action);
    ///
    /// \brief RibbonBar::addTitleButton
    /// Adds a text button to the themed title bar.
    /// \param icon Icon displayed by the title button.
    /// \param strText Button text and tooltip source.
    /// \return Newly created action owned by the Ribbon bar.
    ///
    QAction *addTitleButton(const QIcon &icon, const QString &strText);
    ///
    /// \brief RibbonBar::clearQuickAccessActions
    /// Removes all actions from the quick access toolbar.
    ///
    void clearQuickAccessActions();
    ///
    /// \brief RibbonBar::setCurrentPageIndex
    /// Selects a Ribbon page by index.
    /// \param index Zero-based tab index.
    ///
    void setCurrentPageIndex(int index);
    ///
    /// \brief RibbonBar::setRibbonMinimized
    /// Collapses or expands the Ribbon command area while keeping tabs visible.
    /// \param minimized true to collapse command pages, false to expand them.
    ///
    void setRibbonMinimized(bool minimized);
    ///
    /// \brief RibbonBar::isRibbonMinimized
    /// Checks whether only the Ribbon tabs are currently visible.
    /// \return true when the command area is collapsed.
    ///
    bool isRibbonMinimized() const;
    ///
    /// \brief RibbonBar::setFrameThemeEnabled
    /// Enables themed title-bar painting and frame controls.
    /// \param enabled true to paint Ribbon frame chrome.
    ///
    void setFrameThemeEnabled(bool enabled);
    ///
    /// \brief RibbonBar::isFrameThemeEnabled
    /// Returns whether themed frame chrome is enabled.
    /// \return true when custom frame painting is active.
    ///
    bool isFrameThemeEnabled() const;
    ///
    /// \brief RibbonBar::isWindowControlPoint
    /// Checks whether a point is inside the painted window-control area.
    /// \param point Point in RibbonBar coordinates.
    /// \return true when the point is on minimize, maximize, or close buttons.
    ///
    bool isWindowControlPoint(const QPoint &point) const;

signals:
    ///
    /// \brief RibbonBar::pageChanged
    /// Emitted after the selected Ribbon page changes.
    /// \param index New selected page index.
    ///
    void pageChanged(int index);
    ///
    /// \brief RibbonBar::searchTextChanged
    /// Emitted when the search text changes.
    /// \param strText New search text.
    ///
    void searchTextChanged(const QString &strText);
    ///
    /// \brief RibbonBar::searchAccepted
    /// Emitted when the user accepts the current search text.
    /// \param strText Accepted search text.
    ///
    void searchAccepted(const QString &strText);
    ///
    /// \brief RibbonBar::searchSuggestionActivated
    /// Emitted when a suggestion row is activated.
    /// \param strText Activated suggestion text.
    ///
    void searchSuggestionActivated(const QString &strText);
    ///
    /// \brief RibbonBar::searchActionTriggered
    /// Emitted after a registered search action is triggered.
    /// \param action Triggered action.
    ///
    void searchActionTriggered(QAction *action);
    ///
    /// \brief RibbonBar::recentSearchActionsChanged
    /// Emitted when the recent search action history changes.
    ///
    void recentSearchActionsChanged();
    ///
    /// \brief RibbonBar::ribbonMinimizedChanged
    /// Emitted after the Ribbon command area is collapsed or expanded.
    /// \param minimized true when the command area is collapsed.
    ///
    void ribbonMinimizedChanged(bool minimized);

protected:
    bool event(QEvent *event) override;
    bool eventFilter(QObject *object, QEvent *event) override;
    void paintEvent(QPaintEvent *event) override;
    void resizeEvent(QResizeEvent *event) override;

private:
    void updateRibbonTabGeometry();
    void updateSearchGeometry();
    void updateTitleButtonGeometry();
    void updateQuickAccessGeometry();
    void updateRibbonMetrics();
    void setupWindowControlButton(QToolButton *button);
    void updateWindowControlGeometry();
    void updateWindowControlState();
    void updateWindowControlVisibility();
    void updateLocalizedText();
    int windowControlWidth() const;
    void updateSearchPopup();
    void hideSearchPopup();
    void finishSearch();
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
    QAction *m_searchLineAction;
    QToolBar *m_quickAccessBar;
    QToolBar *m_titleButtonBar;
    QToolButton *m_minimizeButton;
    QToolButton *m_maximizeButton;
    QToolButton *m_closeButton;
    QToolButton *m_collapseButton;
    QStringList m_searchSuggestionList;
    QList<SearchCommand> m_searchCommandList;
    QHash<QString, QPointer<QAction>> m_searchActionIndex;
    QList<QPointer<QAction>> m_recentSearchActionList;
    QStringListModel *m_searchSuggestionModel;
    QCompleter *m_searchCompleter;
    bool m_searchActionTriggerEnabled;
    int m_recentSearchLimit;
    bool m_frameThemeEnabled;
    bool m_ribbonMinimized;
    bool m_searchVisibleExplicitlySet;
    bool m_searchPlaceholderExplicitlySet;
};

///
/// \brief The RibbonMainWindow class hosts a Ribbon bar and optional frame.
///
/// RibbonMainWindow provides the common Ribbon main-window shape: a Ribbon bar
/// at the top, a central widget below it, flat MDI polish, and optional native
/// frame gesture handling for frameless windows.
///
class RibbonMainWindow : public QMainWindow
{
    Q_OBJECT

public:
    ///
    /// \brief RibbonMainWindow::RibbonMainWindow
    /// Creates a main window with an embedded RibbonBar.
    /// \param parent Parent widget.
    ///
    explicit RibbonMainWindow(QWidget *parent = nullptr);
    ///
    /// \brief RibbonMainWindow::~RibbonMainWindow
    /// Destroys the Ribbon host and restores owned widgets through Qt parenting.
    ///
    ~RibbonMainWindow() override;

    ///
    /// \brief RibbonMainWindow::ribbonBar
    /// Returns the embedded Ribbon bar.
    /// \return RibbonBar owned by the main window.
    ///
    RibbonBar *ribbonBar() const;
    ///
    /// \brief RibbonMainWindow::setCentralWidget
    /// Sets the content widget below the Ribbon bar.
    /// \param widget Widget to place in the central content area.
    ///
    void setCentralWidget(QWidget *widget);
    ///
    /// \brief RibbonMainWindow::setNativeFrameEnabled
    /// Enables native move, resize, system menu, and hit-test behavior.
    /// \param enabled true to use custom native frame handling.
    ///
    void setNativeFrameEnabled(bool enabled);
    ///
    /// \brief RibbonMainWindow::isNativeFrameEnabled
    /// Returns whether native frame handling is enabled.
    /// \return true when native frame gestures are handled by LqRibbon.
    ///
    bool isNativeFrameEnabled() const;
    ///
    /// \brief RibbonMainWindow::setNativeCaptionHeight
    /// Sets the draggable caption height used by native frame handling.
    /// \param height Caption height in logical pixels.
    ///
    void setNativeCaptionHeight(int height);
    ///
    /// \brief RibbonMainWindow::nativeCaptionHeight
    /// Returns the draggable caption height.
    /// \return Caption height in logical pixels.
    ///
    int nativeCaptionHeight() const;
    ///
    /// \brief RibbonMainWindow::setNativeResizeBorderWidth
    /// Sets the fallback resize hit-test border width.
    /// \param width Border width in logical pixels.
    ///
    void setNativeResizeBorderWidth(int width);
    ///
    /// \brief RibbonMainWindow::nativeResizeBorderWidth
    /// Returns the fallback resize hit-test border width.
    /// \return Border width in logical pixels.
    ///
    int nativeResizeBorderWidth() const;
    ///
    /// \brief RibbonMainWindow::setFrameThemeEnabled
    /// Enables themed Ribbon frame painting.
    /// \param enabled true to enable themed frame painting.
    ///
    void setFrameThemeEnabled(bool enabled);
    ///
    /// \brief RibbonMainWindow::isFrameThemeEnabled
    /// Returns whether themed Ribbon frame painting is enabled.
    /// \return true when frame painting is active.
    ///
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
