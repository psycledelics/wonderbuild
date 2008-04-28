isEmpty(jdkmidi_included) {
	jdkmidi_included = 1
	verbose: message("jdkmidi included")
	
	LIBS *= $$linkLibs(jdkmidi)
	
	win32 {
		INCLUDEPATH *= $$EXTERNAL_PKG_DIR/libjdkmidi/include
		win32-g++{
			LIBPATH     *= $$EXTERNAL_PKG_DIR/libjdkmidi/lib
			}
		win32-msvc*{
			LIBPATH     *= $$EXTERNAL_PKG_DIR/libjdkmidi/lib-msvc
			}
	}
}
