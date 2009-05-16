#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2007-2009 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

import os

from wonderbuild.logger import is_debug, debug, colored, out_is_dumb
from wonderbuild.signature import Sig
from wonderbuild.subprocess_wrapper import exec_subprocess, exec_subprocess_pipe

need_sep_fix = os.sep != '/'

class Impl(object):

	@staticmethod
	def progs(cfg):
		if not out_is_dumb: cxx_prog = ld_prog = ((cfg.project.fs.cur / __file__).parent / 'colorgcc').abs_path
		else: cxx_prog, ld_prog = cfg.cxx_prog, cfg.ld_prog or cfg.cxx_prog
		return cxx_prog, ld_prog, 'ar', 'ranlib'
		# see also g++ -print-prog-name=ld
		# for gnu ar, 'ar s' is used instead of ranlib
		
	@property
	def common_env_sig(self):
		try: return self._common_env_sig
		except AttributeError:
			sig = Sig()
			# linux/solaris LD_LIBRARY_PATH, macosx DYLD_LIBRARY_PATH, hpux SHLIB_PATH, aix LIBPATH
			for name in ('LD_LIBRARY_PATH', 'DYLD_LIBRARY_PATH', 'SHLIB_PATH', 'LIBPATH', 'GCC_EXEC_PREFIX', 'COMPILER_PATH'):
				e = os.environ.get(name, None)
				if e is not None: sig.update(e)
			sig = self._common_env_sig = sig.digest()
			return sig

	@property
	def cxx_env_sig(self):
		try: return self._cxx_env_sig
		except AttributeError:
			sig = Sig()
			for name in ('CPATH', 'CPLUS_INCLUDE_PATH'): # TODO C_INCLUDE_PATH for C
				e = os.environ.get(name, None)
				if e is not None: sig.update(e)
			sig = self._cxx_env_sig = sig.digest()
			return sig

	@staticmethod
	def cfg_cxx_args_cwd(cfg): return Impl._cfg_cxx_args(cfg, Impl._cfg_cxx_args_include_cwd)

	@staticmethod
	def cfg_cxx_args_bld(cfg): return Impl._cfg_cxx_args(cfg, Impl._cfg_cxx_args_include_bld)
	
	@staticmethod
	def _cfg_cxx_args(cfg, include_func):
		args = [cfg.cxx_prog, '-pipe']
		if cfg.debug: args.append('-g')
		if cfg.optim is not None: args.append('-O' + cfg.optim)
		if cfg.pic: args.append('-fPIC')
		for k, v in cfg.defines.iteritems():
			if v is None: args.append('-D' + k)
			else: args.append('-D' + k + '=' + v)
		include_func(cfg, args)
		args += cfg.cxx_flags
		#if __debug__ and is_debug: debug('cfg: cxx: impl: gcc: cxx: ' + str(args))
		return args

	@staticmethod
	def _cfg_cxx_args_include_cwd(cfg, args):
		for p in cfg.include_paths: args.append('-I' + p.path)
		if cfg.pch is not None: args += ['-include', cfg.pch.path]
		for i in cfg.includes: args += ['-include', i.path]

	@staticmethod
	def _cfg_cxx_args_include_bld(cfg, args):
		for p in cfg.include_paths: args.append('-I' + os.path.join(os.pardir, os.pardir, p.rel_path(cfg.project.bld_dir)))
		if cfg.pch is not None: args += ['-include', os.path.join(os.pardir, os.pardir, cfg.pch.rel_path(cfg.project.bld_dir))]
		for i in cfg.includes: args += ['-include', os.path.join(os.pardir, os.pardir, i.rel_path(cfg.project.bld_dir))]

	@staticmethod
	def process_precompile_task(precompile_task, lock):
		# some useful options: -Wmissing-include-dirs -Winvalid-pch -H -fpch-deps -Wp,-v
		# to print the include search path: g++ -xc++ /dev/null -E -Wp,-v 2>&1 1>/dev/null | sed -e '/^[^ ]/d' -e 's,^ ,-I,'
		# TODO -xc-header for C
		args = precompile_task.cfg.cxx_args_cwd + ['-xc++-header', precompile_task.header.path, '-MD']
		use_dir = False
		if not use_dir:
			path = (precompile_task.target_dir / (precompile_task.header.name + '.d')).path
			args.append('-MF' + path)
		else:
			dir = precompile_task.target
			dir.make_dir()
			path = os.path.join(dir.path, 'x')
			args.append('-o' + path)
			path += '.d'
		r = exec_subprocess(args)
		if r != 0: raise Exception, r
		# reads deps from the .d files generated as side-effect of compilation by gcc's -MD or -MMD option
		f = open(path, 'r')
		try: deps = f.read().replace('\\\n', '')
		finally: f.close()
		cwd = precompile_task.project.fs.cur
		if need_sep_fix: deps = deps.replace('/', os.sep)
		lock.acquire()
		try: deps = [cwd / d for d in deps[deps.find(':') + 1:].split()]
		finally: lock.release()
		if __debug__ and is_debug: debug('cpp: gcc dep file: ' + path + ': ' + str([str(d) for d in deps]))
		dep_sigs = [d.sig for d in deps]
		dep_sigs.sort()
		precompile_task.persistent = precompile_task.sig, deps, Sig(''.join(dep_sigs)).digest()

	def precompile_task_target_name(self, header_name): return header_name + self.precompile_task_target_ext

	@property
	def precompile_task_target_ext(self): return '.gch'

	@staticmethod
	def process_cxx_task(cxx_task, lock):
		args = cxx_task.cfg.cxx_args_bld + ['-c', '-MMD'] + [s.name for s in cxx_task._actual_sources]
		cwd = cxx_task.target_dir
		r = exec_subprocess(args, cwd = cwd.path)
		if r != 0: raise Exception, r
		implicit_deps = cxx_task.persistent_implicit_deps
		for s in zip(cxx_task.sources, cxx_task._actual_sources):
			# reads deps from the .d files generated as side-effect of compilation by gcc's -MD or -MMD option
			path = s[1].path
			f = open(path[:path.rfind('.')] + '.d', 'r')
			try: deps = f.read().replace('\\\n', '')
			finally: f.close()
			if need_sep_fix: deps = deps.replace('/', os.sep)
			# note: we skip the first implicit dep, which is the dummy actual source
			lock.acquire()
			try: deps = [cwd / d for d in deps[deps.find(':') + 1:].split()[1:]]
			finally: lock.release()
			if __debug__ and is_debug: debug('cpp: gcc dep file: ' + path + ': ' + str([str(d) for d in deps]))
			dep_sigs = [d.sig for d in deps]
			dep_sigs.sort()
			implicit_deps[s[0]] = deps, Sig(''.join(dep_sigs)).digest()

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
			for name in ('LIBRARY_PATH', 'GNUTARGET', 'LDEMULATION', 'COLLECT_NO_DEMANGLE'):
				e = os.environ.get(name, None)
				if e is not None: sig.update(e)
			sig = self._ld_env_sig = sig.digest()
			return sig

	@staticmethod
	def cfg_ld_args(cfg):
		args = [cfg.ld_prog]
		if cfg.shared: args.append('-shared')
		elif cfg.static_prog: args.append('-static') # we can have both -shared and -static but that's not very useful
		args.append('-Wl,-rpath=$ORIGIN' + os.sep + cfg.fhs.lib.rel_path(cfg.fhs.bin))
		for p in cfg.lib_paths: args.append('-L' + p.path)
		for l in cfg.libs: args.append('-l' + l)
		if len(cfg.static_libs):
			args.append('-Wl,-Bstatic')
			for l in cfg.static_libs: args.append('-l' + l)
		if len(cfg.shared_libs):
			args.append('-Wl,-Bdynamic')
			for l in cfg.shared_libs: args.append('-l' + l)
		args += cfg.ld_flags
		#if __debug__ and is_debug: debug('cfg: cxx: impl: gcc: ld: ' + str(args))
		return args

	@staticmethod
	def cfg_ar_ranlib_args(cfg):
		ar_args = [cfg.ar_prog, 'rcs']
		#if __debug__ and is_debug: debug('cfg: cxx: impl: gcc: ar: ' + str(ar_args))
		if True: return ar_args, None # We use the s option in gnu ar to do the same as ranlib.
		else:
			ranlib_args = [cfg.ranlib_prog]
			#if __debug__ and is_debug: debug('cfg: cxx: impl: gcc: ranlib: ' + str(ranlib_args))
			return ar_args, ranlib_args

	@staticmethod
	def process_mod_task(mod_task, obj_names, removed_obj_names):
		path = mod_task.obj_dir.path
		obj_paths = [os.path.join(path, o) for o in obj_names]
		if mod_task.ld:
			args = mod_task.cfg.ld_args
			args = [args[0], '-o' + mod_task.target.path] + obj_paths + args[1:]
			r = exec_subprocess(args)
			if r != 0: raise Exception, r
		else:
			ar_args, ranlib_args = mod_task.cfg.ar_ranlib_args
			if len(obj_names) != 0:
				args = ar_args[:]
				if removed_obj_names is not None: args[1] = args[1].replace('s', '')
				args.append(mod_task.target.path)
				args += obj_paths
				r = exec_subprocess(args)
				if r != 0: raise Exception, r
			if removed_obj_names is not None:
				args = [ar_args[0], ranlib_args is None and 'ds' or 'd', mod_task.target.path] + removed_obj_names
				r = exec_subprocess(args)
				if r != 0: raise Exception, r
			if ranlib_args is not None: # 's' not in ar_args[1]
				args = ranlib_args[:]
				args.append(mod_task.target.path)
				r = exec_subprocess(args)
				if r != 0: raise Exception, r

	@staticmethod
	def mod_task_targets(mod_task): return (mod_task.target,)

	@staticmethod
	def mod_task_target_dev_dir(mod_task):
		if mod_task.cfg.shared and mod_task.cfg.target_platform_binary_format_is_pe: return mod_task.cfg.fhs.bin
		else: return mod_task.cfg.fhs.lib

	@staticmethod
	def mod_task_target_dev_name(mod_task): return mod_task.name

	@staticmethod
	def mod_task_target_dir(mod_task):
		if mod_task.kind == mod_task.Kinds.PROG or \
			mod_task.cfg.shared and mod_task.cfg.target_platform_binary_format_is_pe: return mod_task.cfg.fhs.bin
		else: return mod_task.cfg.fhs.lib

	@staticmethod
	def mod_task_target_name(mod_task):
		if mod_task.kind == mod_task.Kinds.PROG:
			if mod_task.cfg.target_platform_binary_format_is_pe: return mod_task.name + '.exe'
			else: return mod_task.name
		elif mod_task.cfg.shared:
			if mod_task.cfg.target_platform_binary_format_is_pe: return mod_task.name + '.dll'
			else: return 'lib' + mod_task.name + '.so'
		else: return 'lib' + mod_task.name + '.a'

	@staticmethod
	def process_build_check_task(build_check_task):
		cfg = build_check_task.cfg
		cfg.shared = cfg.pic = False
		if os.name != 'posix': o = (build_check_task.bld_dir / 'a').path
		else: o = os.devnull
		# TODO -xc for C
		args = cfg.cxx_args_cwd + ['-xc++', '-', '-o', o] + cfg.ld_args[1:]
		return exec_subprocess_pipe(args, input = build_check_task._prog_source_text, silent = True)
