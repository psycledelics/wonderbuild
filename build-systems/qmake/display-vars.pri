isEmpty(display_vars_included) {
	display_vars_included = 1
	verbose: message("display-vars included")

	verbose {
		message("QMAKE_CXX is $$QMAKE_CXX")
		message("QMAKE_CXXFLAGS are $$QMAKE_CXXFLAGS")
		message("QMAKE_CXXFLAGS_WARN_ON are $$QMAKE_CXXFLAGS_WARN_ON")
		message("QMAKE_CXXFLAGS_WARN_OFF are $$QMAKE_CXXFLAGS_WARN_OFF")
		message("QMAKE_CXXFLAGS_DEBUG are $$QMAKE_CXXFLAGS_DEBUG")
		message("QMAKE_CXXFLAGS_RELEASE are $$QMAKE_CXXFLAGS_RELEASE")
		message("QMAKE_CXXFLAGS_SHLIB are $$QMAKE_CXXFLAGS_SHLIB")
		message("QMAKE_CXXFLAGS_THREAD are $$QMAKE_CXXFLAGS_THREAD")
		message("QMAKE_CXXFLAGS_MT are $$QMAKE_CXXFLAGS_MT")
		message("QMAKE_CXXFLAGS_MT_DBG are $$QMAKE_CXXFLAGS_MT_DBG")
		win32 {
			message("QMAKE_CXXFLAGS_MT_DLL are $$QMAKE_CXXFLAGS_MT_DLL")
			message("QMAKE_CXXFLAGS_MT_DLL_DBG are $$QMAKE_CXXFLAGS_MT_DLL_DBG")
		}

		message("QMAKE_LINK is $$QMAKE_LINK")
		message("QMAKE_LDFLAGS are $$QMAKE_LDFLAGS")
		message("QMAKE_LDFLAGS_DEBUG are $$QMAKE_DEBUG")
		message("QMAKE_LDFLAGS_RELEASE are $$QMAKE_RELEASE")
		message("QMAKE_LDFLAGS_SHAPP are $$QMAKE_SHAPP")
		message("QMAKE_LDFLAGS_SHLIB are $$QMAKE_SHLIB")
		message("QMAKE_LDFLAGS_PLUGIN are $$QMAKE_PLUGIN")
		message("QMAKE_LDFLAGS_SONAME are $$QMAKE_SONAME")
		message("QMAKE_LDFLAGS_THREAD are $$QMAKE_THREAD")
		message("QMAKE_LDFLAGS_QT_DLL are $$QMAKE_QT_DLL")
		message("QMAKE_LDFLAGS_QTPLUGIN are $$QMAKE_QTPLUGIN")
		win32 {
			message("QMAKE_LDFLAGS_CONSOLE are $$QMAKE_CONSOLE")
			message("QMAKE_LDFLAGS_CONSOLE_DLL are $$QMAKE_CONSOLE_DLL")
			message("QMAKE_LDFLAGS_WINDOWS are $$QMAKE_WINDOWS")
			message("QMAKE_LDFLAGS_WINDOWS_DLL are $$QMAKE_WINDOWS_DLL")
		}
	}

	verbose {
		message("CONFIG is $$CONFIG")
		message("PKGCONFIG is $$PKGCONFIG")
		message("DEFINES are $$DEFINES")
		message("INCLUDEPATH is $$INCLUDEPATH")
		message("LIBS are $$LIBS")
	}
}
