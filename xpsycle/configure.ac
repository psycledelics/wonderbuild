AC_PREREQ(2.59)

AC_INIT(Psycle Modular Music Creation Studio (for X Window), 1.10, natti__@users.sourceforge.net, xpsycle)

AC_CONFIG_AUX_DIR(autotools.auxiliary-programs)

AM_INIT_AUTOMAKE(1.9 readme-alpha subdir-objects no-define nostdinc)
AC_DISABLE_STATIC
AC_PROG_LIBTOOL
AC_PROG_CXXCPP
AC_PROG_CXX
# dnl # PKG_PROG_PKG_CONFIG(0.18) # dnl # this macro doesn't exist on pre-0.15 versions

AC_LANG_PUSH(C++)

AC_CHECK_HEADERS(zlib.h,
	[
		AC_CHECK_LIB(z, main, Z_LIBS=-lz)
	],
	[
		AC_MSG_ERROR(z lib required)
	]
)

AC_CHECK_HEADERS(audio/audiolib.h,
	[
		AC_CHECK_LIB(audio, main,
			[
				NETAUDIO_SUPPORT=yes
				NETAUDIO_LIBS=-laudio
			]
		)
	],
	[
		NETAUDIO_SUPPORT="no (reason: netaudio lib not found)"
		AC_MSG_WARN(netaudio support will not be built)
		AC_DEFINE(XPSYCLE__NO_NETAUDIO, [], whether you don't have netaudio)
	]
)

AC_CHECK_HEADERS(dsound.h,
	[
		AC_CHECK_LIB(dsound, main,
			[
				MICROSOFT_DIRECT_SOUND_SUPPORT=yes
				MICROSOFT_DIRECT_SOUND_LIBS=-ldsound
			]
		)
	],
	[
		MICROSOFT_DIRECT_SOUND_SUPPORT="no (reason: dsound lib not found)"
		AC_MSG_WARN(microsoft direct sound support will not be built)
		AC_DEFINE(XPSYCLE__NO_MICROSOFT_DIRECT_SOUND, [], whether you don't like microsoft direct sound)
	]
)

AC_CHECK_HEADERS(asio.h,
	[
		AC_CHECK_LIB(asio, main,
			[
				STEINBERG_ASIO_SUPPORT=yes
				STEINBERG_ASIO_LIBS=-lasio
			]
		)
	],
	[
		STEINBERG_ASIO_SUPPORT="no (reason: asio lib not found)"
		AC_MSG_WARN(steinberg asio support will not be built)
		AC_DEFINE(XPSYCLE__NO_STEINBERG_ASIO, [], whether you don't like steinberg asio)
	]
)

AC_LANG_POP(C++)

for package in Z NETAUDIO MICROSOFT_DIRECT_SOUND STEINBERG_ASIO
do
	for stanza in CFLAGS LIBS
	do
		eval XPSYCLE_NO_PKG_CONFIG_$stanza=\"\$XPSYCLE_NO_PKG_CONFIG_$stanza \$${package}_$stanza\"
	done
done

for private_lib in # list private libs here
do
	XPSYCLE_NO_PKG_CONFIG_LIBS_PRIVATE="$XPSYCLE_NO_PKG_CONFIG_LIBS_PRIVATE $private_lib"
done

AC_SUBST(XPSYCLE_NO_PKG_CONFIG_CFLAGS)
AC_SUBST(XPSYCLE_NO_PKG_CONFIG_LIBS)
AC_SUBST(XPSYCLE_NO_PKG_CONFIG_LIBS_PRIVATE)

ALSA='alsa >= 1.0.8'
PKG_CHECK_MODULES(ALSA, $ALSA,
	[
		ALSA_SUPPORT=yes
		XPSYCLE_PKG_CONFIG="$XPSYCLE_PKG_CONFIG $ALSA"
	],
	[
		ALSA_SUPPORT="no (reason: $ALSA_PKG_ERRORS)"
		AC_MSG_RESULT($ALSA_SUPPORT)
		AC_MSG_WARN(alsa support will not be built)
		AC_DEFINE(XPSYCLE__NO_ALSA, [], whether you don't have alsa)
	]
)

JACK='jack >= 0.100.0'
PKG_CHECK_MODULES(JACK, $JACK,
	[
		JACK_SUPPORT=yes
		XPSYCLE_PKG_CONFIG="$XPSYCLE_PKG_CONFIG $JACK"
	],
	[
		JACK_SUPPORT="no (reason: $JACK_PKG_ERRORS)"
		AC_MSG_RESULT($JACK_SUPPORT)
		AC_MSG_WARN(jack support will not be built)
		AC_DEFINE(XPSYCLE__NO_JACK, [], whether you don't have jack)
	]
)

GSTREAMER='gstreamer-0.10 >= 0.10'
PKG_CHECK_MODULES(GSTREAMER, $GSTREAMER,
	[
		GSTREAMER_SUPPORT=yes
		XPSYCLE_PKG_CONFIG="$XPSYCLE_PKG_CONFIG $GSTREAMER"
	],
	[
		GSTREAMER_SUPPORT="no (reason: $GSTREAMER_PKG_ERRORS)"
		AC_MSG_RESULT($GSTREAMER_SUPPORT)
		AC_MSG_WARN(gstreamer support will not be built)
		AC_DEFINE(XPSYCLE__NO_GSTREAMER, [], whether you don't have gstreamer)
	]
)

ESOUND='esound >= 0'
PKG_CHECK_MODULES(ESOUND, $ESOUND,
	[
		ESOUND_SUPPORT=yes
		XPSYCLE_PKG_CONFIG="$XPSYCLE_PKG_CONFIG $ESOUND"
	],
	[
		ESOUND_SUPPORT="no (reason: $ESOUND_PKG_ERRORS)"
		AC_MSG_RESULT($ESOUND_SUPPORT)
		AC_MSG_WARN(esound support will not be built)
		AC_DEFINE(XPSYCLE__NO_ESOUND, [], whether you don't have esound)
	]
)

if test -n "$XPSYCLE_PKG_CONFIG"
then
	AC_MSG_NOTICE(checking for pkg-config $XPSYCLE_PKG_CONFIG ...)
	PKG_CHECK_MODULES(XPSYCLE_PKG_CONFIG, $XPSYCLE_PKG_CONFIG)
fi
AC_SUBST(XPSYCLE_PKG_CONFIG)

AC_CONFIG_SUBDIRS(nested-source-packages/ngrs)
NGRS_CFLAGS="\$\$(PKG_CONFIG_PATH=nested-source-packages/ngrs:\$\$PKG_CONFIG_PATH \$(PKG_CONFIG) --cflags ngrs)"
NGRS_LIBS="\$\$(PKG_CONFIG_PATH=nested-source-packages/ngrs:\$\$PKG_CONFIG_PATH \$(PKG_CONFIG) --libs ngrs)"

AC_SUBST(XPSYCLE_CFLAGS, "$NGRS_CFLAGS $XPSYCLE_NO_PKG_CONFIG_CFLAGS $XPSYCLE_PKG_CONFIG_CFLAGS")
AC_SUBST(XPSYCLE_LIBS,   "$NGRS_LIBS   $XPSYCLE_NO_PKG_CONFIG_CFLAGS $XPSYCLE_PKG_CONFIG_LIBS")

AC_SUBST(abs_top_srcdir)
AC_SUBST(abs_top_builddir)

m4_include([AC_CONFIG_FILES].ac)
m4_include([AC_CONFIG_HEADERS].ac)

XPSYCLE__INSTALL_PATHS__CONFIGURATION=$(eval echo $sysconfdir)
AC_DEFINE_UNQUOTED(XPSYCLE__INSTALL_PATHS__CONFIGURATION, "$XPSYCLE__INSTALL_PATHS__CONFIGURATION", directory where system-wide configuration is to be found)
AC_SUBST(XPSYCLE__INSTALL_PATHS__CONFIGURATION)

XPSYCLE__INSTALL_PATHS__DOC=$(eval echo $datadir)/doc/$PACKAGE_TARNAME-$PACKAGE_VERSION
AC_DEFINE_UNQUOTED(XPSYCLE__INSTALL_PATHS__DOC, "$XPSYCLE__INSTALL_PATHS__DOC", directory where documentation is to be found)
AC_SUBST(XPSYCLE__INSTALL_PATHS__DOC)

XPSYCLE__INSTALL_PATHS__PIXMAPS=$(eval echo $datadir)/pixmaps/$PACKAGE_TARNAME-$PACKAGE_VERSION
AC_DEFINE_UNQUOTED(XPSYCLE__INSTALL_PATHS__PIXMAPS, "$XPSYCLE__INSTALL_PATHS__PIXMAPS", directory where pixmaps are to be found)
AC_SUBST(XPSYCLE__INSTALL_PATHS__PIXMAPS)

XPSYCLE__INSTALL_PATHS__PLUGINS=$(echo $(eval echo $libdir) | sed "s:^NONE:$prefix:")
AC_DEFINE_UNQUOTED(XPSYCLE__INSTALL_PATHS__PLUGINS, "$XPSYCLE__INSTALL_PATHS__PLUGINS", directory where plugins are to be found)
AC_SUBST(XPSYCLE__INSTALL_PATHS__PLUGINS)

XPSYCLE__INSTALL_PATHS__PRESETS=$(eval echo $datadir)/$PACKAGE_TARNAME.plugins/presets
AC_DEFINE_UNQUOTED(XPSYCLE__INSTALL_PATHS__PRESETS, "$XPSYCLE__INSTALL_PATHS__PRESETS", directory where presets are to be found)
AC_SUBST(XPSYCLE__INSTALL_PATHS__PRESETS)

AC_OUTPUT

echo
echo ==============================================================================
echo
echo AC_PACKAGE_TARNAME AC_PACKAGE_VERSION - 'AC_PACKAGE_NAME'
echo
echo AC_PACKAGE_TARNAME has been configured to be built with the following support:
echo
echo '	'- alsa: $ALSA_SUPPORT
echo '	'- jack: $JACK_SUPPORT
echo '	'- gstreamer: $GSTREAMER_SUPPORT
echo '	'- esound: $ESOUND_SUPPORT
echo '	'- netaudio: $NETAUDIO_SUPPORT
echo '	'- microsoft direct sound: $MICROSOFT_DIRECT_SOUND_SUPPORT
echo '	'- steinberg asio: $STEINBERG_ASIO_SUPPORT
echo
echo ==============================================================================
echo
