include $(top_srcdir)/init.am

SUBDIRS += nested-source-packages/ngrs . src doc pixmaps

pkgversionexampledir = $(datadir)/doc/$(PACKAGE_TARNAME)-$(PACKAGE_VERSION)/examples
nobase_pkgversionexample_DATA = .xpsycle.xml .ngrs.xml

bin_PROGRAMS += xpsycle
xpsycle_CPPFLAGS = $(AM_CPPFLAGS) -DXPSYCLE__CONFIGURATION
xpsycle_CXXFLAGS = $(AM_CXXFLAGS) $(XPSYCLE_CFLAGS)
#xpsycle_LDFLAGS = $(AM_LDFLAGS) ...
xpsycle_LDADD = $(XPSYCLE_LIBS)
xpsycle_SOURCES =
include $(srcdir)/xpsycle_SOURCES.am
EXTRA_DIST += xpsycle_SOURCES.sh
