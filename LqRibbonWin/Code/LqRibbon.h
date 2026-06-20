#ifndef LQRIBBON_H
#define LQRIBBON_H

#include <QAction>
#include <QByteArray>
#include <QCompleter>
#include <QColor>
#include <QDebug>
#include <QEvent>
#include <QFont>
#include <QFrame>
#include <QGridLayout>
#include <QHash>
#include <QIcon>
#include <QLabel>
#include <QLineEdit>
#include <QList>
#include <QListView>
#include <QMenu>
#include <QMainWindow>
#include <QPaintEvent>
#include <QPointer>
#include <QPoint>
#include <QPixmap>
#include <QResizeEvent>
#include <QStatusBar>
#include <QStringList>
#include <QStringListModel>
#include <QStandardItemModel>
#include <QStyle>
#include <QTabWidget>
#include <QToolBar>
#include <QToolButton>
#include <QVBoxLayout>
#include <QWidget>

#include "LqRibbonControls.h"
#include "LqRibbonGallery.h"
#include "LqRibbonStatusBar.h"
#include "LqRibbonExtras.h"

QT_BEGIN_NAMESPACE
class QContextMenuEvent;
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
    explicit RibbonGroup(QWidget *parent = nullptr);
    explicit RibbonGroup(RibbonPage *page, const QString &strTitle);
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
                       Qt::ToolButtonStyle buttonStyle,
                       QMenu *menu = nullptr,
                       QToolButton::ToolButtonPopupMode mode =
                           QToolButton::MenuButtonPopup);
    ///
    /// \brief RibbonGroup::addAction
    /// Adds an existing action to the group with the requested button style.
    /// \param action Existing action to expose in the Ribbon group.
    /// \param buttonStyle Qt tool button style used by the generated button.
    ///
    QAction *addAction(QAction *action,
                       Qt::ToolButtonStyle buttonStyle,
                       QMenu *menu = nullptr,
                       QToolButton::ToolButtonPopupMode mode =
                           QToolButton::MenuButtonPopup);
    QAction *insertAction(QAction *before,
                          QAction *action,
                          Qt::ToolButtonStyle buttonStyle,
                          QMenu *menu = nullptr,
                          QToolButton::ToolButtonPopupMode mode =
                              QToolButton::MenuButtonPopup);
    ///
    /// \brief RibbonGroup::addWidget
    /// Adds a custom widget to the group content area.
    /// \param widget Widget that becomes owned by the group layout.
    ///
    QAction *addWidget(QWidget *widget);
    QAction *addWidget(const QIcon &icon,
                       const QString &strText,
                       QWidget *widget);
    QAction *addWidget(const QIcon &icon,
                       const QString &strText,
                       bool stretch,
                       QWidget *widget);
    ///
    /// \brief RibbonGroup::addMenu
    /// Adds a menu command button that opens the menu directly when clicked.
    ///
    QMenu *addMenu(const QIcon &icon,
                   const QString &strText,
                   Qt::ToolButtonStyle buttonStyle =
                       Qt::ToolButtonFollowStyle);
    QAction *addSeparator();
    void addControl(RibbonControl *control);
    void removeControl(RibbonControl *control);
    void remove(QWidget *widget);
    void clear();
    RibbonBar *ribbonBar() const;
    bool isReduced() const;
    const QFont &titleFont() const;
    void setTitleFont(const QFont &font);
    const QColor &titleColor() const;
    void setTitleColor(const QColor &color);
    const QIcon &icon() const;
    void setIcon(const QIcon &icon);
    bool isOptionButtonVisible() const;
    void setOptionButtonVisible(bool visible = true);
    QAction *optionButtonAction() const;
    void setOptionButtonAction(QAction *action);
    Qt::Alignment contentAlignment() const;
    void setContentAlignment(Qt::Alignment alignment);
    Qt::Alignment controlsAlignment() const;
    void setControlsAlignment(Qt::Alignment alignment);
    int spacing() const;
    void setSpacing(int spacing);
    int controlCount() const;
    RibbonControl *controlByIndex(int index) const;
    RibbonControl *controlByAction(QAction *action) const;
    RibbonWidgetControl *controlByWidget(QWidget *widget) const;
    Qt::TextElideMode titleElideMode() const;
    void setTitleElideMode(Qt::TextElideMode mode);
    RibbonControlSizeDefinition::GroupSizes sizeDefinition() const;
    void setSizeDefinition(
        const RibbonControlSizeDefinition::GroupSizes &sizeDefinition);
    void setControlsCentering(bool enabled = true);
    bool isControlsCentering() const;
    void setControlsGrouping(bool enabled = true);
    bool isControlsGrouping() const;

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

signals:
    void released();
    void actionTriggered(QAction *action);
    void hidePopup();
    void titleChanged(const QString &strTitle);
    void titleFontChanged(const QFont &font);

protected:
    bool event(QEvent *event) override;

private:
    QToolButton *createButton(QAction *action,
                              Qt::ToolButtonStyle buttonStyle,
                              QMenu *menu = nullptr,
                              QToolButton::ToolButtonPopupMode mode =
                                  QToolButton::MenuButtonPopup);
    void addSmallButton(QWidget *widget);
    void setupSmallButton(QToolButton *button);
    QGridLayout *smallButtonLayout();
    void updateMetrics();
    void rememberActionWidget(QAction *action, QWidget *widget);

private:
    QLabel *m_titleLabel;
    QHBoxLayout *m_contentLayout;
    QGridLayout *m_smallButtonLayout;
    QWidget *m_smallButtonWidget;
    QToolButton *m_optionButton;
    int m_smallButtonRow;
    int m_smallButtonColumn;
    QFont m_titleFont;
    QColor m_titleColor;
    QIcon m_icon;
    QAction *m_optionButtonAction;
    Qt::Alignment m_contentAlignment;
    Qt::Alignment m_controlsAlignment;
    Qt::TextElideMode m_titleElideMode;
    RibbonControlSizeDefinition::GroupSizes m_sizeDefinition;
    QList<RibbonControl *> m_controlList;
    QHash<QAction *, QWidget *> m_actionWidgetHash;
    QHash<QWidget *, QAction *> m_widgetActionHash;
    bool m_controlsGrouping;
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
    explicit RibbonPage(QWidget *parent = nullptr);
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
    void addGroup(RibbonGroup *group);
    RibbonGroup *addGroup(const QIcon &icon, const QString &strTitle);
    void insertGroup(int index, RibbonGroup *group);
    RibbonGroup *insertGroup(int index, const QString &strTitle);
    RibbonGroup *insertGroup(int index,
                             const QIcon &icon,
                             const QString &strTitle);
    void removeGroup(RibbonGroup *group);
    void removeGroupByIndex(int index);
    void detachGroup(RibbonGroup *group);
    void detachGroupByIndex(int index);
    void clearGroups();
    RibbonBar *ribbonBar() const;
    QAction *defaultAction() const;
    int groupCount() const;
    RibbonGroup *group(int index) const;
    int groupIndex(RibbonGroup *group) const;
    const RibbonGroupList &groups() const;
    ///
    /// \brief RibbonPage::title
    /// Returns the current page title.
    /// \return Text shown by the Ribbon tab.
    ///
    QString title() const;
    const QColor &contextColor() const;
    const QString &contextTitle() const;
    const QString &contextGroupName() const;
    void setContextColor(ContextColor color);
    void updateLayout();
    ///
    /// \brief RibbonPage::setTitle
    /// Updates the page title and notifies the Ribbon bar.
    /// \param strTitle New page title.
    ///
    void setTitle(const QString &strTitle);
    void setContextColor(const QColor &color);
    void setContextTitle(const QString &strTitle);
    void setContextGroupName(const QString &strGroupName);

signals:
    ///
    /// \brief RibbonPage::titleChanged
    /// Emitted when setTitle changes the visible page title.
    /// \param strTitle New page title.
    ///
    void titleChanged(const QString &strTitle);
    void activated();
    void activating(bool &allow);

protected:
    void paintEvent(QPaintEvent *event) override;

private:
    QString m_strTitle;
    QHBoxLayout *m_groupLayout;
    RibbonGroupList m_groupList;
    QAction *m_defaultAction;
    QColor m_contextColor;
    QString m_contextTitle;
    QString m_contextGroupName;
};

///
/// \brief The RibbonStatusBarSwitchGroup class displays compact switch actions.
///
/// The group converts added actions into flat, checkable buttons suitable for
/// view switches in a status bar.
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
    Q_ENUMS(BarPosition)
    Q_ENUMS(SearchBarAppearance)
    Q_ENUMS(RibbonStyle)

public:
    enum BarPosition
    {
        TopPosition = 1,
        BottomPosition
    };

    enum SearchBarAppearance
    {
        SearchBarCentral = 1,
        SearchBarCompact,
        SearchBarHidden
    };

    enum RibbonStyle
    {
        Office2016Blue = 1,
        Office2019Colorful,
        Microsoft365Light,
        Microsoft365Dark
    };

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
    void addPage(RibbonPage *page);
    RibbonPage *insertPage(int index, const QString &strTitle);
    void insertPage(int index, RibbonPage *page);
    void movePage(RibbonPage *page, int newIndex);
    void movePage(int index, int newIndex);
    void removePage(RibbonPage *page);
    void removePage(int index);
    void detachPage(RibbonPage *page);
    void detachPage(int index);
    void clearPages();
    ///
    /// \brief RibbonBar::page
    /// Returns the page at the requested tab index.
    /// \param index Zero-based page index.
    /// \return Page pointer or nullptr when index is invalid.
    ///
    RibbonPage *page(int index) const;
    int pageCount() const;
    int currentPageIndex() const;
    ///
    /// \brief RibbonBar::currentPage
    /// Returns the currently selected page.
    /// \return Current page pointer or nullptr when no page exists.
    ///
    RibbonPage *currentPage() const;
    RibbonPageList pages() const;
    int pageIndex(RibbonPage *page) const;
    bool isKeyTipsShowing() const;
    bool keyTipsEnabled() const;
    void setKeyTipsEnable(bool enable);
    bool isKeyTipsComplement() const;
    void setKeyTipsComplement(bool complement);
    void setKeyTip(QAction *action, const QString &keyTip);
    bool isMovableTabs() const;
    void setMovableTabs(bool movable);
    Qt::TextElideMode tabsElideMode() const;
    void setTabsElideMode(Qt::TextElideMode mode);
    void setLogoPixmap(const QPixmap &pixmap, Qt::AlignmentFlag alignment);
    QPixmap logoPixmap() const;
    void setTitleBackground(const QPixmap &pixmap);
    const QPixmap &titleBackground() const;
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
    RibbonQuickAccessBar *quickAccessBar() const;
    RibbonProgressBar *progressBar() const;
    RibbonSearchBar *searchBar() const;
    void setQuickAccessBarPosition(BarPosition position);
    BarPosition quickAccessBarPosition() const;
    void setSearchBarAppearance(SearchBarAppearance appearance);
    SearchBarAppearance searchBarAppearance() const;
    void setTabBarPosition(BarPosition position);
    BarPosition tabBarPosition() const;
    void setRibbonStyle(RibbonStyle style);
    RibbonStyle ribbonStyle() const;
    static QString ribbonStyleName(RibbonStyle style);
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
    void removeTitleButton(QAction *action);
    ///
    /// \brief RibbonBar::setCurrentPageIndex
    /// Selects a Ribbon page by index.
    /// \param index Zero-based tab index.
    ///
    void setCurrentPageIndex(int index);
    int rowItemHeight() const;
    int rowItemCount() const;
    ///
    /// \brief RibbonBar::setRibbonMinimized
    /// Collapses or expands the Ribbon command area while keeping tabs visible.
    /// \param minimized true to collapse command pages, false to expand them.
    ///
    void setRibbonMinimized(bool minimized);
    void minimize();
    bool isMinimized() const;
    void setMinimized(bool minimized);
    void maximize();
    bool isMaximized() const;
    void setMaximized(bool maximized);
    void setMinimizationEnabled(bool enabled);
    bool isMinimizationEnabled() const;
    QAction *simplifiedAction() const;
    bool simplifiedMode() const;
    void setSimplifiedMode(bool enabled);
    bool simplifiedModeEnabled() const;
    void setSimplifiedModeEnabled(bool enabled);
    Qt::LayoutDirection expandDirection() const;
    void setExpandDirection(Qt::LayoutDirection direction);
    RibbonCustomizeManager *customizeManager();
    RibbonCustomizeDialog *customizeDialog();
    void showCustomizeDialog();
    QMenu *addMenu(const QString &strText);
    using QWidget::addAction;
    QAction *addAction(const QIcon &icon,
                       const QString &strText,
                       Qt::ToolButtonStyle buttonStyle,
                       QMenu *menu = nullptr);
    QAction *addAction(QAction *action, Qt::ToolButtonStyle buttonStyle);
    QAction *addSystemButton(const QString &strText);
    QAction *addSystemButton(const QIcon &icon, const QString &strText);
    RibbonSystemButton *systemButton() const;
    void setAcrylicEnabled(bool enabled);
    bool isAcrylicEnabled() const;
    void setContextualTabsVisible(bool visible);
    bool isContextualTabsVisible() const;
    void setTitleGroupsVisible(bool visible);
    bool isTitleGroupsVisible() const;
    bool isBackstageVisible() const;
    void updateLayout();
    void beginUpdate();
    void endUpdate();
    static bool loadTranslation(const QString &strCountry = QString());
    static QString tr_compatible(const char *text, const char *context = nullptr);
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
    void minimizationChanged(bool minimized);
    void simplifiedModeChanged(bool enabled);
    void pageAboutToBeChanged(RibbonPage *page, bool &changed);
    void currentPageIndexChanged(int index);
    void currentPageChanged(RibbonPage *page);
    void keyTipsShowed(bool showed);
    void showRibbonContextMenu(QMenu *menu, QContextMenuEvent *event);
    void frameThemeChanged(bool enabled);
    void ribbonStyleChanged(RibbonStyle style);

protected:
    bool event(QEvent *event) override;
    bool eventFilter(QObject *object, QEvent *event) override;
    void paintEvent(QPaintEvent *event) override;
    void resizeEvent(QResizeEvent *event) override;
    void contextMenuEvent(QContextMenuEvent *event) override;

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
    bool isSearchableAction(QAction *action) const;
    bool searchActionMatches(QAction *action, const QString &strNormalizedText) const;
    void appendSearchActionIfMatches(QList<QAction *> &actionList,
                                     QAction *action,
                                     const QString &strNormalizedText) const;
    void appendMenuSearchActions(QList<QAction *> &actionList,
                                 QMenu *menu,
                                 const QString &strNormalizedText) const;
    void updateSearchSuggestions();
    void recordRecentSearchAction(QAction *action);
    void removeInvalidSearchActions();
    void updateChangedSearchAction();
    void rebuildSearchActionIndex();
    QString normalizedSearchText(const QString &strText) const;
    QString searchActionText(QAction *action) const;
    void updateStyleSheet();
    void updateRibbonDisplayState();
    bool isRibbonCommandAreaVisible() const;
    void showTemporaryRibbon();
    void hideTemporaryRibbon();
    void scheduleHideTemporaryRibbon();
    bool isRibbonRelatedObject(QObject *object) const;

private:
    struct SearchCommand
    {
        QPointer<QAction> action;
        QString strText;
        QStringList strKeywords;
    };

private:
    RibbonSearchBar *m_searchEdit;
    QListView *m_searchPopupView;
    QStandardItemModel *m_searchPopupModel;
    QAction *m_searchLineAction;
    RibbonQuickAccessBar *m_quickAccessBar;
    QToolBar *m_titleButtonBar;
    RibbonProgressBar *m_progressBar;
    RibbonSystemButton *m_systemButton;
    QAction *m_simplifiedAction;
    RibbonCustomizeManager *m_customizeManager;
    RibbonCustomizeDialog *m_customizeDialog;
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
    bool m_ribbonTemporaryExpanded;
    bool m_ignoreNextTabRelease;
    bool m_searchVisibleExplicitlySet;
    bool m_searchPlaceholderExplicitlySet;
    BarPosition m_quickAccessBarPosition;
    BarPosition m_tabBarPosition;
    SearchBarAppearance m_searchBarAppearance;
    RibbonStyle m_ribbonStyle;
    QPixmap m_logoPixmap;
    Qt::AlignmentFlag m_logoAlignment;
    QPixmap m_titleBackground;
    bool m_keyTipsEnabled;
    bool m_keyTipsComplement;
    bool m_keyTipsShowing;
    bool m_minimizationEnabled;
    bool m_simplifiedMode;
    bool m_simplifiedModeEnabled;
    bool m_acrylicEnabled;
    bool m_contextualTabsVisible;
    bool m_titleGroupsVisible;
    Qt::LayoutDirection m_expandDirection;
    int m_updateLockCount;
    QHash<QAction *, QString> m_keyTipHash;
    QList<QMenu *> m_ownedMenuList;
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
    explicit RibbonMainWindow(QWidget *parent = nullptr,
                              Qt::WindowFlags flags = Qt::WindowFlags());
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
    void setRibbonBar(RibbonBar *ribbonBar);
    ///
    /// \brief RibbonMainWindow::setCentralWidget
    /// Sets the content widget below the Ribbon bar.
    /// \param widget Widget to place in the central content area.
    ///
    void setCentralWidget(QWidget *widget);
    void setCentralWidget(QStyle *style);
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
    void setRibbonStyle(RibbonBar::RibbonStyle style);
    RibbonBar::RibbonStyle ribbonStyle() const;

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
    void updateNativeContentMargins();
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
using LqRibbonStatusBarSwitchGroup = RibbonStatusBarSwitchGroup;
using LqRibbonSliderPane = RibbonSliderPane;
using LqRibbonProgressBar = RibbonProgressBar;
using LqRibbonProgressOperation = RibbonProgressOperation;
using LqRibbonStatusBar = RibbonStatusBar;
using LqRibbonControlSizeDefinition = RibbonControlSizeDefinition;
using LqRibbonControl = RibbonControl;
using LqRibbonWidgetControl = RibbonWidgetControl;
using LqRibbonColumnBreakControl = RibbonColumnBreakControl;
using LqRibbonLabelControl = RibbonLabelControl;
using LqRibbonToolBarControl = RibbonToolBarControl;
using LqRibbonButtonControl = RibbonButtonControl;
using LqRibbonCheckBoxControl = RibbonCheckBoxControl;
using LqRibbonRadioButtonControl = RibbonRadioButtonControl;
using LqRibbonFontComboBoxControl = RibbonFontComboBoxControl;
using LqRibbonLineEditControl = RibbonLineEditControl;
using LqRibbonComboBoxControl = RibbonComboBoxControl;
using LqRibbonSpinBoxControl = RibbonSpinBoxControl;
using LqRibbonDoubleSpinBoxControl = RibbonDoubleSpinBoxControl;
using LqRibbonSliderControl = RibbonSliderControl;
using LqRibbonSliderPaneControl = RibbonSliderPaneControl;
using LqRibbonDateTimeEditControl = RibbonDateTimeEditControl;
using LqRibbonTimeEditControl = RibbonTimeEditControl;
using LqRibbonDateEditControl = RibbonDateEditControl;
using LqRibbonGalleryItem = RibbonGalleryItem;
using LqRibbonGalleryGroup = RibbonGalleryGroup;
using LqRibbonGallery = RibbonGallery;
using LqRibbonGalleryControl = RibbonGalleryControl;
using LqRibbonButton = RibbonButton;
using LqRibbonQuickAccessBar = RibbonQuickAccessBar;
using LqRibbonSearchBar = RibbonSearchBar;
using LqRibbonBackstageSeparator = RibbonBackstageSeparator;
using LqRibbonBackstageButton = RibbonBackstageButton;
using LqRibbonBackstagePage = RibbonBackstagePage;
using LqRibbonBackstageView = RibbonBackstageView;
using LqRibbonSystemButton = RibbonSystemButton;
using LqRibbonSystemMenu = RibbonSystemMenu;
using LqRibbonPageSystemRecentFileList = RibbonPageSystemRecentFileList;
using LqRibbonPageSystemPopup = RibbonPageSystemPopup;
using LqOfficePopupMenu = OfficePopupMenu;
using LqPopupColorButton = PopupColorButton;
using LqOfficePopupWindow = OfficePopupWindow;
using LqRibbonScrollArea = RibbonScrollArea;
using LqRibbonWorkspace = RibbonWorkspace;
using LqRibbonMdiArea = RibbonMdiArea;
using LqRibbonCustomizeManager = RibbonCustomizeManager;
using LqRibbonCustomizeDialog = RibbonCustomizeDialog;
using LqRibbonQuickAccessBarCustomizePage =
    RibbonQuickAccessBarCustomizePage;
using LqRibbonBarCustomizePage = RibbonBarCustomizePage;

} // namespace LqRibbon

using RibbonBar = LqRibbon::RibbonBar;
using RibbonPage = LqRibbon::RibbonPage;
using RibbonGroup = LqRibbon::RibbonGroup;
using RibbonMainWindow = LqRibbon::RibbonMainWindow;
using RibbonStatusBarSwitchGroup = LqRibbon::RibbonStatusBarSwitchGroup;
using RibbonSliderPane = LqRibbon::RibbonSliderPane;
using RibbonProgressBar = LqRibbon::RibbonProgressBar;
using RibbonProgressData = LqRibbon::RibbonProgressData;
using RibbonProgressOperation = LqRibbon::RibbonProgressOperation;
using RibbonStatusBar = LqRibbon::RibbonStatusBar;
using RibbonControlSizeDefinition = LqRibbon::RibbonControlSizeDefinition;
using RibbonControl = LqRibbon::RibbonControl;
using RibbonWidgetControl = LqRibbon::RibbonWidgetControl;
using RibbonColumnBreakControl = LqRibbon::RibbonColumnBreakControl;
using RibbonLabelControl = LqRibbon::RibbonLabelControl;
using RibbonToolBarControl = LqRibbon::RibbonToolBarControl;
using RibbonButtonControl = LqRibbon::RibbonButtonControl;
using RibbonCheckBoxControl = LqRibbon::RibbonCheckBoxControl;
using RibbonRadioButtonControl = LqRibbon::RibbonRadioButtonControl;
using RibbonFontComboBoxControl = LqRibbon::RibbonFontComboBoxControl;
using RibbonLineEditControl = LqRibbon::RibbonLineEditControl;
using RibbonComboBoxControl = LqRibbon::RibbonComboBoxControl;
using RibbonSpinBoxControl = LqRibbon::RibbonSpinBoxControl;
using RibbonDoubleSpinBoxControl = LqRibbon::RibbonDoubleSpinBoxControl;
using RibbonSliderControl = LqRibbon::RibbonSliderControl;
using RibbonSliderPaneControl = LqRibbon::RibbonSliderPaneControl;
using RibbonDateTimeEditControl = LqRibbon::RibbonDateTimeEditControl;
using RibbonTimeEditControl = LqRibbon::RibbonTimeEditControl;
using RibbonDateEditControl = LqRibbon::RibbonDateEditControl;
using RibbonGalleryItem = LqRibbon::RibbonGalleryItem;
using RibbonGalleryGroup = LqRibbon::RibbonGalleryGroup;
using RibbonGallery = LqRibbon::RibbonGallery;
using RibbonGalleryControl = LqRibbon::RibbonGalleryControl;
using RibbonButton = LqRibbon::RibbonButton;
using RibbonQuickAccessBar = LqRibbon::RibbonQuickAccessBar;
using RibbonSearchBar = LqRibbon::RibbonSearchBar;
using RibbonBackstageSeparator = LqRibbon::RibbonBackstageSeparator;
using RibbonBackstageButton = LqRibbon::RibbonBackstageButton;
using RibbonBackstagePage = LqRibbon::RibbonBackstagePage;
using RibbonBackstageView = LqRibbon::RibbonBackstageView;
using RibbonSystemButton = LqRibbon::RibbonSystemButton;
using RibbonSystemMenu = LqRibbon::RibbonSystemMenu;
using RibbonPageSystemRecentFileList = LqRibbon::RibbonPageSystemRecentFileList;
using RibbonPageSystemPopup = LqRibbon::RibbonPageSystemPopup;
using OfficePopupMenu = LqRibbon::OfficePopupMenu;
using PopupColorButton = LqRibbon::PopupColorButton;
using OfficePopupWindow = LqRibbon::OfficePopupWindow;
using RibbonScrollArea = LqRibbon::RibbonScrollArea;
using RibbonWorkspace = LqRibbon::RibbonWorkspace;
using RibbonMdiArea = LqRibbon::RibbonMdiArea;
using RibbonCustomizeManager = LqRibbon::RibbonCustomizeManager;
using RibbonCustomizeDialog = LqRibbon::RibbonCustomizeDialog;
using RibbonQuickAccessBarCustomizePage =
    LqRibbon::RibbonQuickAccessBarCustomizePage;
using RibbonBarCustomizePage = LqRibbon::RibbonBarCustomizePage;
using RibbonPageList = LqRibbon::RibbonPageList;
using RibbonGroupList = LqRibbon::RibbonGroupList;

#endif // LQRIBBON_H
