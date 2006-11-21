# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006 johan boule <bohan@jabber.org>
# copyright 2006 psycledelics http://psycle.pastnotecut.org

def gnu(chain, debug):
	from check.cxx_build import cxx_build as cxx_build_check
	if cxx_build_check(chain.project(), name = 'gnug', source_text = \
		"""\
			#if !defined __GNUG__
				#error this is not gcc g++
			#endif
		\n""" # gcc -E -dM -std=c++98 -x c++-header /dev/null | sort
	).result():
		chain.compilers().cxx().flags().add([
			'-pipe',
			'-combine',
			'-fmessage-length=0',
			'-Winvalid-pch',
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
				'-Wunsafe-loop-optimizations',
				'-Wpointer-arith',
				'-Wcast-qual',
				'-Wcast-align',
				'-Wwrite-strings',
				'-Wconversion',
				#####'-Wmissing-no-return',
				#####'-Wmissing-format-attribute',
				#'-Wunreachable-code',
				'-Wvolatile-register-var',
				'-Wno-unused-parameter',
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
		if False: # for ELF target
			chain.linker().flags().add([
				'-Wl,--soname=xxx',
				'-Wl,--default-symver',
				'-Wl,--default-imported-symver'
			])
		if False: # for PE target
			# --outout-def file.def
			# --out-implib file.dll.a
			# if there is no export attributes for any symbol, use --export-all-symbols
			# for import of data, use --enable-auto-import and for data with offset use --enable-runtime-pseudo-relocs, and use --enable-extra-pe-debug for debug info of thunking
			# --enable-auto-image-base: same as --image-base hash(dll file name)
			# --minor/major-image/os/subsystem-version value
			# --subsystem which:major.minor: 'which' is native|console|windows|xbox
			# --dll-search-prefix prefix: for -l, first tries with prefix before trying with 'lib'
			chain.linker().flags().add([
				'-Wl,--large-address-aware',
				'-Wl,--export-dynamic'
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
		if sys.stdout.isatty():
			colorgcc = os.path.join('packageneric', 'generic', 'scons', 'colorgcc')
			chain.os_env().add({
				'TERM': 'packageneric--color-pipe',
				'PACKAGENERIC__GCC': str(chain.compilers().cxx().command())
			})
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
