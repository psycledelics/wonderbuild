TARGET = psycle-plugin-vd_allpass

include(psycle-plugins.pri)

SOURCES_PRESERVE_PATH += \
	$$findFiles($$PSYCLE_PLUGINS_DIR/src/psycle/plugins/vincenzo_demasi/vdAllPass, *.cpp)
HEADERS += \
	$$findFiles($$PSYCLE_PLUGINS_DIR/src/psycle/plugins/vincenzo_demasi/vdAllPass, *.hpp) \
	$$findFiles($$PSYCLE_PLUGINS_DIR/src/psycle/plugins/vincenzo_demasi/vdAllPass, *.h)