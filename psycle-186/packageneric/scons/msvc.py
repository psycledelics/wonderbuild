# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006-2007 johan boule <bohan@jabber.org>
# copyright 2006-2007 psycledelics http://psycle.pastnotecut.org

def detect(chain):
	from check.cxx_build import cxx_build as cxx_build_check
	msvc14 = cxx_build_check(chain.project(), name = 'msvc 14', source_text = \
		"""\
			#if _MSC_VER < 1400
				#error this is not msvc >= 14.0 (comes with IDE studio version 8.0 (2005))
			#endif
		\n"""
	)
	if msvc14.result(): msvc = msvc14
	else:
		# We don't bother checking for older versions.
		# Instead we simply make it so the msvc compiler is not detected at all,
		# and thus microsoft-specific options will not be used at all.
		msvc = msvc14 # this has the effect that msvc.result() is False since we have msvc < 14.0
	if msvc.result():
		chain.project().contexes().check_and_build().os_env().paths().add_inherited([
			'INCLUDE',
			'LIB',
			'LIBPATH' # todo which of LIB and LIBPATH is the right one?
		])
		if True:
			chain.compilers().cxx().defines().add({ # todo for mingw too!
				'STRICT': None,
				'_CRT_SECURE_NO_DEPRECATE': None,
				'NOMINMAX': None,
				'WINVER': '0x510',
				'_WIN32_WINDOWS': 'WINVER',
				'_WIN32_WINNT': 'WINVER',
				'_WIN32_IE': '0x600'
			})
		chain.compilers().cxx().flags().add([
			#'-WL', # enable one line diagnostics
			#####'-GX', # same as EHsc
			#####'-EHc', # extern "C" defaults to nothrow (GX == EHsc)
			#####'-EHs', # enable c++ exceptions handling, without structured exceptions handling (GX == EHsc)
			'-EHa', # enable c++ exceptions handling, with structured exceptions handling
			'-W4', # set warning level (min 1, max 4)
			'-Wp64', # warn about code that doesn't work on 64-bit systems
			'-Zc:forScope' # ensure scope of vars conforms to iso (not sure whether it's the default)
		])
		chain.linker().flags().add([
			'/NOASSEMBLY'
		])
		chain.linker().libraries().add([
			'kernel32.lib',
			'user32.lib',
			'gdi32.lib',
			'winspool.lib',
			'comdlg32.lib',
			'advapi32.lib',
			'shell32.lib',
			'ole32.lib',
			'oleaut32.lib',
			'uuid.lib',
			'odbc32.lib',
			'odbccp32.lib'
		])
	return msvc.result()

def implementation(chain):
	debug = chain.debug().get()
	if debug is None: debug = False

	link_library = chain.link_library().get()
	if link_library is None: link_library = False
	
	link_with_static_libraries = chain.link_with_static_libraries().get()
	if link_with_static_libraries is None: link_with_static_libraries = False

	if debug:
		chain.compilers().cxx().flags().add([
			'-Gm', # enable minimal rebuild
			'-Gy', # separate functions for linker
			'-Od', # disable optimisations
			'-fp:except', # consider floating point exceptions when generating code
			'-RTC1', # same as RTCsu (this #defines __MSVC_RUNTIME_CHECKS)
			#####'-RTCs', # enable runtime checking of stack frame (RTC1 == RTCsu) (this #defines __MSVC_RUNTIME_CHECKS)
			#####'-RTCu', # enable runtime checking of uninitialised local usage (RTC1 == RTCsu) (this #defines __MSVC_RUNTIME_CHECKS)
			'-RTCc', # enable runtime checking of conversions to smaller types (this #defines __MSVC_RUNTIME_CHECKS)
			'-ZI', # enable edit-and-continue debug info
			'-UNDEBUG'
		])
		if link_with_static_libraries:
			chain.compilers().cxx().flags().add([
				'-MTd' # link with debuggable library libcmtd.lib (static) (this does not #define _DLL. this #defines _DEBUG, like -LDd)
			])
		else:
			chain.compilers().cxx().flags().add([
				'-MDd' # link with debuggable library msvcrtd.lib (this #defines _DLL. this #defines _DEBUG, like -LDd)
			])
		chain.linker().flags().add([
		])
	else:
		chain.compilers().cxx().defines().add({
			'NDEBUG': None
		})
		chain.compilers().cxx().flags().add([
			#####'-GT', # generate fiber-safe tls accesses
			'-GL', # enable link-time code generation
			'-GF', # enable read-only string pooling
			'-GS-', # disable security checks
			'-O2', # maximize speed
			'-Ob2', # inline expansion level 2
			'-Oi', # enable intrinsic functions
			'-Op-', # keep all 80-bit intermediate results
			'-Ot', # favor code speed
			'-Oy', # enable frame pointer omission
			#####'-Op-', # this option is being removed in msvc 14
			'-fp:fast', # fast but unpredictable floating point operations
			#####'-QIfist', # not so interesting since SSE, and dangerous since it changes the behaviour of static_cast<int>
			#'-arch:SSE2', # use SSE2 CPU instructions (x86 specific)
			'-arch:SSE', # use SSE CPU instructions (x86 specific)
			#'-Zi' # enable debug info
		])
		if link_with_static_libraries:
			chain.compilers().cxx().flags().add([
				'-MT' # link with non-debuggable library libcmt.lib (static) (this does not #define _DLL. this does not #define _DEBUG, like -LD)
			])
		else:
			chain.compilers().cxx().flags().add([
				'-MD' # link with non-debuggable library msvcrt.lib (this #defines _DLL. this does not #define _DEBUG, like -LD)
			])
		chain.linker().flags().add([
			'/LTCG' # enable link-time code generation
		])
		chain.archiver().flags().add([
			'/LTCG' # enable link-time code generation
		])

	if link_library:
		chain.compilers().cxx().defines().add({
			'_WINDLL': None # dunno why the IDE defines it, we already have _DLL
		})
		if debug:
			chain.compilers().cxx().flags().add([
				'-LDd' # create a debuggable dll (this #defines _DEBUG, like -MDd and -MTd)
			])
			chain.linker().flags().add([
				'/DEBUG',
				'/INCREMENTAL'
			])
		else:
			chain.compilers().cxx().flags().add([
				'-LD' # create a dll (this does not #define _DEBUG, like -MD and -MT)
			])
			chain.linker().flags().add([
				#'/RELEASE',
				'/INCREMENTAL:NO',
				'/OPT:REF',
				'/OPT:ICF'
			])
		chain.linker().flags().add([
			'/DLL'
		])
	else:
		chain.compilers().cxx().defines().add({
		})
		chain.compilers().cxx().flags().add([
		])
		chain.archiver().flags().add([
		])
