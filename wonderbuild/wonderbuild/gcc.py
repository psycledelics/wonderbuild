#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2007-2009 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

import os

from logger import is_debug, debug, colored
from signature import Sig
from task import exec_subprocess, exec_subprocess_pipe

class Impl(object):

	@property
	def common_env_sig(self):
		sig = Sig()
		for name in ('LD_LIBRARY_PATH',):
			e = os.environ.get(name, None)
			if e is not None: sig.update(e)
		return sig.digest()

	@property
	def cxx_prog(self): return 'g++'

	@property
	def cxx_env_sig(self):
		sig = Sig()
		for name in ('CPATH', 'CPLUS_INCLUDE_PATH'):
			e = os.environ.get(name, None)
			if e is not None: sig.update(e)
		return sig.digest()

	@staticmethod
	def cfg_cxx_args(cfg):
		args = [cfg.cxx_prog, '-pipe'] + cfg.cxx_flags
		if cfg.debug: args.append('-g')
		if cfg.optim is not None: args.append('-O' + cfg.optim)
		if cfg.pic: args.append('-fPIC')
		for k, v in cfg.defines.iteritems():
			if v is None: args.append('-D' + k)
			else: args.append('-D' + k + '=' + v)
		for i in cfg.includes: args += ['-include', os.path.join(os.pardir, os.pardir, i.rel_path(cfg.project.bld_node))]
		for p in cfg.include_paths: args += ['-I', os.path.join(os.pardir, os.pardir, p.rel_path(cfg.project.bld_node))]
		#if __debug__ and is_debug: debug('cfg: cxx: impl: gcc: cxx: ' + str(args))
		return args
	
	@staticmethod
	def process_cxx_task(cxx_task):
		args = cxx_task.cfg.cxx_args + ['-c', '-MMD'] + [s.name for s in cxx_task._actual_sources]
		r = exec_subprocess(args, cwd = cxx_task.target_dir.path)
		if r != 0: raise Exception, r
		implicit_deps = cxx_task.project.task_states[cxx_task.uid][2]
		for s in zip(cxx_task.sources, cxx_task._actual_sources):
			# reads deps from the .d files generated as side-effect of compilation by gcc's -MD or -MMD option
			path = s[1].path
			f = open(path[:path.rfind('.')] + '.d', 'rb')
			try: deps = f.read().replace('\\\n', '')
			finally: f.close()
			target_dir = cxx_task.target_dir
			# note: we skip the first implicit dep, which is the dummy actual source
			deps = [target_dir.node_path(d) for d in deps[deps.find(':') + 1:].split()[1:]]
			if __debug__ and is_debug: debug('cpp: gcc dep file: ' + path + ': ' + str([str(d) for d in deps]))
			sigs = [d.sig for d in deps]
			sigs.sort()
			implicit_deps[s[0]] = Sig(''.join(sigs)).digest(), deps

	@property
	def cxx_task_target_ext(self): return '.o'
		
	@property
	def ld_prog(self): return 'g++'
	
	@property
	def ar_prog(self): return 'ar'
	
	@property
	def ranlib_prog(self): return 'ranlib' # for gnu ar, 'ar s' is used instead of ranlib
	
	@property
	def common_mod_env_sig(self): return ''

	@property
	def ar_ranlib_env_sig(self): return ''

	@property
	def ld_env_sig(self):
		sig = Sig()
		for name in ('GNUTARGET', 'LDEMULATION', 'COLLECT_NO_DEMANGLE'):
			e = os.environ.get(name, None)
			if e is not None: sig.update(e)
		return sig.digest()

	@staticmethod
	def cfg_ld_args(cfg):
		args = [cfg.ld_prog] + cfg.ld_flags
		if cfg.shared: args.append('-shared')
		for p in cfg.lib_paths: args += ['-L', p.path]
		for l in cfg.libs: args.append('-l' + l)
		if len(cfg.static_libs):
			args.append('-Wl,-Bstatic')
			for l in cfg.static_libs: args.append('-l' + l)
		if len(cfg.static_libs):
			args.append('-Wl,-Bdynamic')
			for l in cfg.shared_libs: args.append('-l' + l)
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
	def process_mod_task(mod_task, obj_names):
		path = mod_task.target_dir.path
		obj_paths = [os.path.join(path, o) for o in obj_names]
		if mod_task.ld:
			args = mod_task.cfg.ld_args[:]
			args = [args[0], '-o', mod_task.target.path] + obj_paths + args[1:]
			r = exec_subprocess(args)
			if r != 0: raise Exception, r
		else:
			ar_args, ranlib_args = mod_task.cfg.ar_ranlib_args
			args = ar_args[:]
			args.append(mod_task.target.path)
			args += obj_paths
			r = exec_subprocess(args)
			if r != 0: raise Exception, r
			if ranlib_args is not None:
				args = ranlib_args[:]
				args.append(mod_task.target.path)
				r = exec_subprocess(args)
				if r != 0: raise Exception, r

	@staticmethod
	def mod_task_target_name(mod_task):
		if mod_task.kind == mod_task.Kinds.PROG: name = mod_task.name
		elif mod_task.cfg.shared: name = 'lib' + mod_task.name + '.so'
		else: name = 'lib' + mod_task.name + '.a'
		return name
	
	@staticmethod
	def build_check(base_cfg, source_text, silent = False):
		cfg = base_cfg.clone()
		cfg.shared = cfg.pic = False
		args = cfg.cxx_args + ['-xc++', '-', '-o', os.devnull] + cfg.ld_args[1:]
		return exec_subprocess_pipe(args, input = source_text, silent = silent)
