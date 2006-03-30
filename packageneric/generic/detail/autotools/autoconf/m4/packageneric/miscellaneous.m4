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
# miscellaneous



###############################################################################################
###############################################################################################
###############################################################################################



AC_DEFUN([PACKAGENERIC__UPPER_CASE],
	[$(echo $1 | sed 'y:m4_cr_letters-:m4_cr_LETTERS[]_:')]
)
AC_DEFUN([PACKAGENERIC__NORMALIZED_NAME],
	[PACKAGENERIC__UPPER_CASE($(echo $1 | sed 's/\./__/g'))]
)



###############################################################################################
###############################################################################################
###############################################################################################



AC_DEFUN([PACKAGENERIC__DEFINE],
	[
		PACKAGENERIC__ECHO(define [$1] $2)
		AC_DEFINE([$1], [$2], [$3])
	]
)

AC_DEFUN([PACKAGENERIC__DEFINE_UNQUOTED],
	[
		PACKAGENERIC__ECHO(define unquoted [$1] '$2')
		AC_DEFINE_UNQUOTED([$1], [$2], [$3])
	]
)

AC_DEFUN([PACKAGENERIC__DEFINE_AND_SUBST],
	[
		PACKAGENERIC__ECHO(define and subst [$1] $2)
		AC_DEFINE([$1], [$2], [$3])
		AC_SUBST([$1], [$2])
	]
)

AC_DEFUN([PACKAGENERIC__DEFINE_UNQUOTED_AND_SUBST],
	[
		PACKAGENERIC__ECHO(define unquoted and subst [$1] '$2')
		AC_DEFINE_UNQUOTED([$1], [$2], [$3])
		AC_SUBST([$1], [$2])
	]
)



###############################################################################################
###############################################################################################
###############################################################################################
# configuration header



PACKAGENERIC__INCLUDE(packageneric/generic/detail/autotools/autoconf/m4/packageneric/ax_prefix_config_h.modified.m4)

# wrapper for AX_PREFIX_CONFIG_H
AC_DEFUN([PACKAGENERIC__CONFIGURATION__HEADER_WITH_NAMESPACE],
	[
		#AC_REQUIRE([AX_PREFIX_CONFIG_H__MODIFIED])
		packageneric__echo configuration header with namespace '[$1] [$2]'
		AC_CONFIG_HEADERS([$1.private.hpp:$1.hpp.in])
		AX_PREFIX_CONFIG_H__MODIFIED([$1.hpp], [$2], [$1.private.hpp])
	]
)



###############################################################################################
###############################################################################################
###############################################################################################
# relative install paths



PACKAGENERIC__INCLUDE(packageneric/generic/detail/autotools/autoconf/m4/autoconf-archive/relpaths.m4)
PACKAGENERIC__INCLUDE(packageneric/generic/detail/autotools/autoconf/m4/autoconf-archive/normpath.m4)

# wrapper for adl_COMPUTE_RELATIVE_PATHS
AC_DEFUN([PACKAGENERIC__COMPUTE_RELATIVE_PATHS],
	[
		#AC_REQUIRE([adl_COMPUTE_RELATIVE_PATHS])
		packageneric__echo compute relative path '$1'
		adl_COMPUTE_RELATIVE_PATHS([$1])
	]
)
