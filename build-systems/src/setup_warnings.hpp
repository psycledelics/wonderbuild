// This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
// copyright 1999-2013 members of the psycle project http://psycle.pastnotecut.org ; johan boule <bohan@jabber.org>

#pragma once
#include <diversalis.hpp>

#if defined DIVERSALIS__COMPILER__GNU

	#if DIVERSALIS__COMPILER__VERSION >= 40200 // 4.2.0
		#pragma GCC diagnostic error "-Wsequence-point"
			// Warn about code that may have undefined semantics because of violations of sequence point rules in the C and C++ standards.
			// man gcc 3.4.4 and 4.1.2: The present implementation of this option only works for C programs.  A future implementation may also work for C++ programs.

		#pragma GCC diagnostic error "-Wreturn-type"
			// Warn whenever a function is defined with a return-type that defaults to int. Also warn about any return statement with no return-value in a function whose return-type is not void.

		#pragma GCC diagnostic error "-Wuninitialized"
			// Warn if an automatic variable is used without first being initialized or if a variable may be clobbered by a setjmp call.
	#endif

#elif defined DIVERSALIS__COMPILER__MICROSOFT

	#pragma warning(push, 4) // generate level-4 (i.e. all) warnings
		// [bohan] note: we never pops this one... but there's no syntax without push.

	//////////////////////////////
	// warnings treated as errors
	//////////////////////////////
	#pragma warning(error:4662) // explicit instantiation; template-class 'X' has no definition from which to specialize X<...>
	#pragma warning(error:4150) // deletion of pointer to incomplete type 'X<...>'; no destructor called
	#pragma warning(error:4518) // storage-class or type specifier(s) unexpected here; ignored

	//////////
	// shiatz
	//////////
	#pragma warning(disable:4258) // definition from the for loop is ignored; the definition from the enclosing scope is used
	#pragma warning(disable:4673) // thrown exception type not catched
	#pragma warning(disable:4290) // c++ exception specification ignored (not yet implemented) except to indicate a function is not __declspec(nothrow)
		// "A function is declared using exception specification, which Visual C++ accepts but does not implement.
		// Code with exception specifications that are ignored during compilation may need to be
		// recompiled and linked to be reused in future versions supporting exception specifications."

	//////////
	// stupid
	//////////
	#pragma warning(disable:4251) // class 'X' needs to have dll-interface to be used by clients of class 'Y'
	#pragma warning(disable:4275) // non dll-interface class 'X' used as base for dll-interface class 'Y'"

	/////////
	// style
	/////////
	#pragma warning(disable:4554) // check operator precedence for possible error; use parentheses to clarify precedence
	#pragma warning(disable:4706) // assignment within conditional expression
	#pragma warning(disable:4127) // conditional expression is constant
	#pragma warning(disable:4100) // unreferenced formal parameter

	////////
	// cast
	////////
	#pragma warning(disable:4800) // forcing value to bool 'true' or 'false' (performance warning)
	#pragma warning(disable:4244) // conversion from 'numeric type A' to 'numeric type B', possible loss of data
	#pragma warning(disable:4018) // '<', '<=', '>', '>=' : signed/unsigned mismatch
	#pragma warning(disable:4389) // '==', '!=' : signed/unsigned mismatch
	//#pragma warning(disable:4245) // conversion from 'int' to 'unsigned int', signed/unsigned mismatch

	//////////
	// inline
	//////////
	#pragma warning(disable:4711) // selected for automatic inline expansion
	#pragma warning(disable:4710) // function was not inlined
	#pragma warning(disable:4714) // function marked as __forceinline not inlined

	/////////////////////////
	// implicit constructors
	/////////////////////////
	#pragma warning(disable:4512) // assignment operator could not be generated
	#pragma warning(disable:4511) // copy constructor could not be generated

	///////////////
	// yes, yes...
	///////////////
	#pragma warning(disable:4355) // 'this' : used in base member initializer list
	//#pragma warning(disable:4096) // '__cdecl' must be used with '...'
	#pragma warning(disable:4652) // compiler option 'link-time code generation (/GL)' inconsistent with precompiled header; current command-line option will override that defined in the precompiled header
		// see the comments about the /GL option in the optimization section
		// note:
		// since the warning is issued before the first line of code is even parsed,
		// it is not possible to disable it using a #pragma.
		// i just put it here for consistency and documentation, but you should disable it
		// using the /Wd4652 command line option to cl, or
		// in the project settings under C++ / Advanced / Disable Specific Warnings.
	#pragma warning(disable:4651) // '/DXXX' specified for pre-compiled header but not for current compilation
		// beware with this ... it is disabled because of /D_WINDLL ... otherwise it could be relevant

	// warnings about __STDC_SECURE_LIB__ and others
	// see http://www.opengroup.org/platform/single_unix_specification/uploads/40/6355/n1093.pdf
	// see http://msdn.microsoft.com/en-us/library/aa985974.aspx
#if !defined _SCL_SECURE_NO_WARNINGS
	#define _SCL_SECURE_NO_WARNINGS
#endif
#if !defined _CRT_SECURE_NO_WARNINGS
	#define _CRT_SECURE_NO_WARNINGS
#endif
#if !defined _CRT_NONSTDC_NO_WARNINGS
	#define _CRT_NONSTDC_NO_WARNINGS
#endif
   // posix is okay
	//#define _ATL_SECURE_NO_WARNINGS
	//#define _AFX_SECURE_NO_WARNINGS
#endif
