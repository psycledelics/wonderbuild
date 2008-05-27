TARGET = qpsycle

include(../../psycle-core/qmake/common.pri)

TEMPLATE = app # This project builds an executable program.

include(qt-xml.pri)
#include(jdkmidi.pri) no need for this now
include($$TOP_SRC_DIR/psycle-core/qmake/psycle-core.pri)

QPSYCLE_DIR = $$TOP_SRC_DIR/qpsycle

BUILD_DIR = $$QPSYCLE_DIR/++build
OBJECTS_DIR = $$BUILD_DIR/objects # Where the .o files go.
MOC_DIR = $$BUILD_DIR/moc # Where intermediate moc files go.
RCC_DIR = $$BUILD_DIR/rcc # Where intermediate resource files go.
UI_DIR = $$BUILD_DIR/uic # Where compiled uic files go.
DESTDIR = $$BUILD_DIR # Where the final executable goes.

FORMS = $$QPSYCLE_DIR/src/gui/configdlg/behaviourpage.ui \
	$$QPSYCLE_DIR/src/gui/configdlg/dirspage.ui

CONFIG *= precompile_header
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

DEPENDPATH  += $$local_includepath
INCLUDEPATH += $$local_includepath

sources_or_headers = \
	$$QPSYCLE_DIR/src/gui/configdlg/audiopage \
	$$QPSYCLE_DIR/src/gui/configdlg/behaviourpage \
	$$QPSYCLE_DIR/src/gui/configdlg/configdlg \
	$$QPSYCLE_DIR/src/gui/configdlg/dirspage \
	$$QPSYCLE_DIR/src/gui/configdlg/lookspage \
	$$QPSYCLE_DIR/src/gui/configuration \
	$$QPSYCLE_DIR/src/gui/global \
	$$QPSYCLE_DIR/src/gui/inputhandler \
	$$QPSYCLE_DIR/src/gui/logconsole \
	$$QPSYCLE_DIR/src/gui/machineview/effectgui \
	$$QPSYCLE_DIR/src/gui/machineview/generatorgui \
	$$QPSYCLE_DIR/src/gui/machineview/machinegui \
	$$QPSYCLE_DIR/src/gui/machineview/machinetweakdlg \
	$$QPSYCLE_DIR/src/gui/machineview/machineview \
	$$QPSYCLE_DIR/src/gui/machineview/mastergui \
	$$QPSYCLE_DIR/src/gui/machineview/mixertweakdlg \
	$$QPSYCLE_DIR/src/gui/machineview/newmachinedlg \
	$$QPSYCLE_DIR/src/gui/machineview/wiredlg \
	$$QPSYCLE_DIR/src/gui/machineview/wiregui \
	$$QPSYCLE_DIR/src/gui/mainwindow \
	$$QPSYCLE_DIR/src/gui/patternbox \
	$$QPSYCLE_DIR/src/gui/patternview/linenumbercolumn \
	$$QPSYCLE_DIR/src/gui/patternview/patterndraw \
	$$QPSYCLE_DIR/src/gui/patternview/patterngrid \
	$$QPSYCLE_DIR/src/gui/patternview/patternview \
	$$QPSYCLE_DIR/src/gui/patternview/trackheader \
	$$QPSYCLE_DIR/src/gui/samplebrowser \
	$$QPSYCLE_DIR/src/gui/sequencer/beatruler \
	$$QPSYCLE_DIR/src/gui/sequencer/sequencerarea \
	$$QPSYCLE_DIR/src/gui/sequencer/sequencerdraw \
	$$QPSYCLE_DIR/src/gui/sequencer/sequenceritem \
	$$QPSYCLE_DIR/src/gui/sequencer/sequencerline \
	$$QPSYCLE_DIR/src/gui/sequencer/sequencerview \
	$$QPSYCLE_DIR/src/gui/waveview/waveamp \
	$$QPSYCLE_DIR/src/gui/waveview/wavedisplay \
	$$QPSYCLE_DIR/src/gui/waveview/waveview \
	$$QPSYCLE_DIR/src/model/instrumentsmodel \
	$$QPSYCLE_DIR/src/qpsycle

SOURCES += $$sources(sources_or_headers)
HEADERS += $$headers(sources_or_headers)

RESOURCES += $$QPSYCLE_DIR/src/qpsycle.qrc

win32 {
	RC_FILE = $$QPSYCLE_DIR/src/qpsycle.rc 
	message("Adding $$RC_FILE for executable icon")
}

include($$COMMON_DIR/display-vars.pri)
