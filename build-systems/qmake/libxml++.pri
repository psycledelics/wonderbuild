# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2008-2011 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

isEmpty(libxmlpp_included) {
	libxmlpp_included = 1
	verbose: message("libxml++ included")
	
	unix | *-g++ {
		CONFIG *= link_pkgconfig # adds support for pkg-config via the PKG_CONFIG var

		system(pkg-config --exists libxml++-2.6) {
			message("pkg-config thinks libxml++-2.6 libs are available...")
			PKGCONFIG += libxml++-2.6
			DEFINES += PSYCLE__LIBXMLPP_AVAILABLE # This is used in the source to determine when to include libxml++-specific things.
		} else {
			error( "Couldn't find libxml++-2.6." )
		}
	} else {
		# TODO for win32-msvc*
	}
}
