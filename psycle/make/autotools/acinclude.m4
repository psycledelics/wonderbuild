#!/usr/bin/m4

##############################################################################
#
# custom m4 macros.
#
# Copyright (C) 2004 Johan Boulé
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
##############################################################################

# The following macro is a helper to add a package option to configure (configure --with-PACKAGE=xxx) with a help string shown in configure --help, and a cached value.
# It also declares a condition for automake and a definition in the config header.
AC_DEFUN(
	[AC_ARG_WITH_HANDLE],
	# $1: package option name
	# $2: description
	# $3: default value
	[
		AC_ARG_WITH(
			[$1],
			AC_HELP_STRING([--with-$1], [$2 (default=$3)]),
			ac_cv_with_$1=$withval,
			ac_cv_with_$1=$3
		)
		AC_CACHE_CHECK([whether to use $1], [ac_cv_with_$1], [ac_cv_with_$1=$3])
		AM_CONDITIONAL([WITH_$1], [test "$ac_cv_with_$1" != no])
		if test "$ac_cv_with_$1" != no
		then
			AC_DEFINE_UNQUOTED([WITH_$1], [$ac_cv_with_$1], [$2])
		fi
	]
)

# The following macro is a helper to add a feature option to configure (configure --enable-FEATURE=xxx) with a help string shown in configure --help, and a cached value.
# It also declares a condition for automake and a definition in the config header.
AC_DEFUN(
	[AC_ARG_ENABLE_HANDLER],
	# $1: feature option name
	# $2: description
	# $3: default value
	[
		AC_ARG_ENABLE(
			[$1],
			AC_HELP_STRING([--enable-$1], [$2 (default=$3)]),
			ac_cv_enable_$1=$enableval,
			ac_cv_enable_$1=$3
		)
		AC_CACHE_CHECK([whether to enable $1], [ac_cv_enable_$1], [ac_cv_enable_$1=$3])
		AM_CONDITIONAL([ENABLE_$1], [test "$ac_cv_enable_$1" != no])
		if test "$ac_cv_enable_$1" != no
		then
			AC_DEFINE_UNQUOTED([ENABLE_$1], [$ac_cv_enable_$1], [$2])
		fi
	]
)

# The following macro is a helper to check for an external lib and substitute $(PACKAGE_CFLAGS) and $(PACKAGE_LIBS) in files generated from makefile.am files.
AC_DEFUN(
	[PKG_CHECK_MODULES_SUBST],
	[
		PKG_CHECK_MODULES([$1], [$2])
		AC_SUBST([$1_CFLAGS])
		AC_SUBST([$1_LIBS])
	]
)
