#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006-2008 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

class RootProject: pass
class Project : pass

class Contexes:
	def check_and_build(self):
		'when performing build checks, or building the sources'
		pass
		
	def build(self):
		'when building the sources'
		pass
		
	def source(self):
		'when building a tarball of the sources'
		pass
	
	class client:
		'when used as a dependency'
		pass

class Cxx(Cmd): pass
class GnuCxx(Cxx): pass
class MingwGnuCxx(GnuCxx): pass
class MsCxx(Cxx): pass

class Archiver(Cmd): pass
class GnuArchiver(Archiver): pass
class MsArchiver(Archiver): pass

class ArchiveIndexer(Cmd): pass
class GnuArchiveIndexer(ArchiveIndexer): pass
class MsArchiveIndexer(ArchiveIndexer): pass

class Linker(Cmd): pass
class GnuLinker(Linker): pass
class MingwGnuLinker(GnuLinker): pass
class MsLinker(Linker): pass

class Chain:
	def __init__(self, compilers, archiver, archive_indexer, linker):
		self._compilers = compilers
		self._archiver = archiver
		self._archive_indexer = archive_indexer
		self._linker = linker

