QT       -= core gui

TARGET = gamefx
TEMPLATE = lib

DEFINES += gamefx_built

SOURCES += ../src/psycle/plugins/jme/gamefxn/aaf.cpp\
../src/psycle/plugins/jme/gamefxn/atlantisfilter.cpp\
../src/psycle/plugins/jme/gamefxn/gamefx.cpp\
../src/psycle/plugins/jme/gamefxn/voice.cpp\

HEADERS += ../src/psycle/plugins/jme/gamefxn/aaf.h\
../src/psycle/plugins/jme/gamefxn/atlantisfilter.h\
../src/psycle/plugins/jme/gamefxn/voice.h\

include (common.pri)
