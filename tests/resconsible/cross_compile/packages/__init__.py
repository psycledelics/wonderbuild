#! /usr/bin/env python

import sys, os, imp

def import_package(filename):
	path, name = os.path.split(filename)
	name, ext  = os.path.splitext(name)
	file, filename, data = imp.find_module(name, __path__)
	modname = 'mingw_package_' + name
	mod = imp.load_module(modname, file, filename, data)
	return mod

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
	
class Packages:
	def __init__(self):
		self._mirrors = {
			'sourceforge': 'kent.dl.sourceforge.net'
		}
		self._target = 'i386-mingw32msvc'
		self._prefix = os.getcwd() + '/++install'
		self._make = 'make' # or gmake
		self._packages = []
		self._package_names = {}
		
	def mirror(self, name): return self._mirrors[name]
	def target(self): return self._target
	def prefix(self): return self._prefix
	def make(self): return self._make
	
	def add(self, package):
		self._packages.append(package)
		self._package_names[package.name()] = package
		
	def package_by_name(self, name):
		try: return self._package_names[name]
		except KeyError:
			try:
				mod = import_package(name)
				return mod.package(self)
			except:
				print 'package not found: ' + name
				raise
				#sys.exit(1)

class Package:
	def __init__(self, packages, name, version = None):
		self._name = name
		self._version = version
		self._deps = []
		self._packages = packages
		packages.add(self)
		
	def packages(self): return self._packages
	
	def mirror(self, name): return self._packages.mirror(name)
	def http_get(self, url): exec_subprocess(['wget', '-c', 'http://' + url])
	def target(self): return self._packages.target()
	def prefix(self): return self._packages.prefix()
	def make(self): return self._packages.make()

	def shell(self, script):
		print script
		return os.system(script)
	
	def name(self): return self._name
	def version(self): return self._version
	def deps(self): return self._deps
	
	def add_dep(self, name, version = None):
		self._deps.append((name, version))
		
	def find_deps(self):
		result = []
		for d in self._deps:
			p = self._packages.package_by_name(d[0])
			result.extend(p.find_deps())
			result.append(p)
		return result
		
	def download_deps(self):
		for d in self.find_deps(): d.download()
		self.download()

	def build_deps(self):
		for d in self.find_deps(): d.build()
		self.build()

	def new_version(self): pass
	def download(self): pass
	def build(self): pass
	def install(self): pass

