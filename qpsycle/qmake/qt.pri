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
