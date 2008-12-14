#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006-2008 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

def main():
	import sys, os
	sys.path.append(os.path.split(os.path.abspath(os.path.join(os.getcwd(), os.pardir)))[0])

	from wonderbuild.project import Project
	project = Project()

	from wonderbuild.cxx_chain import BaseObjConf, BaseModConf
	base_obj_conf = BaseObjConf(project)
	base_mod_conf = BaseModConf(base_obj_conf)

	from wonderbuild.cxx_chain import PkgConf, ObjConf, ModConf, Mod

	top_src_dir = project.src_node.node_path('bench')

	bench_libs = []
