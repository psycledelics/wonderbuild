isEmpty(qt_xml_included) {
	qt_xml_included = 1
	verbose: message("qt xml included")
	
	include(qt.pri)
	
	QT *= xml
	
	win32: INCLUDEPATH *= $(QTDIR)/include/QtXml # is this really needed?
}
