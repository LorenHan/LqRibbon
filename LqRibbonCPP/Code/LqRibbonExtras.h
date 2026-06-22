#ifndef LQRIBBON_EXTRAS_H
#define LQRIBBON_EXTRAS_H

#include <QAction>
#include <QColor>
#include <QDialog>
#include <QFrame>
#include <QHash>
#include <QIcon>
#include <QLineEdit>
#include <QList>
#include <QMdiArea>
#include <QMenu>
#include <QPointer>
#include <QPoint>
#include <QPixmap>
#include <QScrollArea>
#include <QSet>
#include <QSize>
#include <QStringList>
#include <QToolBar>
#include <QToolButton>
#include <QWidget>
#include <QXmlStreamReader>
#include <QXmlStreamWriter>

QT_BEGIN_NAMESPACE
class QActionEvent;
class QIODevice;
class QLabel;
class QListWidget;
class QMoveEvent;
class QPainter;
class QStackedWidget;
class QTimer;
class QVBoxLayout;
class QWidgetAction;
QT_END_NAMESPACE

namespace LqRibbon {

class RibbonBar;
class RibbonPage;
class RibbonGroup;

typedef QList<RibbonPage *> RibbonPageList;
typedef QList<RibbonGroup *> RibbonGroupList;
using IXmlStreamWriter = QXmlStreamWriter;
using IXmlStreamReader = QXmlStreamReader;

enum ContextColor
{
    ContextColorNone,
    ContextColorBlue,
    ContextColorYellow,
    ContextColorGreen,
    ContextColorRed,
    ContextColorPurple,
    ContextColorCyan,
    ContextColorOrange
};

class RibbonButton : public QToolButton
{
    Q_OBJECT
    Q_PROPERTY(bool wordWrap READ wordWrap WRITE setWordWrap)

public:
    explicit RibbonButton(QWidget *parent = nullptr);
    ~RibbonButton() override;

    bool wordWrap() const;
    void setWordWrap(bool on);
    bool isLargeIcon() const;
    void setLargeIcon(bool large);
    bool simplifiedMode() const;
    void setSimplifiedMode(bool enabled);
    QSize sizeHint() const override;
    void changed();

protected:
    void updateIconSize();
    bool event(QEvent *event) override;
    void paintEvent(QPaintEvent *event) override;
    void actionEvent(QActionEvent *event) override;
    void changeEvent(QEvent *event) override;

private:
    bool m_wordWrap;
    bool m_largeIcon;
    bool m_simplifiedMode;
};

class RibbonQuickAccessBar : public QToolBar
{
    Q_OBJECT

public:
    explicit RibbonQuickAccessBar(QWidget *parent = nullptr);
    ~RibbonQuickAccessBar() override;

    QAction *actionCustomizeButton() const;
    bool isActionVisible(QAction *action) const;
    void setActionVisible(QAction *action, bool visible);
    int visibleCount() const;
    void paintContent(QPainter *painter);
    QSize sizeHint() const override;

signals:
    void showCustomizeMenu(QMenu *menu);

protected:
    bool event(QEvent *event) override;
    void actionEvent(QActionEvent *event) override;
    void paintEvent(QPaintEvent *event) override;
    void resizeEvent(QResizeEvent *event) override;

private:
    QAction *m_customizeAction;
    QSet<QAction *> m_hiddenActions;
};

class RibbonSearchBar : public QLineEdit
{
    Q_OBJECT

public:
    explicit RibbonSearchBar(RibbonBar *ribbonBar);
    ~RibbonSearchBar() override;

    QSize minimumSizeHint() const override;
    void setCompact(bool compact);
    bool isCompact() const;
    const QIcon &icon() const;
    bool isHelpEnabled() const;
    void setHelpEnabled(bool enabled);
    const QList<QAction *> &suggestedActions() const;
    void addSuggestedAction(QAction *action);
    void removeSuggestedAction(QAction *action);
    int maxSearchItemCount() const;
    void setMaxSearchItemCount(int count);

public slots:
    void showPopup(const QString &text);
    void closePopup();

protected slots:
    void animationFinished();
    void animationValueChanged(const QVariant &value);
    void helpClicked();

signals:
    void showHelp(const QString &help);

protected:
    void mousePressEvent(QMouseEvent *event) override;
    void keyPressEvent(QKeyEvent *event) override;
    void paintEvent(QPaintEvent *event) override;
    void focusInEvent(QFocusEvent *event) override;
    void focusOutEvent(QFocusEvent *event) override;
    void resizeEvent(QResizeEvent *event) override;

private:
    RibbonBar *m_ribbonBar;
    QIcon m_icon;
    QList<QAction *> m_suggestedActions;
    QMenu *m_popupMenu;
    bool m_compact;
    bool m_helpEnabled;
    int m_maxSearchItemCount;
};

class RibbonBackstageSeparator : public QFrame
{
    Q_OBJECT
    Q_PROPERTY(Qt::Orientation orientation READ orientation WRITE setOrientation)

public:
    explicit RibbonBackstageSeparator(QWidget *parent = nullptr);
    ~RibbonBackstageSeparator() override;

    void setOrientation(Qt::Orientation orient);
    Qt::Orientation orientation() const;

private:
    Qt::Orientation m_orientation;
};

class RibbonBackstageButton : public QToolButton
{
    Q_OBJECT
    Q_PROPERTY(bool tabStyle READ tabStyle WRITE setTabStyle)

public:
    explicit RibbonBackstageButton(QWidget *parent = nullptr);
    ~RibbonBackstageButton() override;

    bool tabStyle() const;
    void setTabStyle(bool style);
    QSize minimumSizeHint() const override;
    QSize sizeHint() const override;

protected:
    bool event(QEvent *event) override;
    void paintEvent(QPaintEvent *event) override;

private:
    bool m_tabStyle;
};

class RibbonBackstagePage : public QWidget
{
    Q_OBJECT

public:
    explicit RibbonBackstagePage(QWidget *parent = nullptr);
    ~RibbonBackstagePage() override;

protected:
    void paintEvent(QPaintEvent *event) override;
};

class RibbonBackstageView : public QWidget
{
    Q_OBJECT
    Q_PROPERTY(int closePrevented READ isClosePrevented WRITE setClosePrevented)

public:
    explicit RibbonBackstageView(QWidget *parent = nullptr);
    ~RibbonBackstageView() override;

    bool isClosePrevented() const;
    void setClosePrevented(bool prevent);
    QAction *addAction(const QIcon &icon, const QString &text);
    QAction *addSeparator();
    QAction *addPage(QWidget *widget);
    QWidget *activePage() const;
    void setActivePage(QWidget *widget);
    QRect actionGeometry(QAction *action) const;
    QRect menuGeometry() const;

    using QWidget::addAction;

public slots:
    void open();

signals:
    void aboutToShow();
    void aboutToHide();

protected:
    bool event(QEvent *event) override;
    void paintEvent(QPaintEvent *event) override;
    void resizeEvent(QResizeEvent *event) override;
    bool eventFilter(QObject *object, QEvent *event) override;
    void actionEvent(QActionEvent *event) override;
    void showEvent(QShowEvent *event) override;
    void hideEvent(QHideEvent *event) override;
    void wheelEvent(QWheelEvent *event) override;

private:
    void rebuildMenu();
    void addActionButton(QAction *action);

private:
    QWidget *m_menuWidget;
    QVBoxLayout *m_menuLayout;
    QStackedWidget *m_pageStack;
    QHash<QAction *, RibbonBackstageButton *> m_actionButtons;
    QHash<QAction *, QWidget *> m_actionPages;
    bool m_closePrevented;
};

class RibbonSystemMenu;

class RibbonSystemButton : public QToolButton
{
    Q_OBJECT

public:
    explicit RibbonSystemButton(RibbonBar *ribbonBar);
    explicit RibbonSystemButton(QWidget *parent = nullptr);
    ~RibbonSystemButton() override;

    RibbonBar *ribbonBar() const;
    RibbonBackstageView *backstage() const;
    void setBackstage(RibbonBackstageView *backstage);
    QColor backgroundColor() const;
    void setBackgroundColor(const QColor &color);
    RibbonSystemMenu *systemMenu() const;
    void setSystemMenu(RibbonSystemMenu *menu);
    QSize sizeHint() const override;

protected:
    bool event(QEvent *event) override;
    bool eventFilter(QObject *watched, QEvent *event) override;
    void paintEvent(QPaintEvent *event) override;
    void mousePressEvent(QMouseEvent *event) override;

private:
    RibbonBar *m_ribbonBar;
    QPointer<RibbonBackstageView> m_backstage;
    QPointer<RibbonSystemMenu> m_systemMenu;
    QColor m_backgroundColor;
};

class RibbonPageSystemRecentFileList;
class RibbonPageSystemPopup;

class RibbonSystemMenu : public QMenu
{
    Q_OBJECT

public:
    explicit RibbonSystemMenu(RibbonBar *ribbonBar);
    ~RibbonSystemMenu() override;

    RibbonBar *ribbonBar() const;
    QAction *addPopupBarAction(const QString &text);
    void addPopupBarAction(QAction *action,
                           Qt::ToolButtonStyle style =
                               Qt::ToolButtonTextOnly);
    RibbonPageSystemRecentFileList *addPageRecentFile(const QString &caption);
    RibbonPageSystemPopup *addPageSystemPopup(const QString &caption,
                                              QAction *defaultAction,
                                              bool splitAction);
    void setVisible(bool visible) override;
    QSize sizeHint() const override;
    void updateLayout();

protected:
    void paintEvent(QPaintEvent *event) override;
    void mousePressEvent(QMouseEvent *event) override;
    void mouseReleaseEvent(QMouseEvent *event) override;
    void keyPressEvent(QKeyEvent *event) override;
    void changeEvent(QEvent *event) override;

private:
    RibbonBar *m_ribbonBar;
    QToolBar *m_popupBar;
};

class RibbonPageSystemRecentFileList : public QWidget
{
    Q_OBJECT

public:
    explicit RibbonPageSystemRecentFileList(const QString &caption);
    ~RibbonPageSystemRecentFileList() override;

    QSize sizeHint() const override;
    void setSize(int size);
    int getSize() const;
    QAction *getCurrentAction() const;

public slots:
    void updateRecentFileActions(const QStringList &files);

signals:
    void openRecentFile(const QString &file);

protected:
    void paintEvent(QPaintEvent *event) override;
    void mousePressEvent(QMouseEvent *event) override;
    void mouseMoveEvent(QMouseEvent *event) override;
    void mouseReleaseEvent(QMouseEvent *event) override;
#if (QT_VERSION >= QT_VERSION_CHECK(6, 0, 0))
    void enterEvent(QEnterEvent *event) override;
#else
    void enterEvent(QEvent *event) override;
#endif
    void leaveEvent(QEvent *event) override;
    void keyPressEvent(QKeyEvent *event) override;
    void resizeEvent(QResizeEvent *event) override;

private:
    int hitAction(const QPoint &point) const;

private:
    QString m_caption;
    QList<QAction *> m_actions;
    int m_size;
    int m_currentIndex;
    int m_pressedIndex;
};

class RibbonPageSystemPopup : public QMenu
{
    Q_OBJECT

public:
    explicit RibbonPageSystemPopup(const QString &caption,
                                   QWidget *parent = nullptr);
    ~RibbonPageSystemPopup() override;
    QSize sizeHint() const override;

protected:
    bool event(QEvent *event) override;
    void paintEvent(QPaintEvent *event) override;
};

class OfficePopupMenu : public QMenu
{
    Q_OBJECT
    Q_PROPERTY(bool gripVisible READ isGripVisible WRITE setGripVisible)

public:
    explicit OfficePopupMenu(QWidget *parent = nullptr);
    ~OfficePopupMenu() override;

    static OfficePopupMenu *createPopupMenu(QWidget *parent = nullptr);
    QAction *addWidget(QWidget *widget);
    void setGripVisible(bool visible);
    bool isGripVisible() const;

protected:
    void setWidgetBar(QWidget *widget);
    bool event(QEvent *event) override;
    void paintEvent(QPaintEvent *event) override;
    void mousePressEvent(QMouseEvent *event) override;
    void mouseMoveEvent(QMouseEvent *event) override;
    void mouseReleaseEvent(QMouseEvent *event) override;
    void moveEvent(QMoveEvent *event) override;
    void showEvent(QShowEvent *event) override;
    void hideEvent(QHideEvent *event) override;

private:
    QWidgetAction *m_widgetAction;
    bool m_gripVisible;
    bool m_dragging;
    QPoint m_dragStartPos;
};

class PopupColorButton : public QToolButton
{
    Q_OBJECT
    Q_PROPERTY(QColor color READ color WRITE setColor)

public:
    explicit PopupColorButton(QWidget *parent = nullptr);
    ~PopupColorButton() override;

    const QColor &color() const;
    void setColor(const QColor &color);
    QSize sizeHint() const override;

signals:
    void colorChanged(const QColor &color);

protected:
    void paintEvent(QPaintEvent *event) override;
    void mousePressEvent(QMouseEvent *event) override;

private:
    QColor m_color;
};

class OfficePopupWindow : public QWidget
{
    Q_OBJECT
    Q_ENUMS(PopupAnimation)
    Q_ENUMS(PopupLocation)
    Q_PROPERTY(PopupAnimation animation READ animation WRITE setAnimation)
    Q_PROPERTY(qreal transparency READ transparency WRITE setTransparency)
    Q_PROPERTY(int displayTime READ displayTime WRITE setDisplayTime)
    Q_PROPERTY(int animationSpeed READ animationSpeed WRITE setAnimationSpeed)
    Q_PROPERTY(QIcon titleIcon READ titleIcon WRITE setTitleIcon)
    Q_PROPERTY(QString titleText READ titleText WRITE setTitleText)
    Q_PROPERTY(QString bodyText READ bodyText WRITE setBodyText)
    Q_PROPERTY(bool titleCloseButtonVisible READ isTitleCloseButtonVisible
               WRITE setTitleCloseButtonVisible)
    Q_PROPERTY(PopupLocation location READ location WRITE setLocation)

public:
    enum PopupLocation
    {
        PopupLocationNearTaskBar,
        PopupLocationBottomRight,
        PopupLocationCenter
    };

    enum PopupAnimation
    {
        PopupAnimationNone,
        PopupAnimationFade,
        PopupAnimationSlide,
        PopupAnimationUnfold
    };

    explicit OfficePopupWindow(QWidget *parent = nullptr);
    ~OfficePopupWindow() override;

    static void showPopup(QWidget *parent,
                          const QIcon &titleIcon,
                          const QString &titleText,
                          const QString &bodyText,
                          bool closeButtonVisible = true);

    bool showPopup();
    bool showPopup(const QPoint &pos);
    void setCentralWidget(QWidget *widget);
    QWidget *centralWidget() const;
    void setBodyText(const QString &text);
    const QString &bodyText() const;
    void setTitleIcon(const QIcon &icon);
    const QIcon &titleIcon() const;
    void setTitleText(const QString &text);
    const QString &titleText() const;
    void setCloseButtonPixmap(const QPixmap &pm);
    const QPixmap &closeButtonPixmap() const;
    void setTitleCloseButtonVisible(bool visible = true);
    bool isTitleCloseButtonVisible() const;
    QPoint getPosition() const;
    void setPosition(const QPoint &pos);
    void setAnimation(OfficePopupWindow::PopupAnimation popupAnimation);
    OfficePopupWindow::PopupAnimation animation() const;
    void setTransparency(qreal transparency);
    qreal transparency() const;
    void setDisplayTime(int time);
    int displayTime() const;
    void setAnimationSpeed(int time);
    int animationSpeed() const;
    void setDragDropEnabled(bool enabled);
    bool dragDropEnabled() const;
    void setLocation(OfficePopupWindow::PopupLocation location);
    OfficePopupWindow::PopupLocation location() const;
    QSize sizeHint() const override;

public slots:
    void closePopup();

protected slots:
    void showDelayTimer();
    void collapsingTimer();
    void expandingTimer();

signals:
    void aboutToShow();
    void aboutToHide();

protected:
    bool event(QEvent *event) override;
    void paintEvent(QPaintEvent *event) override;
#if (QT_VERSION >= QT_VERSION_CHECK(6, 0, 0))
    void enterEvent(QEnterEvent *event) override;
#else
    void enterEvent(QEvent *event) override;
#endif
    void leaveEvent(QEvent *event) override;

private:
    QPoint defaultPopupPosition() const;
    void rebuildLayout();

private:
    QWidget *m_centralWidget;
    QLabel *m_iconLabel;
    QLabel *m_titleLabel;
    QLabel *m_bodyLabel;
    QToolButton *m_closeButton;
    QTimer *m_displayTimer;
    QIcon m_titleIcon;
    QString m_titleText;
    QString m_bodyText;
    QPixmap m_closePixmap;
    QPoint m_position;
    PopupAnimation m_animation;
    PopupLocation m_location;
    qreal m_transparency;
    int m_displayTime;
    int m_animationSpeed;
    bool m_dragDropEnabled;
};

class RibbonScrollArea : public QScrollArea
{
    Q_OBJECT

public:
    explicit RibbonScrollArea(QWidget *parent = nullptr);
    ~RibbonScrollArea() override;
    QSize viewportSizeHint() const override;

protected:
    void paintEvent(QPaintEvent *event) override;
    bool event(QEvent *event) override;
    void updateScrollBars();
};

class RibbonWorkspace : public RibbonScrollArea
{
    Q_OBJECT

public:
    explicit RibbonWorkspace(QWidget *parent = nullptr);

protected:
    void paintEvent(QPaintEvent *event) override;
};

class RibbonMdiArea : public QMdiArea
{
    Q_OBJECT

public:
    explicit RibbonMdiArea(QWidget *parent = nullptr);

protected:
    static void fixupTabBar(RibbonMdiArea *area);
    bool event(QEvent *event) override;
};

class RibbonCustomizeManager : public QObject
{
    Q_OBJECT

public:
    explicit RibbonCustomizeManager(RibbonBar *ribbonBar);
    ~RibbonCustomizeManager() override;

    QStringList categories() const;
    QList<QAction *> actionsAll() const;
    void addToolBar(QToolBar *toolBar);
    void addAllActionsCategory(const QString &category);
    QList<QAction *> actionsByCategory(const QString &category) const;
    void addToCategory(const QString &category, QAction *act);
    void removeFromCategory(const QString &category, QAction *act);
    QList<QToolBar *> toolBarsByCategory(const QString &category) const;
    void addToCategory(const QString &category, QToolBar *toolBar);
    QList<RibbonPage *> pagesByCategory(const QString &category) const;
    void addToCategory(const QString &category, RibbonPage *page);
    QList<RibbonGroup *> groupsByCategory(const QString &category) const;
    void addToCategory(const QString &category, RibbonGroup *group);
    QString actionId(QAction *action) const;
    void setActionId(QAction *action, const QString &id);
    QString pageId(RibbonPage *page) const;
    void setPageId(RibbonPage *page, const QString &id);
    QString groupId(RibbonGroup *group) const;
    void setGroupId(RibbonGroup *group, const QString &id);
    void setEditMode(bool set = true);
    bool isEditMode() const;
    void reset(QToolBar *toolBar = nullptr);
    void commit();
    void cancel();
    QList<QAction *> actions(QToolBar *toolBar) const;
    void insertAction(QToolBar *toolBar, QAction *action, int index);
    void removeActionAt(QToolBar *toolBar, int index);
    bool containsAction(QToolBar *toolBar, QAction *action) const;
    RibbonPageList pages() const;
    RibbonPage *createPage(const QString &pageName, int index = -1);
    void deletePage(RibbonPage *page);
    int pageIndex(RibbonPage *page) const;
    void movePage(int oldIndex, int newIndex);
    RibbonGroupList pageGroups(RibbonPage *page) const;
    RibbonGroup *createGroup(RibbonPage *page,
                             const QString &groupName,
                             int index = -1);
    void deleteGroup(RibbonPage *page, int index);
    void moveGroup(RibbonPage *page, int oldIndex, int newIndex);
    void insertAction(RibbonGroup *group, QAction *action, int index);
    void appendActions(RibbonGroup *group, const QList<QAction *> &actions);
    void clearActions(RibbonGroup *group);
    void removeActionAt(RibbonGroup *group, int index);
    bool containsAction(RibbonGroup *group, QAction *action) const;
    QList<QAction *> actionsGroup(RibbonGroup *group) const;
    bool isPageHidden(RibbonPage *page) const;
    void setPageHidden(RibbonPage *page, bool hide);
    bool isPageVisible(RibbonPage *page) const;
    void setPageVisible(RibbonPage *page, bool visible);
    QString pageName(RibbonPage *page) const;
    void setPageName(RibbonPage *page, const QString &pageName);
    QString groupName(RibbonGroup *group) const;
    void setGroupName(RibbonGroup *group, const QString &groupName);
    bool saveStateToDevice(QIODevice *device, bool autoFormatting = true);
    bool saveStateToXML(IXmlStreamWriter *xmlwriter);
    bool loadStateFromDevice(QIODevice *device);
    bool loadStateFromXML(IXmlStreamReader *xmlreader);
    void setDefaultState();

private:
    RibbonBar *m_ribbonBar;
    QHash<QString, QList<QAction *>> m_actionsByCategory;
    QHash<QString, QList<QToolBar *>> m_toolBarsByCategory;
    QHash<QString, QList<RibbonPage *>> m_pagesByCategory;
    QHash<QString, QList<RibbonGroup *>> m_groupsByCategory;
    QHash<QAction *, QString> m_actionIds;
    QHash<RibbonPage *, QString> m_pageIds;
    QHash<RibbonGroup *, QString> m_groupIds;
    QList<QToolBar *> m_toolBars;
    bool m_editMode;
};

class RibbonCustomizeDialog : public QDialog
{
    Q_OBJECT

public:
    explicit RibbonCustomizeDialog(QWidget *parent = nullptr);
    ~RibbonCustomizeDialog() override;

    void addPage(QWidget *page);
    void insertPage(int index, QWidget *page);
    int indexOf(QWidget *page) const;
    QWidget *currentPage() const;
    void setCurrentPage(QWidget *page);
    int currentPageIndex() const;
    void setCurrentPageIndex(int index);
    int pageCount() const;
    QWidget *pageByIndex(int index) const;
    void accept() override;
    void reject() override;

protected:
    void showEvent(QShowEvent *event) override;
    void hideEvent(QHideEvent *event) override;

private:
    QListWidget *m_pageList;
    QStackedWidget *m_pageStack;
};

class RibbonQuickAccessBarCustomizePage : public QWidget
{
    Q_OBJECT

public:
    explicit RibbonQuickAccessBarCustomizePage(RibbonBar *ribbonBar);
    ~RibbonQuickAccessBarCustomizePage() override;

    RibbonBar *ribbonBar() const;
    void addCustomCategory(const QString &strCategory);
    void addSeparatorCategory(const QString &strCategory = QString());

public slots:
    void accepted();

protected:
    void showEvent(QShowEvent *event) override;

private:
    RibbonBar *m_ribbonBar;
    QStringList m_categories;
};

class RibbonBarCustomizePage : public QWidget
{
    Q_OBJECT

public:
    explicit RibbonBarCustomizePage(RibbonBar *ribbonBar);
    ~RibbonBarCustomizePage() override;

    RibbonBar *ribbonBar() const;
    void addCustomCategory(const QString &strCategory);
    void addSeparatorCategory(const QString &strCategory = QString());

public slots:
    void accepted();
    void rejected();

protected:
    void showEvent(QShowEvent *event) override;
    void hideEvent(QHideEvent *event) override;

private:
    RibbonBar *m_ribbonBar;
    QStringList m_categories;
};

extern const char *QtnRibbonCustomizeQuickAccessToolBarDotString;
extern const char *QtnRibbonCustomizeQuickAccessToolBarString;
extern const char *QtnRibbonShowQuickAccessToolBarBelowString;
extern const char *QtnRibbonShowQuickAccessToolBarAboveString;
extern const char *QtnRibbonCustomizeActionString;
extern const char *QtnRibbonMinimizeActionString;
extern const char *QtnRibbonCustomizeDialogOptionsString;
extern const char *QtnRibbonSimplifiedRibbonActionString;
extern const char *QtnRibbonSimplifiedRibbonActionToolTipsString;
extern const char *QtnRibbonRecentDocumentsString;
extern const char *QtnRibbonUntitledString;
extern const char *QtnRibbonSeparatorString;
extern const char *QtnRibbonNewPageString;
extern const char *QtnRibbonNewGroupString;
extern const char *QtnRibbonAddCommandWarningString;
extern const char *QtnRibbonSearchBarSearchString;
extern const char *QtnRibbonSearchBarGetHelpString;
extern const char *QtnRibbonSearchBarHelpString;
extern const char *QtnRibbonSearchBarActionsString;
extern const char *QtnRibbonSearchBarSuggestedActionsString;
extern const QSize QtnRibbonGalleryItemSize;
extern const char *QtnRibbonGalleryItemString;

const char *getRibbonVersion();

} // namespace LqRibbon

#endif // LQRIBBON_EXTRAS_H
