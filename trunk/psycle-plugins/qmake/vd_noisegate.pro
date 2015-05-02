TARGET = psycle-plugin-vd_noisegate

include(psycle-plugins.pri)

SOURCES_PRESERVE_PATH += \
	$$findFiles($$PSYCLE_PLUGINS_DIR/src/psycle/plugins/vincenzo_demasi/vdNoiseGate, *.cpp)
HEADERS += \
	$$findFiles($$PSYCLE_PLUGINS_DIR/src/psycle/plugins/vincenzo_demasi/vdNoiseGate, *.hpp) \
	$$findFiles($$PSYCLE_PLUGINS_DIR/src/psycle/plugins/vincenzo_demasi/vdNoiseGate, *.h)