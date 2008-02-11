/* -*- mode:c++, indent-tabs-mode:t -*- */
// This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
// copyright 2002-2007 johan boule <bohan@jabber.org>
// copyright 2004-2007 psycledelics http://psycle.pastnotecut.org

///\file

#pragma once
#if !defined PACKAGENERIC__PRE_COMPILED__INCLUDING
	#error #include <packageneric/pre-compiled.private.hpp>
#endif

////////////////
// c++ standard
////////////////

#if defined DIVERSALIS__COMPILER__MICROSOFT
	#pragma message("packageneric::pre_compiled:: parsing standard c++ headers")
#endif

#if defined DIVERSALIS__COMPILER__MICROSOFT
	#define _CRT_SECURE_NO_DEPRECATE
#endif

#if defined DIVERSALIS__COMPILER__MICROSOFT
	#pragma warning(push)
		#pragma warning(disable:4702) // unreachable code (was for msvc7.1, which still has problems with its own implementation of the c++ standard library)
		#include <stdexcept>
	#pragma warning(pop)
#endif

// c++ headers
#include <algorithm>
//#include <bitset>
//#include <complex>
#include <deque>
#include <exception>
#include <fstream>
#include <functional>
#include <iomanip>
//#include <ios>
//#include <iosfwd>
#include <iostream>
#include <istream>
#include <iterator>
#include <limits>
#include <list>
//#include <locale>
#include <map>
#include <memory>
#include <new>
#include <numeric>
#include <ostream>
#include <queue>
#include <set>
#include <sstream>
#include <stack>
#include <stdexcept>
#include <streambuf>
#include <string>
#include <typeinfo>
//#include <utility>
//#include <valarray>
#include <vector>

// c headers
#include <cassert>
#include <cctype>
#include <cfloat>
//#include <ciso646>
#include <climits>
#include <cerrno>
//#include <clocale>
#include <cmath>
//#include <csetjmp>
//#include <csignal>
//#include <cstdarg>
#include <cstddef>
#include <cstdint> // C1999, so not in C++1998
#include <cstdio>
#include <cstdlib>
#include <cstring>
//#include <ctime>
//#include <cwchar>
//#include <cwctype>

#if defined DIVERSALIS__COMPILER__MICROSOFT
	#pragma message("packageneric::pre_compiled:: done parsing standard c++ headers")
#endif
