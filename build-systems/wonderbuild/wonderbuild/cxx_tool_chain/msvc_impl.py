#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2007-2010 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

import os

from wonderbuild import UserReadableException
from wonderbuild.logger import is_debug, debug, colored
from wonderbuild.signature import Sig
from wonderbuild.subprocess_wrapper import exec_subprocess, exec_subprocess_pipe
from cpp_include_scanner import IncludeScanner

class Impl(object):
	def __init__(self, persistent):
		self.cpp = IncludeScanner(persistent)

	@staticmethod
	def parse_version(out, err):
		v = err[:err.find('\n')]
		x = 'Version '
		v = v[v.find(x) + len(x):]
		x = v.rfind(' for')
		if x >= 0: return tuple(int(v) for v in v[:x].split('.'))
		else: return (0,)

	@staticmethod
	def progs(cfg): return 'cl', 'link', 'lib', None

	@property
	def common_env_sig(self): return ''

	@property
	def cxx_env_sig(self):
		try: return self._cxx_env_sig
		except AttributeError:
			sig = Sig()
			e = os.environ.get('INCLUDE', None)
			if e is not None: sig.update(e)
			sig = self._cxx_env_sig = sig.digest()
			return sig

	def cfg_cxx_args(self, cfg):
		args = [cfg.cxx_prog, '-nologo']
		for k, v in cfg.defines.iteritems():
			if v is None: args.append('-D' + k)
			else: args.append('-D' + k + '=' + repr(v)[1:-1]) # note: assumes that cpp and python escaping works the same way
		if cfg.pch is not None:
			pch = cfg.pch.parent / self.precompile_task_target_name(cfg.pch.name)
			args += [
				'-FI' + cfg.pch.name,
				'-Yu' + cfg.pch.name,
				'-Fp' + cfg.bld_rel_path(pch)
			]
		for p in cfg.include_paths: args.append('-I' + cfg.bld_rel_path_or_abs_path(p))
		for i in cfg.includes: args.append('-FI' + cfg.bld_rel_path(i))
		args += cfg.cxx_flags
		#if __debug__ and is_debug: debug('cfg: cxx: impl: msvc: cxx: ' + str(args))
		return args

	def process_precompile_task(self, precompile_task, lock):
		cwd = precompile_task.target_dir
		#obj = cwd / (precompile_task.header.name[:precompile_task.header.name.rfind('.')] + self.cxx_task_target_ext)
		args = precompile_task.cfg.cxx_args + [
			'-c', '-Yc',
			'-Tp', precompile_task.header.rel_path(cwd),
			#'-Fp' + precompile_task.target.rel_path(cwd), # -Fp option defaults to input file with ext changed to .pch
			#'-Fo' + obj.rel_path(cwd), # -Fo option defaults to input file with ext changed to .obj
		]
		if exec_subprocess(args, cwd=cwd.path) != 0: raise UserReadableException, precompile_task
		lock.acquire()
		try: deps, not_found = self.cpp.scan_deps(precompile_task.header, precompile_task.cfg.include_paths)
		finally: lock.release()
		if __debug__ and is_debug:
			debug('cpp: deps found: ' + str(precompile_task.header) + ': ' + str([str(d) for d in deps]))
			if len(not_found) != 0: debug('cpp: deps not found: ' + str(precompile_task.header) + ': '+ str([str(x) for x in not_found]))
		return deps

	def precompile_task_target_name(self, header_name): return header_name[:header_name.rfind('.')] + self.precompile_task_target_ext

	@property
	def precompile_task_target_ext(self): return '.pch'

	def process_cxx_task(self, cxx_task, lock):
		cwd = cxx_task.target_dir
		args = cxx_task.cfg.cxx_args + ['-c'] + [cxx_task.cfg.bld_rel_path_or_name(p) for p in cxx_task._actual_sources]
		implicit_deps = cxx_task.persistent_implicit_deps
		if exec_subprocess(args, cwd=cwd.path) == 0:
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
		if failed_sources is not None: raise UserReadableException, '  '.join(str(s) for s in failed_sources)

	@property
	def cxx_task_target_ext(self): return '.obj'
		
	@property
	def common_mod_env_sig(self): return ''

	@property
	def ar_ranlib_env_sig(self): return ''

	@property
	def ld_env_sig(self):
		try: return self._ld_env_sig
		except AttributeError:
			sig = Sig()
			e = os.environ.get('LIB', None)
			if e is not None: sig.update(e)
			sig = self._ld_env_sig = sig.digest()
			return sig

	#@staticmethod
	def cfg_ld_args(self, cfg):
		args = [cfg.ld_prog, '-nologo']
		if cfg.shared: args.append('-dll')
		elif cfg.static_prog: pass #args.append('-static')
		if cfg.pch is not None: args.append(cfg.bld_rel_path(cfg.pch.parent / (cfg.pch.name[:cfg.pch.name.rfind('.')] + self.cxx_task_target_ext)))
		for p in cfg.lib_paths: args.append('-libpath:' + cfg.bld_rel_path(p))
		for l in cfg.libs: args.append(l + '.lib')
		if len(cfg.static_libs):
			for l in cfg.static_libs: args.append('lib' + l + '.lib')
		if len(cfg.shared_libs):
			for l in cfg.shared_libs: args.append(l + '.lib')
		args += cfg.ld_flags
		#if __debug__ and is_debug: debug('cfg: cxx: impl: msvc: ld: ' + str(args))
		return args

	@staticmethod
	def cfg_ar_ranlib_args(cfg):
		ar_args = [cfg.ar_prog, '-nologo']
		#if __debug__ and is_debug: debug('cfg: cxx: impl: msvc: ar: ' + str(ar_args))
		if True: return ar_args, None # no ranlib with msvc

	def process_mod_task(self, mod_task, obj_names, removed_obj_names):
		cwd = mod_task.obj_dir
		obj_paths = obj_names
		mod_task_target_path = mod_task.target.rel_path(cwd)
		if mod_task.ld:
			args = mod_task.cfg.ld_args + ['-out:' + mod_task_target_path] + obj_paths
			if mod_task.cfg.shared: args.append('-implib:' + (mod_task.target_dev_dir / mod_task.target_dev_name).rel_path(cwd))
		else:
			ar_args, ranlib_args = mod_task.cfg.ar_ranlib_args
			args = ar_args + ['-out:' + mod_task_target_path)] + obj_paths
			if removed_obj_names is not None:
				for o in removed_obj_names: args.append('-remove:' + o)
		if exec_subprocess(args, cwd=cwd.path) != 0: raise UserReadableException, mod_task
		# no ranlib with msvc

	@staticmethod
	def mod_task_targets(mod_task):
		if mod_task.kind == mod_task.Kinds.PROG or not mod_task.ld: return (mod_task.target,)
		else:
			implib = mod_task.target_dev_dir / mod_task.target_dev_name
			#exp = mod_task.target_dev_dir / mod_task.name + '.exp'
			#pdb = mod_task.target_dev_dir / mod_task.name + '.pdb'
			#ilk = mod_task.target_dev_dir / mod_task.name + '.ilk'
			return (mod_task.target, implib)

	@staticmethod
	def mod_task_target_dev_dir(mod_task): return mod_task.cfg.fhs.lib

	@staticmethod
	def mod_task_target_dev_name(mod_task):
		if mod_task.ld: return mod_task.name + '.lib'
		else: return 'lib' + mod_task.name + '.lib'

	@staticmethod
	def mod_task_target_dir(mod_task):
		if mod_task.ld: return mod_task.cfg.fhs.bin
		else: return mod_task.cfg.fhs.lib

	@staticmethod
	def mod_task_target_name(mod_task):
		if mod_task.kind == mod_task.Kinds.PROG: return mod_task.name + '.exe'
		elif mod_task.ld: return mod_task.name + '.dll'
		else: return 'lib' + mod_task.name + '.lib'

	@staticmethod
	def process_build_check_task(build_check_task):
		cwd = build_check_task.bld_dir
		cfg = build_check_task.cfg
		s = cwd / ('a.' + {'c++': 'cpp', 'c': 'c'}[cfg.lang])
		f = open(s.path, 'w')
		try: f.write(build_check_task._prog_source_text)
		finally: f.close()
		args = cfg.cxx_args + [s.rel_path(cwd)]
		if build_check_task.pipe_preproc: args.append('-EP')
		elif not build_check_task.compile: args.append('-P')
		elif not build_check_task.link: args.append('-c')
		else: args += ['-link'] + cfg.ld_args[1:]
		return exec_subprocess_pipe(args, cwd=cwd.path, silent=True)
