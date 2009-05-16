isEmpty(universalis_included) {
	universalis_included = 1
	verbose: message("universalis included")
	
	include($$COMMON_DIR/boost.pri)
	INCLUDEPATH *= $$TOP_SRC_DIR/diversalis/src
	DEPENDPATH  *= $$TOP_SRC_DIR/diversalis/src

	UNIVERSALIS_DIR = $$TOP_SRC_DIR/universalis
	UNIVERSALIS_BUILD_DIR = $$UNIVERSALIS_DIR/++build
	
	INCLUDEPATH *= $$UNIVERSALIS_DIR/src $$UNIVERSALIS_DIR/src/universalis/standard_library/future_std_include
	DEPENDPATH  *= $$UNIVERSALIS_DIR/src $$UNIVERSALIS_DIR/src/universalis/standard_library/future_std_include

	INCLUDEPATH *= $$UNIVERSALIS_DIR/qmake/src
	DEPENDPATH  *= $$UNIVERSALIS_DIR/qmake/src

	!contains(TARGET, universalis) {
		CONFIG *= link_prl
		LIBPATH *= $$UNIVERSALIS_BUILD_DIR
		LIBS *= $$linkLibs(universalis)
		PRE_TARGETDEPS *= $$UNIVERSALIS_BUILD_DIR
	}
}
