// This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
// copyright 2002-2013 members of the psycle project http://psycle.pastnotecut.org ; johan boule <bohan@jabber.org>

///\file \brief inclusions of boost headers to be pre-compiled.

#pragma once
#include <diversalis.hpp>
#ifdef DIVERSALIS__COMPILER__FEATURE__PRE_COMPILATION // if the compiler supports pre-compilation
	DIVERSALIS__MESSAGE("pre-compiling boost headers ...")

	#include <boost/version.hpp>
	#include <boost/static_assert.hpp>
	#include <boost/filesystem/path.hpp>
	#include <boost/filesystem/operations.hpp>

	#include <boost/thread/thread.hpp>
	#include <boost/thread/condition.hpp>
	#include <boost/thread/mutex.hpp>
	#include <boost/thread/recursive_mutex.hpp>

	DIVERSALIS__MESSAGE("done pre-compiling boost headers.")
#endif
