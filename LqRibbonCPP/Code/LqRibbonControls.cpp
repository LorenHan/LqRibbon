#include "LqRibbonControls.h"

#include "LqRibbon.h"

#include <QActionEvent>
#include <QChildEvent>
#include <QHBoxLayout>
#include <QPainter>
#include <QStyleOption>
#include <QWidgetAction>

namespace {

const int controlHeight = 24;
const int inputControlWidth = 128;
const int narrowControlWidth = 72;
const int toolbarIconSize = 16;

///
/// \brief configureEmbeddedInput
/// Applies compact Ribbon metrics to an embedded input widget.
/// \param widget Widget to configure.
/// \param width Preferred fixed width.
///
void configureEmbeddedInput(QWidget *widget, int width)
{
    widget->setFixedHeight(controlHeight);
    widget->setMinimumWidth(width);
    widget->setMaximumWidth(width);
    widget->setSizePolicy(QSizePolicy::Fixed, QSizePolicy::Fixed);
    widget->setFocusPolicy(Qt::StrongFocus);
}

///
/// \brief configureChoiceWidget
/// Applies compact Ribbon metrics to check and radio widgets.
/// \param widget Widget to configure.
///
void configureChoiceWidget(QWidget *widget)
{
    widget->setFixedHeight(controlHeight);
    widget->setSizePolicy(QSizePolicy::Minimum, QSizePolicy::Fixed);
    widget->setFocusPolicy(Qt::StrongFocus);
}

} // namespace

namespace LqRibbon {

///
/// \brief RibbonControlSizeDefinition::RibbonControlSizeDefinition
/// Creates size hints for a control at one adaptive size.
/// \param parent Owning Ribbon control.
/// \param size Adaptive size key.
///
RibbonControlSizeDefinition::RibbonControlSizeDefinition(RibbonControl *parent,
                                                         GroupSize size)
    : QObject(parent)
    , m_size(size)
    , m_imageSize(ImageSmall)
    , m_labelVisible(true)
    , m_popup(false)
    , m_visualIndex(0)
    , m_wordWrap(false)
    , m_showSeparator(false)
    , m_visible(true)
    , m_enabled(true)
    , m_stretchable(false)
    , m_minimumItemCount(0)
    , m_maximumItemCount(0)
{
}

RibbonControlSizeDefinition::ControlImageSize
RibbonControlSizeDefinition::imageSize() const
{
    return m_imageSize;
}

void RibbonControlSizeDefinition::setImageSize(ControlImageSize size)
{
    m_imageSize = size;
}

bool RibbonControlSizeDefinition::isLabelVisible() const
{
    return m_labelVisible;
}

void RibbonControlSizeDefinition::setLabelVisible(bool visible)
{
    m_labelVisible = visible;
}

bool RibbonControlSizeDefinition::isPopup() const
{
    return m_popup;
}

void RibbonControlSizeDefinition::setPopup(bool popup)
{
    m_popup = popup;
}

int RibbonControlSizeDefinition::visualIndex() const
{
    return m_visualIndex;
}

void RibbonControlSizeDefinition::setVisualIndex(int index)
{
    m_visualIndex = index;
}

bool RibbonControlSizeDefinition::wordWrap() const
{
    return m_wordWrap;
}

void RibbonControlSizeDefinition::setWordWrap(bool on)
{
    m_wordWrap = on;
}

bool RibbonControlSizeDefinition::showSeparator() const
{
    return m_showSeparator;
}

void RibbonControlSizeDefinition::setShowSeparator(bool showSeparator)
{
    m_showSeparator = showSeparator;
}

bool RibbonControlSizeDefinition::isVisible() const
{
    return m_visible;
}

void RibbonControlSizeDefinition::setVisible(bool visible)
{
    m_visible = visible;
}

bool RibbonControlSizeDefinition::isEnabled() const
{
    return m_enabled;
}

void RibbonControlSizeDefinition::setEnabled(bool enabled)
{
    m_enabled = enabled;
}

bool RibbonControlSizeDefinition::isStretchable() const
{
    return m_stretchable;
}

void RibbonControlSizeDefinition::setStretchable(bool stretchable)
{
    m_stretchable = stretchable;
}

int RibbonControlSizeDefinition::minimumItemCount() const
{
    return m_minimumItemCount;
}

void RibbonControlSizeDefinition::setMinimumItemCount(int count)
{
    m_minimumItemCount = qMax(0, count);
}

int RibbonControlSizeDefinition::maximumItemCount() const
{
    return m_maximumItemCount;
}

void RibbonControlSizeDefinition::setMaximumItemCount(int count)
{
    m_maximumItemCount = qMax(0, count);
}

RibbonControlSizeDefinition::GroupSize
RibbonControlSizeDefinition::groupSize() const
{
    return m_size;
}

///
/// \brief RibbonControl::RibbonControl
/// Creates a base Ribbon control.
/// \param parent Parent Ribbon group.
///
RibbonControl::RibbonControl(RibbonGroup *parent)
    : QWidget(parent)
    , m_currentSize(RibbonControlSizeDefinition::GroupMedium)
    , m_dirty(false)
{
    setObjectName(QStringLiteral("lqRibbonControl"));
    setSizePolicy(QSizePolicy::Fixed, QSizePolicy::Fixed);
}

RibbonControl::~RibbonControl() = default;

RibbonGroup *RibbonControl::parentGroup() const
{
    return qobject_cast<RibbonGroup *>(parentWidget());
}

QAction *RibbonControl::defaultAction() const
{
    return m_defaultAction.data();
}

void RibbonControl::setDefaultAction(QAction *action)
{
    if (m_defaultAction == action) {
        return;
    }

    if (m_defaultAction) {
        disconnect(m_defaultAction.data(), nullptr, this, nullptr);
    }

    m_defaultAction = action;
    if (m_defaultAction) {
        connect(m_defaultAction.data(), &QAction::changed,
                this, &RibbonControl::actionChanged);
    }

    actionChanged();
}

bool RibbonControl::adjustCurrentSize(bool expand)
{
    RibbonControlSizeDefinition::GroupSize nextSize = expand
        ? RibbonControlSizeDefinition::GroupLarge
        : RibbonControlSizeDefinition::GroupSmall;
    if (m_currentSize == nextSize) {
        return false;
    }

    m_currentSize = nextSize;
    sizeChanged(m_currentSize);
    updateLayout();
    return true;
}

void RibbonControl::sizeChanged(RibbonControlSizeDefinition::GroupSize size)
{
    Q_UNUSED(size)
}

void RibbonControl::actionChanged()
{
    QAction *action = defaultAction();
    if (!action) {
        return;
    }

    setVisible(action->isVisible());
    setEnabled(action->isEnabled());
    setToolTip(action->toolTip());
    update();
}

void RibbonControl::updateLayout()
{
    m_dirty = false;
    updateGeometry();
    update();
}

RibbonControlSizeDefinition::GroupSize RibbonControl::currentSize() const
{
    return m_currentSize;
}

RibbonControlSizeDefinition *RibbonControl::sizeDefinition(
    RibbonControlSizeDefinition::GroupSize size) const
{
    const int key = static_cast<int>(size);
    RibbonControlSizeDefinition *definition = m_sizeDefinitionHash.value(key);
    if (!definition) {
        definition = new RibbonControlSizeDefinition(
            const_cast<RibbonControl *>(this), size);
        m_sizeDefinitionHash.insert(key, definition);
    }

    return definition;
}

QSize RibbonControl::getBoundedSizeHint(const QWidget *widget)
{
    if (!widget) {
        return QSize();
    }

    QSize hint = widget->sizeHint().expandedTo(widget->minimumSizeHint());
    hint = hint.expandedTo(widget->minimumSize());

    const QSize maximumSize = widget->maximumSize();
    if (maximumSize.width() < QWIDGETSIZE_MAX) {
        hint.setWidth(qMin(hint.width(), maximumSize.width()));
    }
    if (maximumSize.height() < QWIDGETSIZE_MAX) {
        hint.setHeight(qMin(hint.height(), maximumSize.height()));
    }

    return hint;
}

void RibbonControl::paintEvent(QPaintEvent *event)
{
    QWidget::paintEvent(event);
}

void RibbonControl::setDirty()
{
    m_dirty = true;
}

///
/// \brief RibbonWidgetControl::RibbonWidgetControl
/// Creates an empty widget-hosting control.
/// \param parent Parent Ribbon group.
/// \param ignoreActionSettings true to avoid mirroring default action state.
///
RibbonWidgetControl::RibbonWidgetControl(RibbonGroup *parent,
                                         bool ignoreActionSettings)
    : RibbonControl(parent)
    , m_contentWidget(nullptr)
    , m_ignoreActionSettings(ignoreActionSettings)
{
    setMargin(1);
}

RibbonWidgetControl::~RibbonWidgetControl() = default;

int RibbonWidgetControl::margin() const
{
    QMargins margins = contentsMargins();
    return qMax(qMax(margins.left(), margins.right()),
                qMax(margins.top(), margins.bottom()));
}

void RibbonWidgetControl::setMargin(int margin)
{
    setContentsMargins(margin, margin, margin, margin);
    updateLayout();
}

void RibbonWidgetControl::setMargins(int left, int top, int right, int bottom)
{
    setContentsMargins(left, top, right, bottom);
    updateLayout();
}

void RibbonWidgetControl::sizeChanged(RibbonControlSizeDefinition::GroupSize size)
{
    RibbonControl::sizeChanged(size);
}

QSize RibbonWidgetControl::sizeHint() const
{
    QSize hint = m_contentWidget
        ? RibbonControl::getBoundedSizeHint(m_contentWidget)
        : QSize(controlHeight, controlHeight);
    QMargins margins = contentsMargins();
    hint.rwidth() += margins.left() + margins.right();
    hint.rheight() += margins.top() + margins.bottom();
    return hint;
}

QWidget *RibbonWidgetControl::contentWidget() const
{
    return m_contentWidget;
}

void RibbonWidgetControl::setContentWidget(QWidget *widget)
{
    if (m_contentWidget == widget) {
        return;
    }

    if (m_contentWidget) {
        m_contentWidget->removeEventFilter(this);
        m_contentWidget->setParent(nullptr);
    }

    m_contentWidget = widget;
    if (m_contentWidget) {
        m_contentWidget->setParent(this);
        m_contentWidget->installEventFilter(this);
        m_contentWidget->show();
    }

    updateLayout();
}

void RibbonWidgetControl::childEvent(QChildEvent *event)
{
    RibbonControl::childEvent(event);
}

void RibbonWidgetControl::paintEvent(QPaintEvent *event)
{
    RibbonControl::paintEvent(event);
}

void RibbonWidgetControl::resizeEvent(QResizeEvent *event)
{
    RibbonControl::resizeEvent(event);

    if (!m_contentWidget) {
        return;
    }

    const QMargins margins = contentsMargins();
    const QRect contentRect(margins.left(),
                            margins.top(),
                            qMax(0, width() - margins.left()
                                 - margins.right()),
                            qMax(0, height() - margins.top()
                                 - margins.bottom()));
    m_contentWidget->setGeometry(contentRect);
}

///
/// \brief RibbonColumnBreakControl::RibbonColumnBreakControl
/// Creates a visual divider.
/// \param parent Parent Ribbon group.
///
RibbonColumnBreakControl::RibbonColumnBreakControl(RibbonGroup *parent)
    : RibbonWidgetControl(parent, true)
    , m_alignmentText(Qt::AlignCenter)
{
    setFixedSize(8, 72);
}

RibbonColumnBreakControl::~RibbonColumnBreakControl() = default;

Qt::Alignment RibbonColumnBreakControl::alignmentText() const
{
    return m_alignmentText;
}

void RibbonColumnBreakControl::setAlignmentText(Qt::Alignment alignment)
{
    m_alignmentText = alignment;
    update();
}

void RibbonColumnBreakControl::sizeChanged(
    RibbonControlSizeDefinition::GroupSize size)
{
    RibbonWidgetControl::sizeChanged(size);
}

QSize RibbonColumnBreakControl::sizeHint() const
{
    return QSize(8, 72);
}

void RibbonColumnBreakControl::paintEvent(QPaintEvent *event)
{
    Q_UNUSED(event)

    QPainter painter(this);
    painter.setPen(QColor(QStringLiteral("#d6dce5")));
    const int x = width() / 2;
    painter.drawLine(x, 6, x, height() - 6);
}

RibbonLabelControl::RibbonLabelControl(RibbonGroup *parent)
    : RibbonLabelControl(QString(), parent)
{
}

RibbonLabelControl::RibbonLabelControl(const QString &strText,
                                       RibbonGroup *parent)
    : RibbonWidgetControl(parent, true)
{
    QLabel *label = new QLabel(strText, this);
    label->setAlignment(Qt::AlignLeft | Qt::AlignVCenter);
    configureChoiceWidget(label);
    setContentWidget(label);
}

RibbonLabelControl::~RibbonLabelControl() = default;

QLabel *RibbonLabelControl::widget() const
{
    return qobject_cast<QLabel *>(contentWidget());
}

///
/// \brief RibbonToolBarControl::RibbonToolBarControl
/// Creates a compact toolbar control.
/// \param parent Parent Ribbon group.
///
RibbonToolBarControl::RibbonToolBarControl(RibbonGroup *parent)
    : RibbonControl(parent)
    , m_toolBar(new QToolBar(this))
    , m_overflowMenu(new QMenu(this))
    , m_margin(1)
    , m_rowsCount(1)
{
    m_toolBar->setObjectName(QStringLiteral("lqRibbonToolBarControlBar"));
    m_toolBar->setMovable(false);
    m_toolBar->setFloatable(false);
    m_toolBar->setIconSize(QSize(toolbarIconSize, toolbarIconSize));
    m_toolBar->setToolButtonStyle(Qt::ToolButtonTextBesideIcon);
    m_toolBar->setContentsMargins(0, 0, 0, 0);
    setFixedHeight(controlHeight + (m_margin * 2));
}

RibbonToolBarControl::~RibbonToolBarControl() = default;

void RibbonToolBarControl::clear()
{
    m_toolBar->clear();
    m_overflowMenu->clear();
    updateLayout();
}

QAction *RibbonToolBarControl::addWidget(QWidget *widget)
{
    QAction *action = m_toolBar->addWidget(widget);
    updateLayout();
    return action;
}

QAction *RibbonToolBarControl::addWidget(const QIcon &icon,
                                         const QString &strText,
                                         QWidget *widget)
{
    QWidgetAction *action = new QWidgetAction(this);
    action->setIcon(icon);
    action->setText(strText);
    action->setDefaultWidget(widget);
    m_toolBar->addAction(action);
    updateLayout();
    return action;
}

QAction *RibbonToolBarControl::addMenu(
    const QIcon &icon,
    const QString &strText,
    QMenu *menu,
    QToolButton::ToolButtonPopupMode mode)
{
    QAction *action = new QAction(icon, strText, this);
    return addAction(action, Qt::ToolButtonTextBesideIcon, menu, mode);
}

QAction *RibbonToolBarControl::addAction(
    QAction *action,
    Qt::ToolButtonStyle style,
    QMenu *menu,
    QToolButton::ToolButtonPopupMode mode)
{
    return insertAction(nullptr, action, style, menu, mode);
}

QAction *RibbonToolBarControl::insertAction(
    QAction *before,
    QAction *action,
    Qt::ToolButtonStyle style,
    QMenu *menu,
    QToolButton::ToolButtonPopupMode mode)
{
    if (!action) {
        return nullptr;
    }

    if (menu) {
        action->setMenu(menu);
    }

    if (before) {
        m_toolBar->insertAction(before, action);
    } else {
        m_toolBar->addAction(action);
    }

    QToolButton *button = qobject_cast<QToolButton *>(
        m_toolBar->widgetForAction(action));
    if (button) {
        button->setToolButtonStyle(style);
        button->setPopupMode(action->menu() ? mode : QToolButton::DelayedPopup);
        button->setAutoRaise(true);
    }

    updateLayout();
    return action;
}

QAction *RibbonToolBarControl::addAction(const QString &strText)
{
    return addAction(QIcon(), strText);
}

QAction *RibbonToolBarControl::addAction(const QIcon &icon,
                                         const QString &strText)
{
    return addAction(icon,
                     strText,
                     Qt::ToolButtonTextBesideIcon,
                     nullptr,
                     QToolButton::MenuButtonPopup);
}

QAction *RibbonToolBarControl::addAction(
    const QIcon &icon,
    const QString &strText,
    Qt::ToolButtonStyle style,
    QMenu *menu,
    QToolButton::ToolButtonPopupMode mode)
{
    QAction *action = new QAction(icon, strText, this);
    return addAction(action, style, menu, mode);
}

QAction *RibbonToolBarControl::addSeparator()
{
    QAction *action = m_toolBar->addSeparator();
    updateLayout();
    return action;
}

QMenu *RibbonToolBarControl::overflowMenu()
{
    return m_overflowMenu;
}

bool RibbonToolBarControl::isOverflowMenuIsEmpty() const
{
    return m_overflowMenu->actions().isEmpty();
}

int RibbonToolBarControl::margin() const
{
    return m_margin;
}

void RibbonToolBarControl::setMargin(int margin)
{
    m_margin = qMax(0, margin);
    updateLayout();
}

QWidget *RibbonToolBarControl::widgetByAction(QAction *action)
{
    return m_toolBar->widgetForAction(action);
}

void RibbonToolBarControl::sizeChanged(
    RibbonControlSizeDefinition::GroupSize size)
{
    RibbonControl::sizeChanged(size);
}

bool RibbonToolBarControl::adjustCurrentSize(bool expand)
{
    return RibbonControl::adjustCurrentSize(expand);
}

void RibbonToolBarControl::updateLayout()
{
    const QSize hint = m_toolBar->sizeHint();
    setFixedSize(hint.width() + (m_margin * 2),
                 (controlHeight * m_rowsCount) + (m_margin * 2));
    m_toolBar->setGeometry(m_margin,
                           m_margin,
                           qMax(0, width() - (m_margin * 2)),
                           qMax(0, height() - (m_margin * 2)));
    RibbonControl::updateLayout();
}

QSize RibbonToolBarControl::sizeHint() const
{
    QSize hint = m_toolBar->sizeHint();
    hint.rwidth() += m_margin * 2;
    hint.rheight() = (controlHeight * m_rowsCount) + (m_margin * 2);
    return hint;
}

int RibbonToolBarControl::rowsCount() const
{
    return m_rowsCount;
}

void RibbonToolBarControl::setRowsCount(int count)
{
    m_rowsCount = qMax(1, count);
    updateLayout();
}

void RibbonToolBarControl::setDirty()
{
    RibbonControl::setDirty();
}

void RibbonToolBarControl::paintEvent(QPaintEvent *event)
{
    RibbonControl::paintEvent(event);
}

void RibbonToolBarControl::actionEvent(QActionEvent *event)
{
    RibbonControl::actionEvent(event);
    updateLayout();
}

void RibbonToolBarControl::changeEvent(QEvent *event)
{
    RibbonControl::changeEvent(event);
    updateLayout();
}

///
/// \brief RibbonButtonControl::RibbonButtonControl
/// Creates a button control backed by QToolButton.
/// \param parent Parent Ribbon group.
///
RibbonButtonControl::RibbonButtonControl(RibbonGroup *parent)
    : RibbonWidgetControl(parent, false)
{
    QToolButton *button = new QToolButton(this);
    button->setAutoRaise(true);
    button->setToolButtonStyle(Qt::ToolButtonTextBesideIcon);
    button->setPopupMode(QToolButton::DelayedPopup);
    button->setFixedHeight(controlHeight);
    button->setIconSize(QSize(toolbarIconSize, toolbarIconSize));
    setContentWidget(button);
}

RibbonButtonControl::~RibbonButtonControl() = default;

const QIcon &RibbonButtonControl::largeIcon() const
{
    return m_largeIcon;
}

void RibbonButtonControl::setLargeIcon(const QIcon &icon)
{
    m_largeIcon = icon;
    if (currentSize() == RibbonControlSizeDefinition::GroupLarge) {
        widget()->setIcon(icon);
    }
}

const QIcon &RibbonButtonControl::smallIcon() const
{
    return m_smallIcon;
}

void RibbonButtonControl::setSmallIcon(const QIcon &icon)
{
    m_smallIcon = icon;
    if (currentSize() != RibbonControlSizeDefinition::GroupLarge) {
        widget()->setIcon(icon);
    }
}

const QString &RibbonButtonControl::label() const
{
    return m_strLabel;
}

void RibbonButtonControl::setLabel(const QString &strLabel)
{
    m_strLabel = strLabel;
    widget()->setText(strLabel);
    updateLayout();
}

void RibbonButtonControl::setMenu(QMenu *menu)
{
    widget()->setMenu(menu);
}

QMenu *RibbonButtonControl::menu() const
{
    return widget()->menu();
}

void RibbonButtonControl::setPopupMode(QToolButton::ToolButtonPopupMode mode)
{
    widget()->setPopupMode(mode);
}

QToolButton::ToolButtonPopupMode RibbonButtonControl::popupMode() const
{
    return widget()->popupMode();
}

void RibbonButtonControl::setToolButtonStyle(Qt::ToolButtonStyle style)
{
    widget()->setToolButtonStyle(style);
    updateLayout();
}

Qt::ToolButtonStyle RibbonButtonControl::toolButtonStyle() const
{
    return widget()->toolButtonStyle();
}

QToolButton *RibbonButtonControl::widget() const
{
    return qobject_cast<QToolButton *>(contentWidget());
}

QSize RibbonButtonControl::sizeHint() const
{
    return RibbonWidgetControl::sizeHint();
}

void RibbonButtonControl::sizeChanged(RibbonControlSizeDefinition::GroupSize size)
{
    RibbonWidgetControl::sizeChanged(size);
    QToolButton *button = widget();
    if (!button) {
        return;
    }

    const bool large = size == RibbonControlSizeDefinition::GroupLarge;
    button->setToolButtonStyle(large
                               ? Qt::ToolButtonTextUnderIcon
                               : Qt::ToolButtonTextBesideIcon);
    button->setIcon(large ? m_largeIcon : m_smallIcon);
    button->setIconSize(large ? QSize(32, 32) : QSize(16, 16));
}

void RibbonButtonControl::actionChanged()
{
    RibbonWidgetControl::actionChanged();
    QAction *action = defaultAction();
    if (!action || !widget()) {
        return;
    }

    widget()->setDefaultAction(action);
    if (m_strLabel.isEmpty()) {
        m_strLabel = action->text();
    }
}

bool RibbonButtonControl::event(QEvent *event)
{
    return RibbonWidgetControl::event(event);
}

RibbonCheckBoxControl::RibbonCheckBoxControl(const QString &strText,
                                             RibbonGroup *parent)
    : RibbonWidgetControl(parent, true)
{
    QCheckBox *checkBox = new QCheckBox(strText, this);
    configureChoiceWidget(checkBox);
    setContentWidget(checkBox);
}

RibbonCheckBoxControl::~RibbonCheckBoxControl() = default;

QCheckBox *RibbonCheckBoxControl::widget() const
{
    return qobject_cast<QCheckBox *>(contentWidget());
}

RibbonRadioButtonControl::RibbonRadioButtonControl(const QString &strText,
                                                   RibbonGroup *parent)
    : RibbonWidgetControl(parent, true)
{
    QRadioButton *radioButton = new QRadioButton(strText, this);
    configureChoiceWidget(radioButton);
    setContentWidget(radioButton);
}

RibbonRadioButtonControl::~RibbonRadioButtonControl() = default;

QRadioButton *RibbonRadioButtonControl::widget() const
{
    return qobject_cast<QRadioButton *>(contentWidget());
}

RibbonFontComboBoxControl::RibbonFontComboBoxControl(RibbonGroup *parent)
    : RibbonWidgetControl(parent, true)
{
    QFontComboBox *comboBox = new QFontComboBox(this);
    configureEmbeddedInput(comboBox, inputControlWidth);
    setContentWidget(comboBox);
}

RibbonFontComboBoxControl::~RibbonFontComboBoxControl() = default;

QFontComboBox *RibbonFontComboBoxControl::widget() const
{
    return qobject_cast<QFontComboBox *>(contentWidget());
}

RibbonLineEditControl::RibbonLineEditControl(RibbonGroup *parent)
    : RibbonWidgetControl(parent, true)
{
    QLineEdit *lineEdit = new QLineEdit(this);
    configureEmbeddedInput(lineEdit, inputControlWidth);
    setContentWidget(lineEdit);
}

RibbonLineEditControl::~RibbonLineEditControl() = default;

QLineEdit *RibbonLineEditControl::widget() const
{
    return qobject_cast<QLineEdit *>(contentWidget());
}

RibbonComboBoxControl::RibbonComboBoxControl(RibbonGroup *parent)
    : RibbonWidgetControl(parent, true)
{
    QComboBox *comboBox = new QComboBox(this);
    configureEmbeddedInput(comboBox, inputControlWidth);
    setContentWidget(comboBox);
}

RibbonComboBoxControl::~RibbonComboBoxControl() = default;

QComboBox *RibbonComboBoxControl::widget() const
{
    return qobject_cast<QComboBox *>(contentWidget());
}

RibbonSpinBoxControl::RibbonSpinBoxControl(RibbonGroup *parent)
    : RibbonWidgetControl(parent, true)
{
    QSpinBox *spinBox = new QSpinBox(this);
    configureEmbeddedInput(spinBox, narrowControlWidth);
    setContentWidget(spinBox);
}

RibbonSpinBoxControl::~RibbonSpinBoxControl() = default;

QSpinBox *RibbonSpinBoxControl::widget() const
{
    return qobject_cast<QSpinBox *>(contentWidget());
}

RibbonDoubleSpinBoxControl::RibbonDoubleSpinBoxControl(RibbonGroup *parent)
    : RibbonWidgetControl(parent, true)
{
    QDoubleSpinBox *spinBox = new QDoubleSpinBox(this);
    configureEmbeddedInput(spinBox, narrowControlWidth + 20);
    setContentWidget(spinBox);
}

RibbonDoubleSpinBoxControl::~RibbonDoubleSpinBoxControl() = default;

QDoubleSpinBox *RibbonDoubleSpinBoxControl::widget() const
{
    return qobject_cast<QDoubleSpinBox *>(contentWidget());
}

RibbonSliderControl::RibbonSliderControl(Qt::Orientation orientation,
                                         RibbonGroup *parent)
    : RibbonWidgetControl(parent, true)
{
    QSlider *slider = new QSlider(orientation, this);
    configureEmbeddedInput(slider, inputControlWidth);
    setContentWidget(slider);
}

RibbonSliderControl::~RibbonSliderControl() = default;

QSlider *RibbonSliderControl::widget() const
{
    return qobject_cast<QSlider *>(contentWidget());
}

RibbonSliderPaneControl::RibbonSliderPaneControl(RibbonGroup *parent)
    : RibbonWidgetControl(parent, true)
{
    RibbonSliderPane *sliderPane = new RibbonSliderPane(this);
    setContentWidget(sliderPane);
}

RibbonSliderPaneControl::~RibbonSliderPaneControl() = default;

RibbonSliderPane *RibbonSliderPaneControl::widget() const
{
    return qobject_cast<RibbonSliderPane *>(contentWidget());
}

RibbonDateTimeEditControl::RibbonDateTimeEditControl(RibbonGroup *parent)
    : RibbonWidgetControl(parent, true)
{
    QDateTimeEdit *dateTimeEdit = new QDateTimeEdit(this);
    configureEmbeddedInput(dateTimeEdit, inputControlWidth + 24);
    setContentWidget(dateTimeEdit);
}

RibbonDateTimeEditControl::~RibbonDateTimeEditControl() = default;

QDateTimeEdit *RibbonDateTimeEditControl::widget() const
{
    return qobject_cast<QDateTimeEdit *>(contentWidget());
}

bool RibbonDateTimeEditControl::calendarPopup() const
{
    return widget() ? widget()->calendarPopup() : false;
}

void RibbonDateTimeEditControl::setCalendarPopup(bool enable)
{
    if (widget()) {
        widget()->setCalendarPopup(enable);
    }
}

RibbonTimeEditControl::RibbonTimeEditControl(RibbonGroup *parent)
    : RibbonWidgetControl(parent, true)
{
    QTimeEdit *timeEdit = new QTimeEdit(this);
    configureEmbeddedInput(timeEdit, narrowControlWidth + 20);
    setContentWidget(timeEdit);
}

RibbonTimeEditControl::~RibbonTimeEditControl() = default;

QTimeEdit *RibbonTimeEditControl::widget() const
{
    return qobject_cast<QTimeEdit *>(contentWidget());
}

RibbonDateEditControl::RibbonDateEditControl(RibbonGroup *parent)
    : RibbonWidgetControl(parent, true)
{
    QDateEdit *dateEdit = new QDateEdit(this);
    configureEmbeddedInput(dateEdit, inputControlWidth);
    setContentWidget(dateEdit);
}

RibbonDateEditControl::~RibbonDateEditControl() = default;

QDateEdit *RibbonDateEditControl::widget() const
{
    return qobject_cast<QDateEdit *>(contentWidget());
}

bool RibbonDateEditControl::calendarPopup() const
{
    return widget() ? widget()->calendarPopup() : false;
}

void RibbonDateEditControl::setCalendarPopup(bool enable)
{
    if (widget()) {
        widget()->setCalendarPopup(enable);
    }
}

} // namespace LqRibbon
