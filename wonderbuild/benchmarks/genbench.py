#!/usr/bin/python

import sys
import os.path
import random

# for example: ./genbench.py /tmp/build 50 100 15 5

HELP_USAGE = """Usage: generate_libs.py root libs classes internal external.
    root     - Root directory where to create libs.
    libs     - Number of libraries (libraries only depend on those with smaller numbers)
    classes  - Number of classes per library
    internal - Number of includes per file referring to that same library
    external - Number of includes per file pointing to other libraries
"""

def lib_name(i):
    return "lib_" + str(i)

def CreateHeader(name):
    filename = name + ".h"
    handle = file(filename, "w" )

    guard = name + '_h_'
    handle.write ('#ifndef ' + guard + '\n');
    handle.write ('#define ' + guard + '\n\n');

    handle.write ('class ' + name + ' {\n');
    handle.write ('public:\n');
    handle.write ('    ' + name + '();\n');
    handle.write ('    ~' + name + '();\n');
    handle.write ('};\n\n');

    handle.write ('#endif\n');


def CreateCPP(name, lib_number, classes_per_lib, internal_includes, external_includes):
    filename = name + ".cpp"
    handle = file(filename, "w" )

    header= name + ".h"
    handle.write ('#include "' + header + '"\n');

    includes = random.sample(xrange(classes_per_lib), internal_includes)
    for i in includes:
        handle.write ('#include "class_' + str(i) + '.h"\n')

    if (lib_number > 0):
        includes = random.sample(xrange(classes_per_lib), external_includes)
        lib_list = xrange(lib_number)
        for i in includes:
            libname = 'lib_' + str(random.choice(lib_list))
            handle.write ('#include <' + libname + '/' + 'class_' + str(i) + '.h>\n')

    handle.write ('\n');
    handle.write (name + '::' + name + '() {}\n');
    handle.write (name + '::~' + name  + '() {}\n');


def CreateSConscript(lib_number, classes):
    handle = file("SConscript", "w");
    handle.write("Import('env')\n")
    handle.write('list = Split("""\n');
    for i in xrange(classes):
        handle.write('    class_' + str(i) + '.cpp\n')
    handle.write('    """)\n\n')
    handle.write('env.StaticLibrary("lib_' + str(lib_number) + '", list)\n\n')

def CreateLibMakefile(lib_number, classes):
    handle = file("Makefile", "w");
    handle.write ("""COMPILER = g++
INC = -I..
CCFLAGS = -g -Wall $(INC)
ARCHIVE = ar
DEPEND = makedepend
.SUFFIXES: .o .cpp

""")
    handle.write ("lib = lib_" + str(lib_number) + ".a\n")
    handle.write ("src = \\\n")
    for i in xrange(classes):
        handle.write('class_' + str(i) + '.cpp \\\n')
    handle.write ("""

objects = $(patsubst %.cpp, %.o, $(src))

all: depend $(lib)

$(lib): $(objects)
	$(ARCHIVE) cr $@ $^
	touch $@

.cpp.o:
	$(COMPILER) $(CCFLAGS) -c $<

clean:
	@rm $(objects) $(lib) 2> /dev/null

depend:
	@$(DEPEND) $(INC) $(src)

""")

def CreateLibJamFile(lib_number, classes):
    handle = file("Jamfile", "w")
    handle.write ("SubDir TOP lib_" + str(lib_number) + " ;\n\n")
    handle.write ("SubDirHdrs $(INCLUDES) ;\n\n")
    handle.write ("Library lib_" + str(lib_number) + " :\n")
    for i in xrange(classes):
        handle.write('    class_' + str(i) + '.cpp\n')
    handle.write ('    ;\n')

def CreateVCProjFile(lib_number, classes):
    handle = file("lib_" + str(lib_number) + ".vcproj", "w")
    handle.write("""<?xml version="1.0" encoding="Windows-1252"?>
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
				PreprocessorDefinitions="WIN32;_DEBUG;_LIB"
                AdditionalIncludeDirectories=".."
				MinimalRebuild="TRUE"
				BasicRuntimeChecks="3"
				RuntimeLibrary="5"
				UsePrecompiledHeader="0"
				WarningLevel="3"
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
""")

    for i in xrange(classes):
        handle.write('  <File RelativePath=".\class_' + str(i) + '.cpp"/>\n')

    handle.write("""
	</Files>
	<Globals>
	</Globals>
</VisualStudioProject>
""")

def CreateLibrary(lib_number, classes, internal_includes, external_includes):
    name = "lib_" + str(lib_number)
    SetDir(name)
    for i in xrange(classes):
        classname = "class_" + str(i)
        CreateHeader(classname)
        CreateCPP(classname, lib_number, classes, internal_includes, external_includes)
    CreateSConscript(lib_number, classes)
    CreateLibMakefile(lib_number, classes)
    #CreateLibJamFile(lib_number, classes)
    #CreateVCProjFile(lib_number, classes)
    CreateW(lib_number, classes)

    os.chdir("..")

    CreateWonderbuild(lib_number, classes)


def CreateSConstruct(libs):
    handle = file("SConstruct", "w");
    handle.write("""env = Environment(CPPFLAGS=['-Wall'], CPPDEFINES=['LINUX'], CPPPATH=[Dir('#')])\n""")
    handle.write("""env.Decider('timestamp-newer')\n""")
    handle.write("""env.SetOption('implicit_cache', True)\n""")
    handle.write("""env.SourceCode('.', None)\n""")

    for i in xrange(libs):
        handle.write("""env.SConscript("lib_%s/SConscript", exports=['env'])\n""" % str(i))

def CreateFullMakefile(libs):
    handle = file("Makefile", "w")

    handle.write('subdirs = \\\n')
    for i in xrange(libs):
        handle.write('lib_' + str(i) + '\\\n')
    handle.write("""

all: $(subdirs)
	@for i in $(subdirs); do \
    $(MAKE) -C $$i all; done

clean:
	@for i in $(subdirs); do \
	(cd $$i; $(MAKE) clean); done

depend:
	@for i in $(subdirs); do \
	(cd $$i; $(MAKE) depend); done
""")

def CreateFullJamfile(libs):
    handle = file("Jamfile", "w")
    handle.write ("SubDir TOP ;\n\n")

    for i in xrange(libs):
        handle.write('SubInclude TOP ' + lib_name(i) + ' ;\n')

    handle = file("Jamrules", "w")
    handle.write('INCLUDES = $(TOP) ;\n')

def CreateW(lib_number, classes):
    handle = file("wscript", "w");
    handle.write("def build(bld):\n")
    handle.write("    obj = bld.new_task_gen('cxx', 'staticlib')\n")
    handle.write("    obj.includes='..'\n")
    handle.write("    obj.source='''\n")

    for i in xrange(classes):
        handle.write('    class_' + str(i) + '.cpp\n')

    handle.write("    '''\n")
    handle.write("    obj.target = 'lib2'\n")
    handle.write('def set_options(opt): pass\n')
    handle.write('def configure(conf): pass\n\n')

def CreateWonderbuild(lib_number, classes):
    handle = file("wonderbuild_script_" + str(lib_number), "w");
    handle.write(
'''	class BenchLib%s(Mod):
		def __init__(self, name): Mod.__init__(self, ModConf(base_mod_conf, BenchLib%s.BenchObjConf(base_obj_conf), 'lib'), name)
	
		def dyn_in_tasks(self):
			if len(self.in_tasks) != 0: return None
			Mod.dyn_in_tasks(self)
			src_dir = top_src_dir.node_path(self.name)
			self.obj_conf.paths.append(src_dir)\n''' % (str(lib_number), str(lib_number))
    )
    for i in xrange(classes):
        handle.write(
'''			self.new_obj(src_dir.node_path('class_%s.cpp'))\n''' % str(i)
        )
    handle.write(
'''			return self.in_tasks
		class BenchObjConf(ObjConf):
			def conf(self):
				ObjConf.conf(self)
				self.paths.append(top_src_dir)
	bench_libs.append(BenchLib%s('lib_%s'))\n\n''' % (str(lib_number), str(lib_number))
    )

def CreateWtop(libs):
    handle = file("wscript", "w")

    handle.write("VERSION='0.0.1'\n")
    handle.write("APPNAME='build-bench'\n")
    handle.write("srcdir = '.'\n")
    handle.write("blddir = 'build'\n")

    handle.write("def build(bld):\n")
    handle.write("    bld.add_subdirs('''\n")

    for i in xrange(libs):
        handle.write("""lib_%s\n""" % str(i))

    handle.write("    ''')\n")

    handle.write("def configure(conf):\n")
    handle.write("    conf.check_tool('g++')\n")
    handle.write("def set_options(opt):\n")
    handle.write("    pass\n\n")

def CreateFullSolution(libs):
    handle = file("solution.sln", "w")
    handle.write("Microsoft Visual Studio Solution File, Format Version 8.00\n")

    for i in xrange(libs):
        project_name = lib_name(i) + '\\' + lib_name(i) + '.vcproj'
        handle.write('Project("{8BC9CEB8-8B4A-11D0-8D11-00A0C91BC942}") = "' + lib_name(i) +
                      '", "' + project_name + '", "{CF495178-8865-4D20-939D-AAA' + str(i) + '}"\n')
        handle.write('EndProject\n')

def SetDir(dir):
    if (not os.path.exists(dir)):
        os.mkdir(dir)
    os.chdir(dir)

def main(argv):
    if len(argv) != 6:
        print HELP_USAGE
        return

    root_dir = argv[1]
    libs = int(argv[2])
    classes = int(argv[3])
    internal_includes = int(argv[4])
    external_includes = int(argv[5])

    SetDir(root_dir)
    for i in xrange(libs):
        CreateLibrary(i, classes, internal_includes, external_includes)

    CreateSConstruct(libs)
    CreateFullMakefile(libs)
    CreateWtop(libs)
    #CreateFullJamfile(libs)
    #CreateFullSolution(libs)

if __name__ == "__main__":
    main( sys.argv )


