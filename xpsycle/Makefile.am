SUBDIRS = nested-source-packages/ngrs . src

include $(top_srcdir)/init.am



EXTRA_DIST += .xpsycle.xml .ngrs.xml
EXTRA_DIST += xpsycle_SOURCES.sh
EXTRA_DIST += src/nobase_pkgversioninclude_HEADERS.sh



bin_PROGRAMS += xpsycle
#xpsycle_CPPFLAGS = $(AM_CPPFLAGS) ...
xpsycle_CXXFLAGS = $(AM_CXXFLAGS) $(XPSYCLE_CFLAGS)
#xpsycle_LDFLAGS = $(AM_LDFLAGS) ...
xpsycle_LDADD = $(XPSYCLE_LIBS)
xpsycle_SOURCES =
include $(srcdir)/xpsycle_SOURCES.am
