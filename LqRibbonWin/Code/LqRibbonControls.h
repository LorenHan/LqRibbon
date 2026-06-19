#ifndef LQRIBBON_CONTROLS_H
#define LQRIBBON_CONTROLS_H

#include <QAction>
#include <QCheckBox>
#include <QComboBox>
#include <QDateEdit>
#include <QDateTimeEdit>
#include <QDoubleSpinBox>
#include <QFontComboBox>
#include <QHash>
#include <QIcon>
#include <QLabel>
#include <QLineEdit>
#include <QMenu>
#include <QPointer>
#include <QRadioButton>
#include <QSlider>
#include <QSpinBox>
#include <QTimeEdit>
#include <QToolBar>
#include <QToolButton>
#include <QWidget>

#include "LqRibbonStatusBar.h"

namespace LqRibbon {

class RibbonGroup;
class RibbonControl;

///
/// \brief The RibbonControlSizeDefinition class stores adaptive control hints.
///
class RibbonControlSizeDefinition : public QObject
{
    Q_OBJECT

public:
    enum GroupSize
    {
        GroupLarge = 0x01,
        GroupMedium = 0x02,
        GroupSmall = 0x04,
        GroupPopup = 0x08,
        GroupSimplified = 0x10,
        GroupSimplifiedOverflow = 0x20
    };
    Q_DECLARE_FLAGS(GroupSizes, GroupSize)

    enum ControlImageSize
    {
        ImageNone,
        ImageLarge,
        ImageSmall
    };

    explicit RibbonControlSizeDefinition(RibbonControl *parent,
                                         GroupSize size);

    ControlImageSize imageSize() const;
    void setImageSize(ControlImageSize size);
    bool isLabelVisible() const;
    void setLabelVisible(bool visible);
    bool isPopup() const;
    void setPopup(bool popup);
    int visualIndex() const;
    void setVisualIndex(int index);
    bool wordWrap() const;
    void setWordWrap(bool on);
    bool showSeparator() const;
    void setShowSeparator(bool showSeparator);
    bool isVisible() const;
    void setVisible(bool visible);
    bool isEnabled() const;
    void setEnabled(bool enabled);
    bool isStretchable() const;
    void setStretchable(bool stretchable);
    int minimumItemCount() const;
    void setMinimumItemCount(int count);
    int maximumItemCount() const;
    void setMaximumItemCount(int count);
    GroupSize groupSize() const;

private:
    GroupSize m_size;
    ControlImageSize m_imageSize;
    bool m_labelVisible;
    bool m_popup;
    int m_visualIndex;
    bool m_wordWrap;
    bool m_showSeparator;
    bool m_visible;
    bool m_enabled;
    bool m_stretchable;
    int m_minimumItemCount;
    int m_maximumItemCount;
};

///
/// \brief The RibbonControl class is the base for embeddable Ribbon controls.
///
class RibbonControl : public QWidget
{
    Q_OBJECT

public:
    explicit RibbonControl(RibbonGroup *parent = nullptr);
    ~RibbonControl() override;

    RibbonGroup *parentGroup() const;
    QAction *defaultAction() const;
    void setDefaultAction(QAction *action);
    virtual bool adjustCurrentSize(bool expand);
    virtual void sizeChanged(RibbonControlSizeDefinition::GroupSize size);
    virtual void actionChanged();
    virtual void updateLayout();
    RibbonControlSizeDefinition::GroupSize currentSize() const;
    RibbonControlSizeDefinition *sizeDefinition(
        RibbonControlSizeDefinition::GroupSize size) const;
    static QSize getBoundedSizeHint(const QWidget *widget);

protected:
    void paintEvent(QPaintEvent *event) override;
    virtual void setDirty();

private:
    QPointer<QAction> m_defaultAction;
    mutable QHash<int, RibbonControlSizeDefinition *> m_sizeDefinitionHash;
    RibbonControlSizeDefinition::GroupSize m_currentSize;
    bool m_dirty;
};

///
/// \brief The RibbonWidgetControl class hosts one native Qt widget.
///
class RibbonWidgetControl : public RibbonControl
{
    Q_OBJECT

public:
    explicit RibbonWidgetControl(RibbonGroup *parent = nullptr,
                                 bool ignoreActionSettings = false);
    ~RibbonWidgetControl() override;

    int margin() const;
    void setMargin(int margin);
    void setMargins(int left, int top, int right, int bottom);
    void sizeChanged(RibbonControlSizeDefinition::GroupSize size) override;
    QSize sizeHint() const override;

protected:
    QWidget *contentWidget() const;
    void setContentWidget(QWidget *widget);
    void childEvent(QChildEvent *event) override;
    void paintEvent(QPaintEvent *event) override;
    void resizeEvent(QResizeEvent *event) override;

private:
    QWidget *m_contentWidget;
    bool m_ignoreActionSettings;
};

///
/// \brief The RibbonColumnBreakControl class draws a compact column divider.
///
class RibbonColumnBreakControl : public RibbonWidgetControl
{
    Q_OBJECT

public:
    explicit RibbonColumnBreakControl(RibbonGroup *parent = nullptr);
    ~RibbonColumnBreakControl() override;

    Qt::Alignment alignmentText() const;
    void setAlignmentText(Qt::Alignment alignment);
    void sizeChanged(RibbonControlSizeDefinition::GroupSize size) override;
    QSize sizeHint() const override;

protected:
    void paintEvent(QPaintEvent *event) override;

private:
    Qt::Alignment m_alignmentText;
};

class RibbonLabelControl : public RibbonWidgetControl
{
    Q_OBJECT

public:
    explicit RibbonLabelControl(RibbonGroup *parent = nullptr);
    explicit RibbonLabelControl(const QString &strText,
                                RibbonGroup *parent = nullptr);
    ~RibbonLabelControl() override;

    QLabel *widget() const;
};

///
/// \brief The RibbonToolBarControl class exposes compact toolbar rows.
///
class RibbonToolBarControl : public RibbonControl
{
    Q_OBJECT

public:
    explicit RibbonToolBarControl(RibbonGroup *parent = nullptr);
    ~RibbonToolBarControl() override;

    void clear();
    QAction *addWidget(QWidget *widget);
    QAction *addWidget(const QIcon &icon,
                       const QString &strText,
                       QWidget *widget);
    QAction *addMenu(const QIcon &icon,
                     const QString &strText,
                     QMenu *menu,
                     QToolButton::ToolButtonPopupMode mode =
                         QToolButton::MenuButtonPopup);
    QAction *addAction(QAction *action,
                       Qt::ToolButtonStyle style,
                       QMenu *menu = nullptr,
                       QToolButton::ToolButtonPopupMode mode =
                           QToolButton::MenuButtonPopup);
    QAction *insertAction(QAction *before,
                          QAction *action,
                          Qt::ToolButtonStyle style,
                          QMenu *menu = nullptr,
                          QToolButton::ToolButtonPopupMode mode =
                              QToolButton::MenuButtonPopup);
    QAction *addAction(const QString &strText);
    QAction *addAction(const QIcon &icon, const QString &strText);
    QAction *addAction(const QIcon &icon,
                       const QString &strText,
                       Qt::ToolButtonStyle style,
                       QMenu *menu = nullptr,
                       QToolButton::ToolButtonPopupMode mode =
                           QToolButton::MenuButtonPopup);
    QAction *addSeparator();
    QMenu *overflowMenu();
    bool isOverflowMenuIsEmpty() const;
    int margin() const;
    void setMargin(int margin);
    QWidget *widgetByAction(QAction *action);
    using QWidget::addAction;
    using QWidget::insertAction;

    void sizeChanged(RibbonControlSizeDefinition::GroupSize size) override;
    bool adjustCurrentSize(bool expand) override;
    void updateLayout() override;
    QSize sizeHint() const override;

protected:
    int rowsCount() const;
    void setRowsCount(int count);
    void setDirty() override;
    void paintEvent(QPaintEvent *event) override;
    void actionEvent(QActionEvent *event) override;
    void changeEvent(QEvent *event) override;

private:
    QToolBar *m_toolBar;
    QMenu *m_overflowMenu;
    int m_margin;
    int m_rowsCount;
};

class RibbonButtonControl : public RibbonWidgetControl
{
    Q_OBJECT

public:
    explicit RibbonButtonControl(RibbonGroup *parent = nullptr);
    ~RibbonButtonControl() override;

    const QIcon &largeIcon() const;
    void setLargeIcon(const QIcon &icon);
    const QIcon &smallIcon() const;
    void setSmallIcon(const QIcon &icon);
    const QString &label() const;
    void setLabel(const QString &strLabel);
    void setMenu(QMenu *menu);
    QMenu *menu() const;
    void setPopupMode(QToolButton::ToolButtonPopupMode mode);
    QToolButton::ToolButtonPopupMode popupMode() const;
    void setToolButtonStyle(Qt::ToolButtonStyle style);
    Qt::ToolButtonStyle toolButtonStyle() const;
    QToolButton *widget() const;
    QSize sizeHint() const override;
    void sizeChanged(RibbonControlSizeDefinition::GroupSize size) override;
    void actionChanged() override;

protected:
    bool event(QEvent *event) override;

private:
    QIcon m_largeIcon;
    QIcon m_smallIcon;
    QString m_strLabel;
};

class RibbonCheckBoxControl : public RibbonWidgetControl
{
    Q_OBJECT

public:
    explicit RibbonCheckBoxControl(const QString &strText = QString(),
                                   RibbonGroup *parent = nullptr);
    ~RibbonCheckBoxControl() override;

    QCheckBox *widget() const;
};

class RibbonRadioButtonControl : public RibbonWidgetControl
{
    Q_OBJECT

public:
    explicit RibbonRadioButtonControl(const QString &strText = QString(),
                                      RibbonGroup *parent = nullptr);
    ~RibbonRadioButtonControl() override;

    QRadioButton *widget() const;
};

class RibbonFontComboBoxControl : public RibbonWidgetControl
{
    Q_OBJECT

public:
    explicit RibbonFontComboBoxControl(RibbonGroup *parent = nullptr);
    ~RibbonFontComboBoxControl() override;

    QFontComboBox *widget() const;
};

class RibbonLineEditControl : public RibbonWidgetControl
{
    Q_OBJECT

public:
    explicit RibbonLineEditControl(RibbonGroup *parent = nullptr);
    ~RibbonLineEditControl() override;

    QLineEdit *widget() const;
};

class RibbonComboBoxControl : public RibbonWidgetControl
{
    Q_OBJECT

public:
    explicit RibbonComboBoxControl(RibbonGroup *parent = nullptr);
    ~RibbonComboBoxControl() override;

    QComboBox *widget() const;
};

class RibbonSpinBoxControl : public RibbonWidgetControl
{
    Q_OBJECT

public:
    explicit RibbonSpinBoxControl(RibbonGroup *parent = nullptr);
    ~RibbonSpinBoxControl() override;

    QSpinBox *widget() const;
};

class RibbonDoubleSpinBoxControl : public RibbonWidgetControl
{
    Q_OBJECT

public:
    explicit RibbonDoubleSpinBoxControl(RibbonGroup *parent = nullptr);
    ~RibbonDoubleSpinBoxControl() override;

    QDoubleSpinBox *widget() const;
};

class RibbonSliderControl : public RibbonWidgetControl
{
    Q_OBJECT

public:
    explicit RibbonSliderControl(Qt::Orientation orientation,
                                 RibbonGroup *parent = nullptr);
    ~RibbonSliderControl() override;

    QSlider *widget() const;
};

class RibbonSliderPaneControl : public RibbonWidgetControl
{
    Q_OBJECT

public:
    explicit RibbonSliderPaneControl(RibbonGroup *parent = nullptr);
    ~RibbonSliderPaneControl() override;

    RibbonSliderPane *widget() const;
};

class RibbonDateTimeEditControl : public RibbonWidgetControl
{
    Q_OBJECT

public:
    explicit RibbonDateTimeEditControl(RibbonGroup *parent = nullptr);
    ~RibbonDateTimeEditControl() override;

    QDateTimeEdit *widget() const;
    bool calendarPopup() const;
    void setCalendarPopup(bool enable);
};

class RibbonTimeEditControl : public RibbonWidgetControl
{
    Q_OBJECT

public:
    explicit RibbonTimeEditControl(RibbonGroup *parent = nullptr);
    ~RibbonTimeEditControl() override;

    QTimeEdit *widget() const;
};

class RibbonDateEditControl : public RibbonWidgetControl
{
    Q_OBJECT

public:
    explicit RibbonDateEditControl(RibbonGroup *parent = nullptr);
    ~RibbonDateEditControl() override;

    QDateEdit *widget() const;
    bool calendarPopup() const;
    void setCalendarPopup(bool enable);
};

} // namespace LqRibbon

Q_DECLARE_OPERATORS_FOR_FLAGS(LqRibbon::RibbonControlSizeDefinition::GroupSizes)

#endif // LQRIBBON_CONTROLS_H
