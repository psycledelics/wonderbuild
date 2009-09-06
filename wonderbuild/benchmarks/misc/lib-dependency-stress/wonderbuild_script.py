#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2009-2009 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

if __name__ == '__main__':
	import sys, os
	dir = os.path.dirname(__file__)
	sys.argv.append('--src-dir=' + dir)
	try: from wonderbuild.main import main
	except ImportError:
		dir = os.path.abspath(os.path.join(dir, os.pardir, os.pardir, os.pardir))
		if dir not in sys.path: sys.path.append(dir)
		try: from wonderbuild.main import main
		except ImportError:
			print >> sys.stderr, 'could not find wonderbuild'
			sys.exit(1)
		else: main()
	else: main()

else:
	from wonderbuild.script import ScriptTask, ScriptLoaderTask

	class Wonderbuild(ScriptTask):
		def __call__(self, sched_ctx):
			from wonderbuild.cxx_tool_chain import UserBuildCfgTask, ModTask

			src_dir = self.src_dir / 'src'
		
			class CustomBuildCfgTask(UserBuildCfgTask):
				def __call__(self, sched_ctx):
					for x in UserBuildCfgTask.__call__(self, sched_ctx): yield x
					self.cxx_flags = ['-g', '-O0', '-Wall']
					#self.shared = self.pic = False
					self.defines['WRAPPER'] = None
					self.include_paths.append(src_dir)
		
			build_cfg = CustomBuildCfgTask(self.project)
			for x in sched_ctx.parallel_wait(build_cfg): yield x
			
			class Wrapper(ModTask):
				def __init__(self, i):
					ModTask.__init__(self, 'wrapper' + str(i), ModTask.Kinds.LIB, build_cfg)
					self.i = i
	
				def __call__(self, sched_ctx):
					self.private_deps = [wrappers[j] for j in xrange(self.i)]
					self.result = True
					for x in ModTask.__call__(self, sched_ctx): yield x

				def do_mod_phase(self):
					self.sources = [src_dir / ('wrapper' + str(self.i)) / 'wrapper.cpp']

			count = 0
			for n in src_dir.find_iter(in_pats = ('wrapper*',), prune_pats = ('*',)): count += 1
			wrappers = [Wrapper(i) for i in xrange(count)]
			self.project.add_task_aliases(wrappers[-1].mod_phase, 'default')
