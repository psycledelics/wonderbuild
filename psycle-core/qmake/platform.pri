# we use these c++ language features
CONFIG *= rtti exceptions threads

unix: include(platform-unix.pri)
else:win32: include(platform-win32.pri)
