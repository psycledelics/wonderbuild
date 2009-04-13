#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2009-2009 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

from wonderbuild.script import ScriptTask

class Wonderbuild(ScriptTask):
	def __call__(self, sched_ctx):

		src_dir = self.src_dir / 'src'
		project = self.project

		from wonderbuild.install import InstallTask
	
		class Diversalis(InstallTask):
			def __init__(self): InstallTask.__init__(self, project)

			@property
			def trim_prefix(self): return src_dir

			@property
			def sources(self):
				try: return self._sources
				except AttributeError:
					self._sources = []
					for s in (self.trim_prefix / 'diversalis').find_iter(in_pats = ['*.hpp'], ex_pats = ['*.private.hpp'], prune_pats = ['todo']): self._sources.append(s)
					return self._sources
	
			@property
			def dest_dir(self): return self.fhs.include
		
		self.project.add_task_aliases(Diversalis(), 'all')
