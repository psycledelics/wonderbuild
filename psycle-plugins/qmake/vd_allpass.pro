QT       -= core gui

TARGET = vd_allpass
TEMPLATE = lib

DEFINES += vd_allpass_built

SOURCES += ../src/psycle/plugins/vincenzo_demasi/vdAllPass/vdAllPass.cpp\

HEADERS += ../src/psycle/plugins/vincenzo_demasi/vdAllPass/vdAllPass.hpp\
 ../src/psycle/plugins/vincenzo_demasi/vdAllPass/allpassfilter.hpp\

include (common.pri)