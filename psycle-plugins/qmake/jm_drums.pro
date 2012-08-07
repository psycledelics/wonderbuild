QT       -= core gui

TARGET = jm_drums
TEMPLATE = lib

DEFINES += jm_drums_built

SOURCES += ../src/psycle/plugins/jm_drums/jm_drums.cpp\
../src/psycle/plugins/jm_drums/drum.cpp\
../src/psycle/plugins/jm_drums/oscillator.cpp\

HEADERS += ../src/psycle/plugins/jm_drums/drum.hpp\
../src/psycle/plugins/jm_drums/oscillator.hpp\

include (common.pri)

