#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006-2013 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

from wonderbuild.cxx_tool_chain import BuildCheckTask, ok_color, failed_color

# gcc -E -dM -std=c++11 -x c++-header /dev/null | sort

class DestPlatformCheckTask(BuildCheckTask):

	@staticmethod
	def shared_uid(*args, **kw): return 'dest-platform'

	def __init__(self, persistent, uid, base_cfg): BuildCheckTask.__init__(self, persistent, uid, base_cfg, pipe_preproc=True)
	
	@property
	def source_text(self): return '''\
#if defined __ELF__
	#define WONDERBUILD__BIN_FMT "elf"
#elif defined __APPLE__ && defined __MACH__
	#define WONDERBUILD__BIN_FMT "mac-o"
#elif defined _WIN32 /* note: is also defined when _WIN64 is defined */ || defined __CYGWIN__ || defined __MSYS__ || defined _UWIN
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
#elif defined _WIN32
	#define WONDERBUILD__OS "win"
#elif defined __QNX__
	#define WONDERBUILD__OS "qnx"
#elif defined __native_client__
	#define WONDERBUILD__OS "nacl"
#elif defined __unix__ || defined unix
	#define WONDERBUILD__OS "unix"
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
#else
	  #define WONDERBUILD__ARCH "unknown"
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
	def bin_fmt(self): return self.results[1]

	@property
	def os(self): return self.results[2]

	@property
	def arch(self): return self.results[3]

	@property
	def result_display(self):
		if self.result: return 'bin-fmt: ' + self.bin_fmt + ', os: ' + self.os + ', arch: ' + self.arch, ok_color
		else: return 'unkown', failed_color
