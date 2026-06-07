#ifndef LQRIBBON_DEMORIBBONWINDOW_H
#define LQRIBBON_DEMORIBBONWINDOW_H

#include <QAction>
#include <QContextMenuEvent>
#include <QMenu>

#include "LqRibbon.h"

class DemoRibbonWindow : public LqRibbon::RibbonMainWindow
{
    Q_OBJECT

public:
    explicit DemoRibbonWindow(QWidget *parent = nullptr);

    void addSearchBar();

protected slots:
    void showHelp(const QString &strText);
    void toggleMinimization();
    void showQuickAccessCustomizeMenu(QMenu *menu);
    void showRibbonContextMenu(QMenu *menu, QContextMenuEvent *event);
    void switchLanguage();

protected:
    QAction *m_minimizeAction;

private:
    void minimizeActionTriggered();
    Q_DISABLE_COPY(DemoRibbonWindow)
};

#endif // LQRIBBON_DEMORIBBONWINDOW_H

