#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006-2009 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

from wonderbuild.cxx_tool_chain import BuildCheckTask

# gcc -E -dM -std=c++98 -x c++-header /dev/null | sort

class BinaryFormatElfCheckTask(BuildCheckTask):
	def __init__(self, base_cfg): BuildCheckTask.__init__(self, 'binary-format-elf', base_cfg, compile=False)

	@property
	def source_text(self): return \
		'#if !defined __ELF__\n' \
		'	#error the target platform binary format is not elf\n' \
		'#endif'

class BinaryFormatPeCheckTask(BuildCheckTask):
	@staticmethod
	def shared(base_cfg):
		try: return base_cfg.project.target_platform_binary_format_is_pe
		except AttributeError:
			task = base_cfg.project.target_platform_binary_format_is_pe = BinaryFormatPeCheckTask(base_cfg)
			return task
		
	def __init__(self, base_cfg): BuildCheckTask.__init__(self, 'binary-format-pe', base_cfg, compile=False)

	@property
	def source_text(self): return \
		'#if !defined _WIN32 && !defined __CYGWIN__\n' \
		'	#error the target platform binary format is not pe\n' \
		'#endif'

class MSWindowsCheckTask(BuildCheckTask):
	def __init__(self, base_cfg): BuildCheckTask.__init__(self, 'mswindows', base_cfg, compile=False)

	@property
	def source_text(self): return \
		'#if !defined _WIN32\n' \
		'	#error the target platform is not mswindows\n' \
		'#endif'

class CygwinCheckTask(BuildCheckTask):
	def __init__(self, base_cfg): BuildCheckTask.__init__(self, 'cygwin', base_cfg, compile=False)

	@property
	def source_text(self): return \
		'#if !defined __CYGWIN__\n' \
		'	#error the target platform is not cygwin\n' \
		'#endif'

class MingwCheckTask(BuildCheckTask):
	def __init__(self, base_cfg): BuildCheckTask.__init__(self, 'mingw', base_cfg, compile=False)

	@property
	def source_text(self): return \
		'#if defined __MINGW32__\n' \
		'	#error this is not mingw gcc\n' \
		'#endif'

class AutoLinkSupportCheckTask(BuildCheckTask):
	def __init__(self, base_cfg): BuildCheckTask.__init__(self, 'auto-link', base_cfg, compile=False)

	@property
	def source_text(self):
		try: return self._source_text
		except AttributeError:
			# TODO don't include <boost/config.hpp>
			self._source_text = \
				"""
					// text below copied from <boost/config/auto_link.hpp>
					#include <boost/config.hpp>
					#if !( \\
							defined BOOST_MSVC || \\
							defined __BORLANDC__ || \\
							__MWERKS__ >= 0x3000 && _WIN32 || \\
							defined __ICL && defined _MSC_EXTENSIONS && _MSC_VER >= 1200 \\
					)
						#error no auto link support
					#endif
				"""
			return self._source_text

from pthread import PThreadCheckTask
from std_math import StdMathCheckTask
from dlfcn import DlfcnCheckTask
from boost import BoostCheckTask
