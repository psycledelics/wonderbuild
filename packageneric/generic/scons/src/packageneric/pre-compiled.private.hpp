// This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
// copyright 2002-2006 johan boule <bohan@jabber.org>
// copyright 2004-2006 psycledelics http://psycle.pastnotecut.org

///\file
///\brief inclusions of headers which must be pre-compiled.

#if defined PACKAGENERIC__PRE_COMPILED__INCLUDED
	#error pre-compiled headers already included
#else
	#define PACKAGENERIC__PRE_COMPILED__INCLUDED
#endif
#include <diversalis/compiler.hpp>
#if defined DIVERSALIS__COMPILER__FEATURE__PRE_COMPILATION
	#if defined DIVERSALIS__COMPILER__MICROSOFT
		#pragma message("packageneric::pre_compiled:: parsing " __FILE__)
	#endif
	#include <diversalis/diversalis.hpp>
	#include <universalis/compiler.hpp> // includes universalis' warning settings
	#if defined DIVERSALIS__COMPILER__MICROSOFT && DIVERSALIS__COMPILER__VERSION__MAJOR < 7
		#pragma warning(push, 3) // msvc6's standard libraries generate level-4 warnings... hmm, no comment
	#endif
	#define PACKAGENERIC__PRE_COMPILED__INCLUDING
	#if defined PACKAGENERIC__PRE_COMPILED__INCLUDE
		#include PACKAGENERIC__PRE_COMPILED__INCLUDE
	#else
		#include "microsoft.private.hpp"
		#include "standard.private.hpp"
		#include "posix.private.hpp"
		#include "boost.private.hpp"
	#endif
	#undef PACKAGENERIC__PRE_COMPILED__INCLUDING
	#if defined DIVERSALIS__COMPILER__MICROSOFT && DIVERSALIS__COMPILER__VERSION__MAJOR < 7
		#pragma warning(pop)
	#endif
	#if defined DIVERSALIS__COMPILER__MICROSOFT
		#pragma message("packageneric::pre_compiled:: done parsing " __FILE__)
	#endif
#endif // defined DIVERSALIS__COMPILER__FEATURE__PRE_COMPILATION
