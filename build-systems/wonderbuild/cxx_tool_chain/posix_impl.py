#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2007-2009 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

import os

from wonderbuild import UserReadableException
from wonderbuild.logger import is_debug, debug, colored, out_is_dumb
from wonderbuild.signature import Sig
from wonderbuild.subprocess_wrapper import exec_subprocess, exec_subprocess_pipe

class Impl(object):
	def __init__(self, persistent):
		self.cpp = IncludeScanner(persistent)

	@staticmethod
	def parse_version(out, err): return None

	@staticmethod
	def progs(cfg):
		cxx_prog, ld_prog = \
			cfg.cxx_prog or 'c++', \
			cfg.ld_prog or cfg.cxx_prog or 'c++' # or 'ld'
		return cxx_prog, ld_prog, 'ar', 'ranlib' # for posix ar, 'ar -s' is used instead of ranlib
		
	@property
	def common_env_sig(self): return ''

	@property
	def cxx_env_sig(self): return ''

	@staticmethod
	def cfg_cxx_args_cwd(cfg): return Impl._cfg_cxx_args(cfg, Impl._cfg_cxx_args_include_cwd)

	@staticmethod
	def cfg_cxx_args_bld(cfg): return Impl._cfg_cxx_args(cfg, Impl._cfg_cxx_args_include_bld)
	
	@staticmethod
	def _cfg_cxx_args(cfg, include_func):
		args = [cfg.cxx_prog]
		for k, v in cfg.defines.iteritems():
			if v is None: args.append('-D' + k)
			else: args.append('-D' + k + '=' + v)
		include_func(cfg, args)
		args += cfg.cxx_flags
		#if __debug__ and is_debug: debug('cfg: cxx: impl: posix: cxx: ' + str(args))
		return args

	@staticmethod
	def _cfg_cxx_args_include_cwd(cfg, args):
		for p in cfg.include_paths: args.append('-I' + p.path)
	@staticmethod
	def _cfg_cxx_args_include_bld(cfg, args):
		for p in cfg.include_paths: args.append('-I' + os.path.join(os.pardir, os.pardir, p.rel_path(cfg.project.bld_dir)))

	def process_cxx_task(self, cxx_task, lock):
		args = cxx_task.cfg.cxx_args_bld + ['-c'] + [s.name for s in cxx_task._actual_sources]
		cwd = cxx_task.target_dir
		implicit_deps = cxx_task.persistent_implicit_deps
		if exec_subprocess(args, cwd = cwd.path) != 0:
			succeeded_sources = cxx_task.sources
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
					src = s[0]
					obj = cwd / (s[1].name[:s[1].name.rfind('.')] + self.cxx_task_target_ext)
					obj.clear()
					if obj.exists: succeeded_sources.append(src)
					else:
						failed_sources.append(src)
						try: had_failed, old_cxx_sig, deps, old_dep_sig = implicit_deps[src]
						except KeyError: implicit_deps[src] = True, None, None, None # This is a new source.
						else: implicit_deps[src] = True, old_cxx_sig, deps, old_dep_sig
			finally: lock.release()
		for s in succeeded_sources:
			lock.acquire()
			try: deps, not_found = self.cpp.scan_deps(s, cxx_task.cfg.include_paths)
			finally: lock.release()
			if __debug__ and is_debug:
				debug('cpp: deps found: ' + str(s) + ': ' + str([str(d) for d in deps]))
				if len(not_found) != 0: debug('cpp: deps not found: ' + str(s) + ': '+ str([str(x) for x in not_found]))
			dep_sigs = [d.sig for d in deps]
			implicit_deps[s] = False, cxx_task.cfg.cxx_sig, deps, Sig(''.join(dep_sigs)).digest()
		if failed_sources is not None: raise UserReadableException, ' '.join(str(s) for s in failed_sources)

	@property
	def cxx_task_target_ext(self): return '.o'
		
	@property
	def common_mod_env_sig(self): return ''

	@property
	def ar_ranlib_env_sig(self): return ''

	@property
	def ld_env_sig(self): return ''

	@staticmethod
	def cfg_ld_args(cfg):
		args = [cfg.ld_prog]
		for p in cfg.lib_paths: args.append('-L' + p.path)
		for l in cfg.libs: args.append('-l' + l)
		for l in cfg.static_libs: args.append('-l' + l)
		for l in cfg.shared_libs: args.append('-l' + l)
		args += cfg.ld_flags
		#if __debug__ and is_debug: debug('cfg: cxx: impl: posix: ld: ' + str(args))
		return args

	@staticmethod
	def cfg_ar_ranlib_args(cfg):
		ar_args = [cfg.ar_prog, '-r']
		if __debug__ and is_debug: ar_args.append('-v')
		else: ar_args.append('-c')
		#if __debug__ and is_debug: debug('cfg: cxx: impl: posix: ar: ' + str(ar_args))
		if True: return ar_args, None # We use the s option in posix ar to do the same as ranlib.
		else:
			ranlib_args = [cfg.ranlib_prog]
			#if __debug__ and is_debug: debug('cfg: cxx: impl: posix: ranlib: ' + str(ranlib_args))
			return ar_args, ranlib_args

	@staticmethod
	def process_mod_task(mod_task, obj_names, removed_obj_names):
		path = mod_task.obj_dir.path
		obj_paths = [os.path.join(path, o) for o in obj_names]
		if mod_task.ld:
			args = mod_task.cfg.ld_args
			args = [args[0], '-o' + mod_task.target.path] + obj_paths + args[1:]
			if exec_subprocess(args) != 0: raise UserReadableException, mod_task
		else:
			ar_args, ranlib_args = mod_task.cfg.ar_ranlib_args
			if len(obj_names) != 0:
				args = ar_args[:]
				if removed_obj_names is not None: args.append('-s')
				args.append(mod_task.target.path)
				args += obj_paths
				if exec_subprocess(args) != 0: raise UserReadableException, mod_task
			if removed_obj_names is not None:
				if ranlib_args is None: args = [ar_args[0], '-d']
				if ranlib_args is None: args.append('-s')
				args.append(mod_task.target.path)
				args += removed_obj_names
				if exec_subprocess(args) != 0: raise UserReadableException, mod_task
			if ranlib_args is not None: # '-s' not in ar_args
				args = ranlib_args[:]
				args.append(mod_task.target.path)
				if exec_subprocess(args) != 0: raise UserReadableException, mod_task

	@staticmethod
	def mod_task_targets(mod_task): return (mod_task.target,)

	@staticmethod
	def mod_task_target_dev_dir(mod_task): return mod_task.cfg.fhs.lib

	@staticmethod
	def mod_task_target_dev_name(mod_task): return mod_task.name

	@staticmethod
	def mod_task_target_dir(mod_task):
		if mod_task.kind == mod_task.Kinds.PROG or \
			mod_task.cfg.shared and mod_task.cfg.target_platform_binary_format_is_pe: return mod_task.cfg.fhs.bin
		else: return mod_task.cfg.fhs.lib

	@staticmethod
	def process_build_check_task(build_check_task):
		cfg = build_check_task.cfg
		cwd = build_check_task.bld_dir
		s = cwd / 'a.cpp' # TODO a.c for C
		f = open(s.path, 'w')
		try: f.write(build_check_task._prog_source_text)
		finally: f.close()
		args = cfg.cxx_args_bld + [s.rel_path(cwd)]
		if build_check_task.pipe_preproc: args.append('-E')
		elif not build_check_task.compile: args += ['-E', '-o', os.devnull]
		elif not build_check_task.link: args += ['-c', '-o', os.devnull]
		else: args += ['-o', os.devnull] + cfg.ld_args[1:]
		return exec_subprocess_pipe(args, cwd = cwd.path, silent = True)
