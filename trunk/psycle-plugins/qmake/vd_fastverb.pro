TARGET = psycle-plugin-vd_fastverb

include(psycle-plugins.pri)

SOURCES_PRESERVE_PATH += \
	$$findFiles($$PSYCLE_PLUGINS_DIR/src/psycle/plugins/vincenzo_demasi/vsFastVerb, *.cpp)
HEADERS += \
	$$findFiles($$PSYCLE_PLUGINS_DIR/src/psycle/plugins/vincenzo_demasi/vsFastVerb, *.hpp) \
	$$findFiles($$PSYCLE_PLUGINS_DIR/src/psycle/plugins/vincenzo_demasi/vsFastVerb, *.h)