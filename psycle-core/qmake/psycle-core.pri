isEmpty(psycle_core_included) {
	psycle_core_included = 1
	verbose: message("psycle-core included")

	include($$COMMON_DIR/boost.pri)
	include($$COMMON_DIR/libxml++.pri)
	include($$COMMON_DIR/zlib.pri)
	
	include($$TOP_SRC_DIR/psycle-audiodrivers/qmake/psycle-audiodrivers.pri)
	CONFIG *= link_prl
	unix | win32-g++:  LIBS *= -lpsycle-audiodrivers
	else: win32-msvc*: LIBS *=   psycle-audiodrivers.lib

	INCLUDEPATH *= $$TOP_SRC_DIR/diversalis/src
	DEPENDPATH  *= $$TOP_SRC_DIR/diversalis/src
	INCLUDEPATH *= $$TOP_SRC_DIR/universalis/src
	DEPENDPATH  *= $$TOP_SRC_DIR/universalis/src

	PSYCLE_CORE_DIR = $$TOP_SRC_DIR/psycle-core

	LIBPATH     *= $$PSYCLE_CORE_DIR/++build
	INCLUDEPATH *= $$PSYCLE_CORE_DIR/src
	DEPENDPATH  *= $$PSYCLE_CORE_DIR/src

}
