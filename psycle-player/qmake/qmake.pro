TARGET = psycle-player

include(../../psycle-core/qmake/common.pri)

TEMPLATE = app # This project builds an executable program.

include($$TOP_SRC_DIR/psycle-core/qmake/psycle-core.pri)

PSYCLE_PLAYER_DIR = $$TOP_SRC_DIR/psycle-player

BUILD_DIR = $$PSYCLE_PLAYER_DIR/++build
OBJECTS_DIR = $$BUILD_DIR # Where the .o files go.
MOC_DIR = $$BUILD_DIR # Where intermediate moc files go.
RCC_DIR = $$BUILD_DIR # Where intermediate resource files go.
DESTDIR = $$BUILD_DIR # Where the final executable goes.

INCLUDEPATH *= $$PSYCLE_PLAYER_DIR/src
DEPENDPATH  *= $$PSYCLE_PLAYER_DIR/src

#CONFIG *= precompile_header
#PRECOMPILED_HEADER = $$QPSYCLE_DIR/src/psycle/player/psyclePlayerPch.hpp

sources_or_headers = \
	$$PSYCLE_PLAYER_DIR/src/psycle/player/configuration \
	$$PSYCLE_PLAYER_DIR/src/psycle/player/main
	
SOURCES += $$sources(sources_or_headers)
HEADERS += $$headers(sources_or_headers)

false: win32 {
	RC_FILE = $$QPSYCLE_DIR/src/psycle-player.rc 
	message("Adding $$RC_FILE for executable icon")
}

include($$COMMON_DIR/display-vars.pri)
