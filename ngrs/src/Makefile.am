bin_PROGRAMS = ngrs3
ngrs3_SOURCES = ngrs3.cpp

# set the include path found by configure
INCLUDES = -I /usr/include/freetype2 $(all_includes)

# the library search path.
ngrs3_LDFLAGS = $(all_libraries) 
lib_LTLIBRARIES = libngrs.la
libngrs_la_LDFLAGS = -all-static


libngrs_la_SOURCES = nalignlayout.cpp napp.cpp nautoscrolllayout.cpp \
		nbevelborder.cpp nbitmap.cpp nborder.cpp nborderlayout.cpp nbutton.cpp nbuttonevent.cpp \
		ncheckbox.cpp ncheckmenuitem.cpp ncolor.cpp ncombobox.cpp nconfig.cpp \
		ncustombutton.cpp ncustomitem.cpp ncustommenuitem.cpp ndialog.cpp nedit.cpp nevent.cpp \
		nfile.cpp nfiledialog.cpp nfilelistbox.cpp nflowlayout.cpp nfont.cpp \
		nfontmetrics.cpp nfontstructure.cpp nframeborder.cpp ngradient.cpp ngraphics.cpp \
		ngridlayout.cpp ngroupbox.cpp nimage.cpp nimgfilter.cpp nisvisualcomponent.cpp \
		niswindow.cpp nitem.cpp nitemevent.cpp nkeyaccelerator.cpp nkeyevent.cpp nlabel.cpp \
		nlayout.cpp nline.cpp nlineshape.cpp nlistbox.cpp nlistlayout.cpp nmenubar.cpp \
		nmenu.cpp nmenuitem.cpp nmenuseperator.cpp nmoveable.cpp nmoveevent.cpp nnfa.cpp \
		nnotebook.cpp nobject.cpp npage.cpp npanel.cpp npngfilter.cpp npoint3d.cpp npoint.cpp \
		npopupmenu.cpp nprogressbar.cpp nrect.cpp nrectshape.cpp nruntime.cpp nscrollbar.cpp \
		nscrollbox.cpp nscrollevent.cpp nscrollslider.cpp nshape.cpp nsize.cpp nskin.cpp \
		nslider.cpp nsplashscreen.cpp nstate.cpp nsystem.cpp ntabbar.cpp ntabbook.cpp \
		ntab.cpp ntestwindow.cpp ntimer.cpp ntogglepanel.cpp ntoolbar.cpp \
		ntoolbarseparator.cpp nvisitor.cpp nvisualcomponent.cpp nvisual.cpp nwindow.cpp \
		nxpmfilter.cpp nspinbutton.cpp nspinedit.cpp nxmlparser.cpp nregexp.cpp \
		color_converter.cpp nfntstring.cpp nregion.cpp
noinst_HEADERS = nalignlayout.h napp.h nautoscrolllayout.h nbevelborder.h \
		nbitmap.h nborder.h nborderlayout.h nbuttonevent.h nbutton.h ncheckbox.h \
		ncheckmenuitem.h ncolor.h ncombobox.h nconfig.h ncustombutton.h ncustomitem.h \
		ncustommenuitem.h ndialog.h nedit.h nevent.h nfiledialog.h nfile.h nfilelistbox.h \
		nflowlayout.h nfont.h nfontmetrics.h nfontstructure.h nframeborder.h ngradient.h \
		ngraphics.h ngridlayout.h ngroupbox.h nimage.h nimgfilter.h nisvisualcomponent.h \
		niswindow.h nitemevent.h nitem.h nkeyaccelerator.h nkeyevent.h nlabel.h nlayout.h \
		nline.h nlineshape.h nlistbox.h nlistlayout.h nmenubar.h nmenu.h nmenuitem.h \
		nmenuseperator.h nmoveable.h nmoveevent.h nnfa.h nnotebook.h nobject.h npage.h npanel.h \
		npngfilter.h npoint3d.h npoint.h npopupmenu.h nprogressbar.h nrect.h nrectshape.h \
		nruntime.h nscrollbar.h nscrollbox.h nscrollevent.h nscrollslider.h nshape.h \
		nsize.h nskin.h nslider.h nsplashscreen.h nstate.h nsystem.h ntabbar.h \
		ntabbook.h ntab.h ntestwindow.h ntimer.h ntogglepanel.h ntoolbar.h \
		ntoolbarseparator.h nvisitor.h nvisualcomponent.h nvisual.h nwindow.h nxpmfilter.h \
		sigslot.h nspinbutton.h nspinedit.h nxmlparser.h nregexp.h color_converter.hpp \
	nfntstring.h nregion.h
ngrs3_LDADD = $(top_builddir)/src/libngrs.la -lXpm -lxerces-c -L/usr/X11R6/lib \
	-lXrandr -lXcursor -lXft -lXrender -lX11 -lm -ldl -lpthread -lfreetype
