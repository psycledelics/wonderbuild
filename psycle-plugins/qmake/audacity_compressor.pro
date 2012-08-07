QT       -= core gui

TARGET = audacity_compressor
TEMPLATE = lib

DEFINES += audacity_compressor_built

SOURCES += ../src/psycle/plugins/audacity/compressor/plugin.cpp\
        ../src/psycle/plugins/audacity/compressor/Compressor.cpp\

HEADERS += ../src/psycle/plugins/audacity/compressor/Compressor.h\

include (common.pri)