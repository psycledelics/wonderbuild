win32 {
	message("System is win32")
	TOP_SRC_DIR = $$system(cd ..\.. && cd)
	message("Top src dir is $$TOP_SRC_DIR")
	EXTERNAL_PKG_DIR = $$TOP_SRC_DIR/external-packages
	win32-g++ {
		message("Compiler is g++")
		#DEFINES *= NOMINMAX # no problem on mingw if stl algo header is included before the winapi
	} else:win32-msvc* {
		message("Compiler is MS Visual C++")
		QMAKE_CXXFLAGS *= /Zi
		QMAKE_LFLAGS *= /debug
		LIBS *= advapi32.lib user32.lib
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
	
	# On win32, qmake decides to feed the 'ar' command from script files (ar -M < script)
	# whenever there are more than QMAKE_LINK_OBJECT_MAX files to put in the archive.
	# The idea is probably to avoid reaching the command line length limit of that platform (which is?).
	# Unfortunatly, these scripts don't allow '+' characters in paths.
	# A quick workaround is to disable the use of scripts by setting a high-enough limit that's unlikely to be reached.
	QMAKE_LINK_OBJECT_MAX = 10000
}
