#include <QApplication>
#include <QActionGroup>
#include <QDate>
#include <QLabel>
#include <QMdiArea>
#include <QMdiSubWindow>
#include <QMenu>
#include <QMessageBox>
#include <QStyle>
#include <QTableWidget>
#include <QTimer>
#include <QToolButton>
#include <QVBoxLayout>

#include "LqRibbon.h"

int main(int argc, char *argv[])
{
    QApplication application(argc, argv);
    const QStringList argumentList = application.arguments();
    const int previewIndex = argumentList.indexOf(QStringLiteral("--grab-preview"));
    const bool previewRequested = previewIndex >= 0
        && previewIndex + 1 < argumentList.count();
    const QString strPreviewPath = previewRequested
        ? argumentList.at(previewIndex + 1)
        : QString();
    const bool searchPreviewRequested =
        argumentList.contains(QStringLiteral("--grab-search-preview"));
    const bool collapsedPreviewRequested =
        argumentList.contains(QStringLiteral("--grab-collapsed-preview"));
    const bool mdiPreviewRequested =
        argumentList.contains(QStringLiteral("--grab-mdi-preview"));
    const bool tabPreviewRequested =
        argumentList.contains(QStringLiteral("--grab-tab-preview"));
    const bool controlsPreviewRequested =
        argumentList.contains(QStringLiteral("--grab-controls-preview"));
    const bool galleryPreviewRequested =
        argumentList.contains(QStringLiteral("--grab-gallery-preview"));

    LqRibbon::RibbonMainWindow mainWindow;
    mainWindow.setWindowTitle(QObject::tr("LqRibbon Example"));
    mainWindow.resize(920, 560);
    if (controlsPreviewRequested || galleryPreviewRequested) {
        mainWindow.resize(1180, 560);
    }

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

    LqRibbon::RibbonGroup *specialistGroup = driverPage->addGroup(QObject::tr("Specialist"));
    QAction *basicAction = specialistGroup->addAction(
        mainWindow.style()->standardIcon(QStyle::SP_FileDialogContentsView),
        QObject::tr("Basic Operation"),
        Qt::ToolButtonTextBesideIcon);
    QAction *driverAction = specialistGroup->addAction(
        mainWindow.style()->standardIcon(QStyle::SP_DriveHDIcon),
        QObject::tr("Driver Configuration"),
        Qt::ToolButtonTextBesideIcon);

    QToolButton *toolButtonControl = new QToolButton(&mainWindow);
    toolButtonControl->setText(QObject::tr("Control Modes"));
    toolButtonControl->setIcon(
        mainWindow.style()->standardIcon(QStyle::SP_FileDialogListView));
    toolButtonControl->setToolButtonStyle(Qt::ToolButtonTextBesideIcon);
    toolButtonControl->setPopupMode(QToolButton::MenuButtonPopup);
    toolButtonControl->setMenu(new QMenu(toolButtonControl));
    toolButtonControl->menu()->addAction(QObject::tr("Pulse Mode"));
    toolButtonControl->menu()->addAction(QObject::tr("Analog Velocity Mode"));
    specialistGroup->addWidget(toolButtonControl);

    LqRibbon::RibbonPage *controlsPage =
        mainWindow.ribbonBar()->addPage(QObject::tr("Controls"));
    LqRibbon::RibbonGroup *selectorGroup =
        controlsPage->addGroup(QObject::tr("Selectors"));
    LqRibbon::RibbonComboBoxControl *modeCombo =
        new LqRibbon::RibbonComboBoxControl(selectorGroup);
    modeCombo->widget()->addItems(QStringList()
                                  << QObject::tr("Position")
                                  << QObject::tr("Velocity")
                                  << QObject::tr("Torque"));
    selectorGroup->addWidget(modeCombo);

    LqRibbon::RibbonFontComboBoxControl *fontCombo =
        new LqRibbon::RibbonFontComboBoxControl(selectorGroup);
    selectorGroup->addWidget(fontCombo);

    LqRibbon::RibbonCheckBoxControl *enabledCheck =
        new LqRibbon::RibbonCheckBoxControl(QObject::tr("Enabled"),
                                            selectorGroup);
    enabledCheck->widget()->setChecked(true);
    selectorGroup->addWidget(enabledCheck);

    LqRibbon::RibbonRadioButtonControl *autoRadio =
        new LqRibbon::RibbonRadioButtonControl(QObject::tr("Auto"),
                                               selectorGroup);
    autoRadio->widget()->setChecked(true);
    selectorGroup->addWidget(autoRadio);

    LqRibbon::RibbonGroup *valueGroup =
        controlsPage->addGroup(QObject::tr("Values"));
    LqRibbon::RibbonLineEditControl *nameEdit =
        new LqRibbon::RibbonLineEditControl(valueGroup);
    nameEdit->widget()->setPlaceholderText(QObject::tr("Axis name"));
    valueGroup->addWidget(nameEdit);

    LqRibbon::RibbonSpinBoxControl *speedSpin =
        new LqRibbon::RibbonSpinBoxControl(valueGroup);
    speedSpin->widget()->setRange(0, 6000);
    speedSpin->widget()->setValue(1500);
    valueGroup->addWidget(speedSpin);

    LqRibbon::RibbonDoubleSpinBoxControl *gainSpin =
        new LqRibbon::RibbonDoubleSpinBoxControl(valueGroup);
    gainSpin->widget()->setRange(0.0, 10.0);
    gainSpin->widget()->setSingleStep(0.1);
    gainSpin->widget()->setValue(1.5);
    valueGroup->addWidget(gainSpin);

    LqRibbon::RibbonDateEditControl *dateEdit =
        new LqRibbon::RibbonDateEditControl(valueGroup);
    dateEdit->setCalendarPopup(true);
    dateEdit->widget()->setDate(QDate::currentDate());
    valueGroup->addWidget(dateEdit);

    LqRibbon::RibbonGroup *rangeGroup =
        controlsPage->addGroup(QObject::tr("Range"));
    LqRibbon::RibbonSliderControl *limitSlider =
        new LqRibbon::RibbonSliderControl(Qt::Horizontal, rangeGroup);
    limitSlider->widget()->setRange(0, 100);
    limitSlider->widget()->setValue(35);
    rangeGroup->addWidget(limitSlider);

    LqRibbon::RibbonSliderPaneControl *fineSlider =
        new LqRibbon::RibbonSliderPaneControl(rangeGroup);
    fineSlider->widget()->setValue(65);
    rangeGroup->addWidget(fineSlider);

    LqRibbon::RibbonButtonControl *applyButton =
        new LqRibbon::RibbonButtonControl(rangeGroup);
    applyButton->setSmallIcon(
        mainWindow.style()->standardIcon(QStyle::SP_DialogApplyButton));
    applyButton->setLargeIcon(
        mainWindow.style()->standardIcon(QStyle::SP_DialogApplyButton));
    applyButton->setLabel(QObject::tr("Apply"));
    rangeGroup->addWidget(applyButton);

    LqRibbon::RibbonPage *galleryPage =
        mainWindow.ribbonBar()->addPage(QObject::tr("Gallery"));
    LqRibbon::RibbonGroup *styleGroup =
        galleryPage->addGroup(QObject::tr("Styles"));
    LqRibbon::RibbonGalleryGroup *styleGalleryGroup =
        new LqRibbon::RibbonGalleryGroup(&mainWindow);
    styleGalleryGroup->setSize(QSize(72, 42));
    styleGalleryGroup->addItem(
        QObject::tr("Normal"),
        mainWindow.style()->standardIcon(QStyle::SP_FileDialogDetailedView));
    styleGalleryGroup->addItem(
        QObject::tr("Compact"),
        mainWindow.style()->standardIcon(QStyle::SP_FileDialogListView));
    styleGalleryGroup->addItem(
        QObject::tr("Drive"),
        mainWindow.style()->standardIcon(QStyle::SP_DriveHDIcon));
    styleGalleryGroup->addItem(
        QObject::tr("Network"),
        mainWindow.style()->standardIcon(QStyle::SP_ComputerIcon));
    styleGalleryGroup->addItem(
        QObject::tr("Apply"),
        mainWindow.style()->standardIcon(QStyle::SP_DialogApplyButton));
    styleGalleryGroup->addItem(
        QObject::tr("Help"),
        mainWindow.style()->standardIcon(QStyle::SP_MessageBoxQuestion));

    LqRibbon::RibbonGallery *styleGallery =
        new LqRibbon::RibbonGallery(styleGroup);
    styleGallery->setGalleryGroup(styleGalleryGroup);
    styleGallery->setColumnCount(3);
    styleGallery->setRowCount(2);
    styleGallery->setCheckedIndex(1);

    QMenu *galleryMenu = new QMenu(styleGallery);
    galleryMenu->addAction(QObject::tr("More styles"));
    galleryMenu->addAction(QObject::tr("Reset style"));
    styleGallery->setPopupMenu(galleryMenu);

    LqRibbon::RibbonGalleryControl *styleGalleryControl =
        new LqRibbon::RibbonGalleryControl(styleGroup, styleGallery);
    styleGroup->addWidget(styleGalleryControl);

    LqRibbon::RibbonGroup *galleryActionGroup =
        galleryPage->addGroup(QObject::tr("Actions"));
    LqRibbon::RibbonToolBarControl *galleryToolBar =
        new LqRibbon::RibbonToolBarControl(galleryActionGroup);
    galleryToolBar->addAction(
        mainWindow.style()->standardIcon(QStyle::SP_DialogOpenButton),
        QObject::tr("Open"));
    galleryToolBar->addAction(
        mainWindow.style()->standardIcon(QStyle::SP_DialogSaveButton),
        QObject::tr("Save"));
    galleryToolBar->addSeparator();
    galleryToolBar->addMenu(
        mainWindow.style()->standardIcon(QStyle::SP_ArrowDown),
        QObject::tr("More"),
        galleryMenu);
    galleryActionGroup->addWidget(galleryToolBar);

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

    if (mdiPreviewRequested || tabPreviewRequested) {
        QMdiArea *mdiArea = new QMdiArea(&mainWindow);
        mdiArea->setViewMode(tabPreviewRequested
                             ? QMdiArea::TabbedView
                             : QMdiArea::SubWindowView);

        for (int index = 0; index < 2; ++index) {
            QTableWidget *tableWidget = new QTableWidget(8, 4, mdiArea);
            tableWidget->setWindowTitle(index == 0
                                        ? QObject::tr("Write Settings")
                                        : QObject::tr("Control Loop Specialist"));
            QMdiSubWindow *subWindow = mdiArea->addSubWindow(tableWidget);
            subWindow->setWindowTitle(tableWidget->windowTitle());
            subWindow->resize(index == 0 ? 360 : 300, 220);
            subWindow->move(index == 0 ? 40 : 460, index == 0 ? 60 : 80);
            subWindow->show();
        }

        mainWindow.setCentralWidget(mdiArea);
    } else {
        QLabel *contentLabel = new QLabel(
            QObject::tr("LqRibbon Qt 5.15.2 C++ example"));
        contentLabel->setAlignment(Qt::AlignCenter);
        mainWindow.setCentralWidget(contentLabel);
    }

    LqRibbon::RibbonStatusBar *ribbonStatusBar =
        new LqRibbon::RibbonStatusBar(&mainWindow);
    ribbonStatusBar->addAction(QObject::tr("Ready"));
    ribbonStatusBar->addSeparator();
    ribbonStatusBar->addAction(QObject::tr("Online"));

    LqRibbon::RibbonStatusBarSwitchGroup *switchGroup =
        new LqRibbon::RibbonStatusBarSwitchGroup(ribbonStatusBar);
    QActionGroup *viewActionGroup = new QActionGroup(switchGroup);
    viewActionGroup->setExclusive(true);
    QAction *normalViewAction = viewActionGroup->addAction(
        mainWindow.style()->standardIcon(QStyle::SP_FileDialogDetailedView),
        QObject::tr("Normal View"));
    QAction *compactViewAction = viewActionGroup->addAction(
        mainWindow.style()->standardIcon(QStyle::SP_FileDialogListView),
        QObject::tr("Compact View"));
    normalViewAction->setCheckable(true);
    compactViewAction->setCheckable(true);
    normalViewAction->setChecked(true);
    switchGroup->addAction(normalViewAction);
    switchGroup->addAction(compactViewAction);

    LqRibbon::RibbonSliderPane *zoomSlider =
        new LqRibbon::RibbonSliderPane(ribbonStatusBar);
    zoomSlider->setRange(10, 200);
    zoomSlider->setSingleStep(10);
    zoomSlider->setValue(100);

    LqRibbon::RibbonProgressBar *progressBar =
        new LqRibbon::RibbonProgressBar(ribbonStatusBar);
    progressBar->setValue(42);

    QAction *syncAction = new QAction(
        mainWindow.style()->standardIcon(QStyle::SP_BrowserReload),
        QObject::tr("Sync"),
        ribbonStatusBar);
    ribbonStatusBar->addPermanentAction(syncAction);
    ribbonStatusBar->addPermanentWidget(switchGroup);
    ribbonStatusBar->addPermanentWidget(zoomSlider);
    ribbonStatusBar->addPermanentWidget(progressBar);
    mainWindow.setStatusBar(ribbonStatusBar);

    QObject::connect(zoomSlider, &LqRibbon::RibbonSliderPane::valueChanged,
                     progressBar, &LqRibbon::RibbonProgressBar::setValueSafe);

    const int controlsPageIndex = mainWindow.ribbonBar()->indexOf(controlsPage);
    const int galleryPageIndex = mainWindow.ribbonBar()->indexOf(galleryPage);
    if (galleryPreviewRequested) {
        mainWindow.ribbonBar()->setCurrentPageIndex(galleryPageIndex);
    } else if (controlsPreviewRequested) {
        mainWindow.ribbonBar()->setCurrentPageIndex(controlsPageIndex);
    } else {
        mainWindow.ribbonBar()->setCurrentPageIndex(1);
    }
    mainWindow.setFrameThemeEnabled(true);
    mainWindow.ribbonBar()->setSearchVisible(true);
    mainWindow.ribbonBar()->setSearchPlaceholderText(QObject::tr("Search commands"));
    mainWindow.ribbonBar()->setRecentSearchLimit(5);
    mainWindow.ribbonBar()->registerSearchAction(fullScreenAction);
    mainWindow.ribbonBar()->registerSearchAction(mdiAction);
    mainWindow.ribbonBar()->registerSearchAction(tabAction);
    mainWindow.ribbonBar()->registerSearchAction(settingsAction);
    mainWindow.ribbonBar()->registerSearchAction(connectAction);
    mainWindow.ribbonBar()->registerSearchAction(basicAction);
    mainWindow.ribbonBar()->registerSearchAction(driverAction);
    mainWindow.ribbonBar()->addQuickAccessAction(fullScreenAction);
    mainWindow.ribbonBar()->addQuickAccessAction(connectAction);

    QAction *helpTitleAction = mainWindow.ribbonBar()->addTitleButton(
        mainWindow.style()->standardIcon(QStyle::SP_MessageBoxQuestion),
        QObject::tr("Help"));
    QAction *accountTitleAction = mainWindow.ribbonBar()->addTitleButton(
        mainWindow.style()->standardIcon(QStyle::SP_DirHomeIcon),
        QObject::tr("Account"));
    QObject::connect(helpTitleAction, &QAction::triggered, [&mainWindow]() {
        QMessageBox::information(&mainWindow,
                                 QObject::tr("LqRibbon"),
                                 QObject::tr("Help"));
    });
    QObject::connect(accountTitleAction, &QAction::triggered, [&mainWindow]() {
        QMessageBox::information(&mainWindow,
                                 QObject::tr("LqRibbon"),
                                 QObject::tr("Account"));
    });

    QObject::connect(mainWindow.ribbonBar(), &LqRibbon::RibbonBar::searchAccepted,
                     [&mainWindow](const QString &strText) {
                         QMessageBox::information(&mainWindow,
                                                  QObject::tr("Search"),
                                                  QObject::tr("No command: %1").arg(strText));
                     });

    mainWindow.show();

    if (!strPreviewPath.isEmpty()) {
        QTimer::singleShot(300, &mainWindow, [&mainWindow, strPreviewPath]() {
            mainWindow.grab().save(strPreviewPath);
            qApp->quit();
        });
    }

    if (searchPreviewRequested) {
        QTimer::singleShot(120, &mainWindow, [&mainWindow]() {
            mainWindow.ribbonBar()->searchLineEdit()->setFocus();
            mainWindow.ribbonBar()->setSearchText(QStringLiteral("ba"));
        });
    }

    if (collapsedPreviewRequested) {
        QTimer::singleShot(120, &mainWindow, [&mainWindow]() {
            mainWindow.ribbonBar()->setRibbonMinimized(true);
        });
    }

    return application.exec();
}
