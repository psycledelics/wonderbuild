unix | win32-g++: LIBS *= -lz
else:win32-msvc*: LIBS *= zlib.lib
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
