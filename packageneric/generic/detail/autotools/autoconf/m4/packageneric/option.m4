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
# configure options



# The following macro is a helper to add a package option to configure (configure --with-PACKAGE=xxx) with a help string shown in configure --help, and a cached value.
# It also declares a condition for automake (PACKAGENERIC__CONFIGURATION__OPTION__WITH__xxx) and a definition in configuration headers (PACKAGENERIC__CONFIGURATION__OPTION__WITH__xxx).
AC_DEFUN([PACKAGENERIC__CONFIGURATION__OPTION__WITH__DEFINE],
	# 1: package option name
	# 2: description
	# 3: lower case
	# 4: upper case
	# 5: default value
	# 6: file exists condition
	[
		AC_REQUIRE([AC_ARG_WITH])
		AC_REQUIRE([AC_CACHE_CHECK])
		AC_REQUIRE([AM_CONDITIONAL])
		#AC_REQUIRE([AC_DEFINE_UNQUOTED])
		packageneric__echo option: with: '[$1]: [$2]'
		packageneric__configuration__option__with__$3__file_exists_condition=$6
		if test -z "$packageneric__configuration__option__with__$3__file_exists_condition" -o -e "$packageneric__configuration__option__with__$3__file_exists_condition"
		then
			AC_ARG_WITH(
				[$1],
				AC_HELP_STRING([--with-$1], [$2 @<:@default=$5@:>@]),
				packageneric__cv__configuration__option__with__$3=$withval,
				packageneric__cv__configuration__option__with__$3=$5
			)
			AC_CACHE_CHECK([whether to use $1], [packageneric__cv__configuration__option__with__$3], [packageneric__cv__configuration__option__with__$3=$5])
			packageneric__configuration__option__with__$3=$packageneric__cv__configuration__option__with__$3
		else
			packageneric__configuration__option__with__$3=no
		fi
		unset packageneric__configuration__option__with__$3__file_exists_condition
		AM_CONDITIONAL([PACKAGENERIC__CONFIGURATION__OPTION__WITH__$4], [test "$packageneric__configuration__option__with__$3" != no])
		if test "$packageneric__configuration__option__with__$3" != no
		then
			AC_DEFINE_UNQUOTED([PACKAGENERIC__CONFIGURATION__OPTION__WITH__$4], [$packageneric__configuration__option__with__$3], [$2])
		fi
	]
)

AC_DEFUN([PACKAGENERIC__CONFIGURATION__OPTION__WITH],
	[test -n "$packageneric__configuration__option__with__$1" -a "$packageneric__configuration__option__with__$1" != no]
)



# The following macro is a helper to add a feature option to configure (configure --enable-FEATURE=xxx) with a help string shown in configure --help, and a cached value.
# It also declares a condition for automake (PACKAGENERIC__CONFIGURATION__OPTION__ENABLE__xxx) and a definition in configuration headers (PACKAGENERIC__CONFIGURATION__OPTION__ENABLE__xxx).
AC_DEFUN([PACKAGENERIC__CONFIGURATION__OPTION__ENABLE__DEFINE],
	# 1: feature option name
	# 2: description
	# 3: lower case
	# 4: upper case
	# 5: default value
	# 6: file exists condition
	[
		AC_REQUIRE([AC_ARG_ENABLE])
		AC_REQUIRE([AC_CACHE_CHECK])
		AC_REQUIRE([AM_CONDITIONAL])
		#AC_REQUIRE([AC_DEFINE_UNQUOTED])
		packageneric__echo option: enable: '[$1]: [$2]'
		packageneric__configuration__option__enable__$3__file_exists_condition=$6
		if test -z "$packageneric__configuration__option__enable__$3__file_exists_condition" -o -e "$packageneric__configuration__option__enable__$3__file_exists_condition"
		then
			AC_ARG_ENABLE(
				[$1],
				AC_HELP_STRING([--enable-$1], [$2 @<:@default=$5@:>@]),
				packageneric__cv__configuration__option__enable__$3=$enableval,
				packageneric__cv__configuration__option__enable__$3=$5
			)
			AC_CACHE_CHECK([whether to enable $1], [packageneric__cv__configuration__option__enable__$3], [packageneric__cv__configuration__option__enable__$3=$5])
			packageneric__configuration__option__enable__$3=$packageneric__cv__configuration__option__enable__$3
		else
			packageneric__configuration__option__enable__$3=no
		fi
		AM_CONDITIONAL([PACKAGENERIC__CONFIGURATION__OPTION__ENABLE__$4], [test "$packageneric__configuration__option__enable__$3" != no])
		if test "$packageneric__configuration__option__enable__$3" != no
		then
			AC_DEFINE_UNQUOTED([PACKAGENERIC__CONFIGURATION__OPTION__ENABLE__$4], [$packageneric__configuration__option__enable__$3], [$2])
		fi
	]
)

AC_DEFUN([PACKAGENERIC__CONFIGURATION__OPTION__ENABLE],
	[test -n "$packageneric__configuration__option__enable__$1" -a "$packageneric__configuration__option__enable__$1" != no]
)
