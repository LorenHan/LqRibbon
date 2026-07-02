QT += widgets

CONFIG += c++17
TEMPLATE = app
TARGET = LqRibbonExample

include(../LqRibbon.pri)

SOURCES += \
    main.cpp \
    mainwindow.cpp

HEADERS += \
    mainwindow.h

RESOURCES += \
    resources.qrc
