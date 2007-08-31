unix {
	macx: LIBS *= -lboost_signals-1_33_1
	else: LIBS *= -lboost_signals
} else:win32 {
	EXTERNAL_PKG_DIR = $$TOP_SRC_DIR/external-packages
	
	exists($(BOOST_DIR)) {
		message("Existing BOOST_DIR is $(BOOST_DIR)")
		BOOST_DIR = $(BOOST_DIR)
		INCLUDEPATH *= $$BOOST_DIR
		LIBPATH *= $$BOOST_DIR/lib
		# Note: this is broken unless the compiler has auto-linking because we also need to set the LIBS var
	} else {
		BOOST_DIR = $$EXTERNAL_PKG_DIR/boost-1.33.1
		!exists($$BOOST_DIR) {
			warning("The local boost dir does not exist: $${BOOST_DIR}. Make sure you have boost libs installed.")
		} else {
			!exists($$BOOST_DIR/include) {
				warning("The boost headers are not unpacked. See the dir $$BOOST_DIR")
			} else {
				win32-g++ {
					!exists($$BOOST_DIR/lib-mswindows-mingw-cxxabi-1002) {
						warning("The boost libraries are not unpacked. See the dir $$BOOST_DIR")
					} else {
						INCLUDEPATH *= $$BOOST_DIR/include
						LIBPATH *= $$BOOST_DIR/lib-mswindows-mingw-cxxabi-1002
					}
				} else:win32-msvc2005 {
					!exists($$BOOST_DIR/lib-mswindows-msvc-8.0-cxxabi-1400) {
						warning("The boost libraries are not unpacked. See the dir $$BOOST_DIR")
					} else {
						INCLUDEPATH *= $$BOOST_DIR/include
						LIBPATH *= $$BOOST_DIR/lib-mswindows-msvc-8.0-cxxabi-1400
					}
				} else:win32-msvc* {
					INCLUDEPATH *= $$BOOST_DIR/include
					LIBPATH *= $$BOOST_DIR/lib-mswindows-mcvc-7-cxxabi
				} else {
					warning("We do not have boost libs built for your compiler. Make sure you have them installed.")
				}
			}
		}
	}
	
	win32-g++: LIBS *= -lboost_signals-mgw-mt-1_33_1
	else: win32-msvc2005: LIBS *= boost_signals-vc80-mt-1_33_1.lib
	else: win32-msvc*: LIBS *= boost_signals-vc71-mt-1_33_1.lib
}
