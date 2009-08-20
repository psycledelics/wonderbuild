#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006-2009 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

from wonderbuild.cxx_tool_chain import BuildCheckTask, ok_color, failed_color

# gcc -E -dM -std=c++98 -x c++-header /dev/null | sort

class BinaryFormatCheckTask(BuildCheckTask):
	@staticmethod
	def shared(base_cfg):
		try: return base_cfg.project.target_platform_binary_format
		except AttributeError:
			task = base_cfg.project.target_platform_binary_format = BinaryFormatCheckTask(base_cfg)
			return task

	def __init__(self, base_cfg): BuildCheckTask.__init__(self, 'binary-format', base_cfg, pipe_preproc=True)
	
	@property
	def source_text(self): return \
		'#if defined __ELF__\n' \
		'	elf\n' \
		'#elif defined __APPLE__ and defined __MACH__\n' \
		'	mac-o\n' \
		'#elif defined _WIN32 || defined __CYGWIN__ || defined __MSYS__ || defined _UWIN\n' \
		'	pe\n' \
		'#else\n' \
		'	#error unkown binary format\n' \
		'#endif\n'
	
	def do_check_and_set_result(self, sched_ctx):
		for x in BuildCheckTask.do_check_and_set_result(self, sched_ctx): yield x
		r, out = self.results
		if not r: self.results = False, None
		else: self.results = True, out.split('\n')[-2][1:]
	
	@property
	def result(self): return self.results[0]
	
	@property
	def format(self): return self.results[1]
	
	@property
	def result_display(self):
		if self.result: return self.format, ok_color
		else: return 'unkown (neither of elf, mac-o, nor pe)', failed_color

class MSWindowsCheckTask(BuildCheckTask):
	@staticmethod
	def shared(base_cfg):
		try: return base_cfg.project.target_platform_is_mswindows
		except AttributeError:
			task = base_cfg.project.target_platform_is_mswindows = MSWindowsCheckTask(base_cfg)
			return task

	def __init__(self, base_cfg): BuildCheckTask.__init__(self, 'ms-windows', base_cfg, compile=False)

	@property
	def source_text(self): return \
		'#if !defined _WIN32\n' \
		'	#error the target platform is not mswindows\n' \
		'#endif\n'

class CygwinCheckTask(BuildCheckTask):
	@staticmethod
	def shared(base_cfg):
		try: return base_cfg.project.target_platform_is_cygwin
		except AttributeError:
			task = base_cfg.project.target_platform_is_cygwin = CygwinCheckTask(base_cfg)
			return task

	def __init__(self, base_cfg): BuildCheckTask.__init__(self, 'cygwin', base_cfg, compile=False)

	@property
	def source_text(self): return \
		'#if !defined __CYGWIN__\n' \
		'	#error the target platform is not cygwin\n' \
		'#endif\n'

class MingwCheckTask(BuildCheckTask):
	@staticmethod
	def shared(base_cfg):
		try: return base_cfg.project.cxx_compiler_is_mingw
		except AttributeError:
			task = base_cfg.project.cxx_compiler_is_mingw = MingwCheckTask(base_cfg)
			return task

	def __init__(self, base_cfg): BuildCheckTask.__init__(self, 'mingw', base_cfg, compile=False)

	@property
	def source_text(self): return \
		'#if !defined __MINGW32__\n' \
		'	#error this is not mingw gcc\n' \
		'#endif\n'

class PicFlagDefinesPicCheckTask(BuildCheckTask):
	@staticmethod
	def shared(base_cfg):
		try: return base_cfg.project.cxx_compiler_pic_flag_defines_pic
		except AttributeError:
			task = base_cfg.project.cxx_compiler_pic_flag_defines_pic = PicFlagDefinesPicCheckTask(base_cfg)
			return task

	def __init__(self, base_cfg): BuildCheckTask.__init__(self, 'pic-flag-defines-pic', base_cfg, compile=False)

	def apply_to(self, cfg):
		cfg.pic = True

	@property
	def source_text(self): return \
		'#if !defined __PIC__ && !defined __pic__\n' \
		'	#error no pic\n' \
		'#endif\n'

class AutoLinkSupportCheckTask(BuildCheckTask):
	@staticmethod
	def shared(base_cfg):
		try: return base_cfg.project.cxx_compiler_has_auto_link_support
		except AttributeError:
			task = base_cfg.project.cxx_compiler_has_auto_link_support = AutoLinkSupportCheckTask(base_cfg)
			return task

	def __init__(self, base_cfg): BuildCheckTask.__init__(self, 'auto-link-support', base_cfg, compile=False)

	@property
	def source_text(self):
		try: return self._source_text
		except AttributeError:
			self._source_text = \
				"""
					// check below is the same as in <boost/config/auto_link.hpp>
					#if !( \\
							defined __BORLANDC__ || \\
							__MWERKS__ >= 0x3000 && _WIN32 || \\
							defined __ICL && defined _MSC_EXTENSIONS && _MSC_VER >= 1200 || \\
							!defined __ICL && defined _MSC_VER \\
					)
						#error no auto link support
					#endif
				"""
			return self._source_text
