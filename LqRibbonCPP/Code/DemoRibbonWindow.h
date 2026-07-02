#ifndef LQRIBBON_DEMORIBBONWINDOW_H
#define LQRIBBON_DEMORIBBONWINDOW_H

#include <QAction>
#include <QContextMenuEvent>
#include <QMenu>

#include "LqRibbon.h"

///
/// \brief The DemoRibbonWindow class demonstrates common LqRibbon features.
///
/// The class is intentionally kept in the Example area. It shows search,
/// quick access customization, Ribbon context menus, and minimization behavior
/// without adding application-specific logic to the library classes.
///
class DemoRibbonWindow : public LqRibbon::RibbonMainWindow
{
    Q_OBJECT

public:
    ///
    /// \brief DemoRibbonWindow::DemoRibbonWindow
    /// Creates the demonstration window and populates the Ribbon pages.
    /// \param parent Parent widget.
    ///
    explicit DemoRibbonWindow(QWidget *parent = nullptr);

    ///
    /// \brief DemoRibbonWindow::addSearchBar
    /// Shows the search box and registers sample searchable commands.
    ///
    void addSearchBar();

protected slots:
    ///
    /// \brief DemoRibbonWindow::showHelp
    /// Displays help text for a search query.
    /// \param strText Query text entered by the user.
    ///
    void showHelp(const QString &strText);
    ///
    /// \brief DemoRibbonWindow::toggleMinimization
    /// Toggles the Ribbon minimized state in the example window.
    ///
    void toggleMinimization();
    ///
    /// \brief DemoRibbonWindow::showQuickAccessCustomizeMenu
    /// Fills the quick access customization menu.
    /// \param menu Menu opened from the quick access toolbar.
    ///
    void showQuickAccessCustomizeMenu(QMenu *menu);
    ///
    /// \brief DemoRibbonWindow::showRibbonContextMenu
    /// Fills the Ribbon context menu for the example.
    /// \param menu Menu shown to the user.
    /// \param event Context menu event that requested the menu.
    ///
    void showRibbonContextMenu(QMenu *menu, QContextMenuEvent *event);
    ///
    /// \brief DemoRibbonWindow::switchLanguage
    /// Demonstrates how an application can refresh translated Ribbon text.
    ///
    void switchLanguage();

protected:
    QAction *m_minimizeAction;

private:
    void minimizeActionTriggered();
    Q_DISABLE_COPY(DemoRibbonWindow)
};

#endif // LQRIBBON_DEMORIBBONWINDOW_H
