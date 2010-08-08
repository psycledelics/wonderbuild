// This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
// copyright 2002-2008 members of the psycle project http://psycle.pastnotecut.org ; johan boule <bohan@jabber.org>

///\file \brief inclusions of Microsoft's specific headers to be pre-compiled.

#ifndef PSYCLE__BUILD_SYSTEMS__PRE_COMPILED__MICROSOFT__INCLUDED
#define PSYCLE__BUILD_SYSTEMS__PRE_COMPILED__MICROSOFT__INCLUDED
#pragma once

#include <diversalis.hpp>
#if defined DIVERSALIS__COMPILER__FEATURE__PRE_COMPILATION // if the compiler supports pre-compilation
	#if defined DIVERSALIS__OS__MICROSOFT
		#if defined DIVERSALIS__COMPILER__MICROSOFT
			#pragma message("pre-compiling " __FILE__ " ...")
		#endif
		#include <universalis/os/include_windows_without_crap.hpp>
		#if defined DIVERSALIS__COMPILER__MICROSOFT
			#pragma message("pre-compiling " __FILE__ " ... done")
		#endif
	#endif
#endif

#endif
