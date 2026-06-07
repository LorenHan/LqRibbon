#include "DemoRibbonWindow.h"

DemoRibbonWindow::DemoRibbonWindow(QWidget *parent)
    : LqRibbon::RibbonMainWindow(parent)
    , m_minimizeAction(new QAction(tr("Minimize the Ribbon"), this))
{
    m_minimizeAction->setCheckable(true);
    connect(m_minimizeAction, &QAction::triggered,
            this, &DemoRibbonWindow::minimizeActionTriggered);
}

void DemoRibbonWindow::addSearchBar()
{
    ribbonBar()->setSearchVisible(true);
}

void DemoRibbonWindow::showHelp(const QString &strText)
{
    Q_UNUSED(strText)
}

void DemoRibbonWindow::toggleMinimization()
{
    m_minimizeAction->toggle();
    minimizeActionTriggered();
}

void DemoRibbonWindow::showQuickAccessCustomizeMenu(QMenu *menu)
{
    Q_UNUSED(menu)
}

void DemoRibbonWindow::showRibbonContextMenu(QMenu *menu, QContextMenuEvent *event)
{
    Q_UNUSED(menu)
    Q_UNUSED(event)
}

void DemoRibbonWindow::switchLanguage()
{
}

void DemoRibbonWindow::minimizeActionTriggered()
{
    ribbonBar()->setVisible(!m_minimizeAction->isChecked());
}
