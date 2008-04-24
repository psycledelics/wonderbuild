PSYCLE_CORE_DIR = $$TOP_SRC_DIR/psycle-core

INCLUDEPATH *= $$PSYCLE_CORE_DIR/src
DEPENDPATH *= $$PSYCLE_COR_DIR/src

INCLUDEPATH *= $$TOP_SRC_DIR/diversalis/src
DEPENDPATH *= $$TOP_SRC_DIR/diversalis/src
INCLUDEPATH *= $$TOP_SRC_DIR/universalis/src
DEPENDPATH *= $$TOP_SRC_DIR/universalis/src

HEADERS += \
	$$PSYCLE_CORE_DIR/src/psycle/core/psycleCorePch.hpp \
	$$PSYCLE_CORE_DIR/src/psycle/core/binread.h \
	$$PSYCLE_CORE_DIR/src/psycle/core/commands.h \
	$$PSYCLE_CORE_DIR/src/psycle/core/constants.h \
	$$PSYCLE_CORE_DIR/src/psycle/core/convert_internal_machines.private.hpp \
	$$PSYCLE_CORE_DIR/src/psycle/core/cstdint.h \
	$$PSYCLE_CORE_DIR/src/psycle/core/datacompression.h \
	$$PSYCLE_CORE_DIR/src/psycle/core/dither.h \
	$$PSYCLE_CORE_DIR/src/psycle/core/dsp.h \
	$$PSYCLE_CORE_DIR/src/psycle/core/eventdriver.h \
	$$PSYCLE_CORE_DIR/src/psycle/core/file.h \
	$$PSYCLE_CORE_DIR/src/psycle/core/fileio.h \
	$$PSYCLE_CORE_DIR/src/psycle/core/filter.h \
	$$PSYCLE_CORE_DIR/src/psycle/core/filterhelper.h \
	$$PSYCLE_CORE_DIR/src/psycle/core/fwd.hpp \
	$$PSYCLE_CORE_DIR/src/psycle/core/helpers.h \
	$$PSYCLE_CORE_DIR/src/psycle/core/instpreview.h \
	$$PSYCLE_CORE_DIR/src/psycle/core/instrument.h \
	$$PSYCLE_CORE_DIR/src/psycle/core/internalhost.hpp \
	$$PSYCLE_CORE_DIR/src/psycle/core/internal_machines.h \
	$$PSYCLE_CORE_DIR/src/psycle/core/ladspa.h \
	$$PSYCLE_CORE_DIR/src/psycle/core/ladspahost.hpp \
	$$PSYCLE_CORE_DIR/src/psycle/core/ladspamachine.h \
	$$PSYCLE_CORE_DIR/src/psycle/core/machine.h \
	$$PSYCLE_CORE_DIR/src/psycle/core/machinehost.hpp \
	$$PSYCLE_CORE_DIR/src/psycle/core/machinefactory.h \
	$$PSYCLE_CORE_DIR/src/psycle/core/machinekey.hpp \
	$$PSYCLE_CORE_DIR/src/psycle/core/mersennetwister.h \
	$$PSYCLE_CORE_DIR/src/psycle/core/mixer.h \
	$$PSYCLE_CORE_DIR/src/psycle/core/nativehost.hpp \
	$$PSYCLE_CORE_DIR/src/psycle/core/patternevent.h \
	$$PSYCLE_CORE_DIR/src/psycle/core/patternline.h \
	$$PSYCLE_CORE_DIR/src/psycle/core/patternpool.h \
	$$PSYCLE_CORE_DIR/src/psycle/core/patternsequence.h \
	$$PSYCLE_CORE_DIR/src/psycle/core/player.h \
	$$PSYCLE_CORE_DIR/src/psycle/core/playertimeinfo.h \
	$$PSYCLE_CORE_DIR/src/psycle/core/plugin.h \
	$$PSYCLE_CORE_DIR/src/psycle/core/plugin_interface.h \
	$$PSYCLE_CORE_DIR/src/psycle/core/plugincatcher.h \
	$$PSYCLE_CORE_DIR/src/psycle/core/pluginfinder.h \
	$$PSYCLE_CORE_DIR/src/psycle/core/plugininfo.h \
	$$PSYCLE_CORE_DIR/src/psycle/core/preset.h \
	$$PSYCLE_CORE_DIR/src/psycle/core/psy2filter.h \
	$$PSYCLE_CORE_DIR/src/psycle/core/psy3filter.h \
	$$PSYCLE_CORE_DIR/src/psycle/core/psy4filter.h \
	$$PSYCLE_CORE_DIR/src/psycle/core/psyfilterbase.h \
	$$PSYCLE_CORE_DIR/src/psycle/core/riff.h \
	$$PSYCLE_CORE_DIR/src/psycle/core/sampler.h \
	$$PSYCLE_CORE_DIR/src/psycle/core/signalslib.h \
	$$PSYCLE_CORE_DIR/src/psycle/core/singlepattern.h \
	$$PSYCLE_CORE_DIR/src/psycle/core/songserializer.h \
	$$PSYCLE_CORE_DIR/src/psycle/core/song.h \
	$$PSYCLE_CORE_DIR/src/psycle/core/timesignature.h \
	$$PSYCLE_CORE_DIR/src/psycle/core/xminstrument.h \
	$$PSYCLE_CORE_DIR/src/psycle/core/xmsampler.h \
	$$PSYCLE_CORE_DIR/src/psycle/core/zipreader.h \
	$$PSYCLE_CORE_DIR/src/psycle/core/zipwriter.h \
	$$PSYCLE_CORE_DIR/src/psycle/core/zipwriterstream.h \
	$$PSYCLE_CORE_DIR/src/psycle/core/helpers/scale.hpp \
	$$PSYCLE_CORE_DIR/src/psycle/core/helpers/math/pi.hpp \
	$$PSYCLE_CORE_DIR/src/psycle/core/helpers/xml.h
	
SOURCES += \
	$$PSYCLE_CORE_DIR/src/psycle/core/psycleCorePch.cpp \
	$$PSYCLE_CORE_DIR/src/psycle/core/binread.cpp \
	$$PSYCLE_CORE_DIR/src/psycle/core/convert_internal_machines.cpp \
	$$PSYCLE_CORE_DIR/src/psycle/core/datacompression.cpp \
	$$PSYCLE_CORE_DIR/src/psycle/core/dither.cpp \
	$$PSYCLE_CORE_DIR/src/psycle/core/dsp.cpp \
	$$PSYCLE_CORE_DIR/src/psycle/core/eventdriver.cpp \
	$$PSYCLE_CORE_DIR/src/psycle/core/file.cpp \
	$$PSYCLE_CORE_DIR/src/psycle/core/fileio.cpp \
	$$PSYCLE_CORE_DIR/src/psycle/core/filter.cpp \
	$$PSYCLE_CORE_DIR/src/psycle/core/helpers.cpp \
	$$PSYCLE_CORE_DIR/src/psycle/core/instpreview.cpp \
	$$PSYCLE_CORE_DIR/src/psycle/core/instrument.cpp \
	$$PSYCLE_CORE_DIR/src/psycle/core/internalhost.cpp \
	$$PSYCLE_CORE_DIR/src/psycle/core/internal_machines.cpp \
	$$PSYCLE_CORE_DIR/src/psycle/core/ladspahost.cpp \
	$$PSYCLE_CORE_DIR/src/psycle/core/ladspamachine.cpp \
	$$PSYCLE_CORE_DIR/src/psycle/core/machine.cpp \
	$$PSYCLE_CORE_DIR/src/psycle/core/machinefactory.cpp \
	$$PSYCLE_CORE_DIR/src/psycle/core/machinehost.cpp \
	$$PSYCLE_CORE_DIR/src/psycle/core/machinekey.cpp \
	$$PSYCLE_CORE_DIR/src/psycle/core/mersennetwister.cpp \
	$$PSYCLE_CORE_DIR/src/psycle/core/mixer.cpp \
	$$PSYCLE_CORE_DIR/src/psycle/core/nativehost.cpp \
	$$PSYCLE_CORE_DIR/src/psycle/core/patternevent.cpp \
	$$PSYCLE_CORE_DIR/src/psycle/core/patternline.cpp \
	$$PSYCLE_CORE_DIR/src/psycle/core/patternpool.cpp \
	$$PSYCLE_CORE_DIR/src/psycle/core/patternsequence.cpp \
	$$PSYCLE_CORE_DIR/src/psycle/core/player.cpp \
	$$PSYCLE_CORE_DIR/src/psycle/core/playertimeinfo.cpp \
	$$PSYCLE_CORE_DIR/src/psycle/core/plugin.cpp \
	$$PSYCLE_CORE_DIR/src/psycle/core/plugincatcher.cpp \
	$$PSYCLE_CORE_DIR/src/psycle/core/pluginfinder.cpp \
	$$PSYCLE_CORE_DIR/src/psycle/core/plugininfo.cpp \
	$$PSYCLE_CORE_DIR/src/psycle/core/preset.cpp \
	$$PSYCLE_CORE_DIR/src/psycle/core/psy2filter.cpp \
	$$PSYCLE_CORE_DIR/src/psycle/core/psy3filter.cpp \
	$$PSYCLE_CORE_DIR/src/psycle/core/psy4filter.cpp \
	$$PSYCLE_CORE_DIR/src/psycle/core/riff.cpp \
	$$PSYCLE_CORE_DIR/src/psycle/core/sampler.cpp \
	$$PSYCLE_CORE_DIR/src/psycle/core/singlepattern.cpp \
	$$PSYCLE_CORE_DIR/src/psycle/core/song.cpp \
	$$PSYCLE_CORE_DIR/src/psycle/core/songserializer.cpp \
	$$PSYCLE_CORE_DIR/src/psycle/core/timesignature.cpp \
	$$PSYCLE_CORE_DIR/src/psycle/core/xminstrument.cpp \
	$$PSYCLE_CORE_DIR/src/psycle/core/xmsampler.cpp \
	$$PSYCLE_CORE_DIR/src/psycle/core/zipreader.cpp \
	$$PSYCLE_CORE_DIR/src/psycle/core/zipwriter.cpp \
	$$PSYCLE_CORE_DIR/src/psycle/core/zipwriterstream.cpp \
	$$PSYCLE_CORE_DIR/src/psycle/core/helpers/xml.cpp

include(boost.pri)
include(libxml++.pri)
include(zlib.pri)
