# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2008-2011 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

isEmpty(boost_included) {
	boost_included = 1
	verbose: message("boost included")

	unix {
		macx: LIBS *= $$linkLibs(boost_signals-1_41 boost_thread-1_41 boost_filesystem-1_41)
		else: LIBS *= $$linkLibs(boost_signals-mt boost_thread-mt boost_filesystem-mt)
	} else: win32 {
		win32-g++:            BOOST_DIR = $$EXTERNAL_PKG_DIR/boost-1.41.0
		else: win32-msvc2010: BOOST_DIR = $$EXTERNAL_PKG_DIR/boost-1.41.0
		else: win32-msvc2008: BOOST_DIR = $$EXTERNAL_PKG_DIR/boost-1.41.0
		else: win32-msvc2005: BOOST_DIR = $$EXTERNAL_PKG_DIR/boost-1.41.0
		else: win32-msvc*:    BOOST_DIR = $$EXTERNAL_PKG_DIR/boost-1.41.1
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
						LIBS *= $$linkLibs(boost_signals-mgw-mt-1_41 boost_thread-mgw-mt-1_41 boost_filesystem-mgw-mt-1_41 winmm)
						CONFIG += local_boost
					}
				} else: win32-msvc2010 {
					!exists($$BOOST_DIR/lib-mswindows-msvc-10.0-cxxabi-1500) {
						warning("The boost libraries are not unpacked. See the dir $$BOOST_DIR")
					} else {
						INCLUDEPATH *= $$BOOST_DIR/include
						LIBPATH *= $$BOOST_DIR/lib-mswindows-msvc-10.0-cxxabi-1500
						LIBS *= $$linkLibs(boost_signals-vc100-mt-1_41 boost_thread-vc100-mt-1_41)
						CONFIG += local_boost
					}
				} else: win32-msvc2008 {
					!exists($$BOOST_DIR/lib-mswindows-msvc-9.0-cxxabi-1500) {
						warning("The boost libraries are not unpacked. See the dir $$BOOST_DIR")
					} else {
						INCLUDEPATH *= $$BOOST_DIR/include
						LIBPATH *= $$BOOST_DIR/lib-mswindows-msvc-9.0-cxxabi-1500
						LIBS *= $$linkLibs(boost_signals-vc90-mt-1_41 boost_thread-vc90-mt-1_41)
						CONFIG += local_boost
					}
				} else: win32-msvc2005 {
					!exists($$BOOST_DIR/lib-mswindows-msvc-8.0-cxxabi-1400) {
						warning("The boost libraries are not unpacked. See the dir $$BOOST_DIR")
					} else {
						INCLUDEPATH *= $$BOOST_DIR/include
						LIBPATH *= $$BOOST_DIR/lib-mswindows-msvc-8.0-cxxabi-1400
						LIBS *= $$linkLibs(boost_signals-vc80-mt-1_41 boost_thread-vc80-mt-1_41)
						CONFIG += local_boost
					}
				} else: win32-msvc* {
					!exists($$BOOST_DIR/lib-mswindows-msvc-7.1-cxxabi-1310) {
						warning("The boost libraries are not unpacked. See the dir $$BOOST_DIR")
					} else {
						INCLUDEPATH *= $$BOOST_DIR/include
						LIBPATH *= $$BOOST_DIR/lib-mswindows-msvc-7.1-cxxabi-1310
						LIBS *= $$linkLibs(boost_signals-vc71-mt-1_33_1 boost_thread-vc71-mt-1_41)
						CONFIG += local_boost
					}
				} else {
					warning("We do not have boost libs built for your compiler. Make sure you have them installed.")
				}
			}
		}
		!CONFIG(local_boost) {
			win32-g++: {
				# We add the lib names of the version that's in the dev-pack:
				LIBS *= $$linkLibs(boost_signals-mgw34-mt-1_41 boost_thread-mgw34-mt-1_41 boost_filesystem-mgw34-mt-1_41 winmm)
			}
			# For msvc, we can't do better than choosing a random version.. this will not work unless you're very lucky.
			else: win32-msvc2010: LIBS *= $$linkLibs(boost_signals-vc100-mt-1_41 boost_thread-vc100-mt-1_41)
			else: win32-msvc2008: LIBS *= $$linkLibs(boost_signals-vc90-mt-1_41  boost_thread-vc90-mt-1_41)
			else: win32-msvc2005: LIBS *= $$linkLibs(boost_signals-vc80-mt-1_41  boost_thread-vc80-mt-1_41)
			else: win32-msvc*:    LIBS *= $$linkLibs(boost_signals-vc71-mt-1_41  boost_thread-vc71-mt-1_41)
		}
	}
}
