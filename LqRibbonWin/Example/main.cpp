#include <QApplication>
#include <QLabel>
#include <QMessageBox>
#include <QStyle>
#include <QVBoxLayout>

#include "LqRibbon.h"

int main(int argc, char *argv[])
{
    QApplication application(argc, argv);

    LqRibbon::RibbonMainWindow mainWindow;
    mainWindow.setWindowTitle(QObject::tr("LqRibbon Example"));
    mainWindow.resize(920, 560);

    LqRibbon::RibbonPage *generalPage = mainWindow.ribbonBar()->addPage(QObject::tr("General"));
    LqRibbon::RibbonGroup *viewGroup = generalPage->addGroup(QObject::tr("View"));

    QAction *fullScreenAction = viewGroup->addAction(
        mainWindow.style()->standardIcon(QStyle::SP_TitleBarMaxButton),
        QObject::tr("Full Screen"),
        Qt::ToolButtonTextUnderIcon);

    QAction *mdiAction = viewGroup->addAction(
        mainWindow.style()->standardIcon(QStyle::SP_FileDialogDetailedView),
        QObject::tr("Mdi Mode"),
        Qt::ToolButtonTextBesideIcon);

    QAction *tabAction = viewGroup->addAction(
        mainWindow.style()->standardIcon(QStyle::SP_FileDialogListView),
        QObject::tr("Tab Mode"),
        Qt::ToolButtonTextBesideIcon);

    LqRibbon::RibbonPage *driverPage = mainWindow.ribbonBar()->addPage(QObject::tr("Driver"));
    LqRibbon::RibbonGroup *communicationGroup = driverPage->addGroup(QObject::tr("Communication"));
    QAction *settingsAction = communicationGroup->addAction(
        mainWindow.style()->standardIcon(QStyle::SP_ComputerIcon),
        QObject::tr("Settings"),
        Qt::ToolButtonTextUnderIcon);
    QAction *connectAction = communicationGroup->addAction(
        mainWindow.style()->standardIcon(QStyle::SP_DialogApplyButton),
        QObject::tr("Connect"),
        Qt::ToolButtonTextUnderIcon);

    QObject::connect(fullScreenAction, &QAction::triggered, [&mainWindow]() {
        mainWindow.setWindowState(mainWindow.windowState() ^ Qt::WindowFullScreen);
    });

    QObject::connect(mdiAction, &QAction::triggered, [&mainWindow]() {
        QMessageBox::information(&mainWindow,
                                 QObject::tr("LqRibbon"),
                                 QObject::tr("Mdi Mode"));
    });

    QObject::connect(tabAction, &QAction::triggered, [&mainWindow]() {
        QMessageBox::information(&mainWindow,
                                 QObject::tr("LqRibbon"),
                                 QObject::tr("Tab Mode"));
    });

    QObject::connect(settingsAction, &QAction::triggered, [&mainWindow]() {
        QMessageBox::information(&mainWindow,
                                 QObject::tr("LqRibbon"),
                                 QObject::tr("Settings"));
    });

    QObject::connect(connectAction, &QAction::triggered, [&mainWindow]() {
        QMessageBox::information(&mainWindow,
                                 QObject::tr("LqRibbon"),
                                 QObject::tr("Connect"));
    });

    QLabel *contentLabel = new QLabel(QObject::tr("LqRibbon Qt 5.15.2 C++ example"));
    contentLabel->setAlignment(Qt::AlignCenter);
    mainWindow.setCentralWidget(contentLabel);
    mainWindow.ribbonBar()->setCurrentPageIndex(1);
    mainWindow.ribbonBar()->setFrameThemeEnabled(true);
    mainWindow.ribbonBar()->setSearchVisible(true);
    mainWindow.ribbonBar()->setSearchPlaceholderText(QObject::tr("Search commands"));
    mainWindow.ribbonBar()->setRecentSearchLimit(5);
    mainWindow.ribbonBar()->registerSearchAction(fullScreenAction);
    mainWindow.ribbonBar()->registerSearchAction(mdiAction);
    mainWindow.ribbonBar()->registerSearchAction(tabAction);
    mainWindow.ribbonBar()->registerSearchAction(settingsAction);
    mainWindow.ribbonBar()->registerSearchAction(connectAction);
    QObject::connect(mainWindow.ribbonBar(), &LqRibbon::RibbonBar::searchAccepted,
                     [&mainWindow](const QString &strText) {
                         QMessageBox::information(&mainWindow,
                                                  QObject::tr("Search"),
                                                  QObject::tr("No command: %1").arg(strText));
                     });

    mainWindow.show();
    return application.exec();
}
