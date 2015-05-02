TARGET = psycle-plugin-haas

include(psycle-plugins.pri)

SOURCES_PRESERVE_PATH += \
	$$findFiles($$PSYCLE_PLUGINS_DIR/src/psycle/plugins, haas.cpp)
HEADERS += \
	$$findFiles($$PSYCLE_PLUGINS_DIR/src/psycle/plugins, haas.hpp) \
	$$findFiles($$PSYCLE_PLUGINS_DIR/src/psycle/plugins, haas.h)

