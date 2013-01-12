TARGET = psycle-plugin-Phantom

include(psycle-plugins.pri)

SOURCES_PRESERVE_PATH += \
	$$findFiles($$PSYCLE_PLUGINS_DIR/src/psycle/plugins/druttis/Phantom, *.cpp)
HEADERS += \
	$$findFiles($$PSYCLE_PLUGINS_DIR/src/psycle/plugins/druttis/Phantom, *.hpp) \
	$$findFiles($$PSYCLE_PLUGINS_DIR/src/psycle/plugins/druttis/Phantom, *.h)

