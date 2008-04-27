isEmpty(jdkmidi_included) {
	jdkmidi_included = 1
	verbose: message("jdkmidi included")
	
	unix | win32-g++: LIBS *= -ljdkmidi
	else:win32-msvc*: LIBS *=   jdkmidi.lib
	
	win32 {
		INCLUDEPATH *= $$EXTERNAL_PKG_DIR/libjdkmidi/include
		LIBPATH     *= $$EXTERNAL_PKG_DIR/libjdkmidi/lib
	}
}
