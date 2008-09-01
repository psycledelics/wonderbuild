// -*- mode:c++; indent-tabs-mode:t -*-
// This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
// copyright 2002-2007 johan boule <bohan@jabber.org>
// copyright 2004-2007 psycledelics http://psycle.pastnotecut.org

///\file

#pragma once
#if !defined PACKAGENERIC__PRE_COMPILED__INCLUDING
	#error #include <packageneric/pre-compiled.private.hpp>
#endif

//////////////////////////
// boost http://boost.org
//////////////////////////

#if defined DIVERSALIS__COMPILER__MICROSOFT
	#pragma message("packageneric::pre_compiled:: parsing boost headers")
#endif
#include <boost/version.hpp>
#include <boost/static_assert.hpp>
//#include "boost/multi_array.hpp"
#include <boost/filesystem/path.hpp>
#define BOOST_THREAD_USE_DLL
#include <boost/thread/thread.hpp>
#include <boost/thread/mutex.hpp>
#include <boost/thread/recursive_mutex.hpp>
#if BOOST_VERSION == 103200
	#include <boost/thread/read_write_mutex.hpp>
#endif
#include <boost/thread/condition.hpp>
// huge include! #include <boost/spirit.hpp>
#if BOOST_VERSION >= 103301
//	#include <boost/archive/text_iarchive.hpp>
//	#include <boost/archive/text_oarchive.hpp>
	#include <boost/archive/xml_iarchive.hpp>
	#include <boost/archive/xml_oarchive.hpp>
	#if defined DIVERSALIS__COMPILER__MICROSOFT && DIVERSALIS__COMPILER__VERSION__MAJOR >= 8
		#pragma warning(push)
		#pragma warning(disable:4267) // 'argument' : conversion from 'size_t' to 'std::streamsize', possible loss of data
	#endif
//	#include <boost/archive/binary_iarchive.hpp>
//	#include <boost/archive/binary_oarchive.hpp>
	#if defined DIVERSALIS__COMPILER__MICROSOFT && DIVERSALIS__COMPILER__VERSION__MAJOR >= 8
		#pragma warning(pop)
	#endif
//	#include <boost/serialization/level.hpp>
//	#include <boost/serialization/version.hpp>
//	#include <boost/serialization/tracking.hpp>
//	#include <boost/serialization/export.hpp>
	#include <boost/serialization/nvp.hpp>
//	#include <boost/serialization/list.hpp>
	#include <boost/serialization/string.hpp>
#endif
#if defined DIVERSALIS__COMPILER__MICROSOFT
	#pragma message("packageneric::pre_compiled:: done parsing boost headers")
#endif
