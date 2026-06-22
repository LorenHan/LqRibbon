#include "LqRibbonMessageBox.h"

#include "LqRibbon.h"

#include <QAbstractButton>
#include <QApplication>
#include <QDialog>
#include <QDialogButtonBox>
#include <QGraphicsDropShadowEffect>
#include <QHBoxLayout>
#include <QLabel>
#include <QMouseEvent>
#include <QPainter>
#include <QPainterPath>
#include <QPushButton>
#include <QScreen>
#include <QStyle>
#include <QToolButton>
#include <QVBoxLayout>

namespace {

struct RibbonMessagePalette
{
    QColor accent;
    QColor captionBackground;
    QColor captionHover;
    QColor captionText;
    QColor surface;
    QColor contentBackground;
    QColor text;
    QColor secondaryText;
    QColor border;
    QColor hover;
    QColor pressed;
    int radius;
};

RibbonMessagePalette messagePalette(LqRibbon::RibbonBar::RibbonStyle style)
{
    switch (style) {
    case LqRibbon::RibbonBar::Office2019Colorful:
        return {
            QColor(QStringLiteral("#185abd")),
            QColor(QStringLiteral("#185abd")),
            QColor(QStringLiteral("#2f6fca")),
            QColor(QStringLiteral("#ffffff")),
            QColor(QStringLiteral("#ffffff")),
            QColor(QStringLiteral("#f7f7f7")),
            QColor(QStringLiteral("#202020")),
            QColor(QStringLiteral("#605e5c")),
            QColor(QStringLiteral("#c8c8c8")),
            QColor(QStringLiteral("#deecf9")),
            QColor(QStringLiteral("#c7e0f4")),
            4
        };
    case LqRibbon::RibbonBar::Microsoft365Light:
        return {
            QColor(QStringLiteral("#0f6cbd")),
            QColor(QStringLiteral("#f8f8f8")),
            QColor(QStringLiteral("#e5f1fb")),
            QColor(QStringLiteral("#242424")),
            QColor(QStringLiteral("#ffffff")),
            QColor(QStringLiteral("#fbfbfb")),
            QColor(QStringLiteral("#242424")),
            QColor(QStringLiteral("#616161")),
            QColor(QStringLiteral("#d1d1d1")),
            QColor(QStringLiteral("#e5f1fb")),
            QColor(QStringLiteral("#cfe4fa")),
            8
        };
    case LqRibbon::RibbonBar::Microsoft365Dark:
        return {
            QColor(QStringLiteral("#60cdff")),
            QColor(QStringLiteral("#202020")),
            QColor(QStringLiteral("#3a3a3a")),
            QColor(QStringLiteral("#f3f2f1")),
            QColor(QStringLiteral("#2d2d2d")),
            QColor(QStringLiteral("#252525")),
            QColor(QStringLiteral("#f3f2f1")),
            QColor(QStringLiteral("#c8c8c8")),
            QColor(QStringLiteral("#4a4a4a")),
            QColor(QStringLiteral("#3a3a3a")),
            QColor(QStringLiteral("#4a4a4a")),
            8
        };
    case LqRibbon::RibbonBar::Office2016Blue:
    default:
        return {
            QColor(QStringLiteral("#2b579a")),
            QColor(QStringLiteral("#2b579a")),
            QColor(QStringLiteral("#386caf")),
            QColor(QStringLiteral("#ffffff")),
            QColor(QStringLiteral("#ffffff")),
            QColor(QStringLiteral("#f4f4f4")),
            QColor(QStringLiteral("#202020")),
            QColor(QStringLiteral("#605e5c")),
            QColor(QStringLiteral("#c8c8c8")),
            QColor(QStringLiteral("#e8f2ff")),
            QColor(QStringLiteral("#c5ddfa")),
            4
        };
    }
}

LqRibbon::RibbonBar::RibbonStyle effectiveRibbonStyle(QWidget *parent)
{
    for (QWidget *widget = parent; widget; widget = widget->parentWidget()) {
        if (LqRibbon::RibbonMainWindow *mainWindow =
                qobject_cast<LqRibbon::RibbonMainWindow *>(widget)) {
            return mainWindow->ribbonStyle();
        }
        if (LqRibbon::RibbonBar *ribbonBar =
                qobject_cast<LqRibbon::RibbonBar *>(widget)) {
            return ribbonBar->ribbonStyle();
        }
    }

    if (parent) {
        if (QWidget *window = parent->window()) {
            if (LqRibbon::RibbonMainWindow *mainWindow =
                    qobject_cast<LqRibbon::RibbonMainWindow *>(window)) {
                return mainWindow->ribbonStyle();
            }
        }
    }

    return LqRibbon::RibbonBar::Office2016Blue;
}

QPoint mouseGlobalPosition(QMouseEvent *event)
{
#if QT_VERSION >= QT_VERSION_CHECK(6, 0, 0)
    return event->globalPosition().toPoint();
#else
    return event->globalPos();
#endif
}

QString colorName(const QColor &color)
{
    return color.name(QColor::HexRgb);
}

QPixmap fallbackWindowIcon(const RibbonMessagePalette &palette, qreal deviceRatio)
{
    QPixmap pixmap(qRound(16 * deviceRatio), qRound(16 * deviceRatio));
    pixmap.setDevicePixelRatio(deviceRatio);
    pixmap.fill(Qt::transparent);

    QPainter painter(&pixmap);
    painter.setRenderHint(QPainter::Antialiasing);
    painter.scale(deviceRatio, deviceRatio);
    painter.setPen(QPen(palette.border, 1));
    painter.setBrush(palette.surface);
    painter.drawRect(QRectF(1.5, 2.5, 13.0, 11.0));
    painter.fillRect(QRectF(3.0, 4.0, 5.0, 5.0), palette.accent);
    painter.fillRect(QRectF(9.0, 4.0, 3.5, 2.0), palette.hover);
    painter.fillRect(QRectF(9.0, 7.0, 3.5, 2.0), palette.border);
    return pixmap;
}

QPixmap windowIconPixmap(QWidget *parent, const RibbonMessagePalette &palette)
{
    const qreal deviceRatio = parent ? parent->devicePixelRatioF() : qApp->devicePixelRatio();
    QIcon icon;
    if (parent && parent->window()) {
        icon = parent->window()->windowIcon();
    }
    if (icon.isNull()) {
        icon = qApp->windowIcon();
    }
    if (!icon.isNull()) {
        QPixmap pixmap = icon.pixmap(QSize(16, 16) * deviceRatio);
        pixmap.setDevicePixelRatio(deviceRatio);
        return pixmap;
    }
    return fallbackWindowIcon(palette, deviceRatio);
}

QPixmap messageIconPixmap(QMessageBox::Icon icon,
                          const RibbonMessagePalette &palette,
                          qreal deviceRatio)
{
    QPixmap pixmap(qRound(40 * deviceRatio), qRound(40 * deviceRatio));
    pixmap.setDevicePixelRatio(deviceRatio);
    pixmap.fill(Qt::transparent);

    QPainter painter(&pixmap);
    painter.setRenderHint(QPainter::Antialiasing);
    painter.scale(deviceRatio, deviceRatio);

    switch (icon) {
    case QMessageBox::Warning: {
        QPainterPath triangle;
        triangle.moveTo(20.0, 4.0);
        triangle.lineTo(37.0, 34.0);
        triangle.lineTo(3.0, 34.0);
        triangle.closeSubpath();
        painter.setPen(QPen(QColor(QStringLiteral("#8a5700")), 1.4));
        painter.setBrush(QColor(QStringLiteral("#fde7b0")));
        painter.drawPath(triangle);
        painter.setPen(QColor(QStringLiteral("#8a5700")));
        QFont font = painter.font();
        font.setBold(true);
        font.setPixelSize(24);
        painter.setFont(font);
        painter.drawText(QRectF(0.0, 9.0, 40.0, 26.0),
                         Qt::AlignCenter,
                         QStringLiteral("!"));
        break;
    }
    case QMessageBox::Critical:
        painter.setPen(Qt::NoPen);
        painter.setBrush(QColor(QStringLiteral("#c42b1c")));
        painter.drawEllipse(QRectF(3.0, 3.0, 34.0, 34.0));
        painter.setPen(QPen(Qt::white, 3.2, Qt::SolidLine, Qt::RoundCap));
        painter.drawLine(QPointF(14.0, 14.0), QPointF(26.0, 26.0));
        painter.drawLine(QPointF(26.0, 14.0), QPointF(14.0, 26.0));
        break;
    case QMessageBox::Question: {
        painter.setPen(Qt::NoPen);
        painter.setBrush(palette.accent);
        painter.drawEllipse(QRectF(3.0, 3.0, 34.0, 34.0));
        painter.setPen(Qt::white);
        QFont font = painter.font();
        font.setBold(true);
        font.setPixelSize(24);
        painter.setFont(font);
        painter.drawText(QRectF(0.0, 5.0, 40.0, 30.0),
                         Qt::AlignCenter,
                         QStringLiteral("?"));
        break;
    }
    case QMessageBox::Information:
        painter.setPen(Qt::NoPen);
        painter.setBrush(palette.accent);
        painter.drawEllipse(QRectF(3.0, 3.0, 34.0, 34.0));
        painter.setPen(Qt::white);
        {
            QFont font = painter.font();
            font.setBold(true);
            font.setPixelSize(24);
            painter.setFont(font);
        }
        painter.drawText(QRectF(0.0, 5.0, 40.0, 30.0),
                         Qt::AlignCenter,
                         QStringLiteral("i"));
        break;
    case QMessageBox::NoIcon:
    default:
        break;
    }

    return pixmap;
}

QMessageBox::StandardButton firstAvailableButton(
    QMessageBox::StandardButtons buttons,
    const QList<QMessageBox::StandardButton> &order)
{
    for (QMessageBox::StandardButton button : order) {
        if (buttons.testFlag(button)) {
            return button;
        }
    }
    return QMessageBox::NoButton;
}

QMessageBox::StandardButton defaultButtonFor(QMessageBox::StandardButtons buttons)
{
    return firstAvailableButton(buttons,
                                {
                                    QMessageBox::Ok,
                                    QMessageBox::Yes,
                                    QMessageBox::Save,
                                    QMessageBox::Open,
                                    QMessageBox::Retry,
                                    QMessageBox::Apply,
                                    QMessageBox::No,
                                    QMessageBox::Cancel,
                                    QMessageBox::Close,
                                });
}

QMessageBox::StandardButton escapeButtonFor(QMessageBox::StandardButtons buttons)
{
    return firstAvailableButton(buttons,
                                {
                                    QMessageBox::Cancel,
                                    QMessageBox::Close,
                                    QMessageBox::No,
                                    QMessageBox::Ok,
                                    QMessageBox::Yes,
                                });
}

QString standardButtonObjectName(QMessageBox::StandardButton button)
{
    switch (button) {
    case QMessageBox::Ok:
        return QStringLiteral("lqRibbonMessageBoxOkButton");
    case QMessageBox::Cancel:
        return QStringLiteral("lqRibbonMessageBoxCancelButton");
    case QMessageBox::Yes:
        return QStringLiteral("lqRibbonMessageBoxYesButton");
    case QMessageBox::No:
        return QStringLiteral("lqRibbonMessageBoxNoButton");
    case QMessageBox::Close:
        return QStringLiteral("lqRibbonMessageBoxCloseCommandButton");
    case QMessageBox::Save:
        return QStringLiteral("lqRibbonMessageBoxSaveButton");
    case QMessageBox::Discard:
        return QStringLiteral("lqRibbonMessageBoxDiscardButton");
    case QMessageBox::Apply:
        return QStringLiteral("lqRibbonMessageBoxApplyButton");
    case QMessageBox::Reset:
        return QStringLiteral("lqRibbonMessageBoxResetButton");
    case QMessageBox::RestoreDefaults:
        return QStringLiteral("lqRibbonMessageBoxRestoreDefaultsButton");
    case QMessageBox::Help:
        return QStringLiteral("lqRibbonMessageBoxHelpButton");
    case QMessageBox::SaveAll:
        return QStringLiteral("lqRibbonMessageBoxSaveAllButton");
    case QMessageBox::Open:
        return QStringLiteral("lqRibbonMessageBoxOpenButton");
    case QMessageBox::Abort:
        return QStringLiteral("lqRibbonMessageBoxAbortButton");
    case QMessageBox::Retry:
        return QStringLiteral("lqRibbonMessageBoxRetryButton");
    case QMessageBox::Ignore:
        return QStringLiteral("lqRibbonMessageBoxIgnoreButton");
    case QMessageBox::NoButton:
    default:
        return QStringLiteral("lqRibbonMessageBoxButton");
    }
}

void centerDialogOnParent(QDialog *dialog, QWidget *parent)
{
    QRect referenceRect;
    if (parent && parent->window()) {
        referenceRect = parent->window()->frameGeometry();
    } else if (QScreen *screen = QGuiApplication::primaryScreen()) {
        referenceRect = screen->availableGeometry();
    }

    if (!referenceRect.isValid()) {
        return;
    }

    const QPoint topLeft = referenceRect.center()
        - QPoint(dialog->width() / 2, dialog->height() / 2);
    dialog->move(topLeft);
}

class RibbonMessageDialog : public QDialog
{
public:
    RibbonMessageDialog(QWidget *parent,
                        QMessageBox::Icon icon,
                        const QString &title,
                        const QString &text,
                        QMessageBox::StandardButtons buttons,
                        QMessageBox::StandardButton defaultButton);

protected:
    bool eventFilter(QObject *object, QEvent *event) override;
    void reject() override;

private:
    void applyStyle(const RibbonMessagePalette &palette);
    void finish(QMessageBox::StandardButton button);

private:
    QWidget *m_titleBar;
    QMessageBox::StandardButtons m_buttons;
    bool m_dragging;
    QPoint m_dragOffset;
};

RibbonMessageDialog::RibbonMessageDialog(
    QWidget *parent,
    QMessageBox::Icon icon,
    const QString &title,
    const QString &text,
    QMessageBox::StandardButtons buttons,
    QMessageBox::StandardButton defaultButton)
    : QDialog(parent)
    , m_titleBar(nullptr)
    , m_buttons(buttons == QMessageBox::NoButton ? QMessageBox::Ok : buttons)
    , m_dragging(false)
{
    const RibbonMessagePalette palette =
        messagePalette(effectiveRibbonStyle(parent));
    const qreal deviceRatio =
        parent ? parent->devicePixelRatioF() : qApp->devicePixelRatio();

    setObjectName(QStringLiteral("lqRibbonMessageBox"));
    setWindowTitle(title);
    setModal(true);
    setWindowFlags((windowFlags() | Qt::Dialog | Qt::FramelessWindowHint)
                   & ~Qt::WindowContextHelpButtonHint);
    setAttribute(Qt::WA_TranslucentBackground, true);
    setMinimumWidth(320);

    QVBoxLayout *outerLayout = new QVBoxLayout(this);
    outerLayout->setContentsMargins(14, 14, 14, 14);
    outerLayout->setSpacing(0);

    QWidget *card = new QWidget(this);
    card->setObjectName(QStringLiteral("lqRibbonMessageBoxCard"));
    QGraphicsDropShadowEffect *shadow = new QGraphicsDropShadowEffect(card);
    shadow->setBlurRadius(28);
    shadow->setOffset(0, 8);
    shadow->setColor(QColor(0, 0, 0, 70));
    card->setGraphicsEffect(shadow);
    outerLayout->addWidget(card);

    QVBoxLayout *cardLayout = new QVBoxLayout(card);
    cardLayout->setContentsMargins(0, 0, 0, 0);
    cardLayout->setSpacing(0);

    m_titleBar = new QWidget(card);
    m_titleBar->setObjectName(QStringLiteral("lqRibbonMessageBoxTitleBar"));
    m_titleBar->setFixedHeight(36);
    m_titleBar->installEventFilter(this);
    QHBoxLayout *titleLayout = new QHBoxLayout(m_titleBar);
    titleLayout->setContentsMargins(10, 0, 4, 0);
    titleLayout->setSpacing(7);

    QLabel *windowIcon = new QLabel(m_titleBar);
    windowIcon->setObjectName(QStringLiteral("lqRibbonMessageBoxWindowIcon"));
    windowIcon->setFixedSize(16, 16);
    windowIcon->setPixmap(windowIconPixmap(parent, palette));
    titleLayout->addWidget(windowIcon);

    QLabel *titleLabel = new QLabel(title, m_titleBar);
    titleLabel->setObjectName(QStringLiteral("lqRibbonMessageBoxTitle"));
    titleLabel->setSizePolicy(QSizePolicy::Expanding, QSizePolicy::Preferred);
    titleLabel->setTextInteractionFlags(Qt::NoTextInteraction);
    titleLayout->addWidget(titleLabel);

    QToolButton *closeButton = new QToolButton(m_titleBar);
    closeButton->setObjectName(QStringLiteral("lqRibbonMessageBoxCloseButton"));
    closeButton->setText(QString(QChar(0x00d7)));
    closeButton->setAutoRaise(true);
    closeButton->setCursor(Qt::ArrowCursor);
    closeButton->setFixedSize(36, 28);
    closeButton->setAccessibleName(QObject::tr("Close"));
    QObject::connect(closeButton, &QToolButton::clicked, this, [this]() {
        reject();
    });
    titleLayout->addWidget(closeButton);
    cardLayout->addWidget(m_titleBar);

    QWidget *content = new QWidget(card);
    content->setObjectName(QStringLiteral("lqRibbonMessageBoxContent"));
    QHBoxLayout *contentLayout = new QHBoxLayout(content);
    contentLayout->setContentsMargins(22, 20, 22, 20);
    contentLayout->setSpacing(14);

    QLabel *messageIcon = new QLabel(content);
    messageIcon->setObjectName(QStringLiteral("lqRibbonMessageBoxIcon"));
    messageIcon->setFixedSize(40, 40);
    messageIcon->setPixmap(messageIconPixmap(icon, palette, deviceRatio));
    messageIcon->setVisible(icon != QMessageBox::NoIcon);
    contentLayout->addWidget(messageIcon, 0, Qt::AlignTop);

    QLabel *textLabel = new QLabel(text, content);
    textLabel->setObjectName(QStringLiteral("lqRibbonMessageBoxText"));
    textLabel->setWordWrap(true);
    textLabel->setTextInteractionFlags(Qt::TextSelectableByMouse);
    textLabel->setMinimumWidth(180);
    textLabel->setMaximumWidth(440);
    contentLayout->addWidget(textLabel, 1, Qt::AlignVCenter);
    cardLayout->addWidget(content);

    QWidget *buttonArea = new QWidget(card);
    buttonArea->setObjectName(QStringLiteral("lqRibbonMessageBoxButtonArea"));
    QHBoxLayout *buttonAreaLayout = new QHBoxLayout(buttonArea);
    buttonAreaLayout->setContentsMargins(18, 10, 18, 14);

    QDialogButtonBox *buttonBox = new QDialogButtonBox(
        static_cast<QDialogButtonBox::StandardButtons>(int(m_buttons)),
        Qt::Horizontal,
        buttonArea);
    buttonBox->setObjectName(QStringLiteral("lqRibbonMessageBoxButtons"));
    buttonAreaLayout->addStretch();
    buttonAreaLayout->addWidget(buttonBox);
    cardLayout->addWidget(buttonArea);

    QObject::connect(buttonBox,
                     &QDialogButtonBox::clicked,
                     this,
                     [this, buttonBox](QAbstractButton *button) {
        const QMessageBox::StandardButton standardButton =
            static_cast<QMessageBox::StandardButton>(
                buttonBox->standardButton(button));
        finish(standardButton == QMessageBox::NoButton
                   ? defaultButtonFor(m_buttons)
                   : standardButton);
    });

    for (QAbstractButton *abstractButton : buttonBox->buttons()) {
        QPushButton *pushButton = qobject_cast<QPushButton *>(abstractButton);
        if (!pushButton) {
            continue;
        }
        const QMessageBox::StandardButton standardButton =
            static_cast<QMessageBox::StandardButton>(
                buttonBox->standardButton(abstractButton));
        pushButton->setObjectName(standardButtonObjectName(standardButton));
        pushButton->setAutoDefault(false);
    }

    QMessageBox::StandardButton effectiveDefault = defaultButton;
    if (effectiveDefault == QMessageBox::NoButton
        || !m_buttons.testFlag(effectiveDefault)) {
        effectiveDefault = defaultButtonFor(m_buttons);
    }
    if (QPushButton *button = buttonBox->button(
            static_cast<QDialogButtonBox::StandardButton>(
                int(effectiveDefault)))) {
        button->setDefault(true);
        button->setFocus();
    }

    applyStyle(palette);
}

bool RibbonMessageDialog::eventFilter(QObject *object, QEvent *event)
{
    if (object != m_titleBar) {
        return QDialog::eventFilter(object, event);
    }

    switch (event->type()) {
    case QEvent::MouseButtonPress: {
        QMouseEvent *mouseEvent = static_cast<QMouseEvent *>(event);
        if (mouseEvent->button() == Qt::LeftButton) {
            m_dragging = true;
            m_dragOffset = mouseGlobalPosition(mouseEvent) - frameGeometry().topLeft();
            return true;
        }
        break;
    }
    case QEvent::MouseMove: {
        if (!m_dragging) {
            break;
        }
        QMouseEvent *mouseEvent = static_cast<QMouseEvent *>(event);
        move(mouseGlobalPosition(mouseEvent) - m_dragOffset);
        return true;
    }
    case QEvent::MouseButtonRelease:
        m_dragging = false;
        return true;
    default:
        break;
    }

    return QDialog::eventFilter(object, event);
}

void RibbonMessageDialog::reject()
{
    finish(escapeButtonFor(m_buttons));
}

void RibbonMessageDialog::applyStyle(const RibbonMessagePalette &palette)
{
    const QString styleSheet = QStringLiteral(
        "QWidget#lqRibbonMessageBoxCard {"
        "    background: %1;"
        "    border: 1px solid %2;"
        "    border-radius: %3px;"
        "}"
        "QWidget#lqRibbonMessageBoxTitleBar {"
        "    background: %4;"
        "    border-top-left-radius: %3px;"
        "    border-top-right-radius: %3px;"
        "}"
        "QLabel#lqRibbonMessageBoxTitle {"
        "    color: %5;"
        "    font-weight: 600;"
        "}"
        "QLabel#lqRibbonMessageBoxText {"
        "    color: %6;"
        "    font-size: 9pt;"
        "}"
        "QWidget#lqRibbonMessageBoxContent {"
        "    background: %7;"
        "}"
        "QWidget#lqRibbonMessageBoxButtonArea {"
        "    background: %7;"
        "    border-bottom-left-radius: %3px;"
        "    border-bottom-right-radius: %3px;"
        "}"
        "QDialogButtonBox#lqRibbonMessageBoxButtons QPushButton {"
        "    min-width: 84px;"
        "    min-height: 26px;"
        "    padding: 3px 16px;"
        "    border: 1px solid %2;"
        "    border-radius: 2px;"
        "    background: %1;"
        "    color: %6;"
        "}"
        "QDialogButtonBox#lqRibbonMessageBoxButtons QPushButton:hover {"
        "    background: %8;"
        "    border-color: %9;"
        "}"
        "QDialogButtonBox#lqRibbonMessageBoxButtons QPushButton:pressed {"
        "    background: %10;"
        "    border-color: %9;"
        "}"
        "QDialogButtonBox#lqRibbonMessageBoxButtons QPushButton:default {"
        "    border: 1px solid %9;"
        "}"
        "QToolButton#lqRibbonMessageBoxCloseButton {"
        "    border: 1px solid transparent;"
        "    border-radius: 2px;"
        "    background: transparent;"
        "    color: %5;"
        "    font-size: 14pt;"
        "}"
        "QToolButton#lqRibbonMessageBoxCloseButton:hover {"
        "    background: #c42b1c;"
        "    color: #ffffff;"
        "}"
        "QToolButton#lqRibbonMessageBoxCloseButton:pressed {"
        "    background: #8f1f15;"
        "    color: #ffffff;"
        "}")
        .arg(colorName(palette.surface),
             colorName(palette.border),
             QString::number(palette.radius),
             colorName(palette.captionBackground),
             colorName(palette.captionText),
             colorName(palette.text),
             colorName(palette.contentBackground),
             colorName(palette.hover),
             colorName(palette.accent),
             colorName(palette.pressed));

    setStyleSheet(styleSheet);
}

void RibbonMessageDialog::finish(QMessageBox::StandardButton button)
{
    done(static_cast<int>(button == QMessageBox::NoButton
                              ? defaultButtonFor(m_buttons)
                              : button));
}

} // namespace

namespace LqRibbon {

QMessageBox::StandardButton RibbonMessageBox::show(
    QWidget *parent,
    QMessageBox::Icon icon,
    const QString &title,
    const QString &text,
    QMessageBox::StandardButtons buttons,
    QMessageBox::StandardButton defaultButton)
{
    RibbonMessageDialog dialog(parent, icon, title, text, buttons, defaultButton);
    dialog.adjustSize();
    centerDialogOnParent(&dialog, parent);
    return static_cast<QMessageBox::StandardButton>(dialog.exec());
}

QMessageBox::StandardButton RibbonMessageBox::information(
    QWidget *parent,
    const QString &title,
    const QString &text,
    QMessageBox::StandardButtons buttons,
    QMessageBox::StandardButton defaultButton)
{
    return show(parent,
                QMessageBox::Information,
                title,
                text,
                buttons,
                defaultButton);
}

QMessageBox::StandardButton RibbonMessageBox::warning(
    QWidget *parent,
    const QString &title,
    const QString &text,
    QMessageBox::StandardButtons buttons,
    QMessageBox::StandardButton defaultButton)
{
    return show(parent, QMessageBox::Warning, title, text, buttons, defaultButton);
}

QMessageBox::StandardButton RibbonMessageBox::critical(
    QWidget *parent,
    const QString &title,
    const QString &text,
    QMessageBox::StandardButtons buttons,
    QMessageBox::StandardButton defaultButton)
{
    return show(parent, QMessageBox::Critical, title, text, buttons, defaultButton);
}

QMessageBox::StandardButton RibbonMessageBox::question(
    QWidget *parent,
    const QString &title,
    const QString &text,
    QMessageBox::StandardButtons buttons,
    QMessageBox::StandardButton defaultButton)
{
    return show(parent, QMessageBox::Question, title, text, buttons, defaultButton);
}

} // namespace LqRibbon
