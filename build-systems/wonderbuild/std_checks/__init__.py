#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006-2009 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

from wonderbuild.cxx_tool_chain import BuildCheckTask, ok_color, failed_color

# gcc -E -dM -std=c++98 -x c++-header /dev/null | sort

class BinaryFormatCheckTask(BuildCheckTask):
	@staticmethod
	def shared(base_cfg):
		try: return base_cfg.project.dest_platform_binary_format
		except AttributeError:
			task = base_cfg.project.dest_platform_binary_format = BinaryFormatCheckTask(base_cfg)
			return task

	def __init__(self, base_cfg): BuildCheckTask.__init__(self, 'binary-format', base_cfg, pipe_preproc=True)
	
	@property
	def source_text(self): return '''\
#if defined __ELF__
	#define WONDERBUILD__BIN_FMT "elf"
#elif defined __APPLE__ && defined __MACH__
	#define WONDERBUILD__BIN_FMT "mac-o"
#elif defined _WIN32 || defined __CYGWIN__ || defined __MSYS__ || defined _UWIN
	#define WONDERBUILD__BIN_FMT "pe"
#else
	#error unkown binary format
#endif
#if defined __linux__
	#define WONDERBUILD__OS "linux"
#elif defined __GNU__
	#define WONDERBUILD__OS "hurd"
#elif defined __OpenBSD__
	#define WONDERBUILD__OS "openbsd"
#elif defined __FreeBSD__
	#define WONDERBUILD__OS "freebsd"
#elif defined __NetBSD__
	#define WONDERBUILD__OS "netbsd"
#elif defined __sun
	#define WONDERBUILD__OS "sunos"
#elif defined __sgi
	#define WONDERBUILD__OS "irix"
#elif defined __hpux
	#define WONDERBUILD__OS "hpux"
#elif defined _AIX
	#define WONDERBUILD__OS "aix"
#elif defined __APPLE__ && defined __MACH__
	#define WONDERBUILD__OS "darwin"
#elif defined __CYGWIN__
	#define WONDERBUILD__OS "cygwin"
#elif defined __MSYS__
	#define WONDERBUILD__OS "msys"
#elif defined _UWIN__
	#define WONDERBUILD__OS "uwin"
#elif defined _WIN64 || defined _WIN32
	#define WONDERBUILD__OS "win"
#elif defined __unix__ || defined unix
	#define WONDERBUILD__OS "generic"
#else
	#error unkown operating system
#endif
#if defined __x86_64__
	  #define WONDERBUILD__ARCH "x86_64"
#elif defined __i386__
	  #define WONDERBUILD__ARCH "x86"
#elif defined __ia64__
	  #define WONDERBUILD__ARCH "ia"
#elif defined __mips__
	  #define WONDERBUILD__ARCH "mips"
#elif defined __sparc__
	  #define WONDERBUILD__ARCH "sparc"
#elif defined __alpha__
	  #define WONDERBUILD__ARCH "alpha"
#elif defined __arm__
	  #define WONDERBUILD__ARCH "arm"
#elif defined __hppa__
	  #define WONDERBUILD__ARCH "hppa"
#elif defined __powerpc__
	  #define WONDERBUILD__ARCH "powerpc"
#endif
WONDERBUILD__BIN_FMT
WONDERBUILD__OS
WONDERBUILD__ARCH
'''

	def do_check_and_set_result(self, sched_ctx):
		for x in BuildCheckTask.do_check_and_set_result(self, sched_ctx): yield x
		r, out = self.results
		if not r: self.results = False, None, None, None
		else:
			out = out.split('\n')
			self.results = True, out[-4][1:-1], out[-3][1:-1], out[-2][1:-1]
	
	@property
	def result(self): return self.results[0]
	
	@property
	def format(self): return self.results[1]

	@property
	def os(self): return self.results[2]

	@property
	def arch(self): return self.results[3]

	@property
	def result_display(self):
		if self.result: return self.format, ok_color
		else: return 'unkown (neither of elf, mac-o, nor pe)', failed_color

def unversioned_sys_platform_to_binary_format(unversioned_sys_platform):
	"infers the binary format from the unversioned_sys_platform name."

	if unversioned_sys_platform in ('linux', 'freebsd', 'netbsd', 'openbsd', 'sunos'): return 'elf'
	elif unversioned_sys_platform == 'darwin': return 'mac-o'
	elif unversioned_sys_platform in ('win', 'cygwin', 'uwin', 'msys'): return 'pe'
	# TODO we assume all other operating systems are elf, which is not true.
	# we may set this to 'unknown' and have ccroot and other tools handle the case "gracefully" (whatever that means).
	return 'elf'

def unversioned_sys_platform():
	"""returns an unversioned name from sys.platform.
	sys.plaform is not very well defined and depends directly on the python source tree.
	The version appended to the names is unreliable as it's taken from the build environment at the time python was built,
	i.e., it's possible to get freebsd7 on a freebsd8 system.
	So we remove the version from the name (except for the stupid name os2).
	Some possible values of sys.platform are, amongst others:
		aix3 aix4 atheos beos5 darwin freebsd2 freebsd3 freebsd4 freebsd5 freebsd6 freebsd7
		generic irix5 irix6 linux2 mac netbsd1 next3 os2emx riscos sunos5 unixware7
	Investigating the python source tree may reveal more values.
	"""
	s = sys.platform
	if s == 'java':
		# The real OS is hidden under the JVM.
		from java.lang import System
		s = System.getProperty('os.name')
		# see http://lopica.sourceforge.net/os.html for a list of possible values
		if s == 'Mac OS X': return 'darwin'
		elif s.startswith('Windows '): return 'win'
		elif s == 'OS/2': return 'os2'
		elif s == 'HP-UX': return 'hpux'
		elif s in ('SunOS', 'Solaris'): return 'sunos'
		else: s = s.lower()
	if s.endswith('os2') and s != 'sunos2': return s
	return re.split('\d+$', s)[0]

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
		'\t#error the target platform is not mswindows\n' \
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
		'\t#error the target platform is not cygwin\n' \
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
		'\t#error this is not mingw gcc\n' \
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
		'\t#error no pic\n' \
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
				'''
					// check below is the same as in <boost/config/auto_link.hpp>
					#if !( \\
							defined __BORLANDC__ || \\
							__MWERKS__ >= 0x3000 && _WIN32 || \\
							defined __ICL && defined _MSC_EXTENSIONS && _MSC_VER >= 1200 || \\
							!defined __ICL && defined _MSC_VER \\
					)
						#error no auto link support
					#endif
				'''
			return self._source_text
