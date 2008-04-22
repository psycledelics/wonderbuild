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
		
	def mirror(self, name): return self._mirrors[name]
	def target(self): return self._target
	def prefix(self): return self._prefix
	def dest_dir(self): return self._dest_dir
	def gmake(self): return self._gmake
	def gsed(self): return self._gsed
	
	def shell(self, script): shell(script)

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
			result = f.readline().rstrip()
			f.close()
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
			for f in os.listdir(path):
				if fnmatch.fnmatch(f, '*.py') and f != '__init__.py' and not fnmatch.fnmatch(f, '.*'):
					mod = import_package(f)
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
				dep_name = dep_name[0]
				for dep_package_recurse in self.flatten_deps([dep_name]):
					if not dep_package_recurse in result: result.append(dep_package_recurse)
			if not package in result: result.append(package)
		return result
	
	def build_dir(self, package): return os.path.join(self._build_dir, package.name() + '-' + package.version())
	def state_dir(self, package): return os.path.join(self._state_dir, package.name() + '-' + package.version())
		
	def install_no_act(self, package_names):
		for package in self.flatten_deps(package_names):
			state_dir = self.state_dir(package)
			if os.path.exists(os.path.join(state_dir, 'installed')): print 'already installed:', package.name(), package.version()
			else: print 'to be installed:', package.name(), package.version()

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
					f.write(text)
					f.write('\n')
					f.close()
				rebuild_this_package = rebuild and package.name() in package_names
				if rebuild_this_package or not os.path.exists(os.path.join(state_dir, 'installed')):
					self._dest_dir = os.path.join(os.getcwd(), 'dest')
					if not os.path.exists('build'): os.mkdir('build')
					built = os.path.exists('built')
					if not built or rebuild_this_package:
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
					if not os.path.exists(state_dir): os.mkdir(state_dir)
					os.chdir(self._dest_dir + self._prefix)
					self.shell('find . ! -type d -exec md5sum {} \\; > ' + os.path.join(state_dir, 'files'))
					self.shell('find . -mindepth 1 -type d | sort -r > ' + os.path.join(state_dir, 'dirs'))
					self.shell('cp -R * ' + self._prefix)
					write_state_file('name', package.name())
					write_state_file('version', package.version())
					write_state_file('description', package.description())
					write_state_file('dependencies', '\n'.join([d.name() + ' ' + d.version() for d in self.flatten_deps([n[0] for n in package.deps()])]))
					if package.name() in package_names: installed = 'user'
					else: installed = 'auto'
					write_state_file('installed', installed)
				if package.name() in package_names: write_state_file('installed', 'user')
			finally: os.chdir(save)
			
	def remove(self, package_names, verbose = False):
		for package in [self.find(name) for name in package_names]:
			state_dir = self.state_dir(package)
			if not os.path.exists(state_dir):
				print 'package is not installed:', package.name()
			else:
				save = os.getcwd()
				os.chdir(state_dir)
				try:
					f = file('files')
					try:
						while True:
							l = f.readline().rstrip()
							if not l: break
							l = l.split('  ')[1] # md5sum precedes the file name
							if verbose: print l
							os.unlink(os.path.join(self._prefix, l))
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
	def add_dep(self, name, version = None): self._deps.append((name, version))

	def description(self): return '(no description)'
	def download(self): pass
	def clean_download(self): pass
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

def shell(script):
	print '# in dir', os.getcwd()
	print script
	result = os.system(script)
	if result != 0: raise OSError(result)

