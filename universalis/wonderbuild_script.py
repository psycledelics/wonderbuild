#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2009-2009 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

from wonderbuild.script import ScriptTask

class Wonderbuild(ScriptTask):
	def __call__(self, sched_ctx):

		diversalis = self.project.script_task(self.src_dir.parent / 'diversalis')

		project = self.project
		src_dir = self.src_dir / 'src'

		from wonderbuild.install import InstallTask
	
		class Universalis(InstallTask):
			def __init__(self): InstallTask.__init__(self, project)

			@property
			def trim_prefix(self): return src_dir

			@property
			def sources(self):
				try: return self._sources
				except AttributeError:
					self._sources = []
					for s in (self.trim_prefix / 'universalis').find_iter(in_pats = ['*.hpp'], ex_pats = ['*.private.hpp'], prune_pats = ['todo']): self._sources.append(s)
					return self._sources
	
			@property
			def dest_dir(self): return self.fhs.include
		
			def __call__(self, sched_ctx):
				sched_ctx.parallel_wait(diversalis)
				InstallTask.__call__(self, sched_ctx)
		
		self.project.add_task_aliases(Universalis(), 'all')
