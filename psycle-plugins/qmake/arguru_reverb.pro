 
QT       -= core gui

TARGET = arguru_reverb
TEMPLATE = lib

DEFINES += arguru_reverb_built

SOURCES += ../src/psycle/plugins/arguru_reverb/arguru_reverb.cpp\
    ../src/psycle/plugins/arguru_reverb/AllPass.cpp\
    ../src/psycle/plugins/arguru_reverb/CombFilter.cpp\
    ../src/psycle/plugins/arguru_reverb/LowPass.cpp\

HEADERS += ../src/psycle/plugins/arguru_reverb/AllPass.hpp\
        ../src/psycle/plugins/arguru_reverb/CombFilter.hpp\
        ../src/psycle/plugins/arguru_reverb/LowPass.hpp\
   

include (common.pri)