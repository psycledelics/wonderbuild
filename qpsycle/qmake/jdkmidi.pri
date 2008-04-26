message(Adding libjdkmidi)
unix {
	# supposing that under unix we have it in /usr/lib and usr/include
	LIBS *= -ljdkmidi
} else:win32 { 
	INCLUDEPATH *= $$EXTERNAL_PKG_DIR/libjdkmidi/include
	LIBPATH *= $$EXTERNAL_PKG_DIR/libjdkmidi/lib
	win32-g++: LIBS *= -ljdkmidi
	else:win32-msvc*: LIBS *= jdkmidi.lib
}
