#! /usr/bin/env python

import sys, os, imp, fnmatch

class Packages:
	def __init__(self):
		self._packages = {}

		self._mirrors = {
			'sourceforge': 'kent.dl.sourceforge.net'
		}

		self._target = 'i386-mingw32msvc'

		self._build_dir = os.path.join(os.getcwd(), '++build')
		if not os.path.exists(self._build_dir): os.mkdir(self._build_dir)

		self._prefix = os.path.join(os.sep, 'prefix')
		
		self._install_dir = os.path.join(os.getcwd(), '++install')
		if not os.path.exists(self._install_dir): os.mkdir(self._install_dir)
		
		self._state_dir = os.path.join(self._install_dir, 'package-states')
		if not os.path.exists(self._state_dir): os.mkdir(self._state_dir)

		sys.path.append(os.getcwd())

		self._gmake = 'make' # or gmake

		for e in ['AR', 'CC', 'CFLAGS', 'CROSS', 'CXX', 'CXXFLAGS', 'EXEEXT', 'LD', 'LIBS', 'NM', 'PKG_CONFIG', 'RANLIB']:
			try: del os.environ[e]
			except KeyError: pass
		
	def mirror(self, name): return self._mirrors[name]
	def target(self): return self._target
	def prefix(self): return self._prefix
	def destdir(self): return self._destdir
	def gmake(self): return self._gmake
	
	def shell(self, script):
		print script
		return os.system(script)

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
		flag_width = 3
		name_width = 35
		version_width = 27
		description_width = 40
		print 'Status=Not/Installed'
		print '| Installed=Auto/User'
		print '|/ ' + 'Name'.ljust(name_width) + 'Version'.ljust(version_width) + 'Description'
		print '++-' + '=' * (name_width - 1) + '-' + '=' * (version_width - 1) + '-' + '=' * description_width

		for dir in os.listdir(self._state_dir):
			state_dir = os.path.join(self._state_dir, dir)
			def state_file_exists(f): return os.path.exists(os.path.join(state_dir, f))
			def read_state_file(f): return file(os.path.join(state_dir, f)).readline().rstrip()
			
			if not state_file_exists('installed'): installed = 'n '
			elif state_file_exists('installed-user'): installed = 'iu'
			elif state_file_exists('installed-auto'): installed = 'ia'
			else: installed = 'i?'

			if state_file_exists('name'): version = read_state_file('name')
			else: name = dir + ' (dir)'

			if state_file_exists('version'): version = read_state_file('version')
			else: version = '(unknown)'
			
			if state_file_exists('description'): description = read_state_file('description')
			else: description = '(no description available)'

			print installed.ljust(flag_width) + \
				name.ljust(name_width) + \
				version.ljust(version_width) + \
				description.ljust(description_width)

		for path in __path__:
			for f in os.listdir(path):
				if fnmatch.fnmatch(f, '*.py') and f != '__init__.py' and not fnmatch.fnmatch(f, '.*'):
					mod = import_package(f)
					package = mod.package(self)
					
					state_dir = self.state_dir(package)
					def state_file_exists(f): return os.path.exists(os.path.join(state_dir, f))
					
					if not state_file_exists('installed'): installed = 'n '
					elif state_file_exists('installed-user'): installed = 'iu'
					elif state_file_exists('installed-auto'): installed = 'ia'
					else: installed = 'i?'
					
					print installed.ljust(flag_width) + \
						package.name().ljust(name_width) + \
						package.version().ljust(version_width) + \
						package.description().ljust(description_width)
				
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
	
	def build_dir(self, package): return os.path.join(self._build_dir, package.name() + '-' + package.version())
	def state_dir(self, package): return os.path.join(self._state_dir, package.name() + '-' + package.version())
		
	def build(self, package_names, continue_build = False):
		for package in self.flatten_deps(package_names):
			build_dir = self.build_dir(package)
			if not os.path.exists(build_dir): os.mkdir(build_dir)
			save = os.curdir
			os.chdir(build_dir)
			try:
				state_dir = self.state_dir(package)
				try:
					if not os.path.exists(os.path.join(state_dir, 'installed')):
						self._destdir = os.path.join(os.getcwd(), 'destdir')
						if not os.path.exists('build'): os.mkdir('build')
						os.chdir('build')
						if not continue_build:
							package.download()
							package.build()
						else: package.continue_build()
						if os.path.exists(self._destdir):
							os.chdir(self._destdir)
							self.shell('find . -type f -exec md5sum {} \\; > ' + os.path.join(state_dir, 'files'))
							self.shell('find . -mindepth 1 -type d | sort -r > ' + os.path.join(state_dir, 'dirs'))
							self.shell('cp -R * ' + self._install_dir)
							os.chdir(state_dir)
							self.shell('echo ' + package.version() + ' > version')
							self.shell('rm -f rdeps && touch rdeps')
							for d in self.flatten_deps(package.deps()): self.shell('echo ' + d.name() + ' > rdeps')
							self.shell('touch installed')
							if not package.name() in package_names: self.shell('touch installed-auto')
					if package.name() in package_names:
						os.chdir(state_dir)
						if not os.path.exists('installed-user'):
							if os.path.exists('installed-auto'): self.shell('rm -f installed-auto')
							self.shell('touch installed-user')
				except:
					os.chdir(state_dir)
					if not os.path.exists('installed-user') or not os.path.exists('installed-auto'):
						self.shell('rm -f installed')
					raise
			finally: os.chdir(save)
			
	def remove(self, package_names):
		for package in self.flatten_deps(package_names):
			state_dir = self.state_dir(package)
			if not os.path.exists(state_dir):
				print 'no information about package:', package.name()
			else:
				save = os.curdir
				os.chdir(state_dir)
				try:
					if not package.name() in package_names:
						print 'not removing:', package.name()
					else:
						self.shell('rm -f installed installed-*')
						self.shell('for f in $(cut -d\\  -f3 < files); do rm -fv ' + self._install + '/$f; done')
						self.shell(
							'for d in $(cat dirs); do test -d %(install)s/$d && rmdir --ignore-fail-on-non-empty -v %(install)s/$d; done' %
							{'install': self._install}
						)
				finally: os.chdir(save)

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
	def destdir(self): return self._packages.destdir()
	def gmake(self): return self._packages.gmake()
	def shell(self, script): return self._packages.shell(script)
	
	def name(self): return self._name
	def version(self): return self._version
	def deps(self): return self._deps
	
	def add_dep(self, name, version = None):
		self._deps.append((name, version))

	def description(self): return '(no description)'
	def download(self): pass
	def configure(self): pass
	def build(self): pass
	def continue_build(self): pass

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

