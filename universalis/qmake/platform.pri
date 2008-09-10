isEmpty(platform_included) {
	platform_included = 1
	verbose: message("platform included")

	defineReplace(linkLibs) {
		list = $$1
		result =
		for(element, list) {
			unix | win32-g++:  result += -l$${element}
			else: win32-msvc*: result += $${element}.lib
		}
		return($$result)
	}
	
	# Treat 64-bit to 32-bit integer casts as errors
	*-g++ {
		#QMAKE_CXXFLAGS *= -Werror=pointer-to-int-cast # gcc 4.3
		#QMAKE_CXXFLAGS *= -Werror=int-to-pointer-cast # gcc 4.3 
		#QMAKE_CXXFLAGS *= -fdiagnostics-show-option
	} else:*-msvc {
		QMAKE_CXXFLAGS *= -Wp64
	}

	unix: include(platform-unix.pri)
	else: win32: include(platform-win32.pri)
	
	# Colors can be disabled either with "qmake CONFIG+=nocolor", or "make TERM=dumb".
	#
	# Note that colors are automatically disabled when output is not a tty terminal
	# (e.g. piped or redirected to files), unless TERM is set to packageneric--color-pipe.
	#
	# On windows, msys's rxvt terminal is not seen as a tty terminal from the non-msys mingw32-make,
	# so you will need to use "mingw32-make TERM=packageneric--color-pipe" to enable colors.
	# Cygwin's rxvt terminal (either in windows or X11 mode) doesn't have this problem since you would use cygwin's make,
	# and it even works in cygwin's bash shell running inside microsoft's ugly and non-ansi "console".
	#
	# If you also use colormake, the output won't be a tty terminal anymore but a pipe,
	# so you will need to use "colormake TERM=packageneric--color-pipe" to enable colorisation of gcc's output.
	#
	!CONFIG(nocolor): exists(/usr/bin/env) { # /usr/bin/env is a good indication we have a posix system and shell (as opposed to microsoft's cmd.exe shell). A better test would be to test the SHELL env var.
		colorgcc = $$TOP_SRC_DIR/packageneric/colorgcc
		exists($$colorgcc) {
			contains(QMAKE_CXX,  g++): QMAKE_CXX  = $$colorgcc
			contains(QMAKE_LINK, g++): QMAKE_LINK = $$colorgcc
		}
	}
}
