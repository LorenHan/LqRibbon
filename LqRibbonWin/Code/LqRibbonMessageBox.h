#ifndef LQRIBBONMESSAGEBOX_H
#define LQRIBBONMESSAGEBOX_H

#include <QMessageBox>
#include <QString>

QT_BEGIN_NAMESPACE
class QWidget;
QT_END_NAMESPACE

namespace LqRibbon {

///
/// \brief The RibbonMessageBox class shows modal messages using Ribbon styling.
///
/// The helper mirrors the common QMessageBox static entry points while drawing
/// a Ribbon-themed frame, caption, icon, and command row.
///
class RibbonMessageBox
{
public:
    static QMessageBox::StandardButton show(
        QWidget *parent,
        QMessageBox::Icon icon,
        const QString &title,
        const QString &text,
        QMessageBox::StandardButtons buttons = QMessageBox::Ok,
        QMessageBox::StandardButton defaultButton = QMessageBox::NoButton);

    static QMessageBox::StandardButton information(
        QWidget *parent,
        const QString &title,
        const QString &text,
        QMessageBox::StandardButtons buttons = QMessageBox::Ok,
        QMessageBox::StandardButton defaultButton = QMessageBox::NoButton);

    static QMessageBox::StandardButton warning(
        QWidget *parent,
        const QString &title,
        const QString &text,
        QMessageBox::StandardButtons buttons = QMessageBox::Ok,
        QMessageBox::StandardButton defaultButton = QMessageBox::NoButton);

    static QMessageBox::StandardButton critical(
        QWidget *parent,
        const QString &title,
        const QString &text,
        QMessageBox::StandardButtons buttons = QMessageBox::Ok,
        QMessageBox::StandardButton defaultButton = QMessageBox::NoButton);

    static QMessageBox::StandardButton question(
        QWidget *parent,
        const QString &title,
        const QString &text,
        QMessageBox::StandardButtons buttons = QMessageBox::StandardButtons(
            QMessageBox::Yes | QMessageBox::No),
        QMessageBox::StandardButton defaultButton = QMessageBox::NoButton);

private:
    RibbonMessageBox() = delete;
};

} // namespace LqRibbon

#endif // LQRIBBONMESSAGEBOX_H
