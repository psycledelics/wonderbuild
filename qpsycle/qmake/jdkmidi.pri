win32-g++{ 
	message(Adding libjdkmidi)
	LIBPATH *= $$EXTERNAL_PKG_DIR/libjdkmidi/lib
	INCLUDEPATH *= $$EXTERNAL_PKG_DIR/libjdkmidi/include
	
	LIBS *= -ljdkmidi
	}
# supposing that under unix we have /usr/lib and usr/include