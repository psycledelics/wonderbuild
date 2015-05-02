# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2008-2011 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

isEmpty(platform_win32_included) {
	platform_win32_included = 1
	verbose: message("platform-win32 included")

	win32 {
		verbose: message("System is win32")
		
		EXTERNAL_PKG_DIR = $$TOP_SRC_DIR/external-packages
		
		win32-g++ {
			message("Compiler is g++")
			#DEFINES *= NOMINMAX # no problem on mingw if stl algo header is included before the winapi
		} else: win32-msvc* {
			message("Compiler is MS Visual C++")
			QMAKE_CXXFLAGS *= /Zi
			QMAKE_LFLAGS *= /debug
			LIBS *= $$linkLibs(advapi32 user32)
			DEFINES *= NOMINMAX # This stops windows headers from creating min & max as defines (not needed on mingw)

			win32-msvc2010 {
				VS_VERSION = 10.0
				message("Compiler is MS Visual C++ version 16 (2010 / VS 10.0)")
			}
			else: win32-msvc2008 {
				VS_VERSION = 9.0
				message("Compiler is MS Visual C++ version 15 (2008 / VS 9.0)")
			}
			else: win32-msvc2005 {
				VS_VERSION = 8.0
				message("Compiler is MS Visual C++ version 14 (2005 / VS 8.0)")
			} else {
				VS_VERSION = 7.1
				message("Compiler is MS Visual C++ version 13.1 (2003 / VS 7.1)")
			}

			# Question: Do these regiser db entries depend on the IDE Studio being installed?
			VC_DIR = $$system("reg query HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\VisualStudio\$$VS_VERSION\Setup\VC /v ProductDir | findstr REG_SZ")
			VC_DIR -= ProductDir  REG_SZ

			#VC_DIR = $$system("reg query HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\VisualStudio\$$VS_VERSION /v InstallDir | findstr REG_SZ")
			#VC_DIR -= InstallDir REG_SZ

			exists($$VC_DIR) {
				#VC_DIR = $$system("dir \"$$VC_DIR\..\..\VC\" | findstr Directory")
				#VC_DIR -= Directory of
				message("Existing VC_DIR is $$VC_DIR")
				LIBPATH *= "$${VC_DIR}/lib"
				win32-msvc2005: LIBPATH *= "$${VC_DIR}/PlatformSDK/lib"
				# todo: include Windows SDK Dirs (aren't they automatically included When Using Vc Command Prompt?
				# todo: what about INCLUDEPATH?
			}
		} else {
			warning("Untested compiler")
		}
		
	}
}
