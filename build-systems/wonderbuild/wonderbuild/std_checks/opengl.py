#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006-2010 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

from wonderbuild.cxx_tool_chain import BuildCheckTask

class OpenGLCheckTask(BuildCheckTask):

	@staticmethod
	def shared_uid(*args, **kw): return 'opengl'

	def apply_to(self, cfg):
		cfg.defines['GL_GLEXT_PROTOTYPES'] = None
		if cfg.dest_platform.os == 'darwin':
			if cfg.dest_platform.arch == 'arm': cfg.frameworks.append('OpenGLES')
			else: cfg.frameworks.append('OpenGL')
		else: cfg.libs.append('GL')

	@property
	def source_text(self): return '''\
#if defined __APPLE__
	#if defined __arm__
		#include <OpenGLES/ES2/gl.h>
	#else
		#include <OpenGL/OpenGL.h>
	#endif
#else
	#include <GL/gl.h>
#endif
void gl() {
	// todo do something with it for a complete check
}
'''

class OpenGLUCheckTask(BuildCheckTask):

	@staticmethod
	def shared_uid(*args, **kw): return 'openglu'

	def __call__(self, sched_ctx):
		self.public_deps = [OpenGLCheckTask.shared(self.base_cfg)]
		for x in BuildCheckTask.__call__(self, sched_ctx): yield x

	def apply_to(self, cfg):
		if cfg.dest_platform.os != 'darwin': cfg.libs.append('GLU')

	@property
	def source_text(self): return '''\
#if defined __APPLE__
	#include <OpenGL/glu.h>
#else
	#include <GL/glu.h>
#endif
void glu() {
	// todo do something with it for a complete check
}
'''

class OpenGLUTCheckTask(BuildCheckTask):

	@staticmethod
	def shared_uid(*args, **kw): return 'openglut'

	def __call__(self, sched_ctx):
		self.public_deps = [OpenGLUCheckTask.shared(self.base_cfg)]
		for x in BuildCheckTask.__call__(self, sched_ctx): yield x

	def apply_to(self, cfg):
		if cfg.dest_platform.os == 'darwin': cfg.frameworks.append('GLUT')
		else: cfg.libs.append('glut')

	@property
	def source_text(self): return '''\
#if defined __APPLE__
	#include <GLUT/glut.h>
#else
	#include <GL/glut.h>
#endif
void glut() {
	// todo do something with it for a complete check
}
'''
