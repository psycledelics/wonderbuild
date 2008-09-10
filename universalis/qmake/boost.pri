isEmpty(boost_included) {
	boost_included = 1
	verbose: message("boost included")

	unix {
		macx: LIBS *= $$linkLibs(boost_signals-1_33_1 boost_thread-1_33_1)
		else {
			# The stable debian version 4.0 ("etch") doesn't have libs with the "-mt" suffix yet,
			# so we need to use the backward compatible symlinks until a new stable debian version is released.
			system(test -f /etc/debian_version) { # test if running debian-based distribution...
				LIBS *= $$linkLibs(boost_signals)
				LIBS *= $$linkLibs(boost_thread)
			} else {
				LIBS *= $$linkLibs(boost_signals-mt)
				LIBS *= $$linkLibs(boost_thread-mt)
			}
		}
	} else: win32 {
		win32-g++:            BOOST_DIR = $$EXTERNAL_PKG_DIR/boost-1.35.0
		else: win32-msvc2008: BOOST_DIR = $$EXTERNAL_PKG_DIR/boost-1.35.0
		else: win32-msvc2005: BOOST_DIR = $$EXTERNAL_PKG_DIR/boost-1.33.1
		else: win32-msvc*:    BOOST_DIR = $$EXTERNAL_PKG_DIR/boost-1.32
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
						LIBS *= $$linkLibs(boost_signals-mgw34-mt-1_35 boost_thread-mgw34-mt-1_35)
						CONFIG+=local_boost
					}
				} else: win32-msvc2008 {
					!exists($$BOOST_DIR/lib-mswindows-msvc-9.0-cxxabi-1500) {
						warning("The boost libraries are not unpacked. See the dir $$BOOST_DIR")
					} else {
						INCLUDEPATH *= $$BOOST_DIR/include
						LIBPATH *= $$BOOST_DIR/lib-mswindows-msvc-9.0-cxxabi-1500
						LIBS *= $$linkLibs(boost_signals-vc90-mt-1_35 boost_thread-vc90-mt-1_35)
						CONFIG+=local_boost
					}
				} else: win32-msvc2005 {
					!exists($$BOOST_DIR/lib-mswindows-msvc-8.0-cxxabi-1400) {
						warning("The boost libraries are not unpacked. See the dir $$BOOST_DIR")
					} else {
						INCLUDEPATH *= $$BOOST_DIR/include
						LIBPATH *= $$BOOST_DIR/lib-mswindows-msvc-8.0-cxxabi-1400
						LIBS *= $$linkLibs(boost_signals-vc80-mt-1_33_1 boost_thread-vc80-mt-1_33_1)
						CONFIG+=local_boost
					}
				} else:win32-msvc* {
					!exists($$BOOST_DIR/lib-mswindows-msvc-7.1-cxxabi-1310) {
						warning("The boost libraries are not unpacked. See the dir $$BOOST_DIR")
					} else {
						INCLUDEPATH *= $$BOOST_DIR/include
						LIBPATH *= $$BOOST_DIR/lib-mswindows-msvc-7.1-cxxabi-1310
						LIBS *= $$linkLibs(boost_signals-vc71-mt-1_33_1 boost_thread-vc71-mt-1_33_1)
						CONFIG+=local_boost
					}
				} else {
					warning("We do not have boost libs built for your compiler. Make sure you have them installed.")
				}
			}
		}
		!CONFIG(local_boost) {
			win32-g++: {
				# We add the lib names of the version that's in the dev-pack:
				LIBS *= $$linkLibs(boost_signals-mgw-mt-1_33_1 boost_thread-mgw-mt-1_33_1)
				#LIBS *= $$linkLibs(boost_signals-mgw34-mt-1_35 boost_thread-mgw34-mt-1_35)
			}
			# For msvc, we can't do better than choosing a random version.. this will not work unless you're very lucky.
			else: win32-msvc2008: LIBS *= $$linkLibs(boost_signals-vc90-mt-1_35 boost_thread-vc90-mt-1_35)
			else: win32-msvc2005: LIBS *= $$linkLibs(boost_signals-vc80-mt-1_33_1 boost_thread-vc80-mt-1_33_1)
			else: win32-msvc*:    LIBS *= $$linkLibs(boost_signals-vc71-mt-1_33_1 boost_thread-vc71-mt-1_33_1)
		}
	}
}
