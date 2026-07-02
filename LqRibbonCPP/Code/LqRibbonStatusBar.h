#ifndef LQRIBBON_STATUSBAR_H
#define LQRIBBON_STATUSBAR_H

#include <QAction>
#include <QHash>
#include <QHBoxLayout>
#include <QProgressBar>
#include <QPushButton>
#include <QSlider>
#include <QStatusBar>
#include <QThread>
#include <QToolBar>
#include <QToolButton>
#include <QWidget>

QT_BEGIN_NAMESPACE
class QActionEvent;
QT_END_NAMESPACE

namespace LqRibbon {

///
/// \brief The RibbonStatusBarSwitchGroup class displays compact switch actions.
///
/// The group converts added actions into flat, checkable buttons suitable for
/// view switches in a status bar.
///
class RibbonStatusBarSwitchGroup : public QWidget
{
    Q_OBJECT

public:
    ///
    /// \brief RibbonStatusBarSwitchGroup::RibbonStatusBarSwitchGroup
    /// Creates an empty status-bar switch group.
    /// \param parent Parent widget.
    ///
    explicit RibbonStatusBarSwitchGroup(QWidget *parent = nullptr);

    ///
    /// \brief RibbonStatusBarSwitchGroup::clear
    /// Removes all switch actions and buttons.
    ///
    void clear();

protected:
    void actionEvent(QActionEvent *event) override;

private:
    QHBoxLayout *m_layout;
    QHash<QAction *, QToolButton *> m_buttonHash;
};

///
/// \brief The RibbonSliderPane class combines minus/plus buttons and a slider.
///
/// It is intended for zoom controls and other compact status-bar ranges.
///
class RibbonSliderPane : public QWidget
{
    Q_OBJECT
    Q_PROPERTY(int singleStep READ singleStep WRITE setSingleStep)
    Q_PROPERTY(int value READ value WRITE setValue NOTIFY valueChanged USER true)
    Q_PROPERTY(int sliderPosition READ sliderPosition WRITE setSliderPosition
               NOTIFY sliderMoved)

public:
    ///
    /// \brief RibbonSliderPane::RibbonSliderPane
    /// Creates a horizontal slider pane.
    /// \param parent Parent widget.
    ///
    explicit RibbonSliderPane(QWidget *parent = nullptr);

    ///
    /// \brief RibbonSliderPane::setRange
    /// Sets the minimum and maximum slider values.
    /// \param minimum Minimum slider value.
    /// \param maximum Maximum slider value.
    ///
    void setRange(int minimum, int maximum);
    ///
    /// \brief RibbonSliderPane::setScrollButtons
    /// Shows or hides the minus and plus buttons.
    /// \param on true to show scroll buttons.
    ///
    void setScrollButtons(bool on);
    ///
    /// \brief RibbonSliderPane::setSliderPosition
    /// Sets the slider handle position.
    /// \param position New slider position.
    ///
    void setSliderPosition(int position);
    ///
    /// \brief RibbonSliderPane::sliderPosition
    /// Returns the slider handle position.
    /// \return Current slider position.
    ///
    int sliderPosition() const;
    ///
    /// \brief RibbonSliderPane::setSingleStep
    /// Sets the step used by buttons and keyboard navigation.
    /// \param step Single step value.
    ///
    void setSingleStep(int step);
    ///
    /// \brief RibbonSliderPane::singleStep
    /// Returns the configured single step.
    /// \return Single step value.
    ///
    int singleStep() const;
    ///
    /// \brief RibbonSliderPane::value
    /// Returns the committed slider value.
    /// \return Current value.
    ///
    int value() const;

public slots:
    ///
    /// \brief RibbonSliderPane::setValue
    /// Sets the committed slider value.
    /// \param value New value.
    ///
    void setValue(int value);

signals:
    ///
    /// \brief RibbonSliderPane::valueChanged
    /// Emitted when the value changes.
    /// \param value New value.
    ///
    void valueChanged(int value);
    ///
    /// \brief RibbonSliderPane::sliderMoved
    /// Emitted when the slider position changes.
    /// \param position New slider position.
    ///
    void sliderMoved(int position);

protected slots:
    void increment();
    void decrement();

private:
    QPushButton *m_decrementButton;
    QPushButton *m_incrementButton;
    QSlider *m_slider;
};

///
/// \brief The RibbonProgressBar class is a compact status-bar progress bar.
///
class RibbonProgressBar : public QProgressBar
{
    Q_OBJECT

public:
    ///
    /// \brief RibbonProgressBar::RibbonProgressBar
    /// Creates a compact progress bar.
    /// \param parent Parent widget.
    ///
    explicit RibbonProgressBar(QWidget *parent = nullptr);

    QSize sizeHint() const override;
    QSize minimumSizeHint() const override;

public slots:
    ///
    /// \brief RibbonProgressBar::setValueSafe
    /// Updates the progress value from any thread.
    /// \param value New progress value.
    ///
    void setValueSafe(int value);
};

///
/// \brief The RibbonProgressData class carries custom operation data.
///
class RibbonProgressData
{
public:
    virtual ~RibbonProgressData() = default;
};

///
/// \brief The RibbonProgressOperation class runs progress work on a thread.
///
class RibbonProgressOperation : public QObject
{
    Q_OBJECT

public:
    ///
    /// \brief RibbonProgressOperation::RibbonProgressOperation
    /// Creates an idle progress operation.
    /// \param parent Parent object.
    ///
    explicit RibbonProgressOperation(QObject *parent = nullptr);
    ~RibbonProgressOperation() override;

    ///
    /// \brief RibbonProgressOperation::isRunning
    /// Checks whether the worker thread is active.
    /// \return true while the operation is running.
    ///
    bool isRunning() const;
    ///
    /// \brief RibbonProgressOperation::start
    /// Starts a worker thread and emits execute from that thread.
    /// \param data Operation data passed through to the signals.
    /// \param progressBar Optional progress bar to update.
    /// \return true when the operation starts.
    ///
    bool start(RibbonProgressData *data,
               RibbonProgressBar *progressBar = nullptr);
    ///
    /// \brief RibbonProgressOperation::stop
    /// Requests interruption and waits for the worker thread to finish.
    ///
    void stop();

signals:
    ///
    /// \brief RibbonProgressOperation::execute
    /// Emitted from the worker thread to execute long-running work.
    /// \param data Operation data.
    /// \param progressBar Optional progress bar.
    ///
    void execute(RibbonProgressData *data, RibbonProgressBar *progressBar);
    ///
    /// \brief RibbonProgressOperation::completed
    /// Emitted after execute returns.
    /// \param data Operation data.
    ///
    void completed(RibbonProgressData *data);

private:
    QThread *m_thread;
};

///
/// \brief The RibbonStatusBar class provides Ribbon-styled status actions.
///
class RibbonStatusBar : public QStatusBar
{
    Q_OBJECT
    Q_PROPERTY(QRect childrenPermanentRect READ childrenPermanentRect)

public:
    ///
    /// \brief RibbonStatusBar::RibbonStatusBar
    /// Creates a status bar with left and permanent action areas.
    /// \param parent Parent widget.
    ///
    explicit RibbonStatusBar(QWidget *parent = nullptr);

    ///
    /// \brief RibbonStatusBar::addAction
    /// Creates and adds a status-bar action.
    /// \param strText Action text.
    /// \return Newly created action owned by the status bar.
    ///
    QAction *addAction(const QString &strText);
    ///
    /// \brief RibbonStatusBar::addSeparator
    /// Adds a visual separator action.
    /// \return Newly created separator action.
    ///
    QAction *addSeparator();
    ///
    /// \brief RibbonStatusBar::addPermanentAction
    /// Adds an action to the permanent action area.
    /// \param action Action to add.
    ///
    void addPermanentAction(QAction *action);
    ///
    /// \brief RibbonStatusBar::childrenPermanentRect
    /// Returns the permanent action area's rectangle.
    /// \return Permanent action rectangle in status-bar coordinates.
    ///
    QRect childrenPermanentRect() const;

    using QWidget::addAction;

protected:
    void actionEvent(QActionEvent *event) override;
    void resizeEvent(QResizeEvent *event) override;

private:
    QToolBar *m_actionBar;
    QToolBar *m_permanentActionBar;
    QHash<QAction *, QAction *> m_statusActionHash;
};

} // namespace LqRibbon

#endif // LQRIBBON_STATUSBAR_H
