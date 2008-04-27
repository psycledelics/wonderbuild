isEmpty(jdkmidi_included) {
	jdkmidi_included = 1
	verbose: message("jdkmidi included")
	
	LIBS *= $$linkLibs(jdkmidi)
	
	win32 {
		INCLUDEPATH *= $$EXTERNAL_PKG_DIR/libjdkmidi/include
		LIBPATH     *= $$EXTERNAL_PKG_DIR/libjdkmidi/lib
	}
}
