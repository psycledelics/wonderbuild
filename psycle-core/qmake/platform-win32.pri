win32 {
	message("System is win32")
	TOP_SRC_DIR = $$system(cd ..\.. && cd)
	message("Top src dir is $$TOP_SRC_DIR")
	win32-g++ {
		message("Compiler is g++")
		#DEFINES *= NOMINMAX # no problem on mingw if stl algo header is included before the winapi
	} else:win32-msvc* {
		message("Compiler is MS Visual C++")
		QMAKE_CXXFLAGS *= /Zi
		QMAKE_LFLAGS *= /debug
		LIBS *= advapi32.lib
		LIBS *= user32.lib
		LIBPATH *= "../external-packages/zlib-1.2.3/lib-mswindows-cabi"
		DEFINES *= NOMINMAX # This stops windows headers from creating min & max as defines (not needed on mingw)

		win32-msvc2005 {
			VC_VERSION = 8.0
			message("Compiler is MS Visual C++ version 14 (2005)")
		} else {
			VC_VERSION = 7.1
		}

		# Question: Do these regiser db entries depend on the IDE Studio being installed?
		VC_DIR = $$system("reg query HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\VisualStudio\$$VC_VERSION\Setup\VC /v ProductDir | findstr REG_SZ")
		VC_DIR -= ProductDir  REG_SZ

		#VC_DIR = $$system("reg query HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\VisualStudio\$$VC_VERSION /v InstallDir | findstr REG_SZ")
		#VC_DIR -= InstallDir REG_SZ

		exists($$VC_DIR) {
			#VC_DIR = $$system("dir \"$$VC_DIR\..\..\VC\" | findstr Directory")
			#VC_DIR -= Directory of
			message("Existing VC_DIR is $$VC_DIR")
			LIBPATH *= "$${VC_DIR}/lib"
			LIBPATH *= "$${VC_DIR}/PlatformSDK/lib"
			# todo: what about INCLUDEPATH?
		}
	} else {
		warning("Untested compiler")
	}
}
