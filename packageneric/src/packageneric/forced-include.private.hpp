// This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
// copyright 2009-2010 members of the psycle project http://psycle.pastnotecut.org

///\file \brief header whose inclusion is forced by a switch on the compiler the command line.
/// This header is meant to be included before anything else.

#ifndef PSYCLE__BUILD_SYSTEMS__FORCED_INCLUDE__INCLUDED
#define PSYCLE__BUILD_SYSTEMS__FORCED_INCLUDE__INCLUDED
#pragma once

#define DIVERSALIS__OS__MICROSOFT__REQUIRED_VERSION 0x501 // winXP. defines WINVER, _WIN32_WINDOWS, and _WIN32_NT

//#define BOOST_FILESYSTEM_NO_DEPRECATED

#include <universalis/compiler/setup_warnings.hpp>
#include <universalis/compiler/setup_optimizations.hpp>

// Everything in pre-compiled headers is entirely optional,
// i.e. the include could be commented out and it should still build the same.
#include "pre-compiled.private.hpp"

#endif
