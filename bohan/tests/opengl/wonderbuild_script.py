#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2009-2009 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

if __name__ == '__main__':
	import sys, os
	dir = os.path.dirname(__file__)
	sys.argv.append('--src-dir=' + dir)
	try: from wonderbuild.main import main
	except ImportError:
		dir = os.path.abspath(os.path.join(dir, os.pardir, 'build-systems', 'wonderbuild'))
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
			tasks = [
				ScriptLoaderTask.shared(self.project, dir) \
				for dir in (
					self.src_dir / 'eagl',
					self.src_dir / 'gl',
					self.src_dir / 'gles',
					self.src_dir / 'glut',
					self.src_dir / 'glsl',
					self.src_dir / 'gtkglextmm'
				)
			]
			from wonderbuild.cxx_tool_chain import UserBuildCfgTask
			cfg = UserBuildCfgTask.shared(self.project)
			for x in sched_ctx.parallel_wait(cfg, *tasks): yield x
			if cfg.dest_platform.os == 'darwin' and cfg.dest_platform.arch == 'arm':
				for t in tasks[0:1]: self.default_tasks += t.script_task.default_tasks
			else:
				for t in tasks[1:]: self.default_tasks += t.script_task.default_tasks
