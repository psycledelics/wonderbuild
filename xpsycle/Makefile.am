include $(top_srcdir)/init.am

SUBDIRS += nested-source-packages/ngrs . src doc pixmaps

include $(srcdir)/EXTRA_DIST.am

nobase_pkgversiondoc_DATA += README README-alpha NEWS ChangeLog TODO AUTHORS COPYING
sysconf_DATA = doc/examples/xpsycle.xml

bin_PROGRAMS += xpsycle
xpsycle_CPPFLAGS = $(AM_CPPFLAGS) -DXPSYCLE__CONFIGURATION
xpsycle_CXXFLAGS = $(AM_CXXFLAGS) $(XPSYCLE_CFLAGS)
#xpsycle_LDFLAGS = $(AM_LDFLAGS) ...
xpsycle_LDADD = $(XPSYCLE_LIBS)
xpsycle_SOURCES =
include $(srcdir)/xpsycle_SOURCES.am
