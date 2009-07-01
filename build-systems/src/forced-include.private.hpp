// This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
// copyright 2009-2009 members of the psycle project http://psycle.pastnotecut.org

///\file \brief header whose inclusion is forced by a switch on the compiler the command line.
/// This header is meant to be included before anything else.

#ifndef PSYCLE__BUILD_SYSTEMS__FORCED_INCLUDE__INCLUDED
#define PSYCLE__BUILD_SYSTEMS__FORCED_INCLUDE__INCLUDED
#pragma once

#define DIVERSALIS__OPERATING_SYSTEM__MICROSOFT__REQUIRED_VERSION 0x500 // win2k
#include <diversalis/operating_system.hpp> // defines WINVER, _WIN32_WINDOWS, and _WIN32_NT.

#if defined DIVERSALIS__OPERATING_SYSTEM__MICROSOFT
	/// tells microsoft's headers not to pollute the global namespace with min and max macros (which break a lot of libraries, including the standard c++ library!)
	#define NOMINMAX
#endif

#include <diversalis/compiler.hpp>
#if defined DIVERSALIS__COMPILER__MICROSOFT
	/// don't warn when unsecure standard functions are used
	#define _CRT_SECURE_NO_DEPRECATE
#endif

// Everything in pre-compiled headers is entirely optional,
// i.e. the include could be commented out and it should still build the same.
#include "pre-compiled.private.hpp"

#endif
