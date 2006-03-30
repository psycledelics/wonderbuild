# !/usr/bin/m4

##############################################################################
#
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# Copyright (C) 1999-2005 Psycledelics http://psycle.pastnotecut.org : Johan Boule
#
# m4 macros for autoconf included by ./configure.ac
# \meta hook ./configure.ac
# \meta generic
# \meta standard posix
#
##############################################################################



###############################################################################################
###############################################################################################
###############################################################################################
# note about syntax



#################
# to output square brackets ([]) in m4/sugar/autoconf..
# m4: @<:@ and @:>@ works. (@%:@ for pound (#)) ... (or temporarily redefining the quoting characters)
# sh: $(echo -e \133) and $(echo -e \135)
#################



m4_define([PACKAGENERIC__ECHO],
	{
		echo -en '\e\13333m' &&
		echo -e 'packageneric.autotools.autoconf.configure: [[$1]]' &&
		echo -en '\e\1330m'
	}
)

m4_define([PACKAGENERIC__INCLUDE],
	PACKAGENERIC__ECHO([include]: push: [[$1]] (push))
	[m4_include]([[$1]])
	PACKAGENERIC__ECHO([include]:  pop: [[$1]] (pop))
)

PACKAGENERIC__INCLUDE(packageneric/generic/detail/autotools/autoconf/m4/packageneric/miscellaneous.m4)
PACKAGENERIC__INCLUDE(packageneric/generic/detail/autotools/autoconf/m4/packageneric/option.m4)
PACKAGENERIC__INCLUDE(packageneric/generic/detail/autotools/autoconf/m4/packageneric/module.m4)
