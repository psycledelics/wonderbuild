AC_PREREQ(2.59)

AC_INIT(Psycle for X Window, 1.9.8, natti__@users.sourceforge.net, xpsycle)

AC_CONFIG_AUX_DIR(autotools.auxiliary-programs)

AM_INIT_AUTOMAKE(1.9 readme-alpha subdir-objects no-define nostdinc)
AC_PROG_LIBTOOL
AC_PROG_CXXCPP
AC_PROG_CXX
# dnl # PKG_PROG_PKG_CONFIG(0.18) # dnl # this macro doesn't exist on pre-0.15 versions

XPSYCLE_REQUIRES='alsa >= 1.0.8'
echo checking for pkg-config XPSYCLE_PKG_CONFIG $XPSYCLE_REQUIRES ...
PKG_CHECK_MODULES(XPSYCLE_PKG_CONFIG, $XPSYCLE_REQUIRES)

AC_CONFIG_SUBDIRS(nested-source-packages/ngrs)
NGRS_CFLAGS="\$\$(PKG_CONFIG_PATH=nested-source-packages/ngrs:\$\$PKG_CONFIG_PATH \$(PKG_CONFIG) --cflags ngrs)"
NGRS_LIBS="\$\$(PKG_CONFIG_PATH=nested-source-packages/ngrs:\$\$PKG_CONFIG_PATH \$(PKG_CONFIG) --libs ngrs)"

AC_SUBST(XPSYCLE_REQUIRES)
AC_SUBST(XPSYCLE_CFLAGS, "$NGRS_CFLAGS $XPSYCLE_PKG_CONFIG_CFLAGS")
AC_SUBST(XPSYCLE_LIBS,   "$NGRS_LIBS   $XPSYCLE_PKG_CONFIG_LIBS")
AC_SUBST(XPSYCLE_LIBS_PRIVATE)
AC_SUBST(abs_top_srcdir)
AC_SUBST(abs_top_builddir)

AC_CONFIG_HEADERS(autotools.autoheader.private.hpp)
AC_CONFIG_HEADERS(src/xpsycle/install_paths.defines.hpp)
AC_DEFINE_UNQUOTED(XPSYCLE__INSTALL_PATHS__DOC, "$(eval echo $datadir)/doc/$PACKAGE_TARNAME-$PACKAGE_VERSION", doc dir)
AC_DEFINE_UNQUOTED(XPSYCLE__INSTALL_PATHS__PIXMAPS, "$(eval echo $datadir)/pixmaps/$PACKAGE_TARNAME-$PACKAGE_VERSION", pixmap dir)
AC_DEFINE_UNQUOTED(XPSYCLE__INSTALL_PATHS__PRESETS, "$(eval echo $datadir)/$PACKAGE_TARNAME.plugins/presets", preset dir)

AC_CONFIG_FILES(
	Makefile
	src/Makefile
	doc/Makefile
	pixmaps/Makefile
)

AC_OUTPUT
