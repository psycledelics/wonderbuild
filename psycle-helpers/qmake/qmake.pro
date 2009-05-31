TARGET = psycle-helpers

# include the base stuff shared amongst all qmake projects.
include(../../build-systems/qmake/common.pri)

include(psycle-helpers.pri)

TEMPLATE = lib # This project builds a library.
!CONFIG(shared): CONFIG *= staticlib # Note: Since shared is in CONFIG by default, you will need to pass CONFIG-=shared on qmake's command line to build a static archive.
CONFIG *= create_prl

# remove default qmake/qt stuff we don't use
CONFIG -= qt uic lex yacc

BUILD_DIR = $$PSYCLE_HELPERS_BUILD_DIR
OBJECTS_DIR = $$BUILD_DIR # Where the .o files go.
MOC_DIR = $$BUILD_DIR # Where intermediate moc files go.
DESTDIR = $$BUILD_DIR # Where the final executable goes.

CONFIG *= precompile_header
PRECOMPILED_HEADER = $$TOP_SRC_DIR/build-systems/src/forced-include.private.hpp

sources_or_headers = \
	$$PSYCLE_HELPERS_DIR/src/psycle/helpers/abstractiff \
	$$PSYCLE_HELPERS_DIR/src/psycle/helpers/appleaiff \
	$$PSYCLE_HELPERS_DIR/src/psycle/helpers/binread \
	$$PSYCLE_HELPERS_DIR/src/psycle/helpers/datacompression \
	$$PSYCLE_HELPERS_DIR/src/psycle/helpers/dither \
	$$PSYCLE_HELPERS_DIR/src/psycle/helpers/dsp \
	$$PSYCLE_HELPERS_DIR/src/psycle/helpers/eaiff \
	$$PSYCLE_HELPERS_DIR/src/psycle/helpers/fft \
	$$PSYCLE_HELPERS_DIR/src/psycle/helpers/filter \
	$$PSYCLE_HELPERS_DIR/src/psycle/helpers/helpers \
	$$PSYCLE_HELPERS_DIR/src/psycle/helpers/math/clip \
	$$PSYCLE_HELPERS_DIR/src/psycle/helpers/math/erase_all_nans_infinities_and_denormals \
	$$PSYCLE_HELPERS_DIR/src/psycle/helpers/math/erase_denormals \
	$$PSYCLE_HELPERS_DIR/src/psycle/helpers/math/fast_unspecified_round_to_integer \
	$$PSYCLE_HELPERS_DIR/src/psycle/helpers/math \
	$$PSYCLE_HELPERS_DIR/src/psycle/helpers/math/log \
	$$PSYCLE_HELPERS_DIR/src/psycle/helpers/math/math \
	$$PSYCLE_HELPERS_DIR/src/psycle/helpers/math/pi \
	$$PSYCLE_HELPERS_DIR/src/psycle/helpers/math/remainder \
	$$PSYCLE_HELPERS_DIR/src/psycle/helpers/math/round \
	$$PSYCLE_HELPERS_DIR/src/psycle/helpers/math/sine_cosine \
	$$PSYCLE_HELPERS_DIR/src/psycle/helpers/math/sine \
	$$PSYCLE_HELPERS_DIR/src/psycle/helpers/math/sine_sequence \
	$$PSYCLE_HELPERS_DIR/src/psycle/helpers/math/truncate \
	$$PSYCLE_HELPERS_DIR/src/psycle/helpers/mersennetwister \
	$$PSYCLE_HELPERS_DIR/src/psycle/helpers/msriff \
	$$PSYCLE_HELPERS_DIR/src/psycle/helpers/riff \
	$$PSYCLE_HELPERS_DIR/src/psycle/helpers/riffwave \
	$$PSYCLE_HELPERS_DIR/src/psycle/helpers/ring_buffer \
	$$PSYCLE_HELPERS_DIR/src/psycle/helpers/scale

SOURCES_PRESERVE_PATH += $$sources(sources_or_headers)
HEADERS += $$headers(sources_or_headers)

include($$COMMON_DIR/display-vars.pri)
