AC_PREREQ(2.59)

AC_INIT(ngrs gui toolkit, 0.0.3, natti__@users.sourceforge.net, ngrs)

AC_CONFIG_AUX_DIR(autotools.auxiliary-programs)

AM_INIT_AUTOMAKE(1.9 readme-alpha subdir-objects no-define nostdinc)
AC_DISABLE_STATIC
AC_PROG_LIBTOOL
AC_PROG_CXXCPP
AC_PROG_CXX
# dnl # PKG_PROG_PKG_CONFIG(0.18) # dnl # this macro doesn't exist on pre-0.15 versions

AC_PATH_X
AC_PATH_XTRA
X_LIBS="$X_PRE_LIBS $X_LIBS -lX11 $X_EXTRA_LIBS -lXpm"

AC_LANG_PUSH(C++)
AC_CHECK_LIB(m, main, M_LIBS=-lm, AC_MSG_WARN(no m lib found))
AC_CHECK_LIB(dl, main, DL_LIBS=-ldl, AC_MSG_WARN(no dl lib found))
AC_CHECK_LIB(pthread, main, PTHREAD_CFLAGS=-D_REENTRANT && PTHREAD_LIBS=-lpthread, AC_MSG_ERROR(pthread lib required))
AC_CHECK_LIB(xerces-c, main, XERCES_LIBS=-lxerces-c, AC_MSG_ERROR(xerces-c lib required))
AC_LANG_POP(C++)

for package in M DL PTHREAD X XERCES
do
	for stanza in CFLAGS LIBS
	do
		eval NGRS_NO_PKG_CONFIG_$stanza=\"\$NGRS_NO_PKG_CONFIG_$stanza \$${package}_$stanza\"
	done
done

for private_lib in # list private libs here
do
	NGRS_NO_PKG_CONFIG_LIBS_PRIVATE="$NGRS_NO_PKG_CONFIG_LIBS_PRIVATE $private_lib"
done

AC_SUBST(NGRS_NO_PKG_CONFIG_CFLAGS)
AC_SUBST(NGRS_NO_PKG_CONFIG_LIBS)
AC_SUBST(NGRS_NO_PKG_CONFIG_LIBS_PRIVATE)

NGRS_PKG_CONFIG='freetype2 >= 0 xft >= 0 xcursor >= 0'

if test -n "$NGRS_PKG_CONFIG"
then
	AC_MSG_NOTICE(checking for pkg-config $NGRS_PKG_CONFIG ...)
	PKG_CHECK_MODULES(NGRS_PKG_CONFIG,    $NGRS_PKG_CONFIG)
fi
AC_SUBST(NGRS_PKG_CONFIG)

AC_SUBST(NGRS_CFLAGS, "$NGRS_NO_PKG_CONFIG_CFLAGS $NGRS_PKG_CONFIG_CFLAGS")
AC_SUBST(NGRS_LIBS,   "$NGRS_NO_PKG_CONFIG_LIBS   $NGRS_PKG_CONFIG_LIBS  ")

AC_SUBST(abs_top_srcdir)
AC_SUBST(abs_top_builddir)

AC_CONFIG_HEADERS(autotools.autoheader.private.hpp)
AC_CONFIG_FILES(
	Makefile
	src/Makefile
	doc/examples/ngrs.xml
)

AC_OUTPUT
