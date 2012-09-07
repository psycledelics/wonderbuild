TEMPLATE = lib # This project builds a library.

# include the base stuff shared amongst all qmake projects.
include(../../build-systems/qmake/common.pri)

include($$TOP_SRC_DIR/psycle-helpers/qmake/psycle-helpers.pri)

CONFIG *= shared # Plugins are loadable modules.

# remove default qmake/qt stuff we don't use
CONFIG -= qt uic lex yacc

PSYCLE_PLUGINS_DIR = $$TOP_SRC_DIR/psycle-plugins
PSYCLE_PLUGINS_BUILD_DIR = $$PSYCLE_PLUGINS_DIR/++qmake-build

INCLUDEPATH += $$PSYCLE_PLUGINS_DIR/src
DEPENDPATH  += $$PSYCLE_PLUGINS_DIR/src

BUILD_DIR = $$PSYCLE_PLUGINS_BUILD_DIR
OBJECTS_DIR = $$BUILD_DIR # Where the .o files go.
MOC_DIR = $$BUILD_DIR # Where intermediate moc files go.
DESTDIR = $$BUILD_DIR # Where the final executable goes.

CONFIG *= precompile_header
PRECOMPILED_HEADER = $$TOP_SRC_DIR/build-systems/src/forced-include.private.hpp

