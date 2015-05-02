TARGET = psycle-plugin-dw_filter

include(psycle-plugins.pri)

SOURCES_PRESERVE_PATH += \
	$$findFiles($$PSYCLE_PLUGINS_DIR/src/psycle/dw, dw_filter.cpp)
HEADERS += \
	$$findFiles($$PSYCLE_PLUGINS_DIR/src/psycle/plugins/dw, *dw_filter.hpp) \
	$$findFiles($$PSYCLE_PLUGINS_DIR/src/psycle/plugins/dw, *.h)

