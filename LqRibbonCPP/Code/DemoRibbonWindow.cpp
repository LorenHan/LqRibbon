#include "DemoRibbonWindow.h"

///
/// \brief DemoRibbonWindow::DemoRibbonWindow
/// Creates the example Ribbon window.
/// \param parent Parent widget.
///
DemoRibbonWindow::DemoRibbonWindow(QWidget *parent)
    : LqRibbon::RibbonMainWindow(parent)
    , m_minimizeAction(new QAction(tr("Minimize the Ribbon"), this))
{
    m_minimizeAction->setCheckable(true);
    connect(m_minimizeAction, &QAction::triggered,
            this, &DemoRibbonWindow::minimizeActionTriggered);
}

///
/// \brief DemoRibbonWindow::addSearchBar
/// Enables Ribbon search and registers example searchable actions.
///
void DemoRibbonWindow::addSearchBar()
{
    ribbonBar()->setSearchVisible(true);
}

///
/// \brief DemoRibbonWindow::showHelp
/// Shows a help message for the current search query.
/// \param strText Search text entered by the user.
///
void DemoRibbonWindow::showHelp(const QString &strText)
{
    Q_UNUSED(strText)
}

///
/// \brief DemoRibbonWindow::toggleMinimization
/// Toggles the example Ribbon between expanded and minimized states.
///
void DemoRibbonWindow::toggleMinimization()
{
    m_minimizeAction->toggle();
    minimizeActionTriggered();
}

///
/// \brief DemoRibbonWindow::showQuickAccessCustomizeMenu
/// Adds example entries to the quick access customization menu.
/// \param menu Menu opened by the quick access toolbar.
///
void DemoRibbonWindow::showQuickAccessCustomizeMenu(QMenu *menu)
{
    Q_UNUSED(menu)
}

///
/// \brief DemoRibbonWindow::showRibbonContextMenu
/// Adds example entries to the Ribbon context menu.
/// \param menu Context menu to populate.
/// \param event Event that requested the context menu.
///
void DemoRibbonWindow::showRibbonContextMenu(QMenu *menu, QContextMenuEvent *event)
{
    Q_UNUSED(menu)
    Q_UNUSED(event)
}

///
/// \brief DemoRibbonWindow::switchLanguage
/// Demonstrates application-side Ribbon text refresh for translation changes.
///
void DemoRibbonWindow::switchLanguage()
{
}

///
/// \brief DemoRibbonWindow::minimizeActionTriggered
/// Updates example UI state after the minimize action is triggered.
///
void DemoRibbonWindow::minimizeActionTriggered()
{
    ribbonBar()->setVisible(!m_minimizeAction->isChecked());
}
