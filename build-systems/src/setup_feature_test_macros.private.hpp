// This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
// copyright 1999-2013 members of the psycle project http://psycle.pastnotecut.org ; johan boule <bohan@jabber.org>

#pragma once

// http://www.gnu.org/s/hello/manual/libc/Feature-Test-Macros.html

#ifdef __GXX_EXPERIMENTAL_CXX0X__
	// http://bugs.debian.org/cgi-bin/bugreport.cgi?bug=575997
	
	// note: It's properly defined since gcc 4.6
	#define _GLIBCXX_USE_SCHED_YIELD
	
	// note: It's properly defined since gcc 4.6
	//#define _GLIBCXX_USE_NANOSLEEP
	
	//#define _GLIBCXX_USE_CLOCK_REALTIME
	//#define _GLIBCXX_USE_CLOCK_MONOTONIC
#endif
