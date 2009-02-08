#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2007-2009 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

import os

from logger import is_debug, debug, colored
from signature import Sig
from subprocess_wrapper import exec_subprocess, exec_subprocess_pipe

class Impl(object):

	@property
	def common_env_sig(self):
		sig = Sig()
		for name in ('LD_LIBRARY_PATH', 'GCC_EXEC_PREFIX'):
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
		for i in cfg.includes: args += ['-include', i.path]

	@staticmethod
	def _cfg_cxx_args_include_bld(cfg, args):
		for p in cfg.include_paths: args.append('-I' + os.path.join(os.pardir, os.pardir, p.rel_path(cfg.project.bld_node)))
		for i in cfg.includes: args += ['-include', os.path.join(os.pardir, os.pardir, i.rel_path(cfg.project.bld_node))]

	@staticmethod
	def process_precompile_task(precompile_task):
		# some useful options: -Wmissing-include-dirs -Winvalid-pch -H -fpch-deps -Wp,-v
		# to print the include search path: g++ -xc++ /dev/null -E -Wp,-v 2>&1 1>/dev/null | sed -e '/^[^ ]/d' -e 's,^ ,-I,'
		args = precompile_task.cfg.cxx_args_cwd + ['-xc++-header', precompile_task.header.path, '-MMD']
		use_dir = False
		if not use_dir:
			path = precompile_task.header.path + '.d'
			args.append('-MF' + path)
		else:
			dir = precompile_task.target
			dir.make_dir()
			path = os.path.join(dir.path, 'x')
			args += ['-o', path]
			path += '.d'
		r = exec_subprocess(args)
		if r != 0: raise Exception, r
		# reads deps from the .d files generated as side-effect of compilation by gcc's -MD or -MMD option
		f = open(path, 'r')
		try: deps = f.read().replace('\\\n', '')
		finally: f.close()
		cwd = precompile_task.project.fs.cur
		deps = [cwd.node_path(d) for d in deps[deps.find(':') + 1:].split()]
		if __debug__ and is_debug: debug('cpp: gcc dep file: ' + path + ': ' + str([str(d) for d in deps]))
		dep_sigs = [d.sig for d in deps]
		dep_sigs.sort()
		precompile_task.project.state_and_cache[precompile_task.uid] = precompile_task.sig, deps, Sig(''.join(dep_sigs)).digest()

	@property
	def precompile_task_target_ext(self): return '.gch'

	@staticmethod
	def process_cxx_task(cxx_task):
		args = cxx_task.cfg.cxx_args_bld + ['-c', '-MMD'] + [s.name for s in cxx_task._actual_sources]
		cwd = cxx_task.target_dir
		r = exec_subprocess(args, cwd = cwd.path)
		if r != 0: raise Exception, r
		implicit_deps = cxx_task.project.state_and_cache[cxx_task.uid][2]
		for s in zip(cxx_task.sources, cxx_task._actual_sources):
			# reads deps from the .d files generated as side-effect of compilation by gcc's -MD or -MMD option
			path = s[1].path
			f = open(path[:path.rfind('.')] + '.d', 'r')
			try: deps = f.read().replace('\\\n', '')
			finally: f.close()
			# note: we skip the first implicit dep, which is the dummy actual source
			deps = [cwd.node_path(d) for d in deps[deps.find(':') + 1:].split()[1:]]
			if __debug__ and is_debug: debug('cpp: gcc dep file: ' + path + ': ' + str([str(d) for d in deps]))
			dep_sigs = [d.sig for d in deps]
			dep_sigs.sort()
			implicit_deps[s[0]] = deps, Sig(''.join(dep_sigs)).digest()

	@property
	def cxx_task_target_ext(self): return '.o'
		
	@property
	def ld_prog(self): return 'g++' # TODO use g++ -print-prog-name=ld
	
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
		args = [cfg.ld_prog]
		if cfg.shared: args.append('-shared')
		for p in cfg.lib_paths: args.append('-L' + p.path)
		for l in cfg.libs: args.append('-l' + l)
		if len(cfg.static_libs):
			args.append('-Wl,-Bstatic')
			for l in cfg.static_libs: args.append('-l' + l)
		if len(cfg.static_libs):
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
	def process_mod_task(mod_task, obj_names):
		path = mod_task.target_dir.path
		obj_paths = [os.path.join(path, o) for o in obj_names]
		if mod_task.ld:
			args = mod_task.cfg.ld_args[:]
			args = [args[0], '-o' + mod_task.target.path] + obj_paths + args[1:]
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
	def process_build_check_task(build_check_task):
		cfg = build_check_task.cfg
		cfg.shared = cfg.pic = False
		args = cfg.cxx_args_cwd + ['-xc++', '-', '-o', os.devnull] + cfg.ld_args[1:]
		return exec_subprocess_pipe(args, input = build_check_task._prog_source_text, silent = True)
