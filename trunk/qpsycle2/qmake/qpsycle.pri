 
isEmpty(qpsycle2_included) {
        qpsycle2_included = 1
        verbose: message("qpsycle2 included")
        

        QPSYCLE_DIR = $$TOP_SRC_DIR/qpsycle2
        QPSYCLE_BUILD_DIR = $$QPSYCLE_DIR/++build
        
        INCLUDEPATH *= $$QPSYCLE_DIR/src $$TOP_SRC_DIR/psycle-core/src $$TOP_SRC_DIR/psycle-audiodrivers/src

        DEPENDPATH  *= $$QPSYCLE_DIR/src $$TOP_SRC_DIR/psycle-core/src $$TOP_SRC_DIR/psycle-audiodrivers/src

        !contains(TARGET, qpsycle2) {
                CONFIG *= link_prl
                QMAKE_LIBDIR *= $$QPSYCLE_BUILD_DIR
                LIBS *= $$linkLibs(pqsycle2)
                PRE_TARGETDEPS *= $$QPSYCLE_BUILD_DIR
        }
}
