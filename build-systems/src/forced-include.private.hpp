// This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
// copyright 2009-2011 members of the psycle project http://psycle.pastnotecut.org

///\file \brief header whose inclusion is forced by a switch on the compiler the command line.
/// This header is meant to be included before anything else.

#pragma once

#ifndef DIVERSALIS__OS__MICROSOFT__REQUIRED_VERSION
#define DIVERSALIS__OS__MICROSOFT__REQUIRED_VERSION 0x501 // winxp. defines WINVER, _WIN32_WINDOWS, and _WIN32_NT
#endif

#ifndef BOOST_ALL_DYN_LINK
#define BOOST_ALL_DYN_LINK
#endif

#ifndef BOOST_THREAD_USE_DLL
#define BOOST_THREAD_USE_DLL
#endif

#include "setup_feature_test_macros.private.hpp"
#include "setup_warnings.private.hpp"
#include "setup_optimizations.private.hpp"

// Everything in pre-compiled headers is entirely optional,
// i.e. the include could be commented out and it should still build the same.
#include "pre-compiled.private.hpp"

