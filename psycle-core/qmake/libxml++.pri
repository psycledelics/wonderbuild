unix | win32-g++ {
	CONFIG *= link_pkgconfig # adds support for pkg-config via the PKG_CONFIG var

	system( pkg-config --exists libxml++-2.6 ) {
		message( "pkg-config thinks libxml++-2.6 libs are available..." )
		PKGCONFIG += libxml++-2.6
		DEFINES += PSYCLE__LIBXMLPP_AVAILABLE # This is used in the source to determine when to include libxml++-specific things.
	} else {
	  error( "Couldn't find libxml++-2.6." )
	}
}
else {
	# TODO for win32-msvc*
}
