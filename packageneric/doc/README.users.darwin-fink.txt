==========================================
notes on using this package on darwin-fink
==========================================

compiling:

	- upgrading fink to unstable:
		-	in /sw/etc/fink.conf, modify the 'Tree:' field line to read:
				Tree: local/main stable/main stable/crypto unstable/main unstable/crypto	
		-	then: fink selfupdate # (note: the network method can be either rsync or cvs)
		-	then: fink index
		-	then: fink update-all
		-	fink manages the /sw/etc/apt/sources.list file by itself.
			To let fink use apt-get to fetch precompiled packages instead of compiling every package,
				-	in /sw/etc/fink.conf, add the field line:
						UseBinaryDist: true
				-	then: fink scanpackages
	
	- list of packages needed to be able to build this package (install them with 'fink install package1 package2 package3 ...'):

		-	packages which are required:

				pkgconfig libtool14 boost1.31
				
		-	packages which are required only to build the gui front-end of psycle:
		
				gtkmm2.4-dev libgnomecanvasmm2-dev
				
		-	packages which may not be really needed, because darwin either has bsd equivalent to these gnu tools, or have them already installed:
			
				coreutils
				fileutils
				textutils
				make g++
			
			(note: some gnu tools that are already installed on darwin/macos may be in a too old version)
			
		-	packages for maintainer mode (not required to build psycle, just needed if you want to develop it further):
			
				autoconf2.5 automake
			
			(note: autoconf and automake are already installed on darwin/macos but maybe in a too old version)

running:
	
	- To run in gui mode:
		You will need access to an X server, either a local or a remote display.

		- For remote display;
			If the X server is running on host 'nixbox', display number 0, run:
			
				DISPLAY=nixbox:0 some-gui-program-name
				
		- For local display:
			You can simply install a vnc X server, if you don't want to install a "real" X server:

				fink install vnc-server
				
			(note: vnc-server is a virtual package, so, maybe you actually have to 'fink install vnc4' instead)
			
			Then, start a vnc X server, and a window manager on it:
			
				Xvnc :0 -geometry 1000x700 -depth 16 &
				DISPLAY=localhost:0 some-window-manager &

			Note: you can optionally pass the option -dpi 75 or -dpi 100 to Xvnc to adjust font size.

			Then, connect a vnc viewer to your running vnc X server by passing it
			'my-osx-box:0' as the display name, or 'localhost:0' if the vnc viewer is on the same host.

EOF
