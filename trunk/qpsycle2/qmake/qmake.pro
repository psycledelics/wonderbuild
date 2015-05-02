TARGET = qpsycle2
TEMPLATE = app # This project builds an executable program.

greaterThan(QT_MAJOR_VERSION, 4): QT += widgets

# include the base stuff shared amongst all qmake projects.
include(../../build-systems/qmake/common.pri)

QMAKE_CXXFLAGS *= -std=c++11

# this include defines a dependency on the qt-xml lib.
include($$COMMON_DIR/qt-xml.pri)

# this include defines a dependency on the jdkmidi lib.
#include($$COMMON_DIR/jdkmidi.pri) no need for this now

# this include defines a dependency on the psycle-core lib.
include($$TOP_SRC_DIR/psycle-core/qmake/psycle-core.pri)

QPSYCLE2_DIR = $$TOP_SRC_DIR/qpsycle2

BUILD_DIR = $$QPSYCLE2_DIR/++build
OBJECTS_DIR = $$BUILD_DIR/objects # Where the .o files go.
MOC_DIR = $$BUILD_DIR/moc # Where intermediate moc files go.
RCC_DIR = $$BUILD_DIR/rcc # Where intermediate resource files go.
UI_DIR = $$BUILD_DIR/uic # Where compiled uic files go.
DESTDIR = $$BUILD_DIR # Where the final executable goes.

local_includepath = \
        $$QPSYCLE2_DIR/src \
        $$QPSYCLE2_DIR/src/MachineView \
        $$QPSYCLE2_DIR/src/menus \
        $$QPSYCLE2_DIR/src/PatternView \

DEPENDPATH  += $$local_includepath
INCLUDEPATH += $$local_includepath

#CONFIG *= precompile_header
#PRECOMPILED_HEADER = $$QPSYCLE_DIR/src/qpsyclePch.hpp


SOURCES +=  $$QPSYCLE2_DIR/src/main.cpp \
            $$QPSYCLE2_DIR/src/qpsycle2.cpp \
            $$QPSYCLE2_DIR/src/statics.cpp \
            $$findFiles($$QPSYCLE2_DIR/src/MachineView, *.cpp) \
            $$findFiles($$QPSYCLE2_DIR/src/menus, *.cpp) \
            $$findFiles($$QPSYCLE2_DIR/src/PatternView, *.cpp) \




HEADERS +=  $$QPSYCLE2_DIR/src/qpsycle2.h\
            $$QPSYCLE2_DIR/src/statics.h\
            $$findFiles($$QPSYCLE2_DIR/src/MachineView, *.hpp) \
            $$findFiles($$QPSYCLE2_DIR/src/MachineView, *.h)\
            $$findFiles($$QPSYCLE2_DIR/src/menus, *.hpp) \
            $$findFiles($$QPSYCLE2_DIR/src/menus, *.h)\
            $$findFiles($$QPSYCLE2_DIR/src/PatternView, *.hpp) \
            $$findFiles($$QPSYCLE2_DIR/src/PatternView, *.h)\




 LIBS *= -lz -ldl -lrt -lboost_filesystem -lboost_system -lboost_signals -lboost_thread -lgomp


include($$COMMON_DIR/display-vars.pri)
