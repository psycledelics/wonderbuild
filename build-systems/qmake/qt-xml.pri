# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2008-2011 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

isEmpty(qt_xml_included) {
	qt_xml_included = 1
	verbose: message("qt xml included")
	
	include(qt.pri)
	
	QT *= xml
	
	win32: INCLUDEPATH *= $(QTDIR)/include/QtXml # is this really needed?
}
