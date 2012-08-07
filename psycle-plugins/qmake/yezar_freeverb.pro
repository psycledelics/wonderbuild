QT       -= core gui

TARGET = yezar_freeverb
TEMPLATE = lib

DEFINES += yezar_freeberb_built

SOURCES += ../src/psycle/plugins/yezar_freeverb/yezar_freeverb.cpp\
../src/psycle/plugins/yezar_freeverb/AllPass.cpp\
../src/psycle/plugins/yezar_freeverb/comb.cpp\
../src/psycle/plugins/yezar_freeverb/RevModel.cpp\

HEADERS += ../src/psycle/plugins/yezar_freeverb/AllPass.hpp\
../src/psycle/plugins/yezar_freeverb/comb.hpp\
../src/psycle/plugins/yezar_freeverb/RevModel.hpp\
../src/psycle/plugins/yezar_freeverb/tuning.hpp\

include (common.pri)
