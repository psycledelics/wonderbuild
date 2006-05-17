SUBDIRS = nested-source-packages/ngrs . src doc pixmaps

include $(top_srcdir)/init.am



EXTRA_DIST += xpsycle_SOURCES.sh
EXTRA_DIST += src/nobase_pkgversioninclude_HEADERS.sh



nobase_pkgversionexampledir = $(datadir)/doc/$(PACKAGE_TARNAME)-$(PACKAGE_VERSION)/examples
nobase_pkgversionexampledir = .xpsycle.xml .ngrs.xml



bin_PROGRAMS += xpsycle
#xpsycle_CPPFLAGS = $(AM_CPPFLAGS) ...
xpsycle_CXXFLAGS = $(AM_CXXFLAGS) $(XPSYCLE_CFLAGS)
#xpsycle_LDFLAGS = $(AM_LDFLAGS) ...
xpsycle_LDADD = $(XPSYCLE_LIBS)
xpsycle_SOURCES =
include $(srcdir)/xpsycle_SOURCES.am
