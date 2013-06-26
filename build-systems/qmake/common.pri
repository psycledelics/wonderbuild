# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2008-2011 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

# some doc worth reading: http://wiki.qtcentre.org/index.php?title=Undocumented_qmake

isEmpty(common_included) {
	common_included = 1
	verbose: message("common included")
	
	build_pass:  message("===================== $$TARGET ($$TEMPLATE) (build pass) ========")
	else:        message("===================== $$TARGET ($$TEMPLATE) =====================")
	
	defineReplace(pathToVarName) {
		s = $$replace($$1, \\.\\., _)
		return($$replace(s, [/\\\\], _))
	}

	# addSubdirs(subdirs, deps): adds directories to the project that depend on other directories
	defineTest(addSubdirs) {
		isEmpty(2): message("Sub dir: $$1")
		else: message("Sub dir: $$1 -> $$2")
		for(subdirs, 1) {
			entries = $$files($$subdirs)
			for(entry, entries) {
				name = subdirs_$$pathToVarName(entry)
				SUBDIRS += $$name
				eval($${name}.subdir = $$entry)
				export($${name}.subdir)
				for(dep, 2): eval($${name}.depends += subdirs_$$pathToVarName(dep))
				export($${name}.depends)
			}
		}
		export(SUBDIRS)
	}

	# addSubprojects(subprojects, deps): same as addSubdirs, but with paths to .pro files
	defineTest(addSubprojects) {
		isEmpty(2): message("Sub project: $$1")
		else: message("Sub project: $$1 -> $$2")
		for(subprojects, 1) {
			entries = $$files($$subprojects)
			for(entry, entries) {
				false {
					# It seems SUBDIRS variables actually don't have a '.file' property.
					name = subdirs_$$pathToVarName(entry)
					SUBDIRS += $$name
					eval($${name}.file = $$entry)
					export($${name}.file)
				} else {
					SUBDIRS += $$entry
				}
				for(dep, 2): eval($${name}.depends += subdirs_$$pathToVarName(dep))
				export($${name}.depends)
			}
		}
		export(SUBDIRS)
	}

	# omit the current directory from the final INCLUDEPATH (no '-I.' in compiler command line)
	CONFIG *= no_include_pwd

	# http://www.boost.org/doc/libs/1_51_0/doc/html/signals/s04.html
	CONFIG += no_keywords # so Qt won't #define any non-all-caps `keywords'
	
	# Define a new compiler that compiles ../src/foo/bar.cpp to $$OBJECTS_DIR/src/foo/bar.o instead of $$OBJECTS_DIR/bar.o
	# To use it, add the .cpp to the SOURCES_PRESERVE_PATH var instead of the SOURCES var.
	{
		cxx_to_object_preserve_path.input = SOURCES_PRESERVE_PATH
		cxx_to_object_preserve_path.dependency_type = TYPE_C
		defineReplace(cxxToObjectPreservePathOutputFunction) {
			variable = $$1
                        return($$OBJECTS_DIR/$$replace(variable, \\.\\., ).o)
		}
		cxx_to_object_preserve_path.output_function = cxxToObjectPreservePathOutputFunction
		*-msvc* {
			CONFIG(precompile_header) {
				cxx_to_object_preserve_path.commands = $(CXX) -c $$QMAKE_USE_PRECOMPILE $(CXXFLAGS) $(INCPATH) -Fo ${QMAKE_FILE_OUT} ${QMAKE_FILE_NAME}
			} else {
				cxx_to_object_preserve_path.commands = $(CXX) -c $(CXXFLAGS) $(INCPATH) -Fo ${QMAKE_FILE_OUT} ${QMAKE_FILE_NAME}
			}
		} else {
			CONFIG(precompile_header) {
				cxx_to_object_preserve_path.commands = $(CXX) -c $$QMAKE_USE_PRECOMPILE $(CXXFLAGS) $(INCPATH) -o ${QMAKE_FILE_OUT} ${QMAKE_FILE_NAME}
			} else {
				cxx_to_object_preserve_path.commands = $(CXX) -c $(CXXFLAGS) $(INCPATH) -o ${QMAKE_FILE_OUT} ${QMAKE_FILE_NAME}
			}
		}
		QMAKE_EXTRA_COMPILERS = cxx_to_object_preserve_path
	}

	false { # qmake segfaults!
		defineReplace(findFiles) {
			path = $$1
			pattern = $$2
			result = $$files($$path/$$pattern)
			entries = $$files($$path/*)
			for(entry, entries): result += $$findFiles($$entry/$$pattern)
			return($$result)
		}
	} else {
		unix: {
			defineReplace(findFiles) {
				path = $$1
				pattern = $$2
				result = $$system(find $$path -name \'$$pattern\')
				return($$result)
			}
		} else: win32: {
			defineReplace(findFiles) {
				path = $$replace(1, /, \\\\)
				pattern = $$2
				result = $$system(dir /s /b $$path\\$$pattern)
				return($$result)
			}
		}
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
	
	unix: TOP_SRC_DIR = $$system(cd ../.. && pwd)
	else: win32: TOP_SRC_DIR = $$system(cd ..\\.. && cd)
	verbose: message("Top src dir is $$TOP_SRC_DIR")

	COMMON_DIR = $$TOP_SRC_DIR/build-systems/qmake
	INCLUDEPATH *= $$TOP_SRC_DIR/build-systems/src
	DEPENDPATH  *= $$TOP_SRC_DIR/build-systems/src

	include(platform.pri)
}
