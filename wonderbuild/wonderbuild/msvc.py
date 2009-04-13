#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2007-2009 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

import os

from logger import is_debug, debug, colored
from signature import Sig
from cpp_include_scanner import IncludeScanner

class Impl(object):
	def __init__(self, persistent):
		self.cpp = IncludeScanner(persistent)

	@property
	def cxx_prog(self): return 'cl'

	@property
	def cxx_env_sig(self):
		sig = Sig()
		e = os.environ.get('INCLUDE', None)
		if e is not None: sig.update(e)
		return sig.digest()

	@staticmethod
	def user_cfg_cxx_args(user_cfg):
		args = [user_cfg.cxx_prog, '-Fo', None, None]
		if user_cfg.debug: args.append('-D')
		if user_cfg.optim is not None: args.append('-O' + user_cfg.optim)
		args += user_cfg.cxx_flags
		if __debug__ and is_debug: debug('cfg: cxx: msvc: compiler: ' + str(args))
		return args

	@staticmethod
	def dev_cfg_cxx_args(dev_cfg, args):
		if dev_cfg.pic: args.append('-xxxx')
		for p in dev_cfg.include_paths: args += ['-I', p.path]
		for k, v in dev_cfg.defines.iteritems():
			if v is None: args.append('-D' + k)
			else: args.append('-D' + k + '=' + v)
	
	@staticmethod
	def process_cxx_task(cxx_task): pass

	if True: # faster
		@staticmethod
		def post_process_cxx_task(cxx_task): cxx_task.project.persistent[cxx_task.uid] = (cxx_task.sig, cxx_task._implicit_deps)

		@staticmethod
		def cxx_task_sig(cxx_task):
			sig = Sig(cxx_task.cfg.sig)
			sig.update(cxx_task.source.sig)
			new_implicit_deps = False
			try: old_sig, cxx_task._implicit_deps = cxx_task.project.persistent[cxx_task.uid]
			except KeyError:
				old_sig = None
				cxx_task._implicit_deps, not_found = cxx_task.cfg.user_cfg.cpp.scan_deps(cxx_task.source, cxx_task.cfg.include_paths)
				if __debug__ and is_debug and len(not_found): debug('cpp: deps not found: ' + cxx_task.source.path + ': '+ str([str(x) for x in not_found]))
				new_implicit_deps = True
				sigs = [s.sig for s in cxx_task._implicit_deps]
			else:
				try: sigs = [s.sig for s in cxx_task._implicit_deps]
				except OSError:
					# A cached implicit dep does not exist anymore.
					# We must recompute the implicit deps.
					cxx_task._implicit_deps, not_found = cxx_task.cfg.user_cfg.cpp.scan_deps(cxx_task.source, cxx_task.cfg.include_paths)
					if __debug__ and is_debug and len(not_found): debug('cpp: deps not found: ' + cxx_task.source.path + ': '+ str([str(x) for x in not_found]))
					new_implicit_deps = True
					sigs = [s.sig for s in cxx_task._implicit_deps]
			sigs.sort()
			sig.update(''.join(sigs))
			sig = sig.digest()
			if sig != old_sig:
				if __debug__ and is_debug: debug('task: sig changed: ' + cxx_task.target.path)
				if not new_implicit_deps:
					# Either the include path or a source or header content has changed.
					# We must recompute the implicit deps.
					sig = Sig(cxx_task.cfg.sig)
					sig.update(cxx_task.source.sig)
					cxx_task._implicit_deps, not_found = cxx_task.cfg.user_cfg.cpp.scan_deps(cxx_task.source, cxx_task.cfg.include_paths)
					if __debug__ and is_debug and len(not_found): debug('cpp: deps not found: ' + cxx_task.source.path + ': '+ str([str(x) for x in not_found]))
					sigs = [s.sig for s in cxx_task._implicit_deps]
					sigs.sort()
					sig.update(''.join(sigs))
					sig = sig.digest()
			return sig
	else: # slower
		@staticmethod
		def post_process_cxx_task(cxx_task): cxx_task.project.persistent[cxx_task.uid] = (cxx_task.sig, cxx_task._implicit_deps, cxx_task._implicit_deps_sig)

		@staticmethod
		def cxx_task_sig(cxx_task):
			scan_implicit_deps = False
			try: old_sig, cxx_task._implicit_deps, cxx_task._implicit_deps_sig = cxx_task.project.persistent[cxx_task.uid]
			except KeyError:
				old_sig = None
				scan_implicit_deps = True
			else:
				try:
					for dep in cxx_task._implicit_deps:
						if dep.changed:
							scan_implicit_deps = True
							break
				except OSError:
					# A cached implicit dep does not exist anymore.
					# We must recompute the implicit deps.
					scan_implicit_deps = True
			if scan_implicit_deps: CfgImpl._do_scan_implicit_deps(cxx_task)
			sig = Sig(cxx_task.cfg.sig)
			sig.update(cxx_task.source.sig)
			sig.update(cxx_task._implicit_deps_sig)
			sig = sig.digest()
			if sig != old_sig:
				if __debug__ and is_debug: debug('task: sig changed: ' + cxx_task.target.path)
				if not scan_implicit_deps:
					# Either the include path or the source content has changed.
					# We must recompute the implicit deps.
					CfgImpl._do_scan_implicit_deps(cxx_task)
					sig = Sig(cxx_task.cfg.sig)
					sig.update(cxx_task.source.sig)
					sig.update(cxx_task._implicit_deps_sig)
					sig = sig.digest()
			return sig

		@staticmethod
		def _do_scan_implicit_deps(cxx_task):
			if __debug__ and is_debug: debug('task: scanning implicit deps: ' + cxx_task.source.path)
			cxx_task._implicit_deps, not_found = cxx_task.cfg.user_cfg.cpp.scan_deps(cxx_task.source, cxx_task.cfg.include_paths)
			sigs = [s.sig for s in cxx_task._implicit_deps]
			sigs.sort()
			cxx_task._implicit_deps_sig = Sig(''.join(sigs)).digest()

	@property
	def ld_prog(self): return 'link'
	
	@property
	def ar_prog(self): return 'lib'
	
	@property
	def ranlib_prog(self): return None
	
	@property
	def mod_env_sig(self): return ''

	@staticmethod
	def user_cfg_mod_args(user_cfg):
		ld_args = [user_cfg.ld_prog, '-o', None, None] + user_cfg.ld_flags
		if __debug__ and is_debug: debug('cfg: cxx: msvc: ld: ' + str(ld_args))

		ar_args = [user_cfg.ar_prog]
		if user_cfg.ar_flags is not None: ar_args.append(user_cfg.ar_flags)
		if __debug__ and is_debug: debug('cfg: cxx: msvc: ar: ' + str(ar_args))

		return ld_args, ar_args

	@staticmethod
	def dev_cfg_mod_args(dev_cfg, args):
		if dev_cfg.shared: args.append('-shared')
		for p in dev_cfg.libs_paths: args += ['-libpath', p.path]
		for l in dev_cfg.libs: args.append(l + '.lib')
		if len(dev_cfg.static_libs):
			for l in dev_cfg.static_libs: args.append('lib' + l + '.lib')
		if len(dev_cfg.static_libs):
			for l in dev_cfg.shared_libs: args.append(l + '.lib')
	
	@staticmethod
	def mod_task_sig(mod_task): return ''

	@staticmethod
	def mod_task_target(mod_task):
		dir = mod_task.project.bld_dir / 'modules' / mod_task.name
		if mod_task.cfg.kind == 'prog': name = mod_task.name
		elif mod_task.cfg.shared: name = mod_task.name + '.dll'
		else: name = 'lib' + mod_task.name + '.lib'
		return dir / name

	@staticmethod
	def process_mod_task(mod_task): pass

	@staticmethod
	def batch_process_mod_task(mod_task):
		args = CfgImpl.user_cfg_cxx_args(mod_task.cfg.user_cfg)
		CfgImpl.dev_cfg_cxx_args(mod_task.cfg, args)[:]

		inputs = []
		for s in mod_task.sources:
			if s.changed: inputs.append(s)
			else:
				old_sig, implicit_deps = mod_task.project.persistent[s.uid]
				for d in implicit_deps:
					if d.changed: inputs.append(s)

		base_names = set()
		for i in inputs:
			if i.name not in base_names: args.append(i.rel_path(mod_task.target.parent))
			else:
				name = i.rel_path(mod_task.project.top_src_dir)
				name.replace(os.sep, ',')
				name.replace(os.pardir, '_')
				args.append(name)
				n = mod_task.target.parent / name
				if not n.exists:
					f = open(n.path, 'w')
					try:
						f.write('#include "')
						f.write(i.rel_path(mod_task.target.parent))
						f.write('"')
					finally: f.close()
			base_names.add(i.name)

		old_cur_dir = os.cwd()
		os.chdir(mod_task.target.parent.path)
		exec_subprocess(args)
		os.chdir(old_cur_dir)
