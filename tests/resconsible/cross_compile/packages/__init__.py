#! /usr/bin/env python

import sys, os, imp, fnmatch

class Packages:
	def __init__(self):
		self._packages = {}

		self._mirrors = {
			'sourceforge': 'kent.dl.sourceforge.net'
		}

		self._target = 'i386-mingw32msvc'

		self._build = os.path.join(os.getcwd(), '++build')
		if not os.path.exists(self._build): os.mkdir(self._build)

		self._prefix = os.path.join(os.getcwd(), '++install')

		sys.path.append(os.getcwd())

		self._gmake = 'make' # or gmake

		for e in ['AR', 'CC', 'CFLAGS', 'CROSS', 'CXX', 'CXXFLAGS', 'EXEEXT', 'LD', 'LIBS', 'NM', 'PKG_CONFIG', 'RANLIB']:
			try: del os.environ[e]
			except KeyError: pass
		
	def mirror(self, name): return self._mirrors[name]
	def target(self): return self._target
	def prefix(self): return self._prefix
	def gmake(self): return self._gmake
	
	def add(self, package):
		self._packages[package.name()] = package
		
	def find(self, name):
		try: return self._packages[name]
		except KeyError:
			try:
				mod = import_package(name)
				return mod.package(self)
			except:
				print 'package not found:', name
				raise
				#sys.exit(1)

	def list(self):
		for path in __path__:
			for file in os.listdir(path):
				if fnmatch.fnmatch(file, '*.py') and file != '__init__.py' and not fnmatch.fnmatch(file, '.*'):
					mod = import_package(file)
					package = mod.package(self)
					print package.name(), package.version()
				
	def flatten_deps(self, package_names):
		result = []
		for package_name in package_names:
			package = self.find(package_name)
			for dep_name in package.deps():
				dep_name = dep_name[0]
				for dep_package_recurse in self.flatten_deps([dep_name]):
					if not dep_package_recurse in result: result.append(dep_package_recurse)
			if not package in result: result.append(package)
		return result
		
	def build(self, package_names):
		for package in self.flatten_deps(package_names):
			build = os.path.join(self._build, package.name() + '-' + package.version())
			if not os.path.exists(build): os.mkdir(build)
			os.chdir(build)
			package.download()
			package.build()
			os.chdir(os.pardir)

class Package:
	def __init__(self, packages, name, version = None):
		self._name = name
		self._version = version
		self._deps = []
		self._packages = packages
		packages.add(self)
		
	def packages(self): return self._packages
	
	def mirror(self, name): return self._packages.mirror(name)
	def http_get(self, url): self.shell('wget -c http://' + url)
	def target(self): return self._packages.target()
	def prefix(self): return self._packages.prefix()
	def gmake(self): return self._packages.gmake()

	def shell(self, script):
		print script
		return os.system(script)
	
	def name(self): return self._name
	def version(self): return self._version
	def deps(self): return self._deps
	
	def add_dep(self, name, version = None):
		self._deps.append((name, version))

	def download(self): pass
	def configure(self): pass
	def build(self): pass

def import_package(filename):
	path, name = os.path.split(filename)
	name, ext  = os.path.splitext(name)
	file, filename, data = imp.find_module(name, __path__)
	modname = 'mingw_package_' + name
	mod = imp.load_module(modname, file, filename, data)
	return mod

if False:
	def exec_subprocess(args):
		print args
		import subprocess
		p = subprocess.Popen(args = args, stdout = subprocess.PIPE, stderr = subprocess.PIPE, bufsize = -1)
		out_eof = err_eof = False
		while not(out_eof and err_eof):
			if not out_eof:
				r = p.stdout.read()
				if not r: out_eof = True
				else: sys.stdout.write(r)
			if not err_eof:
				r = p.stderr.read()
				if not r: err_eof = True
				else: sys.stderr.write(r)
		return p.wait()

