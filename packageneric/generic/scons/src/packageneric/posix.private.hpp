/* -*- mode:c++, indent-tabs-mode:t -*- */
// This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
// copyright 2002-2007 johan boule <bohan@jabber.org>
// copyright 2004-2007 psycledelics http://psycle.pastnotecut.org

///\file

#pragma once
#if !defined PACKAGENERIC__PRE_COMPILED__INCLUDING
	#error #include <packageneric/pre-compiled.private.hpp>
#endif

/////////
// posix
/////////

#if defined DIVERSALIS__OPERATING_SYSTEM__POSIX
	#if defined DIVERSALIS__COMPILER__MICROSOFT
		#pragma message("packageneric::pre_compiled:: parsing standard posix headers")
	#endif
	#include <sys/unistd.h>
	#if defined DIVERSALIS__COMPILER__MICROSOFT
		#pragma message("packageneric::pre_compiled:: done parsing standard posix headers")
	#endif
#endif
