#include <QApplication>
#include <QFont>
#include <QFontDatabase>
#include <QStringList>

#include "mainwindow.h"

int main(int argc, char *argv[])
{
    QStringList rawArgumentList;
    rawArgumentList.reserve(argc);
    for (int index = 0; index < argc; ++index) {
        rawArgumentList.append(QString::fromLocal8Bit(argv[index]));
    }

    QApplication application(argc, argv);
    application.setApplicationName(QStringLiteral("LqRibbon Example"));
    application.setOrganizationName(QStringLiteral("LqRibbon"));
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

    return runLqRibbonExampleMainWindow(application, rawArgumentList);
}