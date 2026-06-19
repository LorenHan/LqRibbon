#include "LqRibbonStatusBar.h"

#include <QActionEvent>
#include <QMetaObject>
#include <QSizePolicy>
#include <QStyle>

namespace {

const int statusBarHeight = 24;
const int statusButtonSize = 22;
const int sliderPaneWidth = 140;
const int progressBarWidth = 120;
const int progressBarHeight = 16;

const char statusBarStyleSheet[] =
    "LqRibbon--RibbonStatusBar {"
    "    background: #f4f6f8;"
    "    border-top: 1px solid #c7d0db;"
    "    color: #2f3338;"
    "}"
    "QToolBar#lqRibbonStatusActionBar,"
    "QToolBar#lqRibbonPermanentActionBar {"
    "    background: transparent;"
    "    border: none;"
    "    spacing: 1px;"
    "}"
    "QToolBar#lqRibbonStatusActionBar QToolButton,"
    "QToolBar#lqRibbonPermanentActionBar QToolButton,"
    "LqRibbon--RibbonStatusBarSwitchGroup QToolButton {"
    "    border: 1px solid transparent;"
    "    border-radius: 2px;"
    "    padding: 1px 6px;"
    "    background: transparent;"
    "}"
    "QToolBar#lqRibbonStatusActionBar QToolButton:hover,"
    "QToolBar#lqRibbonPermanentActionBar QToolButton:hover,"
    "LqRibbon--RibbonStatusBarSwitchGroup QToolButton:hover {"
    "    border-color: #9eb7d5;"
    "    background: #eaf2fb;"
    "}"
    "LqRibbon--RibbonStatusBarSwitchGroup QToolButton:checked {"
    "    border-color: #7ca7da;"
    "    background: #d9e9fb;"
    "}";

///
/// \brief setupStatusToolBar
/// Applies shared status-bar toolbar defaults.
/// \param toolBar Toolbar to initialize.
///
void setupStatusToolBar(QToolBar *toolBar)
{
    toolBar->setMovable(false);
    toolBar->setFloatable(false);
    toolBar->setIconSize(QSize(16, 16));
    toolBar->setToolButtonStyle(Qt::ToolButtonTextBesideIcon);
    toolBar->setSizePolicy(QSizePolicy::Minimum, QSizePolicy::Fixed);
    toolBar->setFixedHeight(statusBarHeight);
}

} // namespace

namespace LqRibbon {

///
/// \brief RibbonStatusBarSwitchGroup::RibbonStatusBarSwitchGroup
/// Creates an empty status-bar switch group.
/// \param parent Parent widget.
///
RibbonStatusBarSwitchGroup::RibbonStatusBarSwitchGroup(QWidget *parent)
    : QWidget(parent)
    , m_layout(new QHBoxLayout(this))
{
    setObjectName(QStringLiteral("lqRibbonStatusBarSwitchGroup"));
    setSizePolicy(QSizePolicy::Minimum, QSizePolicy::Fixed);
    setFixedHeight(statusBarHeight);

    m_layout->setContentsMargins(0, 0, 0, 0);
    m_layout->setSpacing(0);
}

///
/// \brief RibbonStatusBarSwitchGroup::clear
/// Removes all switch actions and buttons.
///
void RibbonStatusBarSwitchGroup::clear()
{
    const QList<QAction *> actionList = actions();
    for (QAction *action : actionList) {
        removeAction(action);
    }
}

///
/// \brief RibbonStatusBarSwitchGroup::actionEvent
/// Converts added actions into flat switch buttons.
/// \param event Action event supplied by Qt.
///
void RibbonStatusBarSwitchGroup::actionEvent(QActionEvent *event)
{
    QAction *action = event->action();
    if (!action) {
        QWidget::actionEvent(event);
        return;
    }

    if (event->type() == QEvent::ActionAdded) {
        QToolButton *button = new QToolButton(this);
        button->setAutoRaise(true);
        button->setDefaultAction(action);
        button->setFixedHeight(statusButtonSize);
        button->setToolButtonStyle(action->icon().isNull()
                                   ? Qt::ToolButtonTextOnly
                                   : Qt::ToolButtonIconOnly);
        m_buttonHash.insert(action, button);
        m_layout->addWidget(button);
    } else if (event->type() == QEvent::ActionRemoved) {
        QToolButton *button = m_buttonHash.take(action);
        if (button) {
            m_layout->removeWidget(button);
            button->deleteLater();
        }
    }

    QWidget::actionEvent(event);
}

///
/// \brief RibbonSliderPane::RibbonSliderPane
/// Creates a horizontal slider pane.
/// \param parent Parent widget.
///
RibbonSliderPane::RibbonSliderPane(QWidget *parent)
    : QWidget(parent)
    , m_decrementButton(new QPushButton(QStringLiteral("-"), this))
    , m_incrementButton(new QPushButton(QStringLiteral("+"), this))
    , m_slider(new QSlider(Qt::Horizontal, this))
{
    setSizePolicy(QSizePolicy::Fixed, QSizePolicy::Fixed);
    setFixedSize(sliderPaneWidth, statusBarHeight);

    m_decrementButton->setFixedSize(statusButtonSize, statusButtonSize);
    m_incrementButton->setFixedSize(statusButtonSize, statusButtonSize);
    m_decrementButton->setFocusPolicy(Qt::NoFocus);
    m_incrementButton->setFocusPolicy(Qt::NoFocus);
    m_slider->setFocusPolicy(Qt::NoFocus);
    m_slider->setRange(0, 100);
    m_slider->setValue(50);
    m_slider->setSingleStep(10);

    QHBoxLayout *layout = new QHBoxLayout(this);
    layout->setContentsMargins(0, 0, 0, 0);
    layout->setSpacing(4);
    layout->addWidget(m_decrementButton);
    layout->addWidget(m_slider, 1);
    layout->addWidget(m_incrementButton);

    connect(m_decrementButton, &QPushButton::clicked,
            this, &RibbonSliderPane::decrement);
    connect(m_incrementButton, &QPushButton::clicked,
            this, &RibbonSliderPane::increment);
    connect(m_slider, &QSlider::valueChanged,
            this, &RibbonSliderPane::valueChanged);
    connect(m_slider, &QSlider::sliderMoved,
            this, &RibbonSliderPane::sliderMoved);
}

///
/// \brief RibbonSliderPane::setRange
/// Sets the minimum and maximum slider values.
/// \param minimum Minimum slider value.
/// \param maximum Maximum slider value.
///
void RibbonSliderPane::setRange(int minimum, int maximum)
{
    m_slider->setRange(minimum, maximum);
}

///
/// \brief RibbonSliderPane::setScrollButtons
/// Shows or hides the minus and plus buttons.
/// \param on true to show scroll buttons.
///
void RibbonSliderPane::setScrollButtons(bool on)
{
    m_decrementButton->setVisible(on);
    m_incrementButton->setVisible(on);
}

///
/// \brief RibbonSliderPane::setSliderPosition
/// Sets the slider handle position.
/// \param position New slider position.
///
void RibbonSliderPane::setSliderPosition(int position)
{
    m_slider->setSliderPosition(position);
}

///
/// \brief RibbonSliderPane::sliderPosition
/// Returns the slider handle position.
/// \return Current slider position.
///
int RibbonSliderPane::sliderPosition() const
{
    return m_slider->sliderPosition();
}

///
/// \brief RibbonSliderPane::setSingleStep
/// Sets the step used by buttons and keyboard navigation.
/// \param step Single step value.
///
void RibbonSliderPane::setSingleStep(int step)
{
    m_slider->setSingleStep(qMax(1, step));
}

///
/// \brief RibbonSliderPane::singleStep
/// Returns the configured single step.
/// \return Single step value.
///
int RibbonSliderPane::singleStep() const
{
    return m_slider->singleStep();
}

///
/// \brief RibbonSliderPane::value
/// Returns the committed slider value.
/// \return Current value.
///
int RibbonSliderPane::value() const
{
    return m_slider->value();
}

///
/// \brief RibbonSliderPane::setValue
/// Sets the committed slider value.
/// \param value New value.
///
void RibbonSliderPane::setValue(int value)
{
    m_slider->setValue(value);
}

///
/// \brief RibbonSliderPane::increment
/// Increases the slider by one configured step.
///
void RibbonSliderPane::increment()
{
    setValue(value() + singleStep());
}

///
/// \brief RibbonSliderPane::decrement
/// Decreases the slider by one configured step.
///
void RibbonSliderPane::decrement()
{
    setValue(value() - singleStep());
}

///
/// \brief RibbonProgressBar::RibbonProgressBar
/// Creates a compact progress bar.
/// \param parent Parent widget.
///
RibbonProgressBar::RibbonProgressBar(QWidget *parent)
    : QProgressBar(parent)
{
    setRange(0, 100);
    setValue(35);
    setTextVisible(false);
    setFixedHeight(progressBarHeight);
    setSizePolicy(QSizePolicy::Fixed, QSizePolicy::Fixed);
}

///
/// \brief RibbonProgressBar::sizeHint
/// Returns the preferred compact progress size.
/// \return Preferred size.
///
QSize RibbonProgressBar::sizeHint() const
{
    return QSize(progressBarWidth, progressBarHeight);
}

///
/// \brief RibbonProgressBar::minimumSizeHint
/// Returns the minimum useful compact progress size.
/// \return Minimum size.
///
QSize RibbonProgressBar::minimumSizeHint() const
{
    return QSize(80, progressBarHeight);
}

///
/// \brief RibbonProgressBar::setValueSafe
/// Updates the progress value from any thread.
/// \param value New progress value.
///
void RibbonProgressBar::setValueSafe(int value)
{
    if (thread() == QThread::currentThread()) {
        setValue(value);
        return;
    }

    QMetaObject::invokeMethod(this,
                              "setValue",
                              Qt::QueuedConnection,
                              Q_ARG(int, value));
}

///
/// \brief RibbonProgressOperation::RibbonProgressOperation
/// Creates an idle progress operation.
/// \param parent Parent object.
///
RibbonProgressOperation::RibbonProgressOperation(QObject *parent)
    : QObject(parent)
    , m_thread(nullptr)
{
}

///
/// \brief RibbonProgressOperation::~RibbonProgressOperation
/// Stops the worker thread before destruction.
///
RibbonProgressOperation::~RibbonProgressOperation()
{
    stop();
}

///
/// \brief RibbonProgressOperation::isRunning
/// Checks whether the worker thread is active.
/// \return true while the operation is running.
///
bool RibbonProgressOperation::isRunning() const
{
    return m_thread && m_thread->isRunning();
}

///
/// \brief RibbonProgressOperation::start
/// Starts a worker thread and emits execute from that thread.
/// \param data Operation data passed through to the signals.
/// \param progressBar Optional progress bar to update.
/// \return true when the operation starts.
///
bool RibbonProgressOperation::start(RibbonProgressData *data,
                                    RibbonProgressBar *progressBar)
{
    if (isRunning()) {
        return false;
    }

    if (m_thread) {
        m_thread->deleteLater();
        m_thread = nullptr;
    }

    m_thread = QThread::create([this, data, progressBar]() {
        emit execute(data, progressBar);
        emit completed(data);
    });
    connect(m_thread, &QThread::finished, this, [this]() {
        QThread *finishedThread = m_thread;
        m_thread = nullptr;
        if (finishedThread) {
            finishedThread->deleteLater();
        }
    });
    m_thread->start();
    return true;
}

///
/// \brief RibbonProgressOperation::stop
/// Requests interruption and waits for the worker thread to finish.
///
void RibbonProgressOperation::stop()
{
    if (!m_thread) {
        return;
    }

    QThread *thread = m_thread;
    m_thread = nullptr;
    thread->requestInterruption();
    thread->quit();
    thread->wait();
    thread->deleteLater();
}

///
/// \brief RibbonStatusBar::RibbonStatusBar
/// Creates a status bar with left and permanent action areas.
/// \param parent Parent widget.
///
RibbonStatusBar::RibbonStatusBar(QWidget *parent)
    : QStatusBar(parent)
    , m_actionBar(new QToolBar(this))
    , m_permanentActionBar(new QToolBar(this))
{
    setObjectName(QStringLiteral("lqRibbonStatusBar"));
    setSizeGripEnabled(false);
    setMinimumHeight(statusBarHeight);
    setStyleSheet(QString::fromLatin1(statusBarStyleSheet));

    m_actionBar->setObjectName(QStringLiteral("lqRibbonStatusActionBar"));
    m_permanentActionBar->setObjectName(
        QStringLiteral("lqRibbonPermanentActionBar"));
    setupStatusToolBar(m_actionBar);
    setupStatusToolBar(m_permanentActionBar);

    QStatusBar::addWidget(m_actionBar);
    QStatusBar::addPermanentWidget(m_permanentActionBar);
}

///
/// \brief RibbonStatusBar::addAction
/// Creates and adds a status-bar action.
/// \param strText Action text.
/// \return Newly created action owned by the status bar.
///
QAction *RibbonStatusBar::addAction(const QString &strText)
{
    QAction *action = new QAction(strText, this);
    QWidget::addAction(action);
    return action;
}

///
/// \brief RibbonStatusBar::addSeparator
/// Adds a visual separator action.
/// \return Newly created separator action.
///
QAction *RibbonStatusBar::addSeparator()
{
    QAction *action = new QAction(this);
    action->setSeparator(true);
    QWidget::addAction(action);
    return action;
}

///
/// \brief RibbonStatusBar::addPermanentAction
/// Adds an action to the permanent action area.
/// \param action Action to add.
///
void RibbonStatusBar::addPermanentAction(QAction *action)
{
    if (!action) {
        return;
    }

    m_permanentActionBar->addAction(action);
}

///
/// \brief RibbonStatusBar::childrenPermanentRect
/// Returns the permanent action area's rectangle.
/// \return Permanent action rectangle in status-bar coordinates.
///
QRect RibbonStatusBar::childrenPermanentRect() const
{
    return m_permanentActionBar->geometry();
}

///
/// \brief RibbonStatusBar::actionEvent
/// Mirrors status-bar actions into the left action toolbar.
/// \param event Action event supplied by Qt.
///
void RibbonStatusBar::actionEvent(QActionEvent *event)
{
    QAction *action = event->action();
    if (!action) {
        QStatusBar::actionEvent(event);
        return;
    }

    if (event->type() == QEvent::ActionAdded) {
        m_actionBar->addAction(action);
        m_statusActionHash.insert(action, action);
    } else if (event->type() == QEvent::ActionRemoved) {
        if (m_statusActionHash.remove(action) > 0) {
            m_actionBar->removeAction(action);
        }
    }

    QStatusBar::actionEvent(event);
}

///
/// \brief RibbonStatusBar::resizeEvent
/// Keeps embedded action toolbars aligned with the status bar height.
/// \param event Resize event supplied by Qt.
///
void RibbonStatusBar::resizeEvent(QResizeEvent *event)
{
    QStatusBar::resizeEvent(event);
    m_actionBar->setFixedHeight(qMax(statusBarHeight, height()));
    m_permanentActionBar->setFixedHeight(qMax(statusBarHeight, height()));
}

} // namespace LqRibbon
