#!/usr/bin/python

import sys, os
from random import Random

# for example: ./genbench.py /tmp/build 50 100 15 5

HELP_USAGE = '''\
Usage: generate_libs.py root libs classes internal external.
    root     - Root directory where to create libs.
    libs     - Number of libraries (libraries only depend on those with smaller numbers)
    classes  - Number of classes per library
    internal - Number of includes per file referring to that same library
    external - Number of includes per file pointing to other libraries

To test the autotools part, do:
	autoreconf --install --symlink &&
	mkdir build-autotools &&
	cd build-autotools &&
	../configure --disable-shared CXXFLAGS= &&
	time make --jobs=4 --silent &&
	time make --jobs=4 --silent
'''

def main(argv):
	if len(argv) != 6:
		print HELP_USAGE
		sys.exit(1)

	root_dir = argv[1]
	libs = int(argv[2])
	classes = int(argv[3])
	internal_includes = int(argv[4])
	external_includes = int(argv[5])

	set_dir(root_dir)

	for tool in (
		create_wonderbuild,
		create_waf,
		create_scons,
		create_autotools,
		create_makefile_rec,
		create_jam,
		create_msvc
	): tool(libs)

	for i in xrange(libs): create_lib(i, classes, internal_includes, external_includes)

def create_lib(lib_number, classes, internal_includes, external_includes):
	set_dir(lib_dir(lib_number))
	for i in xrange(classes):
		classname = "class_" + str(i)
		create_hpp(classname)
		create_cpp(classname, lib_number, classes, internal_includes, external_includes)
	for sub in (
		create_waf_sub,
		create_scons_sub,
		create_autotools_sub,
		create_makefile_rec_sub,
		create_jam_sub,
		create_msvc_sub
	): sub(lib_number, classes)
	os.chdir(os.pardir)

def lib_dir(i): return 'lib_' + str(i)
def lib_name(i): return 'lib' + str(i)

def set_dir(dir):
    if not os.path.exists(dir): os.mkdir(dir)
    os.chdir(dir)

def create_hpp(name):
	f = open(name + '.hpp', 'w' )
	f.write('''\
#ifndef %(guard)s
#define %(guard)s
class %(name)s	{
	public:
		%(name)s();
		~%(name)s();
};
#endif
''' % {
	'guard': name + '_hpp_included',
	'name': name
})

def create_cpp(name, lib_number, classes_per_lib, internal_includes, external_includes):
	random = Random(0) # initialise with seed to have reproductible benches
	f = open(name + '.cpp', 'w')
	f.write ('#include "' + name + '.hpp"\n')
	includes = random.sample(xrange(classes_per_lib), internal_includes)
	for i in includes: f.write ('#include "class_' + str(i) + '.hpp"\n')
	if lib_number > 0:
		includes = random.sample(xrange(classes_per_lib), external_includes)
		lib_list = xrange(lib_number)
		for i in includes: f.write ('#include <' + lib_dir(random.choice(lib_list)) + '/' + 'class_' + str(i) + '.hpp>\n')
	f.write ('\n')
	f.write (name + '::' + name + '() {}\n')
	f.write (name + '::~' + name  + '() {}\n')

def create_wonderbuild(libs):
    f = open('wonderbuild_script.py', 'w')
    f.write('''\
def wonderbuild_script(project):
	from wonderbuild.cxx_chain import BaseCxxCfg, BaseModCfg, PkgCfg, CxxCfg, ModCfg, ModTask

	class CustomBaseCxxCfg(BaseCxxCfg):
		def configure(self):
			BaseCxxCfg.configure(self)
			self.flags += ['-g', 'O0', '-Wall']
			self.pic = False

	base_cxx_cfg = CustomBaseCxxCfg(project)
	base_mod_cfg = BaseModCfg(base_cxx_cfg)

	top_src_dir = project.src_node

	class BenchLib(ModTask):
		def __init__(self, name, i):
			ModTask.__init__(self, ModCfg(base_mod_cfg, BenchLib.BenchCxxCfg(base_cxx_cfg, i), 'lib'), name)
	
		def dyn_in_tasks(self):
			src_dir = top_src_dir.node_path(self.name)
			for s in src_dir.find_iter(in_pat = '*.cpp'): self.add_new_cxx_task(s)
			return self.in_tasks

		class BenchCxxCfg(CxxCfg):
			def __init__(self, base_cfg, i):
				CxxCfg.__init__(self, base_cfg)
				self.i = i
				
			def configure(self):
				CxxCfg.configure(self)
				self.paths.append(top_src_dir)
				self.defines['BENCH'] = None
				self.defines['BENCH_LIB'] = self.i

	bench_libs = []
	for s in top_src_dir.actual_children:
		if s.startswith('lib_'): bench_libs.append(BenchLib(s, s[len('lib_'):]))

	return bench_libs
''')

def create_waf(libs):
	f = open('wscript', 'w')
	f.write('''\
APPNAME = 'build-bench'
VERSION = '1.0.0'
srcdir = '.'
blddir = 'build-waf'

def set_options(opt): pass

def configure(conf): conf.check_tool('g++')

def build(bld):
	bld.add_subdirs('%(subs)s')
''' % {
	'subs': ' '.join([lib_dir(i) for i in xrange(libs)])
})

def create_waf_sub(lib_number, classes):
	f = open('wscript', 'w')
	f.write('''\
def set_options(opt): pass

def configure(conf): pass

def build(bld):
	obj = bld.new_task_gen('cxx', 'staticlib')
	obj.target = '%(tgt)s'
	obj.cxxflags = ['-g', '-O0', '-Wall']
	obj.defines = ['BENCH', 'BENCH_LIB=%(num)s']
	obj.includes = '..'
	obj.source = '%(src)s'
''' % {
	'num': str(lib_number),
	'tgt': lib_name(lib_number),
	'src': ' '.join(['class_' + str(i) + '.cpp' for i in xrange(classes)])
})

def create_scons(libs):
	f = open('SConstruct', 'w')
	f.write('''\
env = Environment(
	CPPFLAGS = ['-g', '-O0', '-Wall'],
	CPPDEFINES = {'BENCH': None},
	CPPPATH = [Dir('#')]
)
env.Decider('timestamp-newer')
env.SetOption('implicit_cache', True)
env.SourceCode('.', None)
%(subs)s
''' % {
	'subs': '\n'.join(
		['''env.SConscript('%(dir)s/SConscript', build_dir = 'build-scons/%(dir)s', duplicate = 0, exports = ['env'])''' % {
			'dir': lib_dir(i)} for i in xrange(libs)])
})

def create_scons_sub(lib_number, classes):
	f = open('SConscript', 'w')
	f.write('''\
Import('env')
env = env.Clone()
env.Append(
	CPPDEFINES = {'BENCH_LIB_%(num)s': None}
)
env.StaticLibrary('%(tgt)s', Split('%(src)s'))
''' % {
	'num': str(lib_number),
	'tgt': lib_name(lib_number),
	'src': ' '.join(['class_' + str(i) + '.cpp' for i in xrange(classes)])
})

def create_autotools(libs):
	for f in ('README', 'AUTHORS', 'NEWS', 'ChangeLog'): open(f, 'w')
	f = open('configure.ac', 'w')
	f.write('''\
AC_INIT([build-bench], [1.0.0])
AC_CONFIG_AUX_DIR([autotools-aux])
AM_INIT_AUTOMAKE([subdir-objects nostdinc no-define tar-pax dist-bzip2])
AM_PROG_LIBTOOL
AC_CONFIG_HEADERS([config.h])
AC_CONFIG_FILES([Makefile])
AC_OUTPUT
''')
	f = open('Makefile.am', 'w')
	f.write('''\
AM_CPPFLAGS = -I$(srcdir) -DBENCH
AM_CXXFLAGS = -g -O0 -Wall
lib_LTLIBRARIES =
%(subs)s
''' % {
	'subs': '\n'.join(['include %s/Makefile.am' % lib_dir(i) for i in xrange(libs)])
})

def create_autotools_sub(lib_number, classes):
	f = open('Makefile.am', 'w')
	f.write('''\
lib_LTLIBRARIES += %(tgt)s.la
%(tgt)s_la_CPPFLAGS = $(AM_CPPFLAGS) -DBENCH_LIB_%(num)s
%(tgt)s_la_SOURCES = %(src)s
''' % {
	'num': str(lib_number),
	'tgt': lib_name(lib_number),
	'src': ' '.join(['%s/class_%s.cpp' % (lib_dir(lib_number), str(i)) for i in xrange(classes)])
})

def create_makefile_rec(libs):
	f = open('Makefile', 'w')
	f.write('''\
subdirs = %(subs)s

all: $(subdirs)
	@for i in $(subdirs); do $(MAKE) -r -C $$i all; done

clean:
	@for i in $(subdirs); do $(MAKE) -r -C $$i clean; done

depend:
	@for i in $(subdirs); do $(MAKE) -r -C $$i depend; done
''' % {
	'subs': ' '.join([lib_dir(i) for i in xrange(libs)])
})

def create_makefile_rec_sub(lib_number, classes):
	f = open('Makefile', 'w')
	f.write ('''\
INCLUDE_PATHS = -I..
DEFINES = -DBENCH -DBENCH_LIB_%(num)s
DEPEND = makedepend
CXX = g++
CXX_FLAGS = -g -O0 -Wall 
AR = ar
AR_FLAGS = crus
.SUFFIXES: .o .cpp
lib = %(tgt)s.a
src = %(src)s
objects = $(patsubst %%.cpp, %%.o, $(src))

all: depend $(lib)

$(lib): $(objects)
	$(AR) $(AR_FLAGS) $@ $^

.cpp.o:
	$(CXX) $(CXX_FLAGS) $(DEFINES) $(INCLUDE_PATHS) -c $< -o $@

clean:
	@rm $(objects) $(lib) 2> /dev/null
	
depend:
	@$(DEPEND) $(DEFINES) $(INCLUDE_PATHS) $(src)
''' % {
	'num': str(lib_number),
	'tgt': lib_name(lib_number),
	'src': ' '.join(['class_%s.cpp' % str(i) for i in xrange(classes)])
})

def create_jam(libs):
	f = open('Jamfile', 'w')
	f.write ('SubDir TOP ;\n\n')
	for i in xrange(libs): f.write('SubInclude TOP ' + lib_dir(i) + ' ;\n')
	f = open('Jamrules', 'w')
	f.write('INCLUDES = $(TOP) ;\n')

def create_jam_sub(lib_number, classes):
	f = open('Jamfile', 'w')
	f.write ('SubDir TOP ' + lib_dir(lib_number) + ' ;\n\n')
	f.write ('SubDirHdrs $(INCLUDES) ;\n\n')
	f.write ('Library ' + lib_name(lib_number) + ' :\n')
	for i in xrange(classes): f.write('    class_' + str(i) + '.cpp\n')
	f.write ('    ;\n')

def create_msvc(libs):
	f = open('solution.sln', 'w')
	f.write('Microsoft Visual Studio Solution File, Format Version 8.00\n')

	for i in xrange(libs):
		project_path = lib_dir(i) + '\\' + lib_name(i) + '.vcproj'
		f.write('Project("{8BC9CEB8-8B4A-11D0-8D11-00A0C91BC942}") = "' + lib_name(i) + '", "' +
			project_path + '", "{CF495178-8865-4D20-939D-AAA' + str(i) + '}"\n')
		f.write('EndProject\n')

def create_msvc_sub(lib_number, classes):
	f = open(lib_name(lib_number) + '.vcproj', 'w')
	f.write('''\
<?xml version="1.0" encoding="Windows-1252"?>
<VisualStudioProject
	ProjectType="Visual C++"
	Version="7.10"
	Name=""" + '"' + lib_name(lib_number) + '"' + """
	ProjectGUID="{CF495178-8865-4D20-939D-AAA""" + str(lib_number) + """}"
	Keyword="Win32Proj">
	<Platforms>
		<Platform
			Name="Win32"/>
	</Platforms>
	<Configurations>
		<Configuration
			Name="Debug|Win32"
			OutputDirectory="Debug"
			IntermediateDirectory="Debug"
			ConfigurationType="4"
			CharacterSet="2">
			<Tool
				Name="VCCLCompilerTool"
				Optimization="0"
				PreprocessorDefinitions="BENCH"
				AdditionalIncludeDirectories=".."
				MinimalRebuild="TRUE"
				BasicRuntimeChecks="3"
				RuntimeLibrary="5"
				UsePrecompiledHeader="0"
				WarningLevel="4"
				Detect64BitPortabilityProblems="TRUE"
				DebugInformationFormat="4"/>
			<Tool
				Name="VCCustomBuildTool"/>
			<Tool
				Name="VCLibrarianTool"
				OutputFile="$(OutDir)/""" + lib_name(lib_number) + """.lib"/>
		</Configuration>
	</Configurations>
	<References>
	</References>
	<Files>
%(src)s
	</Files>
	<Globals>
	</Globals>
</VisualStudioProject>
''' % {
	'src': '\n'.join(['<File RelativePath="class_' + str(i) + '.cpp"/>\n' for i in xrange(classes)])
})

if __name__ == "__main__": main(sys.argv)
