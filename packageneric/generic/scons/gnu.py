# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006-2007 johan boule <bohan@jabber.org>
# copyright 2006-2007 psycledelics http://psycle.pastnotecut.org

def detect(chain):
	from packageneric.pool.gnug import gnug
	gnug = gnug(chain.project())
	if gnug.result():
		chain_os_env_paths_vars = [
			'CPATH',
			'C_INCLUDE_PATH',
			'CPLUS_INCLUDE_PATH',
			'OBJC_INCLUDE_PATH',
			'LIBRARY_PATH'
		]
		#chain.project().contexes().check_and_build().os_env().paths().add_inherited(chain_os_env_paths_vars)
		chain.os_env().paths().add_inherited(chain_os_env_paths_vars)

		chain.compilers().cxx().flags().add([
			'-pipe',
			'-fmessage-length=0',
			'-Winvalid-pch'
		])
		if gnug.version().major() >= 4:
			chain.compilers().cxx().flags().add([
				'-combine',
				'-Wfatal-errors' # aborts on first error
			])
		if True:
			chain.compilers().cxx().flags().add([
				'-std=c++98',
				#'-pedantic',
				'-ffor-scope',
				'-Wall',
				'-Wctor-dtor-privacy',
				#'-Weffc++',
				#'-Wold-style-cast',
				'-Wformat=2',
				#'-Woverloaded-virtual',
				'-Winit-self',
				#'-Wmissing-include-dirs',
				'-Wswitch-default',
				'-Wswitch-enum',
				#'-Wunused-parameter', # or put '-Wno-unused-parameter' at the end
				'-Wstrict-aliasing=2',
				'-Wextra',
				'-Wfloat-equal',
				#'-Wundef',
				#####'-Wshadow', # var in subscope hides var of enclosing scope or argument
				'-Wpointer-arith',
				'-Wcast-qual',
				'-Wcast-align',
				'-Wwrite-strings',
				'-Wconversion',
				#####'-Wmissing-no-return',
				#####'-Wmissing-format-attribute',
				#'-Wunreachable-code',
				'-Wno-unused-parameter'
				#"-Werror=sequence-point" # makes undefined behavior an error. man gcc: The present implementation of this option only works for C programs.  A future implementation may also work for C++ programs.
				#"-Werror=return-type" # makes this an error.
			])
			if gnug.version().major() >= 4:
				chain.compilers().cxx().flags().add([
					'-Wunsafe-loop-optimizations',
					'-Wvolatile-register-var'
				])
		if False: # for c
			chain.compilers().cxx().flags().add([
				'-Wbad-function-cast',
				'-Wc++-compat',
				'-Wstrict-prototypes'
			])
		if False: # try to be produce a binary compatible with the c++ standard abi
			chain.compilers().cxx().flags().add([
				'-fabi=0',
				'-Wabi',
				'-Wstrict-null-sentinel'
			])
		chain.linker().flags().add([
			'-Wl,--demangle',
			#####'-Wl,--export-dynamic',
			#'-Wl,--unresolved-symbols=report-all', # default
			#'-Wl,--unresolved-symbols=ignore-in-shared-libs', # this caused a build error on the factoid host when using thread-local storage variable in shared library: undefined reference to `___tls_get_addr'
			#'-Wl,--unresolved-symbols=ignore-in-object-files',
			#'-Wl,--unresolved-symbols=ignore-all',
			#'-Wl,--warn-unresolved-symbols' # warn instead of erroring
			'-Wl,--warn-once,--warn-common'
		])
		# linker: -Bshareable alias -shared: creates a shared object
		# linker: -Bdynamic -Bstatic: modifies how following -l flags expand to filenames to link against
		if chain.project().platform_executable_format() != 'pe':
			if gnug.elf().result():
				assert chain.project().platform_executable_format() == 'elf'
				if False:
					chain.linker().flags().add([
						'-Wl,--soname=' + xxxx
					])
				chain.linker().flags().add([
					'-Wl,--default-symver,--default-imported-symver,--no-undefined-version',
					'-Wl,--enable-new-dtags'
				])
				if gnug.version().major() >= 4: # or before?
					chain.linker().flags().add([
						'-Wl,--as-needed'
					])
			# linker: one --rpath dir and/or --rpath-link dir for each -L dir
			chain.linker().flags().add([ # todo send to scons RPATH env var (chain.linker().rpaths())
				'-Wl,--rpath=\\$$ORIGIN/../lib', # todo this is elf-specific (or even linux-specific? ... maybe you can tell, sartorius.)
				'-Wl,--rpath=$packageneric__install__lib'
			])
			if gnug.version().major() >= 4:
				chain.linker().flags().add([
					'-Wl,-z origin' # marks objects (cygwin's ld says it doesn't know it despite it being in both its info node and man page!)
					#'-Wl,-z nodlopen' # marks objects as not supporting dlopening
					#'-Wl,-z defs' # marks objects, like -no-undefined, dissallows undefined symbols even in shared libraries where it is normally allowed
				])

			chain.compilers().cxx().flags().add([
				'-fuse-cxa-atexit',
		           # man gcc says:
		           # Register destructors for objects with static storage duration with the "__cxa_atexit" function rather than the "atexit" function.  This option is required for fully
		           # standards-compliant handling of static destructors, but will only work if your C library supports "__cxa_atexit".
		           # bohan says: does not work on cygwin 1.5 gcc 3.3.4, nor with mingw 3.4.2 (msvcrt)
				 # note: we're assuming the use of msvcrt's c runtime
			])
			
			# for fink on macosx
			import os
			if os.path.exists('/sw/include'): chain.compilers().cxx().paths().add(['/sw/include'])
			if os.path.exists('/sw/lib'): chain.linker().paths().add(['/sw/lib'])
			# fink's paths are not in gcc's default paths on macosx so we get paths from the os env:
			# already done above in all case: chain.os_env().paths().add_inherited(chain_os_env_paths_vars)
		else:
			# --add-std-call-alias exports stdcall symbols both as is (with @* suffix), and without
			# --outout-def file.def
			# --out-implib file.dll.a
			# if there is no export attributes for any symbol, use --export-all-symbols
			# for import of data, use --enable-auto-import and for data with offset use --enable-runtime-pseudo-reloc, and use --enable-extra-pe-debug for debug info of thunking
			# --enable-auto-image-base: same as --image-base hash(dll file name)
			# --minor/major-image/os/subsystem-version value
			# --subsystem which:major.minor: 'which' is native|console|windows|xbox
			# --dll-search-prefix prefix: for -l, first tries with prefix before trying with 'lib'
			chain.compilers().cxx().flags().add([
				'-undefine',
				#'-no-undefined'
			])
			chain.linker().flags().add([
				'-Wl,-undefine',
				#'-Wl,-no-undefined'
				'-Wl,--export-all-symbols',
				'-Wl,--enable-auto-import',
				'-Wl,--enable-runtime-pseudo-reloc',
				'-Wl,--enable-auto-image-base',
				'-Wl,--large-address-aware',
				#'-Wl,--subsystem=native',
				#'-Wl,--subsystem=windows',
				'-Wl,--subsystem=console',
				#'-Wl,--subsystem=xbox',
			])
			# -lxxx searches, in order:
			# 1) libxxx.dll.a
			# 2) xxx.dll.a
			# 3) libxxx.a (warning: this is the static lib)
			# 4) <prefix>xxx.dll (e.g. cygxxx.dll on cygwin)
			# 5) libxxx.dll
			# 6) xxx.dll
			# There is no standard location for libraries on mswindows, so we get paths from the os env:
			# already done above in all case: chain.os_env().paths().add_inherited(chain_os_env_paths_vars)

		if chain.project().platform() == 'cygwin':
			if False:
				chain.compilers().cxx().flags().add([
					'-mno-cygwin',
				])

		# -pthread(s) for posix threads (this option sets flags for both the preprocessor and linker)
		# -threads for native threads (this option sets flags for both the preprocessor and linker)
		# mingw: -mthreads (thread-safe exception handling, this adds the _MT define, and -lmingwthrd linker option)
		if gnug.mingw().result():
			chain.compilers().cxx().flags().add([
				'-mthreads' # defines _MT for thread-safe exception handling
			])
			chain.linker().flags().add([
				'-mthreads' # links with -lmingwthrd for thread-safe exception handling
			])
		else:			
			from packageneric.pool.pthread import pthread
			pthread = pthread(chain.project())
			if pthread.result():
				if chain.project().platform() == 'cygwin':
					chain.compilers().cxx().defines().add({
						'_REENTRANT': None
					})
					chain.linker().flags().add([
						'-lpthread'
					])
				else:
					chain.compilers().cxx().flags().add([
						'-pthread' # defines _REENTRANT
					])
					chain.linker().flags().add([
						'-pthread' # links with -lpthread
					])

		if chain.project()._scons().Detect('perl'): # todo we have to check for perl until our colorgcc is rewritten in python
			import tty_font
			if tty_font.ansi_term(): chain.os_env().add({'TERM': 'packageneric--color-pipe'}) # tells our colorgcc that the pipe eventually ends up being displayed on a tty
			# We use colorgcc on the command line regardless of whether the output is a tty (teletype) terminal, where we can colorise the output.
			# This is harmless since colorgcc will check again for tty (which is always false since it's piped) and for the TERM env var to see if it's 'packageneric--color-pipe',
			# and this avoids uneeded rebuild by keeping signatures of command lines the same with and without a tty.
			gcc = chain.compilers().cxx().command().get()
			if gcc is None: gcc = chain.project()._scons().subst('$CXX')
			chain.os_env().add({'PACKAGENERIC__GCC': gcc})
			chain.os_env().add_inherited(['HOME']) # colorgcc reads a config file in home dir.
			import os
			colorgcc = os.path.join(chain.project().packageneric_dir(), 'generic', 'scons', 'colorgcc')
			chain.compilers().cxx().command().set(colorgcc)
			chain.linker().command().set(colorgcc)

		if False: # we can't do that without handling deletion of objects too
			chain.archiver().flags().add(['u', 's'])
			chain.archiver().message().set(chain.project().message('packageneric: ', 'updating objects in archive $TARGET', font = '1;35'))
			def ranlib(*args, **kw): return 'true'
			chain.archiver().indexer().command().set(ranlib)
			chain.archiver().indexer().message().set(chain.project().message('packageneric: ', 'updated symbol index table in archive $TARGET', font = '1;35'))

	return gnug.result()

def implementation(chain):
	debug = chain.debug().get()
	if debug is None: debug = False

	if debug:
		chain.compilers().cxx().flags().add([
			'-O0',
			'-ggdb3',
			#'-fdiagnostics-show-option',
			#'-v',
			'-UNDEBUG'
		])
		chain.linker().flags().add([
			'-Wl,-O0'
			#'-Wl,--trace'
		])
		if False: # low-memory machine
			chain.linker().flags().add([
				'-Wl,--reduce-memory-overheads', # use less memory to link
				'-Wl,--no-keep-memory' # use less memory to link
			])
		if chain.project().platform_executable_format() == 'pe':
			chain.linker().flags().add([
				#'-Wl,--enable-extra-pe-debug'
			])
	else:
		chain.compilers().cxx().defines().add({
			'NDEBUG': None
		})
		chain.compilers().cxx().flags().add([
			'-O3',
			#'-repo',
			#'-fno-enforce-eh-specs',
				# Don't generate code to check for violation of exception specifications at runtime.  This option violates the C++ standard, but may
				# be useful for reducing code size in production builds, much like defining NDEBUG.  This does not give user code permission to
				# throw exceptions in violation of the exception specifications; the compiler will still optimize based on the specifications, so
				# throwing an unexpected exception will result in undefined behavior.
			'-Wpacked',
			#'-Wpadded',
			#'-Winline', # warns about explicit inline functions not inlined
			'-Wdisabled-optimization',
			#'-mfpmath=sse', # todo need to check for x86 or is it ignored otherwise?
			#'-msse' # -msse2 is implicit on 64-bit platforms
			#'-msse2' # -msse2 is implicit on 64-bit platforms
		])
		chain.linker().flags().add([
			'-Wl,-O3',
			'-Wl,--relax',
			'-Wl,--strip-debug',
			#####'-Wl,--strip-all',
			'-Wl,--sort-common'
		])
