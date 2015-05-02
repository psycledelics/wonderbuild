# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2008-2011 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

isEmpty(qt_included) {
	qt_included = 1
	verbose: message("qt included")

	win32 { # is this really needed?
		INCLUDEPATH *= $(QTDIR)/include
		INCLUDEPATH *= $(QTDIR)/include/Qt
		INCLUDEPATH *= $(QTDIR)/include/QtCore
		INCLUDEPATH *= $(QTDIR)/src/3rdparty/zlib
	}
}
