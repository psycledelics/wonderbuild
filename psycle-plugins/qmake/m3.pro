QT       -= core gui

TARGET = m3
TEMPLATE = lib

DEFINES += m3_built

SOURCES += ../src/psycle/plugins/m3/m3.cpp\
../src/psycle/plugins/m3/track.cpp\

HEADERS += ../src/psycle/plugins/m3/track.hpp\

include (common.pri)

