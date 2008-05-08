isEmpty(boost_included) {
	boost_included = 1
	verbose: message("boost included")

	unix {
		macx: LIBS *= $$linkLibs(boost_signals-1_33_1 boost_thread-1_33_1)
		else: LIBS *= $$linkLibs(boost_signals boost_thread)
	} else: win32 {
		win32-g++: LIBS *= $$linkLibs(boost_signals-mgw34-mt-1_35 boost_thread-mgw34-mt-1_35)
		else: win32-msvc2008: LIBS *= $$linkLibs(boost_signals-vc90-mt-1_35 boost_thread-vc90-mt-1_35)
		else: win32-msvc2005: LIBS *= $$linkLibs(boost_signals-vc80-mt-1_33_1 boost_thread-vc80-mt-1_33_1)
		else: win32-msvc*:    LIBS *= $$linkLibs(boost_signals-vc71-mt-1_33_1 boost_thread-vc71-mt-1_33_1)

		exists($(BOOST_DIR)) {
			message("Existing BOOST_DIR is $(BOOST_DIR)")
			BOOST_DIR = $(BOOST_DIR)
			INCLUDEPATH *= $$BOOST_DIR
			LIBPATH *= $$BOOST_DIR/lib
			# Note: this is broken unless the compiler has auto-linking because we also need to set the LIBS var
		} else {
			win32-g++:      BOOST_DIR = $$EXTERNAL_PKG_DIR/boost-1.35.0
			win32-msvc2008: BOOST_DIR = $$EXTERNAL_PKG_DIR/boost-1.35.0
			win32-msvc2005: BOOST_DIR = $$EXTERNAL_PKG_DIR/boost-1.33.1
			win32-msvc*:    BOOST_DIR = $$EXTERNAL_PKG_DIR/boost-1.32
			!exists($$BOOST_DIR) {
				warning("The local boost dir does not exist: $${BOOST_DIR}. Make sure you have boost libs installed.")
			} else {
				win32-g++ {
					!exists($$BOOST_DIR/include) {
						message("Unpacking boost headers $$BOOST_DIR/include")
						system("cd $$BOOST_DIR && tar xjf include.tar.bz2")
					}
					!exists($$BOOST_DIR/lib-mswindows-mingw-cxxabi-1002) {
						message("Unpacking boost libraries $$BOOST_DIR/lib-mswindows-mingw-cxxabi-1002")
						system("cd $$BOOST_DIR && tar xjf lib-mswindows-mingw-cxxabi-1002.tar.bz2")
					}
				}

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
					} else: win32-msvc2008 {
						!exists($$BOOST_DIR/lib-mswindows-msvc-9.0-cxxabi-1500) {
							warning("The boost libraries are not unpacked. See the dir $$BOOST_DIR")
 						} else {
							INCLUDEPATH *= $$BOOST_DIR/include
							LIBPATH *= $$BOOST_DIR/lib-mswindows-msvc-9.0-cxxabi-1500
						}
					} else: win32-msvc2005 {
						!exists($$BOOST_DIR/lib-mswindows-msvc-8.0-cxxabi-1400) {
							warning("The boost libraries are not unpacked. See the dir $$BOOST_DIR")
						} else {
							INCLUDEPATH *= $$BOOST_DIR/include
							LIBPATH *= $$BOOST_DIR/lib-mswindows-msvc-8.0-cxxabi-1400
						}
					} else:win32-msvc* {
						!exists($$BOOST_DIR/lib-mswindows-msvc-7.1-cxxabi-1310) {
							warning("The boost libraries are not unpacked. See the dir $$BOOST_DIR")
						} else {
							INCLUDEPATH *= $$BOOST_DIR/include
							LIBPATH *= $$BOOST_DIR/lib-mswindows-msvc-7.1-cxxabi-1310
						}
					} else {
						warning("We do not have boost libs built for your compiler. Make sure you have them installed.")
					}
				}
			}
		}
	}
}
