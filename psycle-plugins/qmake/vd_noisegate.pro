QT       -= core gui

TARGET = vd_noisegate
TEMPLATE = lib

DEFINES += vd_noisegate_built

SOURCES += ../src/psycle/plugins/vincenzo_demasi/vdNoiseGate/vdNoiseGate.cpp\

HEADERS += ../src/psycle/plugins/vincenzo_demasi/vdNoiseGate/vdNoiseGate.hpp\
 ../src/psycle/plugins/vincenzo_demasi/vdNoiseGate/lowpassfilter.hpp\

include (common.pri)
