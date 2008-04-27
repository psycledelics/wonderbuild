TARGET = psycle-audiodrivers

include(../../psycle-core/qmake/common.pri)
include(psycle-audiodrivers.pri)

TEMPLATE = lib # This project builds a library.
!CONFIG(dll): CONFIG *= staticlib # make it a static archive bt default
CONFIG *= create_prl

# remove default qmake/qt stuff we don't use
CONFIG -= qt uic lex yacc

BUILD_DIR = $$PSYCLE_AUDIODRIVERS_BUILD_DIR
OBJECTS_DIR = $$BUILD_DIR # Where the .o files go.
MOC_DIR = $$BUILD_DIR # Where intermediate moc files go.
DESTDIR = $$BUILD_DIR # Where the final executable goes.

#CONFIG *= precompile_headers
#PRECOMPILED_HEADER = $$PSYCLE_AUDIODRIVERS_DIR/src/psycle/audio-drivers/psycleAudioDriversPch.hpp

HEADERS += \
	$$PSYCLE_AUDIODRIVERS_DIR/src/psycle/audiodrivers/audiodriver.h \
	$$PSYCLE_AUDIODRIVERS_DIR/src/psycle/audiodrivers/wavefileout.h
	
SOURCES += \
	$$PSYCLE_AUDIODRIVERS_DIR/src/psycle/audiodrivers/audiodriver.cpp \
	$$PSYCLE_AUDIODRIVERS_DIR/src/psycle/audiodrivers/wavefileout.cpp

unix {
	CONFIG *= link_pkgconfig # adds support for pkg-config via the PKG_CONFIG var

	system(pkg-config --exists alsa) {
		message( "pkg-config thinks alsa libs are available..." )
		PKGCONFIG *= alsa 
		DEFINES *= PSYCLE__ALSA_AVAILABLE # This is used in the source to determine when to include alsa-specific things.
		HEADERS += $$PSYCLE_AUDIODRIVERS_DIR/src/psycle/audiodrivers/alsaout.h
		SOURCES += $$PSYCLE_AUDIODRIVERS_DIR/src/psycle/audiodrivers/alsaout.cpp
	}

	system(pkg-config --exists jack) {
		message( "pkg-config thinks jack libs are available..." )
		PKGCONFIG *= jack 
		DEFINES *= PSYCLE__JACK_AVAILABLE # This is used in the source to determine when to include jack-specific things.
		HEADERS += $$PSYCLE_AUDIODRIVERS_DIR/src/psycle/audiodrivers/jackout.h
		SOURCES += $$PSYCLE_AUDIODRIVERS_DIR/src/psycle/audiodrivers/jackout.cpp 
	}

	system(pkg-config --exists esound) {
		message( "pkg-config thinks esound libs are available..." )
		PKGCONFIG *= esound
		DEFINES *= PSYCLE__ESOUND_AVAILABLE # This is used in the source to determine when to include esound-specific things.
		HEADERS += $$PSYCLE_AUDIODRIVERS_DIR/src/psycle/audiodrivers/esoundout.h
		SOURCES += $$PSYCLE_AUDIODRIVERS_DIR/src/psycle/audiodrivers/esoundout.cpp 
	}

	false { # gstreamer output is unfinished (we could rip the code from freepsycle, which has it complete)
		system(pkg-config --exists gstreamer) {
			message( "pkg-config thinks gstreamer libs are available..." )
			PKGCONFIG *= gstreamer
			DEFINES *= PSYCLE__GSTREAMER_AVAILABLE # This is used in the source to determine when to include gstreamer-specific things.
			HEADERS += $$PSYCLE_AUDIODRIVERS_DIR/src/psycle/audiodrivers/gstreamerout.h
			SOURCES += $$PSYCLE_AUDIODRIVERS_DIR/src/psycle/audiodrivers/gstreamerout.cpp 
		}
	}

	false { # note: the net audio output driver is probably not (well) polished/tested anyway. esound is a good alternative.
		# FIXME: not sure how to test for netaudio...
		exists(/usr/include/audio/audiolib.h) {
			LIBS *= -laudio
			DEFINES *= PSYCLE__NET_AUDIO_AVAILABLE # This is used in the source to determine when to include net-audio-specific things.
			HEADERS += $$PSYCLE_AUDIODRIVERS_DIR/src/psycle/audiodrivers/netaudioout.h
			SOURCES += $$PSYCLE_AUDIODRIVERS_DIR/src/psycle/audiodrivers/netaudioout.cpp
		}
	}
} else: win32 {
	exists($(DXSDK_DIR)) {
		message("Existing DXSDK_DIR is $(DXSDK_DIR)")
		INCLUDEPATH *= $(DXSDK_DIR)/include
		LIBPATH     *= $(DXSDK_DIR)/lib
		CONFIG *= dsound
	} else {
		DSOUND_DIR = $$EXTERNAL_PKG_DIR/dsound-9
		!exists($$DSOUND_DIR) {
			warning("The local dsound dir does not exist: $${DSOUND_DIR}. Make sure you have the dsound lib installed.")
			!CONFIG(dsound): message("Assuming you do not have dsound lib. Call qmake CONFIG+=dsound to enable dsound support.")
		} else {
			CONFIG += dsound
			INCLUDEPATH *= $$DSOUND_DIR/include
			win32-g++: LIBPATH *= $$DSOUND_DIR/lib-mswindows-mingw-cxxabi-1002
			else:      LIBPATH *= $$DSOUND_DIR/lib-mswindows-msvc-cxxabi
		}
	}
	CONFIG(dsound) {
		win32-g++: LIBS *= -ldsound   -luuid   -lwinmm     # is this last one needed?
		else:      LIBS *=   dsound.lib uuid.lib winmm.lib # is this last one needed?
		DEFINES *= PSYCLE__MICROSOFT_DIRECT_SOUND_AVAILABLE # This is used in the source to determine when to include direct-sound-specific things.
		HEADERS += $$PSYCLE_AUDIODRIVERS_DIR/src/psycle/audiodrivers/microsoftdirectsoundout.h
		SOURCES += $$PSYCLE_AUDIODRIVERS_DIR/src/psycle/audiodrivers/microsoftdirectsoundout.cpp
	}

	true { # FIXME: not sure how to test for mme...
		message("Assuming you have microsoft mme.")
		win32-g++: LIBS *= -lwinmm     -luuid     # is this last one needed?
		else:      LIBS *=   winmm.lib   uuid.lib # is this last one needed?
		DEFINES *= PSYCLE__MICROSOFT_MME_AVAILABLE # This is used in the source to determine when to include mme-specific things.
		HEADERS += $$PSYCLE_AUDIODRIVERS_DIR/src/psycle/audiodrivers/microsoftmmewaveout.h
		SOURCES += $$PSYCLE_AUDIODRIVERS_DIR/src/psycle/audiodrivers/microsoftmmewaveout.cpp
	}

	false { # FIXME: asio needs to be built as a lib, which is rather cubersome, or embeeded into qpsycle itself, which sucks...
		message("Blergh... steinberg asio.")
		win32-g++: LIBS *= -lasio
		else:      LIBS *=   asio.lib
		DEFINES *= PSYCLE__STEINBERG_ASIO_AVAILABLE # This is used in the source to determine when to include asio-specific things.
		HEADERS += $$PSYCLE_AUDIODRIVERS_DIR/src/psycle/audiodrivers/steinbergasioout.h
		SOURCES += $$PSYCLE_AUDIODRIVERS_DIR/src/psycle/audiodrivers/steinbergasioout.cpp
	}
}

include($$COMMON_DIR/display-vars.pri)
