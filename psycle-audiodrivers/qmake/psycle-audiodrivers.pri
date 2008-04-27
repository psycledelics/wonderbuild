isEmpty(psycle_audiodrivers_included) {
	psycle_audiodrivers_included = 1
	verbose: message("psycle-audiodrivers included")
	
	INCLUDEPATH *= $$TOP_SRC_DIR/diversalis/src
	DEPENDPATH  *= $$TOP_SRC_DIR/diversalis/src
	INCLUDEPATH *= $$TOP_SRC_DIR/universalis/src
	DEPENDPATH  *= $$TOP_SRC_DIR/universalis/src

	PSYCLE_AUDIODRIVERS_DIR = $$TOP_SRC_DIR/psycle-audiodrivers
	PSYCLE_AUDIODRIVERS_BUILD_DIR = $$PSYCLE_AUDIODRIVERS_DIR/++build
	
	INCLUDEPATH *= $$PSYCLE_AUDIODRIVERS_DIR/src
	DEPENDPATH  *= $$PSYCLE_AUDIODRIVERS_DIR/src

	!contains(TARGET, psycle-audiodrivers) {
		CONFIG *= link_prl
		LIBPATH *= $$PSYCLE_AUDIODRIVERS_BUILD_DIR
		LIBS *= $$linkLibs(psycle-audiodrivers)
	}
}
