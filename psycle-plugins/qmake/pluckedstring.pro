QT       -= core gui

TARGET = PluckedString
TEMPLATE = lib

DEFINES += PluckedString_built

SOURCES += ../src/psycle/plugins/druttis/PluckedString/PluckedString.cpp\
../src/psycle/plugins/druttis/PluckedString/CVoice.cpp\
../src/psycle/plugins/druttis/PluckedString/BiQuad.cpp\

HEADERS += ../src/psycle/plugins/druttis/PluckedString/CVoice.h\
../src/psycle/plugins/druttis/PluckedString/BiQuad.h\

include (common.pri)

