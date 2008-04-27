isEmpty(zlib_included) {
	zlib_included = 1
	verbose: message("zlib included")

	unix | win32-g++: LIBS *= $$linkLibs(z)
	else: win32-msvc*: LIBS *= LIBS *= $$linkLibs(zlib)

	win32 {
		exists($(ZLIB_DIR)) {
			message("Existing ZLIB_DIR is $(ZLIB_DIR)")
			ZLIB_DIR = $(ZLIB_DIR)
			INCLUDEPATH *= $$ZLIB_DIR
			LIBPATH *= $$ZLIB_DIR/lib
		} else {
			ZLIB_DIR = $$EXTERNAL_PKG_DIR/zlib-1.2.3
			!exists($$ZLIB_DIR) {
				warning("The local zlib dir does not exist: $${ZLIB_DIR}. Make sure you have zlib installed.")
			} else {
				INCLUDEPATH *= $$ZLIB_DIR/include
				LIBPATH *= $$ZLIB_DIR/lib-mswindows-cabi
			}
		}
	}
}
