# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2008-2011 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

isEmpty(jdkmidi_included) {
	jdkmidi_included = 1
	verbose: message("jdkmidi included")
	
	LIBS *= $$linkLibs(jdkmidi)
	
	win32 {
		INCLUDEPATH *= $$EXTERNAL_PKG_DIR/libjdkmidi/include
		win32-g++:         LIBPATH *= $$EXTERNAL_PKG_DIR/libjdkmidi/lib
		else: win32-msvc*: LIBPATH *= $$EXTERNAL_PKG_DIR/libjdkmidi/lib-msvc
	}
}
