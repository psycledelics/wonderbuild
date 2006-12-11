# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006 johan boule <bohan@jabber.org>
# copyright 2006 psycledelics http://psycle.pastnotecut.org

def gnu(chain, debug):
	from check.cxx_build import cxx_build as cxx_build_check
	gnug4 = cxx_build_check(chain.project(), name = 'gnug 4', source_text = \
		"""\
			#if __GNUG__ < 4
				#error this is not gcc g++ >= 4
			#endif
		\n""" # gcc -E -dM -std=c++98 -x c++-header /dev/null | sort
	)
	if gnug4.result(): gnug = gnug3 = gnug4
	else:
		gnug3 = cxx_build_check(chain.project(), name = 'gnug 3', source_text = \
			"""\
				#if __GNUG__ < 3
					#error this is not gcc g++ >= 3
				#endif
			\n""" # gcc -E -dM -std=c++98 -x c++-header /dev/null | sort
		)
		if gnug3.result(): gnug = gnug3
		else:
			# We don't bother checking for older versions.
			# Instead we simply make it so the gnu g++ compiler is not detected at all,
			# and thus gnu-specific options will not be used at all.
			gnug = gnug3 # this has the effect that gnug.result() is False since we have gnu g++ < 3
	if gnug.result():
		build_platform = chain.project()._scons().subst('$PLATFORM')
		host_platform = build_platform # todo how does scons handle cross-compilation, if it does?
		target_platform = host_platform # todo how does scons handle cross-compilation, if it does?
		if target_platform in ('win32', 'win64', 'cygwin'): target_binary_format = 'pe'
		else: target_binary_format = 'elf'
		chain.project().trace('target binary format is ' + target_binary_format)
		chain.compilers().cxx().flags().add([
			'-pipe',
			'-fmessage-length=0',
			'-Winvalid-pch'
		])
		if gnug4.result():
			chain.compilers().cxx().flags().add([
				'-combine',
				'-Wfatal-errors' # aborts on first error
			])
		if True:
			chain.compilers().cxx().flags().add([
				'-std=c++98',
				#'-pedantic',
				'-ffor-scope',
				'-fuse-cxa-atexit',
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
				'-Wundef',
				#####'-Wshadow', # var in subscope hides var of enclosing scope or argument
				'-Wpointer-arith',
				'-Wcast-qual',
				'-Wcast-align',
				'-Wwrite-strings',
				'-Wconversion',
				#####'-Wmissing-no-return',
				#####'-Wmissing-format-attribute',
				#'-Wunreachable-code',
				'-Wno-unused-parameter',
			])
			if gnug4.result():
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
			'-Wl,--demangle'
		])
		# linker: -Bshareable alias -shared: creates a shared object
		# linker: -Bdynamic -Bstatic: modifies how following -l flags expand to filenames to link against
		# linker: one --rpath dir and/or --rpath-link dir for each -L dir (what about dll PE targets?)
		chain.linker().flags().add([
			'-Wl,-z origin', # it appears not to be needed on linux, and cygwin's ld says it doesn't know it despite it being in its manpage!
			'-Wl,--rpath=\\$$ORIGIN/../lib', # todo this is elf-specific (or even linux-specific? ... maybe you can tell, sartorius.)
			'-Wl,--rpath=$packageneric__install__lib'
		])
		if False and target_binary_format == 'elf':
			chain.linker().flags().add([
				'-Wl,--soname=xxx',
				'-Wl,--default-symver',
				'-Wl,--default-imported-symver'
			])
		if target_binary_format == 'pe':
			# --outout-def file.def
			# --out-implib file.dll.a
			# if there is no export attributes for any symbol, use --export-all-symbols
			# for import of data, use --enable-auto-import and for data with offset use --enable-runtime-pseudo-reloc, and use --enable-extra-pe-debug for debug info of thunking
			# --enable-auto-image-base: same as --image-base hash(dll file name)
			# --minor/major-image/os/subsystem-version value
			# --subsystem which:major.minor: 'which' is native|console|windows|xbox
			# --dll-search-prefix prefix: for -l, first tries with prefix before trying with 'lib'
			chain.linker().flags().add([
				'-Wl,--large-address-aware',
				'-Wl,--export-dynamic',
				'-Wl,--export-all-symbols',
				'-Wl,--enable-auto-import',
				'-Wl,--enable-runtime-pseudo-reloc',
				'-Wl,--enable-auto-image-base'
			])
			if debug:
				chain.linker().flags().add([
					'-Wl,--enable-extra-pe-debug'
				])
			# --add-std-call-alias exports stdcall symbols both as is (with @* suffix), and without
		if debug:
			chain.compilers().cxx().flags().add([
				'-UNDEBUG',
				'-O0',
				'-ggdb3',
				#'-fdiagnostics-show-option',
				#'-v'
			])
			chain.linker().flags().add([
				'-Wl,-O0'
			])
		else:
			chain.compilers().cxx().flags().add([
				'-DNDEBUG',
				'-O3',
				#'-repo',
				'-fno-enforce-eh-specs',
				'-Wpacked',
				#'-Wpadded',
				#'-Winline', # warns about explicit inline functions not inlined
				'-Wdisabled-optimization'
			])
			chain.linker().flags().add([
				'-Wl,-O3',
				'-Wl,--relax',
				'-Wl,--strip-debug'
			])
		import sys, os.path
		if chain.project()._scons().Detect('perl'): # todo we have to check for perl until our colorgcc is rewritten in python
			if sys.stdout.isatty(): chain.os_env().add({'TERM': 'packageneric--color-pipe'}) # tells our colorgcc that the pipe eventually ends up being displayed on a tty
			# We use colorgcc on the command line regardless of whether the output is a tty (teletype terminal), where we can colorise the output.
			# This is harmless since colorgcc will check again for tty,
			# and this avoids uneeded rebuild by keeps signatures of command lines the same with and without a tty.
			colorgcc = os.path.join(chain.project().packageneric_directory(), 'generic', 'scons', 'colorgcc')
			chain.os_env().add({'PACKAGENERIC__GCC': str(chain.compilers().cxx().command())})
			chain.compilers().cxx().command().set(colorgcc)
			chain.linker().command().set(colorgcc)
			try: chain.os_env().add_inherited(['HOME'])
			except KeyError: pass
		if False: # we can't do that without handling deletion of objects too
			chain.archiver().flags().add(['u', 's'])
			chain.archiver().message().set(chain.project().message('packageneric: ', 'updating objects in archive $TARGET', font = '1;35'))
			def ranlib(*args, **kw): return 'true'
			chain.archiver().indexer().command().set(ranlib)
			chain.archiver().indexer().message().set(chain.project().message('packageneric: ', 'updated symbol index table in archive $TARGET', font = '1;35'))
