bin_PROGRAMS = xpsycle
xpsycle_SOURCES = xpsycle.cpp alsaout.cpp analyzer.cpp audiodriver.cpp \
		childview.cpp configuration.cpp datacompression.cpp deserializer.cpp dsp.cpp \
		filter.cpp framemachine.cpp global.cpp helpers.cpp inputhandler.cpp instrument.cpp \
		machine.cpp machinegui.cpp machineview.cpp macprop.cpp mainwindow.cpp masterdlg.cpp \
		newmachine.cpp patdlg.cpp patternview.cpp player.cpp plugin.cpp sequencerbar.cpp \
		serializer.cpp song.cpp songpdlg.cpp wiredlg.cpp wiregui.cpp xmsampler.cpp \
	defaultbitmaps.cpp greetdlg.cpp

# set the include path found by configure
INCLUDES = -I /usr/include/freetype2 -I /home/natti/ngrs3/src $(all_includes)

# the library search path.
xpsycle_LDFLAGS = $(all_libraries) 
noinst_HEADERS = alsaout.h analyzer.h audiodriver.h childview.h configuration.h \
		Constants.h datacompression.h deserializer.h dsp.h filter.h framemachine.h global.h \
		helpers.h inputhandler.h instrument.h machinegui.h machine.h machineview.h \
		macprop.h mainwindow.h masterdlg.h newmachine.h patdlg.h patternview.h player.h \
		plugin.h plugin_interface.h sequencerbar.h serializer.h song.h songpdlg.h \
		songstructs.h wiredlg.h wiregui.h xmsampler.h defaultbitmaps.h greetdlg.h
xpsycle_LDADD = -L/usr/X11R6/lib -lXrandr -lXcursor -lXft -lXrender -lX11 -lm\
	-ldl -lpthread -lfreetype -lxerces-c -lXpm -lasound\
	-L/home/natti/ngrs3/optimized/src/ -lngrs
