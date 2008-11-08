#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006-2008 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

class TaskMaster:
	def __init__(self):
		self._tasks = []
		self._leaf_tasks = []
		self._ready_tasks = []
		self._done_tasks = []

