SUBDIRS = . src

include $(top_srcdir)/init.am



EXTRA_DIST += introduction.html
EXTRA_DIST += libngrs_la_SOURCES.sh
EXTRA_DIST += src/nobase_pkgversioninclude_HEADERS.sh



lib_LTLIBRARIES += libngrs.la
#libngrs_la_CPPFLAGS = $(AM_CPPFLAGS) ...
libngrs_la_CXXFLAGS = $(AM_CXXFLAGS) $(NGRS_CFLAGS)
libngrs_la_LDFLAGS = $(AM_LDFLAGS) -version-info 0:0:0
libngrs_la_LIBADD = $(NGRS_LIBS) $(NGRS_LIBS_PRIVATE)
libngrs_la_SOURCES =
include $(srcdir)/libngrs_la_SOURCES.am



pkgconfig_DATA += ngrs.pc
ngrs.pc: Makefile
	echo Name: ngrs > $@ && \
	echo Description: '$(PACKAGE_NAME)' >> $@ && \
	echo Version: '$(PACKAGE_VERSION)' >> $@ && \
	echo Cflags: -I'$(pkgversionincludedir)' >> $@ && \
	echo Libs: -L'$(libdir)' -lngrs '$(NGRS_LIBS)' >> $@ && \
	echo Libs.private: '$(NGRS_LIBS_PRIVATE)' >> $@ && \
	echo Requires: '$(NGRS_REQUIRES)' >> $@
CLEANFILES += ngrs.pc

BUILT_SOURCES += ngrs-uninstalled.pc
ngrs-uninstalled.pc: Makefile
	echo Name: ngrs > $@ && \
	echo Description: '$(PACKAGE_NAME)' >> $@ && \
	echo Version: '$(PACKAGE_VERSION)' >> $@ && \
	echo Cflags: -I'$(abs_top_srcdir)'/src >> $@ && \
	echo Libs: -L'$(abs_top_builddir)'/.libs -lngrs '$(NGRS_LIBS)' >> $@ && \
	echo Libs.private: '$(NGRS_LIBS_PRIVATE)' >> $@ && \
	echo Requires: '$(NGRS_REQUIRES)' >> $@
CLEANFILES += ngrs-uninstalled.pc



bin_PROGRAMS += ngrs3
#ngrs3_CPPFLAGS = $(AM_CPPFLAGS) ...
ngrs3_CXXFLAGS = $(AM_CXXFLAGS) $(NGRS_CFLAGS)
#ngrs3_LDFLAGS = $(AM_LDFLAGS) ...
ngrs3_LDADD = $(NGRS_LIBS) libngrs.la
ngrs3_SOURCES =
ngrs3_SOURCES += src/ngrs-tests/ngrs3.cpp
ngrs3_SOURCES += src/ngrs-tests/ntestwindow.cpp
