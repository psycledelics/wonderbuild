isEmpty(common_included) {
	common_included = 1
	verbose: message("common included")
	
	message("===================== $$TARGET =====================")
	# Check to see what build mode has been specified.
	CONFIG(debug):CONFIG(release): CONFIG -= debug
	CONFIG(debug):CONFIG(release) {
		warning("debug and release are both specified, separately, in CONFIG. \
			This is possibly not what you want.  Consider using CONFIG+=debug_and_release if \
			you want to build debug and release versions concurrently, or CONFIG-=release \
			or CONFIG-=debug if you want just one mode.")
	}
	CONFIG(release): message("Configured to make a release mode Makefile.")
	CONFIG(debug): message("Configured to make a debug mode Makefile.")
	CONFIG(debug_and_release): message("Configured to make both Makefile.Debug and Makefile.Release.")
	CONFIG(debug):CONFIG(release):!CONFIG(debug_and_release): warning("Debug overrides release.")

	# we use these c++ language features
	CONFIG *= rtti exceptions thread

	# qmake decides to feed the 'ar' command from script files (ar -M < script) whenever there are
	# more than QMAKE_LINK_OBJECT_MAX files to put in the archive.
	# The idea is probably to avoid reaching the command line length limit.
	# Unfortunatly, these scripts don't allow '+' characters in paths.
	# A quick workaround is to disable the use of scripts by setting a high-enough limit that's unlikely to be reached.
	# This is mostly needed for the win32 platform where qmake defaults to a rather low value for QMAKE_LINK_OBJECT_MAX.
	QMAKE_LINK_OBJECT_MAX = 10000

	include(platform.pri)

	COMMON_DIR = $$TOP_SRC_DIR/psycle-core/qmake
	
	definelinkLib(libname) {
		unix | win3-g++:   return(-l$${libname})
		else: win32-msvc*: return($${libname}.lib)
	}
}
