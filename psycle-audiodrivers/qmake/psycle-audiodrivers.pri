isEmpty(psycle_audiodrivers_included) {
	psycle_audiodrivers_included = 1
	verbose: message("psycle-audiodrivers included")
	
	include($$COMMON_DIR/boost.pri)
	INCLUDEPATH *= $$TOP_SRC_DIR/diversalis/src
	DEPENDPATH  *= $$TOP_SRC_DIR/diversalis/src
	INCLUDEPATH *= $$TOP_SRC_DIR/universalis/src
	DEPENDPATH  *= $$TOP_SRC_DIR/universalis/src
	INCLUDEPATH *= $$TOP_SRC_DIR/psycle-helpers/src
	DEPENDPATH  *= $$TOP_SRC_DIR/psycle-helpers/src

	unix {
		CONFIG *= link_pkgconfig # adds support for pkg-config via the PKG_CONFIG var

		system(pkg-config --exists alsa) {
			message( "pkg-config thinks alsa libs are available..." )
			DEFINES *= PSYCLE__ALSA_AVAILABLE # This is used in the source to determine when to include alsa-specific things.
		}

		system(pkg-config --exists jack) {
			message( "pkg-config thinks jack libs are available..." )
			DEFINES *= PSYCLE__JACK_AVAILABLE # This is used in the source to determine when to include jack-specific things.
		}

		system(pkg-config --exists esound) {
			message( "pkg-config thinks esound libs are available..." )
			DEFINES *= PSYCLE__ESOUND_AVAILABLE # This is used in the source to determine when to include esound-specific things.
		}

		false { # gstreamer output is unfinished (we could rip the code from freepsycle, which has it complete)
			system(pkg-config --exists gstreamer) {
				message( "pkg-config thinks gstreamer libs are available..." )
				DEFINES *= PSYCLE__GSTREAMER_AVAILABLE # This is used in the source to determine when to include gstreamer-specific things.
			}
		}

		false { # note: the net audio output driver is probably not (well) polished/tested anyway. pulse through alsa is a good alternative.
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

		true { # FIXME: not sure how to test for mme...
			message("Assuming you have microsoft mme.")
			DEFINES *= PSYCLE__MICROSOFT_MME_AVAILABLE # This is used in the source to determine when to include mme-specific things.
		}

		false { # FIXME: asio needs to be built as a lib, which is rather cubersome, or embeeded into qpsycle itself, which sucks...
			message("Blergh... steinberg asio.")
			DEFINES *= PSYCLE__STEINBERG_ASIO_AVAILABLE # This is used in the source to determine when to include asio-specific things.
		}
	}

	PSYCLE_AUDIODRIVERS_DIR = $$TOP_SRC_DIR/psycle-audiodrivers
	PSYCLE_AUDIODRIVERS_BUILD_DIR = $$PSYCLE_AUDIODRIVERS_DIR/++build
	
	INCLUDEPATH *= $$PSYCLE_AUDIODRIVERS_DIR/src
	DEPENDPATH  *= $$PSYCLE_AUDIODRIVERS_DIR/src

	!contains(TARGET, psycle-audiodrivers) {
		CONFIG *= link_prl
		LIBPATH *= $$PSYCLE_AUDIODRIVERS_BUILD_DIR
		LIBS *= $$linkLibs(psycle-audiodrivers)
	}
}
