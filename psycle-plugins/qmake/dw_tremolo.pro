TARGET = psycle-plugin-dw_tremolo

include(psycle-plugins.pri)

SOURCES_PRESERVE_PATH += \
	$$findFiles($$PSYCLE_PLUGINS_DIR/src/psycle/dw/tremolo, *.cpp)
HEADERS += \
	$$findFiles($$PSYCLE_PLUGINS_DIR/src/psycle/plugins/dw/tremolo, *.hpp) \
	$$findFiles($$PSYCLE_PLUGINS_DIR/src/psycle/plugins/dw/tremolo, *.h)

