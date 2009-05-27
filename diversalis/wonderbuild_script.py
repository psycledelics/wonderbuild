#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2009-2009 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

if __name__ == '__main__':
	try: from wonderbuild.main import main
	except ImportError:
		import sys, os
		dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'build-systems'))
		if dir not in sys.path: sys.path.append(dir)
		try: from wonderbuild.main import main
		except ImportError:
			print >> sys.stderr, 'could not find wonderbuild'
			sys.exit(1)
		else: main()
	else: main()

from wonderbuild.script import ScriptTask

class Wonderbuild(ScriptTask):

	@property
	def client_headers(self): return self._client_headers

	def __call__(self, sched_ctx):
		project = self.project
		src_dir = self.src_dir / 'src'

		from wonderbuild.install import InstallTask
	
		class ClientHeaders(InstallTask):
			def __init__(self): InstallTask.__init__(self, project)

			@property
			def trim_prefix(self): return src_dir

			@property
			def dest_dir(self): return self.fhs.include

			@property
			def sources(self):
				try: return self._sources
				except AttributeError:
					self._sources = []
					for s in (self.trim_prefix / 'diversalis').find_iter(
							in_pats = ('*.hpp',),
							ex_pats = ('*.private.hpp',),
							prune_pats = ('todo',)
						): self._sources.append(s)
					return self._sources
			
			def apply_to(self, cfg):
				if not self.fhs.include in cfg.include_paths: cfg.include_paths.append(self.fhs.include)
		
		self._client_headers = ClientHeaders()
		self.project.add_task_aliases(self._client_headers, 'diversalis', 'all')
