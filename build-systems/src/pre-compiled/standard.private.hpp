// This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
// copyright 2002-2013 members of the psycle project http://psycle.pastnotecut.org ; johan boule <bohan@jabber.org>

///\file \brief inclusions of C/C++'s standard lib headers to be pre-compiled.

#pragma once
#include <diversalis.hpp>
#ifdef DIVERSALIS__COMPILER__FEATURE__PRE_COMPILATION // if the compiler supports pre-compilation
	DIVERSALIS__MESSAGE("pre-compiling standard c++ headers ...")

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
	#if __cplusplus >= 201103L
		#include <thread>
		#include <mutex>
		#include <condition_variable>
		#include <ratio>
		#include <chrono>
	#endif

	// c headers
	#include <cassert>
	#include <cctype>
	#include <cfloat>
	//#include <ciso646>
	#include <climits>
	#include <cerrno>
	//#include <clocale>
	//#include <csetjmp>
	//#include <csignal>
	//#include <cstdarg>
	#include <cstddef>
	#include <cstdio>
	#include <cstdlib>
	#include <cstring>
	//#include <ctime>
	//#include <cwchar>
	//#include <cwctype>
	#include <cmath>
	#if __cplusplus >= 201103L
		#include <cstdint> // C1999, so not in C++1998
	#endif

	DIVERSALIS__MESSAGE("done pre-compiling standard c++ headers.")
#endif

