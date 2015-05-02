isEmpty(psycle_core_included) {
	psycle_core_included = 1
	verbose: message("psycle-core included")

	include(libxml++.pri)
	include(zlib.pri)
	include($$TOP_SRC_DIR/universalis/qmake/universalis.pri)
	include($$TOP_SRC_DIR/psycle-audiodrivers/qmake/psycle-audiodrivers.pri)

	PSYCLE_CORE_DIR = $$TOP_SRC_DIR/psycle-core
	PSYCLE_CORE_BUILD_DIR = $$PSYCLE_CORE_DIR/++build

	INCLUDEPATH *= $$PSYCLE_CORE_DIR/src
	DEPENDPATH  *= $$PSYCLE_CORE_DIR/src

	!contains(TARGET, psycle-core) {
		CONFIG *= link_prl
		LIBPATH *= $$PSYCLE_CORE_BUILD_DIR
		LIBS *= $$linkLibs(psycle-core)
		PRE_TARGETDEPS += $$PSYCLE_CORE_BUILD_DIR
	}
}
