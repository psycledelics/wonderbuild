QT       -= core gui

TARGET = FeedMe
TEMPLATE = lib

DEFINES += FeedMe_built

SOURCES += ../src/psycle/plugins/druttis/FeedMe/FeedMe.cpp\
../src/psycle/plugins/druttis/FeedMe/CTrack.cpp

HEADERS += ../src/psycle/plugins/druttis/FeedMe/CTrack.h\

include (common.pri)
