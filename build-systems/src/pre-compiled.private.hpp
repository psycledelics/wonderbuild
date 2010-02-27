// This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
// copyright 2002-2010 members of the psycle project http://psycle.pastnotecut.org ; johan boule <bohan@jabber.org>

///\file \brief inclusions of headers to be pre-compiled.

#ifndef PSYCLE__BUILD_SYSTEMS__PRE_COMPILED_PRIVATE__INCLUDED
#define PSYCLE__BUILD_SYSTEMS__PRE_COMPILED_PRIVATE__INCLUDED
#pragma once

#include <diversalis.hpp>
#if defined DIVERSALIS__COMPILER__FEATURE__PRE_COMPILATION // if the compiler supports pre-compilation

	#if defined DIVERSALIS__COMPILER__MICROSOFT
		#pragma message("pre-compiling " __FILE__ " ...")
	#endif

	#include "pre-compiled/microsoft.private.hpp"
	#include "pre-compiled/standard.private.hpp"
	#include "pre-compiled/posix.private.hpp"
	#include "pre-compiled/boost.private.hpp"

	#if defined DIVERSALIS__COMPILER__MICROSOFT
		#pragma message("pre-compiling " __FILE__ " ... done")
	#endif
#endif

#endif
