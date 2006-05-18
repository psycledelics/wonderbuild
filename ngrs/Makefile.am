include $(top_srcdir)/init.am

SUBDIRS += . src

EXTRA_DIST += introduction.html

lib_LTLIBRARIES += libngrs.la
#libngrs_la_CPPFLAGS = $(AM_CPPFLAGS) ...
libngrs_la_CXXFLAGS = $(AM_CXXFLAGS) $(NGRS_CFLAGS)
libngrs_la_LDFLAGS = $(AM_LDFLAGS) -version-info 0:0:0
libngrs_la_LIBADD = $(NGRS_LIBS) $(NGRS_LIBS_PRIVATE)
libngrs_la_SOURCES =
include $(srcdir)/libngrs_la_SOURCES.am
EXTRA_DIST += libngrs_la_SOURCES.sh

pkgconfig_DATA += ngrs.pc
ngrs.pc: Makefile
	$(ECHO) Name: ngrs > $@ && \
	$(ECHO) Description: '$(PACKAGE_NAME)' >> $@ && \
	$(ECHO) Version: '$(PACKAGE_VERSION)' >> $@ && \
	$(ECHO) Cflags: -I'$(pkgversionincludedir)' >> $@ && \
	$(ECHO) Libs: -L'$(libdir)' -lngrs '$(NGRS_LIBS)' >> $@ && \
	$(ECHO) Libs.private: '$(NGRS_LIBS_PRIVATE)' >> $@ && \
	$(ECHO) Requires: '$(NGRS_REQUIRES)' >> $@
CLEANFILES += ngrs.pc

BUILT_SOURCES += ngrs-uninstalled.pc
ngrs-uninstalled.pc: Makefile
	$(ECHO) Name: ngrs > $@ && \
	$(ECHO) Description: '$(PACKAGE_NAME)' >> $@ && \
	$(ECHO) Version: '$(PACKAGE_VERSION)' >> $@ && \
	$(ECHO) Cflags: -I'$(abs_top_srcdir)'/src >> $@ && \
	$(ECHO) Libs: -L'$(abs_top_builddir)'/$(am__leading_dot)libs -lngrs '$(NGRS_LIBS)' >> $@ && \
	$(ECHO) Libs.private: '$(NGRS_LIBS_PRIVATE)' >> $@ && \
	$(ECHO) Requires: '$(NGRS_REQUIRES)' >> $@
CLEANFILES += ngrs-uninstalled.pc

bin_PROGRAMS += ngrs
#ngrs_CPPFLAGS = $(AM_CPPFLAGS) ...
ngrs_CXXFLAGS = $(AM_CXXFLAGS) $(NGRS_CFLAGS)
#ngrs_LDFLAGS = $(AM_LDFLAGS) ...
ngrs_LDADD = $(NGRS_LIBS) libngrs.la
ngrs_SOURCES =
ngrs_SOURCES += src/ngrs-tests/ngrs3.cpp
ngrs_SOURCES += src/ngrs-tests/ntestwindow.cpp
EXTRA_DIST += src/ngrs-tests/ntestwindow.h
