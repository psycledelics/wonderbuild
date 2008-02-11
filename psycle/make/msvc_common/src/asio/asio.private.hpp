// -*- mode:c++; indent-tabs-mode:t -*-
// This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published b$
// copyright 2004-2007 psycledelics http://psycle.pastnotecut.org

// steinberg's headers are unable to correctly detect the platform,
// so we need to detect the platform ourselves,
// and declare steinberg's unstandard/specific options: WIN32/MAC
#include <diversalis/operating_system.hpp>

#if defined DIVERSALIS__OPERATING_SYSTEM__MICROSOFT
	#if defined _WIN64
		#error internal steinberg error (actually, it might work)
	#elif defined _WIN32
		#define WIN32 // steinberg's asio build option
	#else
		#error internal steinberg error
	#endif

	// steinberg's headers also lack some #include,
	// so we include the missing headers ourselves
	#include <objbase.h>

#elif defined DIVERSALIS__OPERATING_SYSTEM__APPLE
	#define MAC // steinberg's asio build option

#else
	#error internal steinberg error
#endif
