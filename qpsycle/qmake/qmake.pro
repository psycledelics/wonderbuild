include(../../psycle-core/qmake/common.pri)

TEMPLATE = app # This project builds an executable program.
TARGET = qpsycle

CONFIG *= link_prl
include($$TOP_SRC_DIR/psycle-core/qmake/psycle-core.pri)
unix | win32-g++:  LIBS *= -lpsycle-core
else: win32-msvc*: LIBS *=   psycle-core.lib

include(qt-xml.pri)
#include(jdkmidi.pri) no need for this now

QPSYCLE_DIR = $$TOP_SRC_DIR/qpsycle

BUILD_DIR = $$QPSYCLE_DIR/++build
OBJECTS_DIR = $$BUILD_DIR # Where the .o files go.
MOC_DIR = $$BUILD_DIR # Where intermediate moc files go.
RCC_DIR = $$BUILD_DIR # Where intermediate resource files go.
DESTDIR = $$BUILD_DIR # Where the final executable goes.

CONFIG *= precompiled_header
PRECOMPILED_HEADER = $$QPSYCLE_DIR/src/qpsyclePch.hpp

local_includepath = \
	$$QPSYCLE_DIR/src \
	$$QPSYCLE_DIR/src/mididrivers \
	$$QPSYCLE_DIR/src/model \
	$$QPSYCLE_DIR/src/gui \
	$$QPSYCLE_DIR/src/gui/machineview \
	$$QPSYCLE_DIR/src/gui/patternview \
	$$QPSYCLE_DIR/src/gui/waveview \
	$$QPSYCLE_DIR/src/gui/sequencer \
	$$QPSYCLE_DIR/src/gui/configdlg

DEPENDPATH += $$local_includepath
INCLUDEPATH += $$local_includepath

HEADERS += \
	$$QPSYCLE_DIR/src/gui/mainwindow.hpp \
	$$QPSYCLE_DIR/src/gui/global.hpp \
	$$QPSYCLE_DIR/src/gui/configuration.hpp \
	$$QPSYCLE_DIR/src/gui/inputhandler.hpp \
	$$QPSYCLE_DIR/src/gui/patternbox.hpp \
	$$QPSYCLE_DIR/src/gui/configdlg/audiopage.hpp \
	$$QPSYCLE_DIR/src/gui/configdlg/behaviourpage.hpp \
	$$QPSYCLE_DIR/src/gui/configdlg/configdlg.hpp \
	$$QPSYCLE_DIR/src/gui/configdlg/lookspage.hpp \
	$$QPSYCLE_DIR/src/gui/configdlg/dirspage.hpp \
	$$QPSYCLE_DIR/src/gui/samplebrowser.hpp \
	$$QPSYCLE_DIR/src/gui/logconsole.hpp \
	$$QPSYCLE_DIR/src/gui/machineview/machinegui.hpp \
	$$QPSYCLE_DIR/src/gui/machineview/machinetweakdlg.hpp \
	$$QPSYCLE_DIR/src/gui/machineview/machineview.hpp \
	$$QPSYCLE_DIR/src/gui/machineview/mixertweakdlg.hpp \
	$$QPSYCLE_DIR/src/gui/machineview/newmachinedlg.hpp \
	$$QPSYCLE_DIR/src/gui/machineview/wiregui.hpp \
	$$QPSYCLE_DIR/src/gui/machineview/wiredlg.hpp \
	$$QPSYCLE_DIR/src/gui/machineview/generatorgui.hpp \
	$$QPSYCLE_DIR/src/gui/machineview/mastergui.hpp \
	$$QPSYCLE_DIR/src/gui/machineview/effectgui.hpp \
	$$QPSYCLE_DIR/src/gui/patternview/patternview.hpp \
	$$QPSYCLE_DIR/src/gui/patternview/linenumbercolumn.hpp \
	$$QPSYCLE_DIR/src/gui/patternview/trackheader.hpp \
	$$QPSYCLE_DIR/src/gui/patternview/patterngrid.hpp \
	$$QPSYCLE_DIR/src/gui/patternview/patterndraw.hpp \
	$$QPSYCLE_DIR/src/gui/sequencer/sequencerarea.hpp \
	$$QPSYCLE_DIR/src/gui/sequencer/sequencerdraw.hpp \
	$$QPSYCLE_DIR/src/gui/sequencer/sequenceritem.hpp \
	$$QPSYCLE_DIR/src/gui/sequencer/sequencerline.hpp \
	$$QPSYCLE_DIR/src/gui/sequencer/sequencerview.hpp \
	$$QPSYCLE_DIR/src/gui/sequencer/beatruler.hpp \
	$$QPSYCLE_DIR/src/gui/waveview/waveview.hpp \
	$$QPSYCLE_DIR/src/gui/waveview/wavedisplay.hpp \
	$$QPSYCLE_DIR/src/gui/waveview/waveamp.hpp \
	$$QPSYCLE_DIR/src/model/instrumentsmodel.hpp

SOURCES += \
	$$QPSYCLE_DIR/src/qpsycle.cpp \
	$$QPSYCLE_DIR/src/gui/mainwindow.cpp \
	$$QPSYCLE_DIR/src/gui/global.cpp \
	$$QPSYCLE_DIR/src/gui/configuration.cpp \
	$$QPSYCLE_DIR/src/gui/inputhandler.cpp \
	$$QPSYCLE_DIR/src/gui/patternbox.cpp \
	$$QPSYCLE_DIR/src/gui/configdlg/audiopage.cpp \
	$$QPSYCLE_DIR/src/gui/configdlg/behaviourpage.cpp \
	$$QPSYCLE_DIR/src/gui/configdlg/configdlg.cpp \
	$$QPSYCLE_DIR/src/gui/configdlg/lookspage.cpp \
	$$QPSYCLE_DIR/src/gui/configdlg/dirspage.cpp \
	$$QPSYCLE_DIR/src/gui/samplebrowser.cpp \
	$$QPSYCLE_DIR/src/gui/logconsole.cpp \
	$$QPSYCLE_DIR/src/gui/machineview/machinegui.cpp \
	$$QPSYCLE_DIR/src/gui/machineview/machinetweakdlg.cpp \
	$$QPSYCLE_DIR/src/gui/machineview/machineview.cpp \
	$$QPSYCLE_DIR/src/gui/machineview/mixertweakdlg.cpp \ 
	$$QPSYCLE_DIR/src/gui/machineview/newmachinedlg.cpp \
	$$QPSYCLE_DIR/src/gui/machineview/wiregui.cpp \
	$$QPSYCLE_DIR/src/gui/machineview/wiredlg.cpp \
	$$QPSYCLE_DIR/src/gui/machineview/generatorgui.cpp \
	$$QPSYCLE_DIR/src/gui/machineview/mastergui.cpp \
	$$QPSYCLE_DIR/src/gui/machineview/effectgui.cpp \
	$$QPSYCLE_DIR/src/gui/patternview/patternview.cpp \
	$$QPSYCLE_DIR/src/gui/patternview/linenumbercolumn.cpp \
	$$QPSYCLE_DIR/src/gui/patternview/trackheader.cpp \
	$$QPSYCLE_DIR/src/gui/patternview/patterngrid.cpp \
	$$QPSYCLE_DIR/src/gui/patternview/patterndraw.cpp \
	$$QPSYCLE_DIR/src/gui/sequencer/sequencerarea.cpp \
	$$QPSYCLE_DIR/src/gui/sequencer/sequencerdraw.cpp \
	$$QPSYCLE_DIR/src/gui/sequencer/sequenceritem.cpp \
	$$QPSYCLE_DIR/src/gui/sequencer/sequencerline.cpp \
	$$QPSYCLE_DIR/src/gui/sequencer/sequencerview.cpp \
	$$QPSYCLE_DIR/src/gui/sequencer/beatruler.cpp \
	$$QPSYCLE_DIR/src/gui/waveview/waveview.cpp \
	$$QPSYCLE_DIR/src/gui/waveview/wavedisplay.cpp \
	$$QPSYCLE_DIR/src/gui/waveview/waveamp.cpp \
	$$QPSYCLE_DIR/src/model/instrumentsmodel.cpp

RESOURCES += $$QPSYCLE_DIR/src/qpsycle.qrc

win32 {
	RC_FILE = $$QPSYCLE_DIR/src/qpsycle.rc 
	message("Adding $$RC_FILE for executable icon")
}

include($$COMMON_DIR/display-vars.pri)
