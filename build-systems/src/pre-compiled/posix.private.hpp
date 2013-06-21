// This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
// copyright 2002-2011 members of the psycle project http://psycle.pastnotecut.org ; johan boule <bohan@jabber.org>

///\file \brief inclusions of POSIX standard headers to be pre-compiled.

#pragma once
#include <diversalis.hpp>
#ifdef DIVERSALIS__COMPILER__FEATURE__PRE_COMPILATION // if the compiler supports pre-compilation
	#ifdef DIVERSALIS__OS__POSIX
		DIVERSALIS__MESSAGE("pre-compiling ...")

		#include <sys/unistd.h>
		#include <dlfcn.h>
		#include <pthread.h>

		DIVERSALIS__MESSAGE("pre-compiling ... done")
	#endif
#endif

