TARGET = psycle-plugin-gverb

include(psycle-plugins.pri)

SOURCES_PRESERVE_PATH += \
	$$findFiles($$PSYCLE_PLUGINS_DIR/src/psycle/plugins/gverb, *.cpp)
HEADERS += \
	$$findFiles($$PSYCLE_PLUGINS_DIR/src/psycle/plugins/gverb, *.hpp) \
	$$findFiles($$PSYCLE_PLUGINS_DIR/src/psycle/plugins/gverb, *.h)

