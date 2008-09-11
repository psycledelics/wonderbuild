TARGET = universalis

# include the base stuff shared amongst all qmake projects.
include(../../universalis/qmake/common.pri)

# this include defines a dependency on the universalis lib.
include(universalis.pri)

TEMPLATE = lib # This project builds a library.
!CONFIG(shared): CONFIG *= staticlib # Note: Since shared is in CONFIG by default, you will need to pass CONFIG-=shared on qmake's command line to build a static archive.
CONFIG *= create_prl

# remove default qmake/qt stuff we don't use
CONFIG -= qt uic lex yacc

BUILD_DIR = $$UNIVERSALIS_BUILD_DIR
OBJECTS_DIR = $$BUILD_DIR # Where the .o files go.
DESTDIR = $$BUILD_DIR # Where the final executable goes.

#CONFIG *= precompile_header
#PRECOMPILED_HEADER = $$TOP_SRC_DIR/packageneric/src/packageneric/pre-compiled.private.hpp

sources_or_headers = \
	$$UNIVERSALIS_DIR/src/universalis/compiler/cast \
	$$UNIVERSALIS_DIR/src/universalis/compiler/compiler \
	$$UNIVERSALIS_DIR/src/universalis/compiler/concatenated \
	$$UNIVERSALIS_DIR/src/universalis/compiler/detail/gnu/diagnostics \
	$$UNIVERSALIS_DIR/src/universalis/compiler/detail/gnu/typeof \
	$$UNIVERSALIS_DIR/src/universalis/compiler/detail/microsoft/assume \
	$$UNIVERSALIS_DIR/src/universalis/compiler/detail/microsoft/namespace \
	$$UNIVERSALIS_DIR/src/universalis/compiler/detail/microsoft/optimizations \
	$$UNIVERSALIS_DIR/src/universalis/compiler/detail/microsoft/property \
	$$UNIVERSALIS_DIR/src/universalis/compiler/detail/microsoft/super \
	$$UNIVERSALIS_DIR/src/universalis/compiler/detail/microsoft/warnings \
	$$UNIVERSALIS_DIR/src/universalis/compiler/detail/pragmatic/align \
	$$UNIVERSALIS_DIR/src/universalis/compiler/detail/pragmatic/asm \
	$$UNIVERSALIS_DIR/src/universalis/compiler/detail/pragmatic/attribute \
	$$UNIVERSALIS_DIR/src/universalis/compiler/detail/pragmatic/auto_link \
	$$UNIVERSALIS_DIR/src/universalis/compiler/detail/pragmatic/calling_convention \
	$$UNIVERSALIS_DIR/src/universalis/compiler/detail/pragmatic/const_function \
	$$UNIVERSALIS_DIR/src/universalis/compiler/detail/pragmatic/demangle \
	$$UNIVERSALIS_DIR/src/universalis/compiler/detail/pragmatic/deprecated \
	$$UNIVERSALIS_DIR/src/universalis/compiler/detail/pragmatic/dynamic_link \
	$$UNIVERSALIS_DIR/src/universalis/compiler/detail/pragmatic/finally \
	$$UNIVERSALIS_DIR/src/universalis/compiler/detail/pragmatic/hardware_exception \
	$$UNIVERSALIS_DIR/src/universalis/compiler/detail/pragmatic/pack \
	$$UNIVERSALIS_DIR/src/universalis/compiler/detail/pragmatic/pragmas \
	$$UNIVERSALIS_DIR/src/universalis/compiler/detail/pragmatic/thread_local_storage \
	$$UNIVERSALIS_DIR/src/universalis/compiler/detail/pragmatic/virtual \
	$$UNIVERSALIS_DIR/src/universalis/compiler/detail/pragmatic/weak \
	$$UNIVERSALIS_DIR/src/universalis/compiler/detail/standard/restrict \
	$$UNIVERSALIS_DIR/src/universalis/compiler/detail/standard/wchar_t \
	$$UNIVERSALIS_DIR/src/universalis/compiler/dynamic_link/begin \
	$$UNIVERSALIS_DIR/src/universalis/compiler/dynamic_link/end \
	$$UNIVERSALIS_DIR/src/universalis/compiler/exceptions/ellipsis \
	$$UNIVERSALIS_DIR/src/universalis/compiler \
	$$UNIVERSALIS_DIR/src/universalis/compiler/location \
	$$UNIVERSALIS_DIR/src/universalis/compiler/numeric \
	$$UNIVERSALIS_DIR/src/universalis/compiler/stringized \
	$$UNIVERSALIS_DIR/src/universalis/compiler/template_constructors \
	$$UNIVERSALIS_DIR/src/universalis/compiler/token \
	$$UNIVERSALIS_DIR/src/universalis/compiler/typenameof \
	$$UNIVERSALIS_DIR/src/universalis/compiler/virtual_factory \
	$$UNIVERSALIS_DIR/src/universalis/detail/configuration \
	$$UNIVERSALIS_DIR/src/universalis/detail/project \
	$$UNIVERSALIS_DIR/src/universalis/detail/quaquaversalis \
	$$UNIVERSALIS_DIR/src/universalis/exception \
	$$UNIVERSALIS_DIR/src/universalis/operating_system/clocks \
	$$UNIVERSALIS_DIR/src/universalis/operating_system/cpu_affinity \
	$$UNIVERSALIS_DIR/src/universalis/operating_system/detail/check_version \
	$$UNIVERSALIS_DIR/src/universalis/operating_system/detail/microsoft/max_path \
	$$UNIVERSALIS_DIR/src/universalis/operating_system/dynamic_link/main \
	$$UNIVERSALIS_DIR/src/universalis/operating_system/dynamic_link/resolver \
	$$UNIVERSALIS_DIR/src/universalis/operating_system/exception \
	$$UNIVERSALIS_DIR/src/universalis/operating_system/exceptions/code_description \
	$$UNIVERSALIS_DIR/src/universalis/operating_system \
	$$UNIVERSALIS_DIR/src/universalis/operating_system/loggers \
	$$UNIVERSALIS_DIR/src/universalis/operating_system/operating_system \
	$$UNIVERSALIS_DIR/src/universalis/operating_system/paths \
	$$UNIVERSALIS_DIR/src/universalis/operating_system/paths/implementation \
	$$UNIVERSALIS_DIR/src/universalis/operating_system/paths/injection/implementation \
	$$UNIVERSALIS_DIR/src/universalis/operating_system/paths/injection/interface \
	$$UNIVERSALIS_DIR/src/universalis/operating_system/paths/interface \
	$$UNIVERSALIS_DIR/src/universalis/operating_system/terminal \
	$$UNIVERSALIS_DIR/src/universalis/processor/atomic/compare_and_swap \
	$$UNIVERSALIS_DIR/src/universalis/processor/exception \
	$$UNIVERSALIS_DIR/src/universalis/processor/exceptions/code_description \
	$$UNIVERSALIS_DIR/src/universalis/processor/exceptions/fpu \
	$$UNIVERSALIS_DIR/src/universalis/processor \
	$$UNIVERSALIS_DIR/src/universalis/processor/processor \
	$$UNIVERSALIS_DIR/src/universalis/standard_library/allocators \
	$$UNIVERSALIS_DIR/src/universalis/standard_library/condition \
	$$UNIVERSALIS_DIR/src/universalis/standard_library/date_time \
	$$UNIVERSALIS_DIR/src/universalis/standard_library/detail/allocators \
	$$UNIVERSALIS_DIR/src/universalis/standard_library/detail/boost_xtime \
	$$UNIVERSALIS_DIR/src/universalis/standard_library/detail/duration \
	$$UNIVERSALIS_DIR/src/universalis/standard_library/detail/hiresolution_clock \
	$$UNIVERSALIS_DIR/src/universalis/standard_library/detail/iso646 \
	$$UNIVERSALIS_DIR/src/universalis/standard_library/detail/utc_time \
	$$UNIVERSALIS_DIR/src/universalis/standard_library/exceptions/code_description \
	$$UNIVERSALIS_DIR/src/universalis/standard_library \
	$$UNIVERSALIS_DIR/src/universalis/standard_library/mutex \
	$$UNIVERSALIS_DIR/src/universalis/standard_library/ndebug \
	$$UNIVERSALIS_DIR/src/universalis/standard_library/standard_library \
	$$UNIVERSALIS_DIR/src/universalis/standard_library/stdc_secure_lib \
	$$UNIVERSALIS_DIR/src/universalis/standard_library/stdint \
	$$UNIVERSALIS_DIR/src/universalis/standard_library/thread \
	$$UNIVERSALIS_DIR/src/universalis/universalis

SOURCES_PRESERVE_PATH += $$sources(sources_or_headers)
HEADERS += $$headers(sources_or_headers) \
	$$UNIVERSALIS_DIR/src/condition \
	$$UNIVERSALIS_DIR/src/date_time \
	$$UNIVERSALIS_DIR/src/mutex \
	$$UNIVERSALIS_DIR/src/cstdint \
	$$UNIVERSALIS_DIR/src/thread

include($$COMMON_DIR/display-vars.pri)
