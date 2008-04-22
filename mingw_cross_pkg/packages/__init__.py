# MinGW cross compiling package handling tool
# copyright 2008-2008 Johan Boule <bohan@jabber.org>

import sys, os, shutil, imp, fnmatch

class Packages:
	def __init__(self):
		self._packages = {}

		self._mirrors = {
			'sourceforge': 'kent.dl.sourceforge.net'
		}

		self._target = 'i386-mingw32msvc'

		self._build_dir = os.path.join(os.getcwd(), '++build')
		if not os.path.exists(self._build_dir): os.makedirs(self._build_dir)

		self._install_dir = os.path.join(os.getcwd(), '++install')
		if not os.path.exists(self._install_dir): os.makedirs(self._install_dir)
		
		self._prefix = os.path.join(self._install_dir, 'prefix')
		if not os.path.exists(self._prefix): os.makedirs(self._prefix)
		os.environ['PATH'] = os.path.join(self.prefix(), 'bin') + os.pathsep + os.environ['PATH']

		self._state_dir = os.path.join(self._install_dir, 'package-states')
		if not os.path.exists(self._state_dir): os.mkdir(self._state_dir)

		sys.path.append(os.getcwd())

		self._gmake = 'make' # or gmake
		self._gsed = 'sed' # or gsed

		for e in ['AR', 'CC', 'CFLAGS', 'CROSS', 'CXX', 'CXXFLAGS', 'EXEEXT', 'LD', 'LIBS', 'NM', 'PKG_CONFIG', 'RANLIB']:
			try: del os.environ[e]
			except KeyError: pass
		
	def state_dir(self, package): return os.path.join(self._state_dir, package.name() + '-' + package.version())
	def build_dir(self, package): return os.path.join(self._build_dir, package.name() + '-' + package.version())

	def mirror(self, name): return self._mirrors[name]
	def target(self): return self._target
	def prefix(self): return self._prefix
	def dest_dir(self): return self._dest_dir
	def gmake(self): return self._gmake
	def gsed(self): return self._gsed
	
	def shell(self, script, verbose = True): shell(script, verbose)

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

		def state_file_exists(f): return os.path.exists(os.path.join(state_dir, f))
		def read_state_file(f):
			f = file(os.path.join(state_dir, f))
			try: result = f.readline().rstrip()
			finally: f.close()
			return result

		for dir in os.listdir(self._state_dir):
			state_dir = os.path.join(self._state_dir, dir)
			
			if not state_file_exists('installed'): installed = 'n '
			else:
				installed = read_state_file('installed')
				if installed == 'user': installed = 'iu'
				elif installed == 'auto': installed = 'ia'
				else: installed = 'i?'

			if state_file_exists('name'): name = read_state_file('name')
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
			for p in os.listdir(path):
				if fnmatch.fnmatch(p, '*.py') and p != '__init__.py' and not fnmatch.fnmatch(p, '.*'):
					mod = import_package(p)
					package = mod.package(self)
					
					state_dir = self.state_dir(package)
					if state_file_exists('version') and read_state_file('version') == package.version(): continue # already listed

					installed = 'n '
					print installed.ljust(flag_width) + \
						package.name().ljust(name_width) + \
						package.version().ljust(version_width) + \
						package.description().ljust(description_width)
				
	def flatten_deps(self, package_names):
		result = []
		for package_name in package_names:
			package = self.find(package_name)
			for dep_name in package.deps():
				for dep_package_recurse in self.flatten_deps([dep_name]):
					if not dep_package_recurse in result: result.append(dep_package_recurse)
			if not package in result: result.append(package)
		return result
		
	def reverse_deps(self, package_name, recursive, installed_only):
		result = []
		
		def state_file_exists(f): return os.path.exists(os.path.join(state_dir, f))
		def read_state_file(f):
			f = file(os.path.join(state_dir, f))
			try:
				r = []
				while True:
					l = f.readline().rstrip()
					if not l: break
					r.append(l)
			finally: f.close()
			return r

		for dir in os.listdir(self._state_dir):
			state_dir = os.path.join(self._state_dir, dir)
			
			if state_file_exists('direct-dependencies'):
				for dep_name in [dep.split(' ')[0] for dep in read_state_file('direct-dependencies')]:
					if dep_name == package_name and state_file_exists('name'):
						name = read_state_file('name')[0]
						result.append(name)
						if recursive:
							recurse = self.reverse_deps(name, recursive, installed_only)
							if len(recurse): result.append(recurse)

		if not installed_only:
			for path in __path__:
				for p in os.listdir(path):
					if fnmatch.fnmatch(p, '*.py') and p != '__init__.py' and not fnmatch.fnmatch(p, '.*'):
						mod = import_package(p)
						package = mod.package(self)

						if package.name() in result: continue # already listed

						for dep_name in package.deps():
							if dep_name == package_name:
								result.append(package.name())
								if recursive:
									recurse = self.reverse_deps(package.name(), recursive, installed_only)
									if len(recurse): result.append(recurse)
		return result

	def print_reverse_deps(self, package_names, installed_only):
		for package_name in package_names:
			def recurse(deps, t = 0):
				for r in deps:
					if type(r) == str: print '\t' * t + r
					else: recurse(r, t + 1)
			recurse([package_name, self.reverse_deps(package_name, recursive = True, installed_only = installed_only)])
			
	def flatten_reverse_deps(self, package_name, installed_only):
		def recurse(package_names):
			result = []
			for r in package_names:
				if type(r) == str:
					if not r in result: result.append(r)
				else:
					for r in recurse(r):
						if not r in result: result.append(r)
			return result
		return recurse(self.reverse_deps(package_name, recursive = True, installed_only = installed_only))
	
	def show(self, package_names):
		for package in [self.find(name) for name in package_names]:
			print 'Name:', package.name()
			print 'Version:', package.version()
			print 'Description:', package.description()
			
			state_dir = self.state_dir(package)
			if os.path.exists(os.path.join(state_dir, 'installed')):
				f = file(os.path.join(state_dir, 'installed'))
				try: installed = f.readline().rstrip()
				finally: f.close
				installed = 'installed (' + installed + ')'
			else: installed = 'not installed'
			print 'Status:', installed
			print 'Direct-depends:', ', '.join(package.deps())
			print 'Recursed-depends:', ', '.join([dep.name() for dep in self.flatten_deps(package.deps())])
			print 'Installed-direct-reverse-depends:', ', '.join(self.reverse_deps(package.name(), recursive = False, installed_only = True))
			print 'Installed-recursed-reverse-depends:', ', '.join(self.flatten_reverse_deps(package.name(), installed_only = True))
			print
	
	def install_no_act(self, package_names):
		done = []
		todo = []
		for package in self.flatten_deps(package_names):
			state_dir = self.state_dir(package)
			if os.path.exists(os.path.join(state_dir, 'installed')): done.append(package)
			else: todo.append(package)
		print 'would install:', ', '.join([package.name() for package in todo])
		print 'already installed:', ', '.join([package.name() for package in done])

	def install(self, package_names, continue_build = False, rebuild = False):
		for package in self.flatten_deps(package_names):
			build_dir = self.build_dir(package)
			if not os.path.exists(build_dir): os.mkdir(build_dir)
			save = os.getcwd()
			os.chdir(build_dir)
			try:
				state_dir = self.state_dir(package)
				def write_state_file(f, text):
					f = file(os.path.join(state_dir, f), 'w')
					try:
						f.write(text)
						f.write('\n')
					finally: f.close()

				rebuild_this_package = rebuild and package.name() in package_names
				if rebuild_this_package or not os.path.exists(os.path.join(state_dir, 'installed')):

					self._dest_dir = os.path.join(os.getcwd(), 'dest')
					if not os.path.exists('build'): os.mkdir('build')
					built = os.path.exists('built')
					if not built or rebuild_this_package:

						print 'building ', package.name()
						
						if built: os.unlink('built')
						os.chdir('build')
						if not continue_build:
							package.download()
							package.build()
						else: 
							package.continue_build()
							continue_build = False
					file(os.path.join(build_dir, 'built'), 'w').close()
					if not os.path.exists(self._dest_dir): raise Exception('no dest dir after building package: ' + package.name())

					print 'installing', package.name()

					if not os.path.exists(state_dir): os.mkdir(state_dir)
					os.chdir(self._dest_dir + self._prefix)
					verbose = False
					self.shell('find . ! -type d -exec md5sum {} \\; > ' + os.path.join(state_dir, 'files'), verbose)
					self.shell('find . -mindepth 1 -type d | sort -r > ' + os.path.join(state_dir, 'dirs'), verbose)
					self.shell('cp -R * ' + self._prefix, verbose)
					write_state_file('name', package.name())
					write_state_file('version', package.version())
					write_state_file('description', package.description())
					write_state_file('direct-dependencies', '\n'.join([d.name() + ' ' + d.version() for d in [self.find(n) for n in package.deps()]]))
					write_state_file('recursed-dependencies', '\n'.join([d.name() + ' ' + d.version() for d in self.flatten_deps(package.deps())]))
					if package.name() in package_names: installed = 'user'
					else: installed = 'auto'
					write_state_file('installed', installed)

				elif package.name() in package_names: print 'already installed:', package.name()
				
				if package.name() in package_names: write_state_file('installed', 'user')
			finally: os.chdir(save)

	def remove_no_act(self, package_names):
		def recurse(package_names):
			result = []
			for package in [self.find(name) for name in package_names]:
				if not os.path.exists(self.state_dir(package)):
					print 'package is not installed:', package.name()
					#continue # comment out to detect broken dependencies
				elif not package.name() in result: result.append(package.name())
				for dep_name in self.flatten_reverse_deps(package.name(), installed_only = True):
					if not dep_name in result: result.append(dep_name)
			return result
		would_remove = recurse(package_names)
		print 'would remove:', ', '.join(would_remove)
				
	def remove(self, package_names, verbose = False):
		to_remove = package_names
		for package_name in package_names:
			for dep_name in self.reverse_deps(package_name, recursive = True, installed_only = True):
				if not dep_name in to_remove: to_remove.append(dep_name)
				
		for package in [self.find(name) for name in to_remove]:
			state_dir = self.state_dir(package)

			if not os.path.exists(state_dir):
				print 'package is not installed:', package.name()
				continue

			print 'removing', package.name()

			save = os.getcwd()
			os.chdir(state_dir)
			try:
				f = file('files')
				try:
					while True:
						l = f.readline().rstrip()
						if not l: break
						l = l.split('  ')[1] # md5sum precedes the file name
						try: os.unlink(os.path.join(self._prefix, l))
						except OSError: sys.stderr.write('file ' + l + ' was already removed while removing package ' + package.name() + '\n')
						else:
							if verbose: print l
				finally: f.close()
				f = file('dirs')
				try:
					while True:
						l = f.readline().rstrip()
						if not l: break
						try: os.rmdir(os.path.join(self._prefix, l))
						except OSError: pass # directory not empty
						else:
							if verbose: print l
				finally: f.close()
				shutil.rmtree(state_dir)
			finally: os.chdir(save)

	def clean_build(self, package_names, all, dest_dir, download):
		for package in [self.find(name) for name in package_names]:
			build_dir = self.build_dir(package)
			if all:
				if os.path.exists(build_dir):
					print 'removing', build_dir
					shutil.rmtree(build_dir)
			else:
				built = os.path.join(build_dir, 'built')
				if os.path.exists(built):
					print 'removing', built
					os.unlink(built)
				build_dir_build = os.path.join(build_dir, 'build')
				if os.path.exists(build_dir_build):
					if download:
						print 'removing', build_dir_build
						shutil.rmtree(build_dir_build)
					else:
						print 'cleaning', build_dir_build
						os.chdir(build_dir_build)
						package.clean_build()
				if dest_dir:
					dest = os.path.join(build_dir, 'dest')
					if os.path.exists(dest):
						print 'removing', dest
						shutil.rmtree(dest)

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
	def dest_dir(self): return self._packages.dest_dir()
	def gmake(self): return self._packages.gmake()
	def gsed(self): return self._packages.gsed()
	def shell(self, script): return self._packages.shell(script)
	
	def name(self): return self._name
	def version(self): return self._version
	def deps(self): return self._deps
	def add_dep(self, name): self._deps.append(name)

	def description(self): return '(no description)'
	def download(self): pass
	def build(self): pass
	def continue_build(self):
		self.download()
		self.build()
	def clean_build(self): pass

def import_package(filename):
	path, name = os.path.split(filename)
	name, ext  = os.path.splitext(name)
	file, filename, data = imp.find_module(name, __path__)
	modname = 'mingw_package_' + name
	mod = imp.load_module(modname, file, filename, data)
	return mod

def shell(script, verbose = True):
	if verbose:
		print '# in dir', os.getcwd()
		print script
	result = os.system(script)
	if result != 0: raise OSError(result)

