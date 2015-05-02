isEmpty(psycle_audiodrivers_included) {
	psycle_audiodrivers_included = 1
	verbose: message("psycle-audiodrivers included")
	
	include($$TOP_SRC_DIR/psycle-helpers/qmake/psycle-helpers.pri)

	unix {
		CONFIG *= link_pkgconfig # adds support for pkg-config via the PKG_CONFIG var

		system(pkg-config --exists gstreamer-0.10) {
			message( "pkg-config thinks gstreamer libs are available..." )
			PKGCONFIG *= gstreamer-0.10 gstreamer-plugins-base-0.10
			DEFINES *= PSYCLE__GSTREAMER_AVAILABLE # This is used in the source to determine when to include gstreamer-specific things.
		}

		system(pkg-config --exists alsa) {
			message( "pkg-config thinks alsa libs are available..." )
			PKGCONFIG *= alsa 
			DEFINES *= PSYCLE__ALSA_AVAILABLE # This is used in the source to determine when to include alsa-specific things.
		}

		system(pkg-config --exists jack) {
			message( "pkg-config thinks jack libs are available..." )
			PKGCONFIG *= jack 
			DEFINES *= PSYCLE__JACK_AVAILABLE # This is used in the source to determine when to include jack-specific things.
		}

		system(pkg-config --exists esound) {
			message( "pkg-config thinks esound libs are available..." )
			PKGCONFIG *= esound
			DEFINES *= PSYCLE__ESOUND_AVAILABLE # This is used in the source to determine when to include esound-specific things.
		}

		false { # these drivers need testing
			# FIXME: not sure how to test for netaudio...
			exists(/usr/include/audio/audiolib.h) {
				DEFINES *= PSYCLE__NET_AUDIO_AVAILABLE # This is used in the source to determine when to include net-audio-specific things.
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
				win32-g++:        LIBPATH *= $$DSOUND_DIR/lib-mswindows-mingw-cxxabi-1002
				else:win32-msvc*: LIBPATH *= $$DSOUND_DIR/lib-mswindows-msvc-cxxabi
			}
		}
		CONFIG(dsound) {
			DEFINES *= PSYCLE__MICROSOFT_DIRECT_SOUND_AVAILABLE # This is used in the source to determine when to include direct-sound-specific things.
		}

		false { # these drivers need testing
			# FIXME: not sure how to test for mme...
			message("Assuming you have microsoft mme.")
			DEFINES *= PSYCLE__MICROSOFT_MME_AVAILABLE # This is used in the source to determine when to include mme-specific things.

			# FIXME: asio needs to be built as a lib, which is rather cubersome, or embeeded into qpsycle itself, which sucks...
			message("Blergh... steinberg asio.")
			DEFINES *= PSYCLE__STEINBERG_ASIO_AVAILABLE # This is used in the source to determine when to include asio-specific things.
		}
	}

	PSYCLE_AUDIODRIVERS_DIR = $$TOP_SRC_DIR/psycle-audiodrivers
	PSYCLE_AUDIODRIVERS_BUILD_DIR = $$PSYCLE_AUDIODRIVERS_DIR/++qmake
	
	INCLUDEPATH *= $$PSYCLE_AUDIODRIVERS_DIR/src
	DEPENDPATH  *= $$PSYCLE_AUDIODRIVERS_DIR/src

	!contains(TARGET, psycle-audiodrivers) {
		CONFIG *= link_prl
		QMAKE_LIBDIR *= $$PSYCLE_AUDIODRIVERS_BUILD_DIR
		LIBS *= $$linkLibs(psycle-audiodrivers)
		PRE_TARGETDEPS *= $$PSYCLE_AUDIODRIVERS_BUILD_DIR
	}
}
