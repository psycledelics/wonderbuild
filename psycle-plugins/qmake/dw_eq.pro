TARGET = psycle-plugin-dw-eq

include(psycle-plugins.pri)

SOURCES_PRESERVE_PATH += \
	$$findFiles($$PSYCLE_PLUGINS_DIR/src/psycle/plugins/dw/eq, *.cpp)
	$$findFiles($$PSYCLE_PLUGINS_DIR/src/psycle/plugins/dw, *filter.cpp)
HEADERS += \
	$$findFiles($$PSYCLE_PLUGINS_DIR/src/psycle/plugins/dw/eq, *.hpp) \
	$$findFiles($$PSYCLE_PLUGINS_DIR/src/psycle/plugins/dw/eq, *.h)
	$$findFiles($$PSYCLE_PLUGINS_DIR/src/psycle/plugins/dw, *filter.hpp) \
	$$findFiles($$PSYCLE_PLUGINS_DIR/src/psycle/plugins/dw, *filter.h)

# TODO add dependency on psycle-dw-filter (see wonderbuild_script.py)

