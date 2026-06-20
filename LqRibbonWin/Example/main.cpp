#include <QApplication>
#include <QActionGroup>
#include <QBuffer>
#include <QDate>
#include <QDebug>
#include <QFormLayout>
#include <QFontDatabase>
#include <QLabel>
#include <QMouseEvent>
#include <QMdiArea>
#include <QMdiSubWindow>
#include <QMenu>
#include <QMessageBox>
#include <QPlainTextEdit>
#include <QStyle>
#include <QStackedWidget>
#include <QTabBar>
#include <QTableWidget>
#include <QTimer>
#include <QToolButton>
#include <QVBoxLayout>

#include "LqRibbon.h"

namespace {

void processCollapseTestEvents()
{
    qApp->processEvents(QEventLoop::AllEvents, 50);
}

QTabBar *collapseTestTabBar(LqRibbon::RibbonBar *ribbonBar)
{
    return ribbonBar->findChild<QTabBar *>();
}

QStackedWidget *collapseTestStack(LqRibbon::RibbonBar *ribbonBar)
{
    return ribbonBar->findChild<QStackedWidget *>();
}

bool collapseTestCommandAreaVisible(LqRibbon::RibbonBar *ribbonBar)
{
    QStackedWidget *stack = collapseTestStack(ribbonBar);
    return stack && stack->isVisible() && stack->height() > 0;
}

void sendCollapseTestMouse(QWidget *widget,
                           QEvent::Type type,
                           const QPoint &pos,
                           Qt::MouseButton button,
                           Qt::MouseButtons buttons)
{
    QMouseEvent event(type,
                      pos,
                      widget->mapToGlobal(pos),
                      button,
                      buttons,
                      Qt::NoModifier);
    QApplication::sendEvent(widget, &event);
    processCollapseTestEvents();
}

void clickCollapseTestWidget(QWidget *widget, const QPoint &pos)
{
    sendCollapseTestMouse(widget,
                          QEvent::MouseButtonPress,
                          pos,
                          Qt::LeftButton,
                          Qt::LeftButton);
    sendCollapseTestMouse(widget,
                          QEvent::MouseButtonRelease,
                          pos,
                          Qt::LeftButton,
                          Qt::NoButton);
}

void clickCollapseTestTab(LqRibbon::RibbonBar *ribbonBar, int index)
{
    QTabBar *tabBar = collapseTestTabBar(ribbonBar);
    clickCollapseTestWidget(tabBar, tabBar->tabRect(index).center());
}

void doubleClickCollapseTestTab(LqRibbon::RibbonBar *ribbonBar, int index)
{
    QTabBar *tabBar = collapseTestTabBar(ribbonBar);
    const QPoint pos = tabBar->tabRect(index).center();
    clickCollapseTestWidget(tabBar, pos);
    sendCollapseTestMouse(tabBar,
                          QEvent::MouseButtonDblClick,
                          pos,
                          Qt::LeftButton,
                          Qt::LeftButton);
    sendCollapseTestMouse(tabBar,
                          QEvent::MouseButtonRelease,
                          pos,
                          Qt::LeftButton,
                          Qt::NoButton);
}

QToolButton *collapseTestActionButton(LqRibbon::RibbonBar *ribbonBar,
                                      QAction *action)
{
    const QList<QToolButton *> buttons = ribbonBar->findChildren<QToolButton *>();
    for (QToolButton *button : buttons) {
        if (button->defaultAction() == action) {
            return button;
        }
    }
    return nullptr;
}

int runCollapseTests(LqRibbon::RibbonMainWindow &mainWindow)
{
    LqRibbon::RibbonBar *ribbonBar = mainWindow.ribbonBar();
    ribbonBar->setMinimizationEnabled(true);
    mainWindow.setFrameThemeEnabled(true);

    LqRibbon::RibbonPage *firstPage =
        ribbonBar->addPage(QStringLiteral("Collapse Test A"));
    LqRibbon::RibbonGroup *firstGroup =
        firstPage->addGroup(QStringLiteral("Actions"));
    QAction *firstAction = firstGroup->addAction(
        mainWindow.style()->standardIcon(QStyle::SP_DialogApplyButton),
        QStringLiteral("Apply"),
        Qt::ToolButtonTextUnderIcon);

    LqRibbon::RibbonPage *secondPage =
        ribbonBar->addPage(QStringLiteral("Collapse Test B"));
    LqRibbon::RibbonGroup *secondGroup =
        secondPage->addGroup(QStringLiteral("Actions"));
    QAction *secondAction = secondGroup->addAction(
        mainWindow.style()->standardIcon(QStyle::SP_DialogApplyButton),
        QStringLiteral("Connect"),
        Qt::ToolButtonTextUnderIcon);

    QStringList hits;
    QObject::connect(firstAction, &QAction::triggered, [&hits]() {
        hits << QStringLiteral("apply");
    });
    QObject::connect(secondAction, &QAction::triggered, [&hits]() {
        hits << QStringLiteral("connect");
    });

    const int firstIndex = ribbonBar->pageIndex(firstPage);
    const int secondIndex = ribbonBar->pageIndex(secondPage);
    QLabel *content = new QLabel(QStringLiteral("collapse test content"));
    content->setAlignment(Qt::AlignCenter);
    mainWindow.setCentralWidget(content);
    mainWindow.show();
    processCollapseTestEvents();

    auto reset = [&]() {
        hits.clear();
        ribbonBar->setMinimizationEnabled(true);
        ribbonBar->setCurrentPageIndex(firstIndex);
        ribbonBar->setRibbonMinimized(false);
        processCollapseTestEvents();
    };

    auto require = [](bool condition, const QString &name) {
        if (!condition) {
            qWarning().noquote() << "FAIL" << name;
            return false;
        }
        qInfo().noquote() << "PASS" << name;
        return true;
    };

    reset();
    doubleClickCollapseTestTab(ribbonBar, firstIndex);
    if (!require(ribbonBar->isRibbonMinimized()
                     && !collapseTestCommandAreaVisible(ribbonBar),
                 QStringLiteral("double click expanded tab collapses"))) {
        return 1;
    }

    reset();
    ribbonBar->setRibbonMinimized(true);
    doubleClickCollapseTestTab(ribbonBar, firstIndex);
    if (!require(!ribbonBar->isRibbonMinimized()
                     && collapseTestCommandAreaVisible(ribbonBar),
                 QStringLiteral("double click collapsed tab restores"))) {
        return 1;
    }

    reset();
    ribbonBar->setRibbonMinimized(true);
    if (!require(ribbonBar->isRibbonMinimized()
                     && !collapseTestCommandAreaVisible(ribbonBar),
                 QStringLiteral("programmatic collapse hides command area"))) {
        return 1;
    }

    reset();
    ribbonBar->setRibbonMinimized(true);
    clickCollapseTestTab(ribbonBar, firstIndex);
    if (!require(ribbonBar->isRibbonMinimized()
                     && collapseTestCommandAreaVisible(ribbonBar),
                 QStringLiteral("single click collapsed tab temporarily expands"))) {
        return 1;
    }

    QToolButton *firstButton = collapseTestActionButton(ribbonBar, firstAction);
    if (!require(firstButton != nullptr,
                 QStringLiteral("first action button exists"))) {
        return 1;
    }
    hits.clear();
    clickCollapseTestWidget(firstButton, firstButton->rect().center());
    if (!require(hits == QStringList{QStringLiteral("apply")},
                 QStringLiteral("action triggers while temporarily expanded"))) {
        return 1;
    }
    if (!require(ribbonBar->isRibbonMinimized()
                     && !collapseTestCommandAreaVisible(ribbonBar),
                 QStringLiteral("action hides temporary expansion"))) {
        return 1;
    }

    reset();
    ribbonBar->setRibbonMinimized(true);
    clickCollapseTestTab(ribbonBar, firstIndex);
    clickCollapseTestWidget(content, content->rect().center());
    if (!require(ribbonBar->isRibbonMinimized()
                     && !collapseTestCommandAreaVisible(ribbonBar),
                 QStringLiteral("outside click hides temporary expansion"))) {
        return 1;
    }

    reset();
    ribbonBar->setRibbonMinimized(true);
    clickCollapseTestTab(ribbonBar, firstIndex);
    doubleClickCollapseTestTab(ribbonBar, firstIndex);
    if (!require(!ribbonBar->isRibbonMinimized()
                     && collapseTestCommandAreaVisible(ribbonBar),
                 QStringLiteral("double click temporary tab restores permanently"))) {
        return 1;
    }

    reset();
    ribbonBar->setRibbonMinimized(true);
    clickCollapseTestTab(ribbonBar, secondIndex);
    if (!require(ribbonBar->currentIndex() == secondIndex
                     && ribbonBar->isRibbonMinimized()
                     && collapseTestCommandAreaVisible(ribbonBar),
                 QStringLiteral("collapsed click other page selects and expands"))) {
        return 1;
    }
    QToolButton *secondButton = collapseTestActionButton(ribbonBar, secondAction);
    if (!require(secondButton != nullptr,
                 QStringLiteral("second action button exists"))) {
        return 1;
    }
    hits.clear();
    clickCollapseTestWidget(secondButton, secondButton->rect().center());
    if (!require(hits == QStringList{QStringLiteral("connect")},
                 QStringLiteral("other page action triggers while expanded"))) {
        return 1;
    }

    reset();
    ribbonBar->setMinimizationEnabled(false);
    doubleClickCollapseTestTab(ribbonBar, firstIndex);
    if (!require(!ribbonBar->isRibbonMinimized()
                     && collapseTestCommandAreaVisible(ribbonBar),
                 QStringLiteral("minimization disabled blocks collapse"))) {
        return 1;
    }

    return 0;
}

} // namespace

int main(int argc, char *argv[])
{
    QApplication application(argc, argv);
    for (const QString &fontPath : {
             QStringLiteral("C:/Windows/Fonts/segoeui.ttf"),
             QStringLiteral("C:/Windows/Fonts/arial.ttf"),
         }) {
        const int fontId = QFontDatabase::addApplicationFont(fontPath);
        const QStringList families =
            QFontDatabase::applicationFontFamilies(fontId);
        if (!families.isEmpty()) {
            application.setFont(QFont(families.constFirst(), 9));
            break;
        }
    }

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
    const bool shellPreviewRequested =
        argumentList.contains(QStringLiteral("--grab-shell-preview"));
    const bool collapseTestsRequested =
        argumentList.contains(QStringLiteral("--run-collapse-tests"));

    LqRibbon::RibbonMainWindow mainWindow;
    mainWindow.setWindowTitle(QObject::tr("LqRibbon Example"));
    mainWindow.resize(920, 560);
    if (controlsPreviewRequested || galleryPreviewRequested
        || shellPreviewRequested) {
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

    LqRibbon::RibbonPage *shellPage =
        mainWindow.ribbonBar()->addPage(QObject::tr("Shell"));
    LqRibbon::RibbonGroup *windowGroup =
        shellPage->addGroup(QObject::tr("Window"));
    QAction *minimizeRibbonAction = windowGroup->addAction(
        mainWindow.style()->standardIcon(QStyle::SP_TitleBarShadeButton),
        QObject::tr("Minimize"),
        Qt::ToolButtonTextUnderIcon);
    QAction *restoreRibbonAction = windowGroup->addAction(
        mainWindow.style()->standardIcon(QStyle::SP_TitleBarUnshadeButton),
        QObject::tr("Restore"),
        Qt::ToolButtonTextBesideIcon);
    QAction *toggleFrameAction = windowGroup->addAction(
        mainWindow.style()->standardIcon(QStyle::SP_TitleBarNormalButton),
        QObject::tr("Frame Theme"),
        Qt::ToolButtonTextBesideIcon);
    toggleFrameAction->setCheckable(true);
    toggleFrameAction->setChecked(true);
    QAction *simplifiedRibbonAction = mainWindow.ribbonBar()->simplifiedAction();
    simplifiedRibbonAction->setIcon(
        mainWindow.style()->standardIcon(QStyle::SP_ArrowUp));
    windowGroup->addAction(simplifiedRibbonAction,
                           Qt::ToolButtonTextBesideIcon);

    LqRibbon::RibbonGroup *runtimeGroup =
        shellPage->addGroup(QObject::tr("Runtime"));
    QAction *addPageAction = runtimeGroup->addAction(
        mainWindow.style()->standardIcon(QStyle::SP_FileDialogNewFolder),
        QObject::tr("Add Page"),
        Qt::ToolButtonTextUnderIcon);
    QAction *renamePageAction = runtimeGroup->addAction(
        mainWindow.style()->standardIcon(QStyle::SP_FileDialogInfoView),
        QObject::tr("Rename Driver"),
        Qt::ToolButtonTextBesideIcon);
    QAction *moveGalleryAction = runtimeGroup->addAction(
        mainWindow.style()->standardIcon(QStyle::SP_ArrowRight),
        QObject::tr("Move Gallery"),
        Qt::ToolButtonTextBesideIcon);
    QAction *toggleGroupAction = runtimeGroup->addAction(
        mainWindow.style()->standardIcon(QStyle::SP_DialogResetButton),
        QObject::tr("Toggle Specialist"),
        Qt::ToolButtonTextBesideIcon);

    LqRibbon::RibbonGroup *popupGroup =
        shellPage->addGroup(QObject::tr("Popups"));
    QAction *officePopupAction = popupGroup->addAction(
        mainWindow.style()->standardIcon(QStyle::SP_MessageBoxInformation),
        QObject::tr("Popup"),
        Qt::ToolButtonTextUnderIcon);
    QAction *officeMenuAction = popupGroup->addAction(
        mainWindow.style()->standardIcon(QStyle::SP_DirOpenIcon),
        QObject::tr("Popup Menu"),
        Qt::ToolButtonTextBesideIcon);
    LqRibbon::PopupColorButton *colorButton =
        new LqRibbon::PopupColorButton(popupGroup);
    colorButton->setText(QObject::tr("Color"));
    colorButton->setToolButtonStyle(Qt::ToolButtonTextBesideIcon);
    colorButton->setColor(QColor(QStringLiteral("#2b579a")));
    colorButton->setToolTip(QObject::tr("Popup Color Button"));
    popupGroup->addWidget(colorButton);

    LqRibbon::RibbonGroup *customizeGroup =
        shellPage->addGroup(QObject::tr("Customize"));
    QAction *showCustomizeAction = customizeGroup->addAction(
        mainWindow.style()->standardIcon(QStyle::SP_FileDialogDetailedView),
        QObject::tr("Customize"),
        Qt::ToolButtonTextUnderIcon);
    QAction *saveStateAction = customizeGroup->addAction(
        mainWindow.style()->standardIcon(QStyle::SP_DialogSaveButton),
        QObject::tr("Save Layout"),
        Qt::ToolButtonTextBesideIcon);
    QAction *loadStateAction = customizeGroup->addAction(
        mainWindow.style()->standardIcon(QStyle::SP_DialogOpenButton),
        QObject::tr("Load Layout"),
        Qt::ToolButtonTextBesideIcon);

    QAction *specialistOptionsAction = new QAction(
        mainWindow.style()->standardIcon(QStyle::SP_FileDialogInfoView),
        QObject::tr("Specialist Options"),
        specialistGroup);
    specialistGroup->setOptionButtonAction(specialistOptionsAction);
    specialistGroup->setOptionButtonVisible(true);

    QAction *systemButtonAction = mainWindow.ribbonBar()->addSystemButton(
        mainWindow.style()->standardIcon(QStyle::SP_DriveFDIcon),
        QObject::tr("File"));
    Q_UNUSED(systemButtonAction)
    LqRibbon::RibbonBackstageView *backstage =
        new LqRibbon::RibbonBackstageView(&mainWindow);
    backstage->addAction(mainWindow.style()->standardIcon(QStyle::SP_DialogOpenButton),
                         QObject::tr("Open"));
    backstage->addAction(mainWindow.style()->standardIcon(QStyle::SP_DialogSaveButton),
                         QObject::tr("Save"));
    backstage->addSeparator();
    QWidget *backstagePage = new QWidget(backstage);
    QFormLayout *backstageLayout = new QFormLayout(backstagePage);
    backstageLayout->addRow(QObject::tr("Product"),
                            new QLabel(QObject::tr("LqRibbon Demo"), backstagePage));
    backstageLayout->addRow(QObject::tr("Mode"),
                            new QLabel(QObject::tr("Backstage page"), backstagePage));
    backstage->addPage(backstagePage);

    LqRibbon::RibbonSystemMenu *systemMenu =
        new LqRibbon::RibbonSystemMenu(mainWindow.ribbonBar());
    systemMenu->addPopupBarAction(QObject::tr("New"));
    systemMenu->addPopupBarAction(QObject::tr("Open"));
    LqRibbon::RibbonPageSystemRecentFileList *recentFiles =
        systemMenu->addPageRecentFile(QObject::tr("Recent Files"));
    recentFiles->updateRecentFileActions(QStringList()
                                         << QObject::tr("axis-profile.lqr")
                                         << QObject::tr("drive-layout.lqr"));
    QAction *exportAction = new QAction(
        mainWindow.style()->standardIcon(QStyle::SP_DialogSaveButton),
        QObject::tr("Export"), systemMenu);
    systemMenu->addPageSystemPopup(QObject::tr("Export"), exportAction, true);
    if (mainWindow.ribbonBar()->systemButton()) {
        mainWindow.ribbonBar()->systemButton()->setBackstage(backstage);
        mainWindow.ribbonBar()->systemButton()->setSystemMenu(systemMenu);
    }

    LqRibbon::OfficePopupMenu *officeMenu =
        LqRibbon::OfficePopupMenu::createPopupMenu(&mainWindow);
    officeMenu->setGripVisible(true);
    QPlainTextEdit *popupEditor = new QPlainTextEdit(officeMenu);
    popupEditor->setPlainText(QObject::tr("OfficePopupMenu widget host"));
    popupEditor->setFixedSize(260, 120);
    officeMenu->addWidget(popupEditor);

    LqRibbon::RibbonCustomizeManager *customizeManager =
        mainWindow.ribbonBar()->customizeManager();
    customizeManager->addToCategory(QObject::tr("Pages"), generalPage);
    customizeManager->addToCategory(QObject::tr("Pages"), driverPage);
    customizeManager->addToCategory(QObject::tr("Pages"), controlsPage);
    customizeManager->addToCategory(QObject::tr("Pages"), galleryPage);
    customizeManager->addToCategory(QObject::tr("Pages"), shellPage);
    customizeManager->addToCategory(QObject::tr("Actions"), fullScreenAction);
    customizeManager->addToCategory(QObject::tr("Actions"), connectAction);
    customizeManager->addToCategory(QObject::tr("Actions"), officePopupAction);
    customizeManager->addToCategory(QObject::tr("Actions"), showCustomizeAction);
    customizeManager->setPageId(shellPage, QStringLiteral("shell"));
    customizeManager->setGroupId(runtimeGroup, QStringLiteral("runtime"));
    QByteArray savedRibbonState;

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
    QObject::connect(specialistOptionsAction, &QAction::triggered,
                     [&mainWindow]() {
                         mainWindow.statusBar()->showMessage(
                             QObject::tr("Specialist option button clicked"),
                             2500);
                     });
    QObject::connect(minimizeRibbonAction, &QAction::triggered,
                     [&mainWindow]() {
                         mainWindow.ribbonBar()->setRibbonMinimized(true);
                     });
    QObject::connect(restoreRibbonAction, &QAction::triggered,
                     [&mainWindow]() {
                         mainWindow.ribbonBar()->setRibbonMinimized(false);
                     });
    QObject::connect(toggleFrameAction, &QAction::toggled,
                     [&mainWindow](bool checked) {
                         mainWindow.setFrameThemeEnabled(checked);
                     });
    QObject::connect(addPageAction, &QAction::triggered,
                     [&mainWindow]() {
                         static int runtimePageCounter = 1;
                         LqRibbon::RibbonPage *runtimePage =
                             mainWindow.ribbonBar()->addPage(
                                 QObject::tr("Runtime %1")
                                     .arg(runtimePageCounter++));
                         LqRibbon::RibbonGroup *runtimeGroup =
                             runtimePage->addGroup(QObject::tr("Generated"));
                         runtimeGroup->addAction(
                             mainWindow.style()->standardIcon(
                                 QStyle::SP_DialogApplyButton),
                             QObject::tr("Generated Action"),
                             Qt::ToolButtonTextUnderIcon);
                         mainWindow.ribbonBar()->setCurrentWidget(runtimePage);
                     });
    QObject::connect(renamePageAction, &QAction::triggered,
                     [driverPage]() {
                         driverPage->setTitle(
                             driverPage->title() == QObject::tr("Driver")
                                 ? QObject::tr("Drive")
                                 : QObject::tr("Driver"));
                     });
    QObject::connect(moveGalleryAction, &QAction::triggered,
                     [&mainWindow, galleryPage]() {
                         const int currentIndex =
                             mainWindow.ribbonBar()->pageIndex(galleryPage);
                         const int targetIndex = currentIndex == 1
                             ? mainWindow.ribbonBar()->pageCount() - 1
                             : 1;
                         mainWindow.ribbonBar()->movePage(galleryPage,
                                                          targetIndex);
                     });
    QObject::connect(toggleGroupAction, &QAction::triggered,
                     [driverPage, specialistGroup]() {
                         specialistGroup->setVisible(
                             !specialistGroup->isVisible());
                         driverPage->updateLayout();
                     });
    QObject::connect(officePopupAction, &QAction::triggered,
                     [&mainWindow]() {
                         LqRibbon::OfficePopupWindow::showPopup(
                             &mainWindow,
                             mainWindow.style()->standardIcon(
                                 QStyle::SP_MessageBoxInformation),
        QObject::tr("LqRibbon"),
                             QObject::tr("Popup window sample"));
                     });
    QObject::connect(officeMenuAction, &QAction::triggered,
                     [&mainWindow, officeMenu]() {
                         officeMenu->exec(mainWindow.mapToGlobal(
                             QPoint(40, 90)));
                     });
    QObject::connect(colorButton, &LqRibbon::PopupColorButton::colorChanged,
                     [&mainWindow](const QColor &color) {
                         mainWindow.statusBar()->showMessage(
                             QObject::tr("Color changed: %1")
                                 .arg(color.name()),
                             2500);
                     });
    QObject::connect(showCustomizeAction, &QAction::triggered,
                     [&mainWindow]() {
                         mainWindow.ribbonBar()->showCustomizeDialog();
                     });
    QObject::connect(saveStateAction, &QAction::triggered,
                     [&mainWindow, customizeManager, &savedRibbonState]() {
                         savedRibbonState.clear();
                         QBuffer buffer(&savedRibbonState);
                         buffer.open(QIODevice::WriteOnly);
                         customizeManager->saveStateToDevice(&buffer);
                         mainWindow.statusBar()->showMessage(
                             QObject::tr("Ribbon layout saved"), 2500);
                     });
    QObject::connect(loadStateAction, &QAction::triggered,
                     [&mainWindow, customizeManager, &savedRibbonState]() {
                         if (savedRibbonState.isEmpty()) {
                             mainWindow.statusBar()->showMessage(
                                 QObject::tr("No saved Ribbon layout"), 2500);
                             return;
                         }
                         QBuffer buffer(&savedRibbonState);
                         buffer.open(QIODevice::ReadOnly);
                         customizeManager->loadStateFromDevice(&buffer);
                         mainWindow.statusBar()->showMessage(
                             QObject::tr("Ribbon layout loaded"), 2500);
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
    const int shellPageIndex = mainWindow.ribbonBar()->indexOf(shellPage);
    if (shellPreviewRequested) {
        mainWindow.ribbonBar()->setCurrentPageIndex(shellPageIndex);
    } else if (galleryPreviewRequested) {
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
    mainWindow.ribbonBar()->registerSearchAction(minimizeRibbonAction);
    mainWindow.ribbonBar()->registerSearchAction(restoreRibbonAction);
    mainWindow.ribbonBar()->registerSearchAction(addPageAction);
    mainWindow.ribbonBar()->registerSearchAction(renamePageAction);
    mainWindow.ribbonBar()->registerSearchAction(moveGalleryAction);
    mainWindow.ribbonBar()->registerSearchAction(toggleGroupAction);
    mainWindow.ribbonBar()->registerSearchAction(officePopupAction);
    mainWindow.ribbonBar()->registerSearchAction(officeMenuAction);
    mainWindow.ribbonBar()->registerSearchAction(showCustomizeAction);
    mainWindow.ribbonBar()->addQuickAccessAction(fullScreenAction);
    mainWindow.ribbonBar()->addQuickAccessAction(connectAction);
    mainWindow.ribbonBar()->addQuickAccessAction(minimizeRibbonAction);

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

    if (collapseTestsRequested) {
        QTimer::singleShot(0, &mainWindow, [&mainWindow]() {
            qApp->exit(runCollapseTests(mainWindow));
        });
        return application.exec();
    }

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
