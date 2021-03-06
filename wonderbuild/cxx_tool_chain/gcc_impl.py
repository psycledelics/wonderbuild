#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2007-2011 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

import os, errno

from wonderbuild import UserReadableException
from wonderbuild.logger import is_debug, debug, colored, out_is_dumb
from wonderbuild.signature import Sig
from wonderbuild.subprocess_wrapper import exec_subprocess, exec_subprocess_pipe

_need_sep_fix = os.sep != '/'

if os.name == 'posix':
	def _alias(orig, new):
		try: os.remove(new.path)
		except OSError, e:
			if e.errno != errno.ENOENT: raise
		os.symlink(orig.rel_path(new.parent), new.path)
else: # when cross-compiling from windows
	import shutils
	def _alias(orig, new):
		try: os.remove(new.path)
		except OSError, e:
			if e.errno != errno.ENOENT: raise
		shutil.copy2(orig.path, new.path)

def _colorgcc(cfg):
	# note: clang already does colorisation
	if not out_is_dumb and not cfg.impl.kind_is_clang:
		cfg.project.fs.cur.lock.acquire()
		try: return ((cfg.project.fs.cur / __file__).parent / 'colorgcc-arg')
		finally: cfg.project.fs.cur.lock.release()
	else: return None
	
class Impl(object):

	@staticmethod
	def parse_version(out, err):
		v = out.rstrip('\n').split('.')
		v[-1] = v[-1].split('-')[0]
		return tuple(int(i) for i in v)

	@staticmethod
	def progs(cfg):
		cxx_prog, ld_prog = \
			cfg.cxx_prog or 'g++', \
			cfg.ld_prog or cfg.cxx_prog or 'g++'
		return cxx_prog, ld_prog, 'ar', 'ranlib' # for gnu ar, 'ar s' is used instead of ranlib
		# see also g++ -print-prog-name=ld, g++ -Wl,--version
		
	@property
	def common_env_sig(self):
		try: return self._common_env_sig
		except AttributeError:
			sig = Sig()
			# for LIBRARY_PATH, see http://www.mingw.org/wiki/LibraryPathHOWTO
			for name in (
				'LD_LIBRARY_PATH', # linux/solaris/macosx
				'DYLD_LIBRARY_PATH', 'DYLD_FALLBACK_LIBRARY_PATH', # macosx
				'SHLIB_PATH', # hpux
				'LIBPATH', # aix
				'GCC_EXEC_PREFIX', 'COMPILER_PATH',
				'LIBRARY_PATH' # used by both the compiler and the linker according to man page
			):
				e = os.environ.get(name, None)
				if e is not None: sig.update(name + '=' + e)
			sig = self._common_env_sig = sig.digest()
			return sig

	@property
	def cxx_env_sig(self):
		try: return self._cxx_env_sig
		except AttributeError:
			sig = Sig()
			for name in ('CPATH', 'CPLUS_INCLUDE_PATH', 'C_INCLUDE_PATH'):
				e = os.environ.get(name, None)
				if e is not None: sig.update(name + '=' + e)
			sig = self._cxx_env_sig = sig.digest()
			return sig

	@staticmethod
	def client_cfg_cxx_args(cfg, prefix_var):
		args = []
		for k, v in cfg.defines.iteritems():
			if v is None: args.append('-D' + k)
			else: args.append('-D' + k + '=' + repr(str(v))[1:-1]) # note: assumes that cpp and python escaping work the same way
		for p in cfg.include_paths:
			path = p.rel_path(cfg.fhs.prefix, allow_abs_path=False)
			if path == os.curdir: path = prefix_var
			else: path = prefix_var + os.sep + path
			args.append('-I' + path)
		if cfg.dest_platform.os == 'darwin':
			for f in cfg.frameworks: args.append('-F' + f)
		args += cfg.cxx_flags
		return args

	@staticmethod
	def cfg_cxx_args(cfg):
		args = [cfg.cxx_prog, '-pipe']
		if cfg.pic and cfg.dest_platform.pic_flag_defines_pic: args.append('-fPIC')
		for k, v in cfg.defines.iteritems():
			if v is None: args.append('-D' + k)
			else: args.append('-D' + k + '=' + repr(str(v))[1:-1]) # note: assumes that cpp and python escaping work the same way
		if cfg.pch is not None: args += ['-Winvalid-pch', '-include', cfg.bld_rel_path(cfg.pch)]
		for i in cfg.includes: args += ['-include', cfg.bld_rel_path(i)]
		for p in cfg.include_paths: args.append('-I' + cfg.bld_rel_path_or_abs_path(p))
		if cfg.dest_platform.os == 'darwin':
			for f in cfg.frameworks: args.append('-F' + f)
		args += cfg.cxx_flags
		#if __debug__ and is_debug: debug('cfg: cxx: impl: gcc: cxx: ' + str(args))
		return args
		
	@staticmethod
	def _read_dep_file(dep_file_path, lock, cwd, first_is_dummy=False):
		"reads deps from the .d files generated as side-effect of compilation by gcc's -MD or -MMD option"
		f = open(dep_file_path, 'r')
		try: deps = f.read().replace('\\\n', '')
		finally: f.close()
		deps = deps[deps.find(':') + 1:]
		if _need_sep_fix: deps = deps.replace('\\\\', '/')
		deps = deps.replace('\\ ', '\\') # temporarily replace spaces so that split() works
		if first_is_dummy:
			# We skip the first implicit dep, which is the dummy actual source.
			deps = deps.split()[1:]
		else:
			deps = deps.split()
		deps = [d.replace('\\', ' ') for d in deps] # put back spaces that where temporarily removed for split() to work
		if _need_sep_fix: deps = [d.replace('/', os.sep) for d in deps]
		lock.acquire()
		try: cwd = cwd.canonical_node; deps = [cwd / d for d in deps]
		finally: lock.release()
		if __debug__ and is_debug: debug('cpp: gcc dep file: ' + dep_file_path + ': ' + str([str(d) for d in deps]))
		return deps

	@staticmethod
	def process_precompile_task(precompile_task, lock):
		# some useful options: -Wmissing-include-dirs -Winvalid-pch -H -fpch-deps -Wp,-v
		# to print the include search path: g++ -xc++ /dev/null -E -Wp,-v 2>&1 1>/dev/null | sed -e '/^[^ ]/d' -e 's,^ ,-I,'
		cwd = precompile_task.target_dir
		args = precompile_task.cfg.cxx_args + ['-MD', '-x' + precompile_task.cfg.lang + '-header', precompile_task.header.rel_path(cwd)]
		colorgcc = _colorgcc(precompile_task.cfg)
		if colorgcc is not None: args = [colorgcc.rel_path(cwd)] + args
		use_dir = False
		if not use_dir:
			dep_file = (precompile_task.target_dir / (precompile_task.header.name[:precompile_task.header.name.rfind('.')] + '.d'))
			# that's the default path anyway
			if False: args.append('-MF' + dep_file.rel_path(cwd)) 
		else:
			dir = precompile_task.target
			dir.make_dir()
			o = dir / 'x'
			args.append('-o' + o.rel_path(cwd))
			dep_file = o.parent / (o.name + '.d')
		if exec_subprocess(args, cwd=cwd.path) != 0: raise UserReadableException, precompile_task
		return Impl._read_dep_file(dep_file.path, lock, cwd)

	def precompile_task_target_name(self, header_name): return header_name + self.precompile_task_target_ext

	@property
	def precompile_task_target_ext(self): return '.gch'

	def process_cxx_task(self, cxx_task, lock):
		cwd = cxx_task.target_dir
		args = cxx_task.cfg.cxx_args + ['-MMD', '-c'] + [cxx_task.cfg.bld_rel_name_or_abs_path(p) for p in cxx_task._actual_sources]
		if False: # TODO clang cannot write that in batch mode!
			if cxx_task.cfg.impl.kind_is_clang:
				args += ['-MJcompile_commands.json']
		colorgcc = _colorgcc(cxx_task.cfg)
		if colorgcc is not None: args = [colorgcc.rel_path(cwd)] + args
		implicit_deps = cxx_task.persistent_implicit_deps
		if exec_subprocess(args, cwd=cwd.path) == 0:
			succeeded_sources = zip(cxx_task.sources, cxx_task._actual_sources)
			failed_sources = None
		else:
			# We check whether each object exists to determine which sources were compiled successfully,
			# so that theses are not rebuilt the next time.
			succeeded_sources = []
			failed_sources = []
			lock.acquire()
			try:
				cwd.clear()
				cwd.actual_children # not needed, just an optimisation
				for s in zip(cxx_task.sources, cxx_task._actual_sources):
					obj = cwd / (s[1].name[:s[1].name.rfind('.')] + self.cxx_task_target_ext)
					obj.clear()
					if obj.exists: succeeded_sources.append(s)
					else:
						src = s[0]
						failed_sources.append(src)
						try: had_failed, old_cxx_sig, deps, old_dep_sig = implicit_deps[src]
						except KeyError: implicit_deps[src] = True, None, None, None # This is a new source.
						else: implicit_deps[src] = True, old_cxx_sig, deps, old_dep_sig
			finally: lock.release()
		for s in succeeded_sources:
			path = s[1].path
			deps = Impl._read_dep_file(path[:path.rfind('.')] + '.d', lock, cwd, first_is_dummy=True)
			# <kluge>
			# The dep file contains the original source s[0] as the second dep,
			# but it may be a different node instance because of the cwd.canonical_node call in read_dep_file.
			# This would result in s[0] from not being signed/used, hence purged, while stored in the persistent pickle, which should never happen.
			# We can either do s[0].sig or replace deps[0] with s[0].
			deps[0] = s[0]
			# </kluge>
			dep_sigs = [d.sig for d in deps]
			implicit_deps[s[0]] = False, cxx_task.cfg.cxx_sig, deps, Sig(''.join(dep_sigs)).digest()
		if failed_sources is not None: raise UserReadableException, '  '.join(str(s) for s in failed_sources)

	@property
	def cxx_task_target_ext(self): return '.o'
		
	@property
	def common_mod_env_sig(self): return ''

	@property
	def ar_ranlib_env_sig(self): return ''

	@property
	def ld_env_sig(self): # gcc -print-search-dirs ; ld --verbose | grep SEARCH_DIR | tr -s ' ;' \\012
		try: return self._ld_env_sig
		except AttributeError:
			sig = Sig()
			for name in (
				'GNUTARGET', 'LDEMULATION', 'COLLECT_NO_DEMANGLE',
				'LD_RUN_PATH', # for elf native linker
				'LD_LIBRARY_PATH' # for native linker
			):
				e = os.environ.get(name, None)
				if e is not None: sig.update(name + '=' + e)
			sig = self._ld_env_sig = sig.digest()
			return sig

	@staticmethod
	def client_cfg_ld_args(cfg, prefix_var):
		args = []
		for p in cfg.lib_paths:
			path = p.rel_path(cfg.fhs.prefix, allow_abs_path=False)
			if path == os.curdir: path = prefix_var
			else: path = prefix_var + os.sep + path
			args.append('-L' + path)
		for l in cfg.libs: args.append('-l' + l)
		if len(cfg.static_libs) != 0:
			args.append('-Wl,-Bstatic')
			for l in cfg.static_libs: args.append('-l' + l)
		if len(cfg.shared_libs) != 0:
			args.append('-Wl,-Bdynamic')
			for l in cfg.shared_libs: args.append('-l' + l)
		if cfg.dest_platform.os == 'darwin':
			for f in cfg.frameworks: args += ['-framework', f]
		args += cfg.ld_flags
		return args

	@staticmethod
	def cfg_ld_args(cfg):
		args = [cfg.ld_prog]
		if cfg.shared: args.append(cfg.dest_platform.bin_fmt == 'mac-o' and '-dynamiclib' or '-shared')
		elif cfg.static_prog: args.append('-static') # we can have both -shared and -static but that's not very useful
		if cfg.dest_platform.bin_fmt == 'elf':
			# we use fhs.lib and fhs.bin here but we could use mod_task.target.parent and fhs.bin
			rpath = '-Wl,-rpath=$ORIGIN' + os.sep + cfg.fhs.lib.rel_path(cfg.fhs.bin)
			if _need_sep_fix: rpath = rpath.replace('\\', '/') # when cross-compiling from windows
			args.append(rpath)
			args.append('-Wl,-rpath-link=' + cfg.bld_rel_path(cfg.fhs.lib))
		for p in cfg.lib_paths: args.append('-L' + cfg.bld_rel_path(p))
		for l in cfg.libs: args.append('-l' + l)
		if len(cfg.static_libs) != 0:
			args.append('-Wl,-Bstatic')
			for l in cfg.static_libs: args.append('-l' + l)
		if len(cfg.shared_libs) != 0:
			args.append('-Wl,-Bdynamic')
			for l in cfg.shared_libs: args.append('-l' + l)
		if cfg.dest_platform.os == 'darwin':
			for f in cfg.frameworks: args += ['-framework', f]
		args += cfg.ld_flags
		#if __debug__ and is_debug: debug('cfg: cxx: impl: gcc: ld: ' + str(args))
		return args

	@staticmethod
	def cfg_ar_ranlib_args(cfg):
		ar_args = [cfg.ar_prog, 'rcsD']
		#if __debug__ and is_debug: debug('cfg: cxx: impl: gcc: ar: ' + str(ar_args))
		if True: return ar_args, None # We use the s option in gnu ar to do the same as ranlib.
		else:
			ranlib_args = [cfg.ranlib_prog]
			#if __debug__ and is_debug: debug('cfg: cxx: impl: gcc: ranlib: ' + str(ranlib_args))
			return ar_args, ranlib_args

	@staticmethod
	def process_mod_task(mod_task, obj_names, removed_obj_names):
		cwd = mod_task.obj_dir
		obj_paths = obj_names
		mod_task_target_path = mod_task.target.rel_path(cwd)
		if mod_task.ld:
			args = [mod_task.cfg.ld_args[0]] + obj_paths + mod_task.cfg.ld_args[1:] + ['-o', mod_task_target_path]
			colorgcc = _colorgcc(mod_task.cfg)
			if colorgcc is not None: args = [colorgcc.rel_path(cwd)] + args
			if mod_task.cfg.dest_platform.bin_fmt == 'elf':
				args.append('-Wl,--as-needed')
				if mod_task.kind != mod_task.Kinds.PROG:
					# soname and symlinks
					link_node = mod_task.target_dev_dir / ('lib' + mod_task.name + '.so')
					elf_so_name_node = mod_task.target_dir / (link_node.name + '.' + str(mod_task.version_interface))
					args.append('-Wl,-h,' + elf_so_name_node.name)
			elif mod_task.cfg.dest_platform.bin_fmt == 'pe':
				args.append('-Wl,--enable-auto-import') # suppress informational messages
				if False and mod_task.cfg.shared: # mingw doesn't need import libs
					args.append('-Wl,--out-implib,' + (mod_task.target_dev_dir / ('lib' + mod_task.name + '.dll.a')).rel_path(cwd))
			if exec_subprocess(args, cwd=cwd.path) != 0:
				if mod_task.cfg.dest_platform.bin_fmt == 'elf' and mod_task.kind != mod_task.Kinds.PROG:
					# remove dangling symlinks
					for x in (link_node, elf_so_name_node):
						try: os.remove(x.path)
						except OSError, e:
							if e.errno != errno.ENOENT: raise
				raise UserReadableException, mod_task
			if mod_task.cfg.dest_platform.bin_fmt == 'elf' and mod_task.kind != mod_task.Kinds.PROG:
				# symlinks
				_alias(mod_task.target, elf_so_name_node)
				_alias(elf_so_name_node, link_node)
		else:
			ar_args, ranlib_args = mod_task.cfg.ar_ranlib_args
			if len(obj_names) != 0:
				args = ar_args[:]
				if removed_obj_names is not None: args[1] = args[1].replace('s', '')
				args.append(mod_task_target_path)
				args += obj_paths
				if exec_subprocess(args, cwd=cwd.path) != 0: raise UserReadableException, mod_task
			if removed_obj_names is not None:
				args = [ar_args[0], ranlib_args is None and 'ds' or 'd', mod_task_target_path] + removed_obj_names
				if exec_subprocess(args, cwd=cwd.path) != 0: raise UserReadableException, mod_task
			if ranlib_args is not None: # 's' not in ar_args[1]
				args = ranlib_args[:]
				args.append(mod_task_target_path)
				if exec_subprocess(args, cwd=cwd.path) != 0: raise UserReadableException, mod_task

	@staticmethod
	def mod_task_targets(mod_task):
		if mod_task.kind == mod_task.Kinds.PROG or not mod_task.ld: return (mod_task.target,)
		elif mod_task.cfg.dest_platform.bin_fmt == 'elf':
			link_name = 'lib' + mod_task.name + '.so'
			return (
				mod_task.target,
				mod_task.target_dir / (link_name + '.' + str(mod_task.version_interface)),
				mod_task.target_dev_dir / link_name
			)
		elif mod_task.cfg.dest_platform.bin_fmt == 'pe':
			if False: # mingw doesn't need import libs
				implib = mod_task.target_dev_dir / 'lib' + mod_task.name + '.dll.a' 
				return mod_task.target, implib
			else: return (mod_task.target,)
		else: return (mod_task.target,)

	@staticmethod
	def mod_task_target_dev_dir(mod_task):
		if mod_task.cfg.shared and mod_task.cfg.dest_platform.bin_fmt == 'pe':
			return mod_task.cfg.fhs.bin # mingw doesn't need import libs
		else: return mod_task.cfg.fhs.lib

	@staticmethod
	def mod_task_target_dev_name(mod_task):
		if mod_task.ld:
			if mod_task.cfg.dest_platform.bin_fmt == 'pe':
				if False: return 'lib' + mod_task.name + '.dll.a' # mingw doesn't need import libs
				else: return 'lib' + mod_task.name + '.dll'
			else: return mod_task.name
		else: return mod_task.name

	@staticmethod
	def mod_task_target_dir(mod_task):
		if mod_task.kind == mod_task.Kinds.PROG or \
			mod_task.cfg.shared and mod_task.cfg.dest_platform.bin_fmt == 'pe': return mod_task.cfg.fhs.bin
		else: return mod_task.cfg.fhs.lib

	@staticmethod
	def mod_task_target_name(mod_task):
		if mod_task.kind == mod_task.Kinds.PROG:
			if mod_task.cfg.dest_platform.bin_fmt == 'pe': return mod_task.name + '.exe'
			else: return mod_task.name
		elif mod_task.cfg.shared:
			if mod_task.cfg.dest_platform.bin_fmt == 'pe': return mod_task.name + '.dll'
			elif mod_task.cfg.dest_platform.bin_fmt == 'mac-o': return 'lib' + mod_task.name + '.dylib'
			else: return 'lib' + mod_task.name + '.so.' + \
				str(mod_task.version_interface) + '.' + \
				str(mod_task.version_interface - mod_task.version_interface_min) + '.' + \
				str(mod_task.version_impl)
		else: return 'lib' + mod_task.name + '.a'

	@staticmethod
	def process_build_check_task(build_check_task):
		cwd = build_check_task.bld_dir
		cfg = build_check_task.cfg
		args = cfg.cxx_args + ['-x' + cfg.lang, '-']
		if build_check_task.pipe_preproc: args.append('-E')
		else:
			# When cross-compiling from linux to windows: /dev/null: final close failed: Inappropriate ioctl for device.
			# If -MD or -MMD is passed by the user with --cxx-flags, this will try and fail to create a /dev/null.d file.
			if os.name == 'posix' and not cfg.dest_platform.bin_fmt == 'pe' and \
				not '-MD' in args and not '-MMD' in args: o = os.devnull
			else:
				if not build_check_task.compile: o = 'a.i'
				elif not build_check_task.link: o = 'a.o'
				else: o = 'a'
			if not build_check_task.compile: args += ['-E', '-o', o]
			elif not build_check_task.link: args += ['-c', '-o', o]
			else: args += ['-o', o] + cfg.ld_args[1:]
		return exec_subprocess_pipe(args, cwd=cwd.path, input=build_check_task._prog_source_text, silent=True)
