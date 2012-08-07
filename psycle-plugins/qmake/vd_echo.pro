QT       -= core gui

TARGET = vd_echo
TEMPLATE = lib

DEFINES += vd_echo_built

SOURCES += ../src/psycle/plugins/vincenzo_demasi/vdEcho/vdEcho.cpp\

HEADERS += ../src/psycle/plugins/vincenzo_demasi/vdEcho/vdEcho.hpp\
 ../src/psycle/plugins/vincenzo_demasi/vdEcho/combfilter.hpp\

include (common.pri)