QT += widgets

macx:equals(QMAKE_HOST.arch, arm64):!contains(QMAKE_APPLE_DEVICE_ARCHS, x86_64) {
    QMAKE_CXXFLAGS += -include arm_acle.h
}

INCLUDEPATH += \
    $$PWD/Code

HEADERS += \
    $$PWD/Code/LqRibbon.h \
    $$PWD/Code/LqRibbonControls.h \
    $$PWD/Code/LqRibbonExtras.h \
    $$PWD/Code/LqRibbonGallery.h \
    $$PWD/Code/LqRibbonMessageBox.h \
    $$PWD/Code/LqRibbonStatusBar.h \
    $$PWD/Code/DemoRibbonWindow.h

SOURCES += \
    $$PWD/Code/LqRibbon.cpp \
    $$PWD/Code/LqRibbonControls.cpp \
    $$PWD/Code/LqRibbonExtras.cpp \
    $$PWD/Code/LqRibbonGallery.cpp \
    $$PWD/Code/LqRibbonMessageBox.cpp \
    $$PWD/Code/LqRibbonStatusBar.cpp \
    $$PWD/Code/DemoRibbonWindow.cpp
