QT       -= core gui

TARGET = gverb
TEMPLATE = lib

DEFINES += gverb_built

SOURCES += ../src/psycle/plugins/gverb/gverb.cpp\
../src/psycle/plugins/gverb/gverbdsp.cpp\
../src/psycle/plugins/gverb/ladspa_gverb.cpp\

HEADERS += ../src/psycle/plugins/gverb/gverb.h\
../src/psycle/plugins/gverb/gverbdsp.h\

include (common.pri)

