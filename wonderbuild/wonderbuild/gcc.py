#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2007-2009 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

import os

from logger import is_debug, debug, colored
from signature import Sig
from task import exec_subprocess

class CfgImpl(object):

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
	def user_cfg_cxx_args(user_cfg):
		args = [user_cfg.cxx_prog, '-o', None, None, '-c', '-pipe', '-MMD']
		if user_cfg.debug: args.append('-g')
		if user_cfg.optim is not None: args.append('-O' + user_cfg.optim)
		args += user_cfg.cxx_flags
		if __debug__ and is_debug: debug('cfg: cxx: user: impl: gcc: cxx: ' + str(args))
		return args

	@staticmethod
	def dev_cfg_cxx_args(dev_cfg, args):
		if dev_cfg.pic: args.append('-fPIC')
		for p in dev_cfg.include_paths: args += ['-I', p.path]
		for k, v in dev_cfg.defines.iteritems():
			if v is None: args.append('-D' + k)
			else: args.append('-D' + k + '=' + v)
		if __debug__ and is_debug: debug('cfg: cxx: dev: impl: gcc: cxx: ' + str(args))
	
	@staticmethod
	def cxx_task_sig(cxx_task):
		try: return cxx_task._sig
		except AttributeError:
			try: old_sig, implicit_deps = cxx_task.project.task_states[cxx_task.uid]
			except KeyError:
				sig = 0
				if __debug__ and is_debug: debug('task: sig first: ' + str(cxx_task))
			else:
				try: sigs = [s.sig for s in implicit_deps]
				except OSError:
					# A cached implicit dep does not exist anymore.
					# We must recompute the implicit deps.
					sig = 0
					if __debug__ and is_debug: debug('cpp: deps not found: ' + cxx_task.source.path)
				else:
					sigs.sort()
					sig = Sig(cxx_task.cfg.cxx_sig)
					sig.update(''.join(sigs))
					sig = sig.digest()
					if sig != old_sig:
						# Either the include path or a source or header content has changed.
						# We must recompute the implicit deps.
						sig = 0
						if __debug__ and is_debug: debug('task: sig changed: ' + str(cxx_task))
			cxx_task._sig = sig
			return sig

	@staticmethod
	def process_cxx_task(cxx_task):
		args = cxx_task.cfg.cxx_args[:]
		args[2] = cxx_task.target.path
		args[3] = cxx_task.source.path
		r = exec_subprocess(args)
		if r != 0: raise Exception, r
		implicit_deps = CfgImpl._read_dep_file(cxx_task.target, cxx_task.project.fs.cur)
		sigs = [s.sig for s in implicit_deps]
		sigs.sort()
		sig = Sig(cxx_task.cfg.cxx_sig)
		sig.update(''.join(sigs))
		sig = cxx_task._sig = sig.digest()
		cxx_task.project.task_states[cxx_task.uid] = (sig, implicit_deps)

	@staticmethod
	def _read_dep_file(target, dep_rel):
		'''reads deps from a .d file generated as side-effect of compilation by gcc's -MD or -MMD option'''
	
		path = target.path[:target.path.rfind('.')] + '.d'
		f = open(path, 'rb')
		try: deps = f.read()
		finally: f.close()
		deps = deps.replace('\\\n', '')
		deps = deps[deps.find(':') + 1:].split()
		deps = [dep_rel.node_path(dep) for dep in deps]
		if __debug__ and is_debug: debug('cpp: gcc dep file: ' + path + ': ' + str([str(d) for d in deps]))
		return deps

	@staticmethod
	def post_process_cxx_task(cxx_task): pass # already done in a thread-safe way in process_cxx_task()

	@property
	def ld_prog(self): return 'g++' # TODO
	
	@property
	def ar_prog(self): return 'ar'
	
	@property
	def ranlib_prog(self): return 'ranlib'
	
	@property
	def mod_env_sig(self):
		sig = Sig()
		for name in ('GNUTARGET', 'LDEMULATION', 'COLLECT_NO_DEMANGLE'):
			e = os.environ.get(name, None)
			if e is not None: sig.update(e)
		return sig.digest()

	@staticmethod
	def user_cfg_mod_args(user_cfg):
		ld_args = [user_cfg.ld_prog, '-o', None, None] + user_cfg.ld_flags
		if __debug__ and is_debug: debug('cfg: cxx: user: impl: gcc: ld: ' + str(ld_args))

		ar_args = [user_cfg.ar_prog]
		if user_cfg.ar_flags is not None: ar_args.append(user_cfg.ar_flags)
		if __debug__ and is_debug: debug('cfg: cxx: user: impl: gcc: ar: ' + str(ar_args))

		ranlib_args = [user_cfg.ranlib_prog]
		if user_cfg.ranlib_flags is not None: ranlib_args.append(user_cfg.ranlib_flags)
		if __debug__ and is_debug: debug('cfg: cxx: user: impl: gcc: ranlib: ' + str(ranlib_args))

		return ld_args, ar_args, ranlib_args

	@staticmethod
	def dev_cfg_ld_args(dev_cfg, args):
		if dev_cfg.shared: args.append('-shared')
		for p in dev_cfg.libs_paths: args += ['-L', p.path]
		for l in dev_cfg.libs: args.append('-l' + l)
		if len(dev_cfg.static_libs):
			args.append('-Wl,-Bstatic')
			for l in dev_cfg.static_libs: args.append('-l' + l)
		if len(dev_cfg.static_libs):
			args.append('-Wl,-Bdynamic')
			for l in dev_cfg.shared_libs: args.append('-l' + l)
		if __debug__ and is_debug: debug('cfg: cxx: dev: impl: gcc: ld: ' + str(args))
	
	@staticmethod
	def mod_task_sig(mod_task): return ''

	@staticmethod
	def mod_task_target(mod_task):
		dir = mod_task.project.bld_node.node_path('modules').node_path(mod_task.name)
		if mod_task.cfg.kind == 'prog': name = mod_task.name
		elif mod_task.cfg.shared: name = 'lib' + mod_task.name + '.so'
		else: name = 'lib' + mod_task.name + '.a'
		return dir.node_path(name)

	@staticmethod
	def process_mod_task(mod_task):
		if mod_task.cfg.ld:
			args = mod_task.cfg.mod_args[:]
			args[2] = mod_task.target.path
			args[3] = [s.path for s in mod_task.sources]
			args = args[:3] + args[3] + args[4:]
			r = exec_subprocess(args)
			if r != 0: raise Exception, r
		else:
			ar_args, ranlib_args = mod_task.cfg.mod_args
			args = ar_args[:]
			args.append(mod_task.target.path)
			args += [s.path for s in mod_task.sources]
			r = exec_subprocess(args)
			if r != 0: raise Exception, r
			if 's' not in mod_task.user_cfg.ar_flags:
				args = ranlib_args[:]
				args.append(mod_task.target.path)
				r = exec_subprocess(args)
				if r != 0: raise Exception, r

	@staticmethod
	def batch_process_mod_task(mod_task):
		args = CfgImpl.user_cfg_cxx_args(mod_task.cfg.user_cfg)
		CfgImpl.dev_cfg_cxx_args(mod_task.cfg, args)[:]

		inputs = []
		for s in mod_task.sources:
			if s.changed: inputs.append(s)
			else:
				old_sig, implicit_deps = mod_task.project.task_states[s.uid]
				for d in implicit_deps:
					if d.changed: inputs.append(s)

		base_names = set()
		for i in inputs:
			if i.name not in base_names: args.append(i.rel_path(mod_task.target.parent))
			else:
				name = i.rel_path(mod_task.project.src_node)
				name.replace(os.sep, ',')
				name.replace(os.pardir, '_')
				args.append(name)
				n = mod_task.target.parent.node_path(name)
				if not n.exists:
					f = open(n.path, 'w')
					try:
						f.write('#include "')
						f.write(i.rel_path(mod_task.target.parent))
						f.write('"')
					finally: f.close()
			base_names.add(i.name)

		exec_subprocess(args, cwd = mod_task.target.parent.path)
