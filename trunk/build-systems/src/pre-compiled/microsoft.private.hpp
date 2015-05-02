// This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
// copyright 2002-2013 members of the psycle project http://psycle.pastnotecut.org ; johan boule <bohan@jabber.org>

///\file \brief inclusions of Microsoft's specific headers to be pre-compiled.

#pragma once
#include <diversalis.hpp>
#ifdef DIVERSALIS__COMPILER__FEATURE__PRE_COMPILATION // if the compiler supports pre-compilation
	#ifdef DIVERSALIS__OS__MICROSOFT
		DIVERSALIS__MESSAGE("pre-compiling microsoft windows headers ...")

		#include <universalis/os/include_windows_without_crap.hpp>

		DIVERSALIS__MESSAGE("done pre-compiling microsoft windows headers.")
	#endif
#endif
