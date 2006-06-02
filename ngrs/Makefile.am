include $(top_srcdir)/init.am

SUBDIRS += . src

EXTRA_DIST += introduction.html

lib_LTLIBRARIES += libngrs.la
libngrs_la_version = 0:0:0
#libngrs_la_CPPFLAGS = $(AM_CPPFLAGS) ...
libngrs_la_CXXFLAGS = $(AM_CXXFLAGS) $(NGRS_CFLAGS)
libngrs_la_LDFLAGS = $(AM_LDFLAGS) -version-info $(libngrs_la_version)
libngrs_la_LIBADD = $(NGRS_LIBS)
libngrs_la_SOURCES =
include $(srcdir)/libngrs_la_SOURCES.am
EXTRA_DIST += libngrs_la_SOURCES.sh

pkgconfig_DATA += ngrs.pc
ngrs.pc: Makefile
	$(ECHO) Name: ngrs > $@ && \
	$(ECHO) Description: '$(PACKAGE_NAME)' >> $@ && \
	$(ECHO) Version: '$(libngrs_la_version)' from source '$(PACKAGE_VERSION)' >> $@ && \
	$(ECHO) Cflags: -I'$(pkgversionincludedir)' $(NGRS_NO_PKG_CONFIG_CFLAGS) >> $@ && \
	$(ECHO) Libs: -L'$(libdir)' -lngrs $(NGRS_NO_PKG_CONFIG_LIBS) >> $@ && \
	$(ECHO) Libs.private: $(NGRS_NO_PKG_CONFIG_LIBS_PRIVATE) >> $@ && \
	$(ECHO) Requires: '$(NGRS_PKG_CONFIG)' >> $@
CLEANFILES += ngrs.pc

BUILT_SOURCES += ngrs-uninstalled.pc
ngrs-uninstalled.pc: Makefile
	$(ECHO) Name: ngrs > $@ && \
	$(ECHO) Description: '$(PACKAGE_NAME)' >> $@ && \
	$(ECHO) Version: '$(libngrs_la_version)' from source '$(PACKAGE_VERSION)' >> $@ && \
	$(ECHO) Cflags: -I'$(abs_top_srcdir)'/src $(NGRS_NO_PKG_CONFIG_CFLAGS) >> $@ && \
	$(ECHO) Libs: -L'$(abs_top_builddir)'/$(am__leading_dot)libs -lngrs $(NGRS_NO_PKG_CONFIG_LIBS) >> $@ && \
	$(ECHO) Libs.private: $(NGRS_PKG_NO_CONFIG_LIBS_PRIVATE) >> $@ && \
	$(ECHO) Requires: '$(NGRS_PKG_CONFIG)' >> $@
CLEANFILES += ngrs-uninstalled.pc

bin_PROGRAMS += ngrs
#ngrs_CPPFLAGS = $(AM_CPPFLAGS) ...
ngrs_CXXFLAGS = $(AM_CXXFLAGS) $(NGRS_CFLAGS)
#ngrs_LDFLAGS = $(AM_LDFLAGS) ...
ngrs_LDADD = libngrs.la
ngrs_SOURCES =
ngrs_SOURCES += src/ngrs-tests/ngrs3.cpp
ngrs_SOURCES += src/ngrs-tests/ntestwindow.cpp
EXTRA_DIST += src/ngrs-tests/ntestwindow.h
