unix: LIBS += -lboost_signals
else:win32 {
    PWD = $$system(echo %CD%)
    EXTERNAL_PKG_DIR = $$PWD/../external-packages
    
    BOOST_DIR = $$EXTERNAL_PKG_DIR/boost-1.33.1
    !exists($$BOOST_DIR) {
        warning("The local boost dir does not exist: $${BOOST_DIR}. Make sure you have boost libs installed.")
    } else {
        !exists($$BOOST_DIR)/include {
            warning("The boost headers are not unpacked. See the dir $${BOOST_DIR}.")
        } else {
            INCLUDEPATH += $$BOOST_DIR/include
            win32-g++ {
                !exists($$BOOST_DIR/lib-mswindows-mingw-cxxabi-1002) {
                    warning("The boost libraries are not unpacked. See the dir $${BOOST_DIR}.")
                    # remove our local include path
                    INCLUDEPATH -= $$BOOST_DIR/include
                } else {
                    LIBPATH += $$BOOST_DIR/lib-mswindows-mingw-cxxabi-1002
                }
            } else:win32-msvc {
                !exists($$BOOST_DIR/lib-mswindows-msvc-8.0-cxxabi-1400) {
                    warning("The boost libraries are not unpacked. See the dir $${BOOST_DIR}.")
                    # remove our local include path
                    INCLUDEPATH -= $$BOOST_DIR/include
                } else {
                    LIBPATH += $$BOOST_DIR/lib-mswindows-msvc-8.0-cxxabi-1400
                }
            } else {
                warning("We do not have boost libs built for your compiler. Make sure you have them installed.")
                # remove our local include path
                INCLUDEPATH -= $$BOOST_DIR/include
            }
        }
    }
    win32-g++ {
        LIBS += -llibboost_signals-mgw-mt-1_33_1
        #FIXME: is there any reason not to use the following instead?
        #LIBS += -lboost_signals-mgw-mt-1_33_1
    } else {
        #LIBS += # we can use auto linking with most other compilers
    }
}
