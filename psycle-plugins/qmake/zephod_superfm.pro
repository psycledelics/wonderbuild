QT       -= core gui

TARGET = zephod_super_fm
TEMPLATE = lib

DEFINES += zephod_super_fm_built

SOURCES += ../src/psycle/plugins/zephod_super_fm/zephod_superfm.cpp\
../src/psycle/plugins/zephod_super_fm/envelope.cpp\

HEADERS += ../src/psycle/plugins/zephod_super_fm/envelope.hpp\

include (common.pri)
