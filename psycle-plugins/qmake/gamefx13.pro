TARGET = psycle-plugin-gamefx13

include(psycle-plugins.pri)

SOURCES_PRESERVE_PATH += \
	$$findFiles($$PSYCLE_PLUGINS_DIR/src/psycle/plugins/jme/gamefx13, *.cpp)
HEADERS += \
	$$findFiles($$PSYCLE_PLUGINS_DIR/src/psycle/plugins/jme/gamefx13, *.hpp) \
	$$findFiles($$PSYCLE_PLUGINS_DIR/src/psycle/plugins/jme/gamefx13, *.h)

