isEmpty(platform_unix_included) {
	platform_unix_included = 1
	verbose: message("platform-unix included")

	unix {
		verbose: message("System is unix")
		TOP_SRC_DIR = $$system(cd ../.. && pwd)
		verbose: message("Top src dir is $$TOP_SRC_DIR")

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
