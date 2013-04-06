# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2008-2011 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

isEmpty(zlib_included) {
        zlib_included = 1
        verbose: message("soxr included")

        unix | *-g++: LIBS *= $$linkLibs(soxr)
        else: *-msvc*: LIBS *= LIBS *= $$linkLibs(soxr)

        win32 {
                exists($(SOXR_DIR)) {
                        message("Existing SOXR_DIR is $(SOXR_DIR)")
                        SOXR_DIR = $(SOXR_DIR)
                        INCLUDEPATH *= $$SOXR_DIR
                        LIBPATH *= $$SOXR_DIR/lib
                } else {
                        SOXR_DIR = $$EXTERNAL_PKG_DIR/libsoxr
                        !exists($$SOXR_DIR) {
                                warning("The local soxr dir does not exist: $${SOXR_DIR}. Make sure you have soxr installed.")
                        } else {
                                INCLUDEPATH *= $$SOXR_DIR/src
                                LIBPATH *= $$SOXR_DIR/lib-mswindows-cabi
                        }
                }
        }

}
