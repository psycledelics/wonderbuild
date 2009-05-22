#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006-2009 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

import sys

from wonderbuild.cxx_tool_chain import MultiBuildCheckTask, BuildCheckTask
from wonderbuild.signature import Sig
from wonderbuild.logger import silent, is_debug, debug

from wonderbuild.std_checks import AutoLinkSupportCheckTask, MingwCheckTask

class BoostCheckTask(MultiBuildCheckTask):
	def __init__(self, min_version_tuple, lib_names, base_cfg):
		# TODO remove useless trailing zeroes in the version tuple
		MultiBuildCheckTask.__init__(
			self, 'boost-' + '.'.join(str(i) for i in min_version_tuple) + \
			'-libs-' + ','.join(lib_names), base_cfg
		)
		self.min_version_tuple = min_version_tuple
		self.lib_names = lib_names

	@property
	def result(self): return self.results[0]

	@property
	def include_path(self): return self.results[1]

	@property
	def libs(self): return self.results[2]

	def apply_to(self, cfg):
		if self.include_path is not None: cfg.include_paths.append(self.include_path)
		cfg.libs.extend(self.libs)

	@property
	def source_text(self): return '' # TODO see property in AllInOneCheckTask class

	def do_check_and_set_result(self, sched_ctx):
		failed = False, None, None
		read_version = BoostCheckTask.ReadVersion(self)
		sched_ctx.parallel_wait(read_version)
		include_path = None
		if not read_version.result:
			if sys.platform != 'cygwin':
				self.results = failed
				return
				
			# damn cygwin installs boost headers in e.g. /usr/include/boost-1_33_1/
			dir = self.project.fs.root / 'usr' / 'include'
			try:
				if dir.exists and dir.is_dir:
					max_entry = None
					max_entry_version = [0]
					for entry in dir.actual_children.itervalues():
						if entry.name.startswith('boost-'):
							if __debug__ and is_debug: debug('cfg: boost: found headers in ' + str(entry))
							entry_version = entry.name[len('boost-'):].split('_')
							for i in xrange(len(max_entry_version)):
								if i >= len(entry_version): break
								try: a = int(entry_version[i])
								except ValueError:
									if __debug__ and is_debug: debug('cfg: boost: ignoring non-integer versioned headers ' + str(entry))
									break
								b = max_entry_version[i]
								if a > b:
									max_entry = entry
									max_entry_version[i] = a
									for s in entry_version[len(max_entry_version):]:
										try: max_entry_version.append(int(s))
										except ValueError:
											if __debug__ and is_debug: debug('cfg: boost: ignoring non-integer in version for headers ' + str(entry))
											break
									break
								if a < b: break
					if max_entry is not None:
						if len(self.min_version_tuple) == 0: include_path = max_entry
						else:
							for i in xrange(len(self.min_version_tuple)):
								if i >= len(max_entry_version): a = 0
								else: a = max_entry_version[i]
								b = self.min_version_tuple[i]
								if a > b: include_path = max_entry; break
								if a < b: break
								if i == len(self.min_version_tuple) - 1: include_path = max_entry
					if include_path is None:
						self.results = self.results = failed
						return
					if __debug__ and is_debug: debug('cfg: boost: selected headers ' + str(entry))
					read_version = BoostCheckTask.ReadVersion(self)
					sched_ctx.parallel_wait(read_version)
					if not read_version.result:
						self.results = self.results = failed
						return
			finally: pass # dir.forget()
		
		selected_source_texts = [self.source_texts()[lib] for lib in self.lib_names]
		lib_version = '-' + read_version.lib_version
		
		def link_check(toolset = None, lib_version = None):
			threading = '-mt'
			abi = ''
			variant = (toolset or '') + (threading or '') + (abi or '') + (lib_version or '')
			link_libs = toolset is not None and [lib + variant for lib in self.lib_names] or []
			cfg_link_libs = ['boost_' + lib for lib in link_libs]
			outer = self
			class AllInOneCheckTask(BuildCheckTask):
				def __init__(self): BuildCheckTask.__init__(
					self, 'boost-' + '.'.join(str(i) for i in outer.min_version_tuple) + \
					'-link-' + ','.join(outer.lib_names) + \
					variant, outer.base_cfg
				)
			
				@property
				def source_text(self):
					try: return self._source_text
					except AttributeError:
						self._source_text = '\n'.join(selected_source_texts)
						return self._source_text
			
				def do_check_and_set_result(self, sched_ctx):
					if include_path is not None: self.cfg.include_paths.append(include_path)
					self.cfg.libs += cfg_link_libs
					BuildCheckTask.do_check_and_set_result(self, sched_ctx)

			all_in_one = AllInOneCheckTask()
			sched_ctx.parallel_wait(all_in_one)
			if not all_in_one.result: self.results = failed;
			else: self.results = True, include_path, cfg_link_libs;
			return self.result

		auto_link_support_check_task = AutoLinkSupportCheckTask.shared(self.base_cfg)
		sched_ctx.parallel_wait(auto_link_support_check_task)
		if auto_link_support_check_task.result: link_check()
		else:
			if self.base_cfg.kind == 'gcc':
				mingw_check_task = MingwCheckTask.shared(self.base_cfg)
				sched_ctx.parallel_wait(mingw_check_task)
				toolset = mingw_check_task.result and '-mgw' or '-gcc'
				versioned_toolset = toolset + str(self.base_cfg.version[0]) + str(self.base_cfg.version[1])
			elif self.base_cfg.kind == 'msvc':
				toolset = '-vc'
				versioned_toolset = toolset + str(self.base_cfg.version[0] - 6) + str(self.base_cfg.version[1])
			else:
				toolset = ''
				versioned_toolset = None
			versioned_toolset is not None and \
				link_check(versioned_toolset, lib_version) or \
				link_check(toolset, lib_version) or \
				link_check(toolset, '') or \
				link_check('', '')

	class ReadVersion(BuildCheckTask):
			def __init__(self, outer):
				BuildCheckTask.__init__(
					self, 'boost-' + '.'.join(str(i) for i in outer.min_version_tuple),
					outer.base_cfg, pipe_preproc=True
				)
				self._outer = outer
			
			@property
			def source_text(self):
				try: return self._source_text
				except AttributeError:
					self._source_text = \
						'#include <boost/version.hpp>\n' \
						'BOOST_VERSION\n' \
						'BOOST_LIB_VERSION\n'
					return self._source_text
			
			def do_check_and_set_result(self, sched_ctx):
				BuildCheckTask.do_check_and_set_result(self, sched_ctx)
				r, out = self.results
				if not r: self.results = False, None, None
				else:
					out = out.split()[-2:]
					int_version = int(out[0])
					min_version_tuple = self._outer.min_version_tuple
					min_int_version = min_version_tuple[0] * 100000
					if len(min_version_tuple) >= 2: min_int_version += min_version_tuple[1] * 100
					if len(min_version_tuple) >= 3: min_int_version += min_version_tuple[2]
					ok = int_version >= min_int_version
					self.results = ok, int_version, out[1].strip('"')
			
			@property
			def result(self): return self.results[0]
			
			@property
			def int_version(self): return self.results[1]
			
			@property
			def lib_version(self): return self.results[2]
			
			@property
			def result_display(self):
				version = self.int_version is not None and ' (found version ' + str(self.lib_version).replace('_', '.') + ')' or ''
				if self.result: return 'yes' + version, '32'
				else: return 'no' + version, '31'

	@classmethod
	def source_texts(class_):
		try: return class_._source_texts
		except AttributeError:
			source_texts = {}

			def auto_link(name, dynamic = True):
				result = \
					"""
						#define BOOST_LIB_NAME boost_%s
					""" % name
				if dynamic: result += \
					"""
						#if defined _DLL || defined _RTLDLL // as tested in <boost/config/auto_link.hpp>
							#define BOOST_DYN_LINK
						#endif
					"""
				result += \
					"""
						#define BOOST_LIB_DIAGNOSTIC
						#include <boost/config/auto_link.hpp>
					"""
				return result

			source_texts['signals'] = \
				"""
					#include <boost/signals/slot.hpp>
					void signals() { /* todo do something with it for a complete check */ }
				""" + auto_link('signals')
			source_texts['thread'] = \
				"""
					#include <boost/thread/thread.hpp>
					void thread() { boost::thread thread; }
				""" + auto_link('thread')
			source_texts['filesystem'] = \
				"""
					#include <boost/filesystem/path.hpp>
					#include <boost/filesystem/operations.hpp>
					void filesystem() { boost::filesystem::path path(boost::filesystem::current_path()); }
				""" + auto_link('filesystem')
			source_texts['serialization'] = \
				"""
					#include <boost/serialization/serialization.hpp>
					#include <boost/archive/basic_archive.hpp>
					void serialization() { /* todo do something with it for a complete check */ }
				""" + auto_link('serialization')
			source_texts['wserialization'] = \
				"""
					#include <boost/serialization/serialization.hpp>
					#include <boost/archive/basic_archive.hpp>
					void wserialization() { /* todo do something with it for a complete check */ }
				""" + auto_link('wserialization')
			source_texts['iostream'] = \
				"""
					//#include <boost/...>
					void iostream() { /* todo do something with it for a complete check */ }
				""" + auto_link('iostream')
			source_texts['regex'] = \
				"""
					#include <boost/regex.hpp>
					void regex() { /* todo do something with it for a complete check */ }
				""" + auto_link('regex')
			source_texts['program_options'] = \
				"""
					#include <boost/program_options.hpp>
					void program_options() { /* todo do something with it for a complete check */ }
				""" + auto_link('program_options')
			source_texts['python'] = \
				"""
					#include <boost/python.hpp>
					void python() { /* todo do something with it for a complete check */ }
				""" + auto_link('python')
			source_texts['date_time'] = \
				"""
					#include <boost/date_time/period.hpp>
					void date_time() { /* todo do something with it for a complete check */ }
				""" + auto_link('date_time')
			source_texts['unit_test_framework'] = \
				"""
					#include <boost/test/framework.hpp>
					void unit_test_framework() { /* todo do something with it for a complete check */ }
				""" + auto_link('unit_test_framework', dynamic = False)
			source_texts['prg_exec_monitor'] = \
				"""
					#include <boost/test/execution_monitor.hpp>
					void prg_exec_monitor() { /* todo do something with it for a complete check */ }
				""" + auto_link('prg_exec_monitor', dynamic = False)
			source_texts['test_exec_monitor'] = \
				"""
					#include <boost/test/execution_monitor.hpp>
					void test_exec_monitor() { /* todo do something with it for a complete check */ }
				""" + auto_link('test_exec_monitor', dynamic = False)
			source_texts['wave'] = \
				"""
					#include <boost/wave/wave_version.hpp>
					void wave() { /* todo do something with it for a complete check */ }
				""" + auto_link('wave', dynamic = False)
			
			class_._source_texts = source_texts
			return source_texts
