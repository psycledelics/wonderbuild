#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006-2008 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

import sys, os

p = os.path.split(os.path.abspath(os.path.join(os.getcwd(), os.pardir)))[0]
print 'xx', p
sys.path.append(p)

from wonderbuild.project import Project
project = Project()

from wonderbuild.cxx_chain import BaseObjConf, BaseModConf
base_obj_conf = BaseObjConf(project)
base_mod_conf = BaseModConf(base_obj_conf)

