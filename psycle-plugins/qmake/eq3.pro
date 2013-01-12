TARGET = psycle-plugin-eq3

include(psycle-plugins.pri)

SOURCES_PRESERVE_PATH += \
	$$findFiles($$PSYCLE_PLUGINS_DIR/src/psycle/plugins/druttis/eq3/, *.cpp)\
	$$findFiles($$PSYCLE_PLUGINS_DIR/src/psycle/plugins/druttis/dsp/, *.cpp)
HEADERS += \
	$$findFiles($$PSYCLE_PLUGINS_DIR/src/psycle/plugins/druttis/eq3/, *.hpp) \
	$$findFiles($$PSYCLE_PLUGINS_DIR/src/psycle/plugins/druttis/eq3/, *.h)\
	$$findFiles($$PSYCLE_PLUGINS_DIR/src/psycle/plugins/druttis/dsp/, *.hpp)\
	$$findFiles($$PSYCLE_PLUGINS_DIR/src/psycle/plugins/druttis/dsp/, *.h)


# TODO add dependency on psycle-druttis-dsp (see wonderbuild_script.py)
