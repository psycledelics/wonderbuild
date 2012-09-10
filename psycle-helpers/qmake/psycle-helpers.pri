isEmpty(psycle_helpers_included) {
	psycle_helpers_included = 1
	verbose: message("psycle-helpers included")
	
	include($$TOP_SRC_DIR/universalis/qmake/universalis.pri)

	PSYCLE_HELPERS_DIR = $$TOP_SRC_DIR/psycle-helpers
	PSYCLE_HELPERS_BUILD_DIR = $$PSYCLE_HELPERS_DIR/++qmake
	
	INCLUDEPATH += $$PSYCLE_HELPERS_DIR/src
	DEPENDPATH  += $$PSYCLE_HELPERS_DIR/src

	!contains(TARGET, psycle-helpers) {
		CONFIG *= link_prl
		QMAKE_LIBDIR *= $$PSYCLE_HELPERS_BUILD_DIR
		LIBS *= $$linkLibs(psycle-helpers)
		PRE_TARGETDEPS *= $$PSYCLE_HELPERS_BUILD_DIR
	}
}
