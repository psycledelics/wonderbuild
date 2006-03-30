bin_PROGRAMS = xpsycle
xpsycle_SOURCES = xpsycle.cpp mainwindow.cpp songpdlg.cpp machineview.cpp \
			patternview.cpp sequencerbar.cpp song.cpp childview.cpp global.cpp configuration.cpp \
			machine.cpp instrument.cpp datacompression.cpp inputhandler.cpp player.cpp \
			audiodriver.cpp helpers.cpp xmsampler.cpp plugin.cpp filter.cpp dsp.cpp alsaout.cpp \
			machinegui.cpp deserializer.cpp newmachine.cpp wiredlg.cpp analyzer.cpp macprop.cpp \
		framemachine.cpp wiregui.cpp masterdlg.cpp serializer.cpp patdlg.cpp

# set the include path found by configure
INCLUDES = -I/home/natti/ngrs3/src -I/usr/include/freetype2 $(all_includes)

# the library search path.
xpsycle_LDFLAGS = $(all_libraries) 
xpsycle_LDADD = -lxerces-c -ldl -lasound -L/usr/X11R6/lib -lXpm -lXrandr \
	-lXcursor -lXft -lXrender -lX11 -lm -ldl -lpthread -lfreetype \
	-L/home/natti/ngrs3/optimized/src -lngrs
noinst_HEADERS = mainwindow.h songpdlg.h machineview.h patternview.h \
			sequencerbar.h song.h childview.h global.h configuration.h Constants.h machine.h \
			instrument.h songstructs.h datacompression.h inputhandler.h player.h audiodriver.h \
			helpers.h xmsampler.h plugin.h filter.h dsp.h alsaout.h machinegui.h \
			deserializer.h plugin_interface.h newmachine.h wiredlg.h analyzer.h macprop.h \
		framemachine.h wiregui.h masterdlg.h serializer.h patdlg.h
