# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2008-2011 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

isEmpty(platform_unix_included) {
	platform_unix_included = 1
	verbose: message("platform-unix included")
                  QMAKE_CXXFLAGS *= -std=c++14
                  QMAKE_CXXFLAGS_DEBUG *= -std=c++14


	unix {
		verbose: message("System is unix")

		# math and dynamic loader
		LIBS *= $$linkLibs(m dl)

		macx {
			#CONFIG *= x86 ppc # make universal binaries on mac
			
			# It looks like xcode discards gcc's env vars, so we make sure they get in by copying them into qmake's vars
			env_cpath = $$system(echo $CPATH | sed \'s,:, ,g\')
			env_library_path = $$system(echo $LIBRARY_PATH | sed \'s,:, ,g\')
			for(path, env_cpath): INCLUDEPATH *= $$path
			for(path, env_library_path): LIBPATH *= $$path
			
			# We add fink's dirs to the search paths. Fink is installed by default with the /sw/ prefix.
			exists(/sw) {
				message("Found fink dir /sw")
				exists(/sw/include): INCLUDEPATH *= /sw/include
				exists(/sw/lib): LIBPATH *= /sw/lib
			}
		}
	}
}
