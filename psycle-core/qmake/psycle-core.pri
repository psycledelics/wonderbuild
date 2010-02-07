isEmpty(psycle_core_included) {
	psycle_core_included = 1
	verbose: message("psycle-core included")

	include($$COMMON_DIR/libxml++.pri)
	include($$COMMON_DIR/zlib.pri)
	include($$TOP_SRC_DIR/psycle-audiodrivers/qmake/psycle-audiodrivers.pri)

	PSYCLE_CORE_DIR = $$TOP_SRC_DIR/psycle-core
	PSYCLE_CORE_BUILD_DIR = $$PSYCLE_CORE_DIR/++qmake-build

	INCLUDEPATH *= $$PSYCLE_CORE_DIR/src $$TOP_SRC_DIR/psycle-plugins/src
	DEPENDPATH  *= $$PSYCLE_CORE_DIR/src $$TOP_SRC_DIR/psycle-plugins/src

	!contains(TARGET, psycle-core) {
		CONFIG *= link_prl
		LIBPATH *= $$PSYCLE_CORE_BUILD_DIR
		LIBS *= $$linkLibs(psycle-core)
		PRE_TARGETDEPS += $$PSYCLE_CORE_BUILD_DIR
	}
}
