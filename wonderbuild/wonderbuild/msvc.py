#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2007-2009 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

import os

from logger import is_debug, debug, colored
from signature import Sig
from subprocess_wrapper import exec_subprocess, exec_subprocess_pipe
from cpp_include_scanner import IncludeScanner

class Impl(object):
	def __init__(self, persistent):
		self.cpp = IncludeScanner(persistent)

	@staticmethod
	def progs(cfg): return 'cl', 'link', 'lib', None

	@property
	def common_env_sig(self): return ''

	@property
	def cxx_env_sig(self):
		sig = Sig()
		e = os.environ.get('INCLUDE', None)
		if e is not None: sig.update(e)
		return sig.digest()

	def cfg_cxx_args_cwd(self, cfg): return self._cfg_cxx_args(cfg, self._cfg_cxx_args_include_cwd)

	def cfg_cxx_args_bld(self, cfg): return self._cfg_cxx_args(cfg, self._cfg_cxx_args_include_bld)
	
	def _cfg_cxx_args(self, cfg, include_func):
		args = [cfg.cxx_prog, '-nologo']
		if cfg.pic: pass #args.append('-fPIC')
		for k, v in cfg.defines.iteritems():
			if v is None: args.append('-D' + k)
			else: args.append('-D' + k + '=' + v)
		include_func(cfg, args)
		args += cfg.cxx_flags
		#if __debug__ and is_debug: debug('cfg: cxx: impl: msvc: cxx: ' + str(args))
		return args

	def _cfg_cxx_args_include_cwd(self, cfg, args):
		if cfg.pch is not None:
			pch = cfg.pch.parent / (cfg.pch.name[:cfg.pch.name.rfind('.')] + self.precompile_task_target_ext)
			args += [
				'-FI' + cfg.pch.name,
				'-Yu' + cfg.pch.name,
				'-Fp' + pch.path
			]
		for p in cfg.include_paths: args.append('-I' + p.path)
		for i in cfg.includes: args.append('-FI' + i.path)

	def _cfg_cxx_args_include_bld(self, cfg, args):
		if cfg.pch is not None:
			pch = cfg.pch.parent / (cfg.pch.name[:cfg.pch.name.rfind('.')] + self.precompile_task_target_ext)
			args += [
				'-FI' + cfg.pch.name,
				'-Yu' + cfg.pch.name,
				'-Fp' + os.path.join(os.pardir, os.pardir, pch.rel_path(cfg.project.bld_dir))
			]
		for p in cfg.include_paths: args.append('-I' + os.path.join(os.pardir, os.pardir, p.rel_path(cfg.project.bld_dir)))
		for i in cfg.includes: args.append('-FI' + os.path.join(os.pardir, os.pardir, i.rel_path(cfg.project.bld_dir)))
	
	def process_precompile_task(self, precompile_task, lock):
		cwd = precompile_task.target_dir
		#basename =  precompile_task.header.name[:precompile_task.header.name.rfind('.')]
		#obj = precompile_task.header.parent / (basename +  self.cxx_task_target_ext)
		#pch = precompile_task.header.parent / (basename +  self.precompile_task_target_ext)
		args = precompile_task.cfg.cxx_args_bld + [
			'-c', '-Yc',
			'-Tp', precompile_task.header.rel_path(cwd),
			#'-Fp' + pch.rel_path(cwd), # -Fp option defaults to input file with ext changed to .pch
			#'-Fo' + obj.rel_path(cwd), # -Fo option defaults to input file with ext changed to .obj
		]
		r = exec_subprocess(args, cwd = cwd.path)
		if r != 0: raise Exception, r
		lock.acquire()
		try: deps, not_found = self.cpp.scan_deps(precompile_task.header, precompile_task.cfg.include_paths)
		finally: lock.release()
		if __debug__ and is_debug:
			debug('cpp: deps found: ' + str(precompile_task.header) + ': ' + str((str(d) for d in deps)))
			if len(not_found) != 0: debug('cpp: deps not found: ' + str(precompile_task.header) + ': '+ str((str(x) for x in not_found)))
		dep_sigs = [d.sig for d in deps]
		dep_sigs.sort()
		precompile_task.persistent = precompile_task.sig, deps, Sig(''.join(dep_sigs)).digest()

	@property
	def precompile_task_target_ext(self): return '.pch'

	def process_cxx_task(self, cxx_task, lock):
		args = cxx_task.cfg.cxx_args_bld + ['-c'] + [s.name for s in cxx_task._actual_sources]
		cwd = cxx_task.target_dir
		r = exec_subprocess(args, cwd = cwd.path)
		if r != 0: raise Exception, r
		implicit_deps = cxx_task.persistent_implicit_deps
		for s in cxx_task.sources:
			lock.acquire()
			try: deps, not_found = self.cpp.scan_deps(s, cxx_task.cfg.include_paths)
			finally: lock.release()
			if __debug__ and is_debug:
				debug('cpp: deps found: ' + str(s) + ': ' + str((str(d) for d in deps)))
				if len(not_found) != 0: debug('cpp: deps not found: ' + str(s) + ': '+ str((str(x) for x in not_found)))
			dep_sigs = [d.sig for d in deps]
			dep_sigs.sort()
			implicit_deps[s] = deps, Sig(''.join(dep_sigs)).digest()

	@property
	def cxx_task_target_ext(self): return '.obj'
		
	@property
	def common_mod_env_sig(self): return ''

	@property
	def ar_ranlib_env_sig(self): return ''

	@property
	def ld_env_sig(self):
		sig = Sig()
		for name in ('LIB'):
			e = os.environ.get(name, None)
			if e is not None: sig.update(e)
		return sig.digest()

	@staticmethod
	def cfg_ld_args(cfg):
		args = [cfg.ld_prog, '-nologo']
		if cfg.shared: args.append('-dll')
		elif cfg.static_prog: pass #args.append('-static')
		for p in cfg.lib_paths: args.append('-libpath:' + p.path)
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
		ar_args = [cfg.ar_prog]
		#if __debug__ and is_debug: debug('cfg: cxx: impl: msvc: ar: ' + str(ar_args))
		if True: return ar_args, None # no ranlib with msvc

	@staticmethod
	def process_mod_task(mod_task, obj_names):
		path = mod_task.obj_dir.path
		obj_paths = [os.path.join(path, o) for o in obj_names]
		if mod_task.ld:
			args = mod_task.cfg.ld_args
			args = [args[0], '-out:' + mod_task.target.path] + obj_paths + args[1:]
			if mod_task.cfg.shared:
				implib = mod_task.target.name
				implib = implib[:implib.rfind('.')] + '.lib'
				implib = mod_task.cfg.fhs.lib / implib
				mod_task.cfg.fhs.lib.make_dir()
				args.append('-implib:' + implib.path)
		else:
			ar_args, ranlib_args = mod_task.cfg.ar_ranlib_args
			args = ar_args[:]
			args.append(mod_task.target.path)
			args += obj_paths
		r = exec_subprocess(args)
		if r != 0: raise Exception, r
		# no ranlib with msvc

	@staticmethod
	def mod_task_target_dir(mod_task):
		if mod_task.kind == mod_task.Kinds.PROG or mod_task.cfg.shared: dir = mod_task.cfg.fhs.bin
		else: dir = mod_task.cfg.fhs.lib
		return dir

	@staticmethod
	def mod_task_target_name(mod_task):
		if mod_task.kind == mod_task.Kinds.PROG: name = mod_task.name + '.exe'
		elif mod_task.cfg.shared: name = mod_task.name + '.dll'
		else: name = 'lib' + mod_task.name + '.lib'
		return name

	@staticmethod
	def process_build_check_task(build_check_task):
		cfg = build_check_task.cfg
		cfg.shared = cfg.pic = False
		cwd = build_check_task.bld_dir
		i = cwd / 'a.cpp'
		f = open(i.path, 'w')
		try: f.write(build_check_task._prog_source_text)
		finally: f.close()
		args = cfg.cxx_args_bld + [i.rel_path(cwd), '-link'] + cfg.ld_args[1:]
		return exec_subprocess_pipe(args, cwd = cwd.path, silent = True)
