AC_PREREQ(2.59)

AC_INIT(ngrs gui toolkit, 0.0.3, natti__@users.sourceforge.net, ngrs)

AC_CONFIG_AUX_DIR(autotools.auxiliary-programs)

AM_INIT_AUTOMAKE(1.9 readme-alpha subdir-objects no-define nostdinc)
AC_PROG_LIBTOOL
AC_PROG_CXXCPP
AC_PROG_CXX
# dnl # PKG_PROG_PKG_CONFIG(0.18) # dnl # this macro doesn't exist on pre-0.15 versions

AC_PATH_X
AC_PATH_XTRA
X_LIBS="$X_PRE_LIBS $X_LIBS -lX11 $X_EXTRA_LIBS -lXpm"

AC_LANG_PUSH(C++)
AC_CHECK_LIB(m, main, M_LIBS=-lm)
AC_CHECK_LIB(dl, main, DL_LIBS=-ldl)
AC_CHECK_LIB(pthread, main, PTHREAD_CFLAGS=-D_REENTRANT && PTHREAD_LIBS=-lpthread)
AC_CHECK_LIB(xerces-c, main, XERCES_LIBS=-lxerces-c, AC_MSG_ERROR(xerces-c lib required))
AC_LANG_POP(C++)

NGRS_REQUIRES='freetype2 >= 0 xft >= 0 xcursor >= 0'
PKG_CHECK_MODULES(NGRS_PKGCONFIG, $NGRS_REQUIRES)

AC_SUBST(NGRS_REQUIRES)
AC_SUBST(NGRS_CFLAGS, "$M_CFLAGS $DL_CFLAGS $PTHREAD_CFLAGS $X_CFLAGS $XERCES_CFLAGS $NGRS_PKGCONFIG_CFLAGS")
AC_SUBST(NGRS_LIBS,   "$M_LIBS   $DL_LIBS   $PTHREAD_LIBS   $X_LIBS   $XERCES_LIBS   $NGRS_PKGCONFIG_LIBS")
AC_SUBST(NGRS_LIBS_PRIVATE)
AC_SUBST(abs_top_srcdir)
AC_SUBST(abs_top_builddir)

AC_CONFIG_HEADERS(autotools.autoheader.private.hpp)
AC_CONFIG_FILES(
	Makefile
	src/Makefile
)

AC_OUTPUT
