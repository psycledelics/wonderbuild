isEmpty(common_included) {
	common_included = 1
	verbose: message("common included")

	# Define a new compiler that compiles ../src/foo/bar.cpp to $$OBJECTS_DIR/src/foo/bar.o instead of $$OBJECTS_DIR/bar.o
	# To use it, add the .cpp to the SOURCES_PRESERVE_PATH var instead of the SOURCES var.
	# TODO: add -include $(PRECOMPILED_HEADER) to the command line
	{
		cxx_to_object_preserve_path.input = SOURCES_PRESERVE_PATH
		cxx_to_object_preserve_path.dependency_type = TYPE_C
		defineReplace(removeDotDot) {
			variable = $$1
			return($$OBJECTS_DIR/$$replace(variable, \.\., ).o)
		}
		cxx_to_object_preserve_path.output_function = removeDotDot
		win32-msvc*: cxx_to_object_preserve_path.commands = $(CXX) -c $(CXXFLAGS) $(INCPATH) -Fo ${QMAKE_FILE_OUT} ${QMAKE_FILE_NAME}
		else:        cxx_to_object_preserve_path.commands = $(CXX) -c $(CXXFLAGS) $(INCPATH) -o ${QMAKE_FILE_OUT} ${QMAKE_FILE_NAME}
		QMAKE_EXTRA_COMPILERS = cxx_to_object_preserve_path
	}


	defineReplace(sources) {
		variable = $$1
		list = $$eval($$variable)
		result =
		for(element, list): {
			filename = $${element}.cpp
			exists($$filename): result += $$filename
		}
		return($$result)
	}
	
	defineReplace(headers) {
		variable = $$1
		list = $$eval($$variable)
		result =
		for(element, list): {
			filename = $${element}.hpp
			exists($$filename): result += $$filename
			else {
				filename = $${element}.h
				exists($$filename): result += $$filename
			}
		}
		return($$result)
	}
	

	!build_pass: message("===================== $$TARGET ==================================")
	else:        message("===================== $$TARGET (build pass) =====================")

	# Check to see what build mode has been specified.
	CONFIG(debug):CONFIG(release) {
		warning("debug and release are both specified, separately, in CONFIG. \
			This is possibly not what you want.  Consider using CONFIG+=debug_and_release if \
			you want to build debug and release versions concurrently, or CONFIG-=release \
			or CONFIG-=debug if you want just one mode.")
	}

	# Note: qmake has different default settings on unix and win32 platforms!
	# Default on unix:  debug, release are set, but not debug_and_release.
	# Default on win32: debug, release, debug_and_release are all set.
	# Both default settings, however, lead to a release build when
	# invoking "make" without specifying any target.
	# The difference is, by default, you can't invoke "make release" nor "make debug" on unix,
	# while you can do so on win32.

	# Print messages or warnings
	!CONFIG(debug):!CONFIG(release):!CONFIG(debug_and_release): {
		warning("None of debug, release nor debug_and_release were specified in CONFIG.")
		message("Release is the default.")
	}
	CONFIG(debug_and_release): message("Configured to make both Makefile.Debug and Makefile.Release.")
	CONFIG(debug):!CONFIG(release): message("Configured to make a debug mode Makefile.")
	!CONFIG(debug):CONFIG(release): message("Configured to make a release mode Makefile.")
	CONFIG(debug):CONFIG(release):!CONFIG(debug_and_release): warning("Release overrides debug.")
	CONFIG(debug):CONFIG(release):CONFIG(debug_and_release): warning("Check above which is the default, debug or release.")
	!CONFIG(debug):!CONFIG(release):CONFIG(debug_and_release): message("Release is the default.")


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

	COMMON_DIR = $$TOP_SRC_DIR/universalis/qmake
}
