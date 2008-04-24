# MinGW cross compiling package handling tool
# copyright 2008-2008 Johan Boule <bohan@jabber.org>

import sys, os, shutil, imp, fnmatch

class Packages:
	def __init__(self):
		self._packages = {}
		self._installed_packages = {}
		self._package_recipees = {}

		self._mirrors = {
			'sourceforge': 'kent.dl.sourceforge.net'
		}

		self._target = 'i386-mingw32msvc'

		self._build_state_dir = os.path.join(os.getcwd(), '++build')
		if not os.path.exists(self._build_state_dir): os.makedirs(self._build_state_dir)

		install_dir = os.path.join(os.getcwd(), '++install')
		if not os.path.exists(install_dir): os.makedirs(install_dir)
		
		self._install_state_dir = os.path.join(install_dir, 'package-states')
		if not os.path.exists(self._install_state_dir): os.mkdir(self._install_state_dir)

		self._prefix = os.path.join(install_dir, 'prefix')
		if not os.path.exists(self._prefix): os.makedirs(self._prefix)
		os.environ['PATH'] = os.path.join(self.prefix(), 'bin') + os.pathsep + os.environ['PATH']

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
	def shell(self, script, verbose = True): shell(script, verbose)

	def install_state_dir(self, package): return os.path.join(self._install_state_dir, package.name())
	def build_state_dir(self, package): return os.path.join(self._build_state_dir, package.name())
		
	def find_package(self, package_name):
		try: return self._packages[package_name]
		except KeyError:
			if os.path.exists(os.path.join(self._install_state_dir, package_name)): package = self.find_installed_package(package_name)
			else: package = self.find_package_recipee(package_name)
			self._packages[package_name] = package
			return package
	
	def find_installed_package(self, package_name):
		try: return self._installed_packages[package_name]
		except KeyError:
			package = InstalledPackage(self, package_name)
			self._installed_packages[package_name] = package
			return package
		
	def find_package_recipee(self, package_name):
		try: return self._package_recipees[package_name]
		except KeyError:
			package = import_package(package_name).package(self)
			self._package_recipees[package_name] = package
			return package

	def installed_packages(self):
		try: return self._all_installed_packages
		except AttributeError:
			self._all_installed_packages = []
			for package_name in os.listdir(self._install_state_dir): self._all_installed_packages.append(self.find_installed_package(package_name))
			return self._all_installed_packages

	def package_recipees(self):
		try: return self._all_package_recipees
		except AttributeError:
			self._all_package_recipees = []
			for path in __path__:
				for p in os.listdir(path):
					if fnmatch.fnmatch(p, '*.py') and p != '__init__.py' and not fnmatch.fnmatch(p, '.*'):
						self._all_package_recipees.append(self.find_package_recipee(p[:-2])) # name without .py extension
			return self._all_package_recipees

	def list(self):
		flag_width = 3; name_width = 35; version_width = 27; description_width = 50
		print 'Status=Not/Installed'
		print '| Installed=Auto/User'
		print '|/ ' + 'Name'.ljust(name_width) + 'Version'.ljust(version_width) + 'Description'
		print '++-' + '=' * (name_width - 1) + '-' + '=' * (version_width - 1) + '-' + '=' * description_width
		package_names = {} # {name: [installed, recipee]}
		for package in self.installed_packages(): package_names[package.name()] = [package]
		for package in self.package_recipees():
			try: packages = package_names[package.name()]
			except KeyError: package_names[package.name()] = [package]
			else:
				if packages[0].version() != package.version(): packages.append(package) # don't list if same version is installed
		sorted = package_names.items()
		sorted.sort()
		for packages in [items[1] for items in sorted]:
			for package in packages: # [installed, recipee]
				if not package.installed(): installed = 'n '
				elif package.auto(): installed = 'ia'
				else: installed = 'iu'
				print installed.ljust(flag_width) + \
					package.name().ljust(name_width) + \
					package.version().ljust(version_width) + \
					package.description().ljust(description_width)
				
	def need_rebuild(self):
		name_width = 35; version_width = 27
		print 'Package'.ljust(name_width) + 'Depends on'.ljust(name_width) + 'Version when built'.ljust(version_width) + 'Version installed'.ljust(version_width)
		print ('=' * (name_width - 1) + '-') * 2 + '=' * (version_width - 1) + '-' + '=' * (version_width - 1)
		for package in self.installed_packages():
			for built_dep in package.recursed_deps():
				installed_dep = self.find_installed_package(built_dep.name())
				if installed_dep.version() != built_dep.version():
					print \
						package.name().ljust(name_width) + \
						built_dep.name().ljust(name_width) + \
						built_dep.version().ljust(version_width) + \
						installed_dep.version().ljust(version_width)

	def direct_reverse_deps(self, package, installed_only = True):
		result = []
		for i in self.installed_packages():
			for dep in i.deps():
				if dep.name() == package.name(): result.append(i)
		if not installed_only:
			for r in self.package_recipees():
				if r.name() in [p.name() for p in result]: continue # already listed as installed package
				for dep in r.deps():
					if dep.name() == package.name(): result.append(r)
		return result

	def recursive_reverse_deps(self, package, installed_only):
		result = []
		for i in self.installed_packages():
			for dep in i.deps():
				if dep.name() == package.name(): result.append((i, self.recursive_reverse_deps(i, installed_only)))
		if not installed_only:
			for r in self.package_recipees():
				if r.name() in [p[0].name() for p in result]: continue # already listed as installed package
				for dep in r.deps():
					if dep.name() == package.name(): result.append((r, self.recursive_reverse_deps(r, installed_only)))
		return result

	def print_reverse_deps(self, package_names, installed_only):
		for package_name in package_names:
			def recurse(packages, t = 0):
				for package in packages:
					print '\t' * t + package[0].name()
					recurse(package[1], t + 1)
			package = self.find_package(package_name)
			if installed_only and not package.installed(): print 'package is not installed:', package.name()
			else: recurse([(package, self.recursive_reverse_deps(package, installed_only))])
			
	def recursed_reverse_deps(self, package, installed_only = True):
		result = []
		def recurse(packages):
			for package in packages:
				recurse(package[1])
				if not package[0] in result: result.append(package[0])
		recurse(self.recursive_reverse_deps(package, installed_only))
		return result
	
	def show(self, package_names):
		def show_package(package):
			print 'Name:', package.name()
			print 'Version:', package.version()
			print 'Description:', package.description()
			if not package.installed(): installed = 'not installed'
			elif package.auto(): installed = 'installed (auto)'
			else: installed = 'installed (user)'
			print 'Status:', installed
			print 'Direct-depends:', ', '.join([dep.name() for dep in package.deps()])
			deps = []
			uninstalled_deps = []
			for dep in package.recursed_deps():
				deps.append(dep.name())
				if not self.find_package(dep.name()).installed(): uninstalled_deps.append(dep.name())
			print 'Recursed-depends:', ', '.join(deps)
			print 'Uninstalled-recursed-depends:', ', '.join(uninstalled_deps)
			print 'Direct-reverse-depends:', ', '.join([p.name() for p in self.direct_reverse_deps(package, installed_only = False)])
			print 'Recursed-reverse-depends:', ', '.join([p.name() for p in self.recursed_reverse_deps(package, installed_only = False)])
			if package.installed():
				print 'Installed-direct-reverse-depends:', ', '.join([p.name() for p in self.direct_reverse_deps(package)])
				print 'Installed-recursed-reverse-depends:', ', '.join([p.name() for p in self.recursed_reverse_deps(package)])
			print
		for package in [self.find_package(package_name) for package_name in package_names]:
			show_package(package)
			if package.installed():
				try: package_recipee = self.find_package_recipee(package.name())
				except: pass # the recipee of an installed package may not exist anymore
				else:
					if package_recipee.version() != package.version(): show_package(package_recipee)
	
	def install_recursed_deps(self, packages):
		result = []
		for package in packages:
			for dep in [self.find_package(d.name()) for d in package.recursed_deps()]:
				if not dep in result: result.append(dep)
			if not package in result: result.append(package)
		return result
		
	def install_no_act(self, package_names):
		done = []; todo = []
		for package in self.install_recursed_deps([self.find_package(package_name) for package_name in package_names]):
			if package.installed(): done.append(package)
			else: todo.append(package)
		print 'would install:', ', '.join([package.name() + ' ' + package.version() for package in todo])
		print 'already installed:', ', '.join([package.name() + ' ' + package.version() for package in done])

	def install(self, package_names, continue_build = False, rebuild = False, skip_download = False):
		for package in self.install_recursed_deps([self.find_package(package_name) for package_name in package_names]):
			built_package = BuiltPackage(self, package.name())
			if package.installed():
				installed_package = package
			else: installed_package = InstalledPackage(self, built_package.name())
			built_package.make_state_dir()
			save = os.getcwd()
			os.chdir(built_package.state_dir())
			try:
				if package.name() in package_names:
					if not rebuild: installed = 'user'
					elif package.installed():
						if package.auto(): installed = 'auto'
						else: installed = 'user'
					else: installed = 'user'
				elif package.installed():
					if package.auto(): installed = 'auto'
					else: installed = 'user'
				else: installed = 'auto'

				if package.installed() and not rebuild:
					if package.name() in package_names: print 'already installed:', package.name(), package.version()
				else:
					if package.installed(): package_recipee = self.find_package_recipee(package.name())
					else: package_recipee = package
					new_build = rebuild and package_recipee.name() in package_names
					if not new_build: new_build = not built_package.state_exists('built') or not built_package.state_exists('dest')
					if new_build:
						print 'building', package_recipee.name(), package_recipee.version()
						built_package.remove_state('built')
						built_package.make_state_dir('build')
						os.chdir(built_package.state_dir('build'))
						self._dest_dir = built_package.state_dir('dest') # transmit dest dir to package
						if not continue_build:
							if not skip_download: package_recipee.download()
							package_recipee.build()
						else: 
							package_recipee.continue_build()
							continue_build = False
						if not built_package.state_exists('dest'): raise Exception('no dest dir after building package: ' + package_recipee.name())
						built_package.write_state('version', package_recipee.version())
						built_package.write_state('description', package_recipee.description())
						built_package.write_state('direct-dependencies', '\n'.join([d.name() + ' ' + d.version() for d in package_recipee.deps()]))
						built_package.write_state('recursed-dependencies', '\n'.join([d.name() + ' ' + d.version() for d in package_recipee.recursed_deps()]))
						built_package.write_state('built', None)

					if not package.installed() or new_build:
						print 'installing', built_package.name(), built_package.version()
						if package.installed(): self.remove_one(installed_package)
						installed_package.make_state_dir()
						os.chdir(built_package.state_dir('dest') + self._prefix)
						self.shell('find . ! -type d -exec md5sum {} \\; > ' + installed_package.state_dir('files'), verbose = False)
						self.shell('find . -mindepth 1 -type d | sort -r > ' + installed_package.state_dir('dirs'), verbose = False)
						if False: shutil.copytree(os.curdir, self._prefix, symlinks = True)
							# note: shutil.copytree is not as good (rated "example code" in the documentation)
						else: self.shell('cp -R * ' + self._prefix, verbose = False)
						for state_name in ['version', 'description', 'direct-dependencies', 'recursed-dependencies']:
							shutil.copy(built_package.state_dir(state_name), installed_package.state_dir())
						try: del self._packages[package.name()]
						except KeyError: pass
				installed_package.write_state('installed', installed)
			finally: os.chdir(save)

	def remove_unneeded_deps(self, to_remove):
		unneeded = []
		for package in to_remove:
			for dep in [self.find_installed_package(d.name()) for d in package.deps()]:
				if dep.auto() and not dep in to_remove:
					needed = False
					for reverse_dep in self.direct_reverse_deps(dep):
						if not reverse_dep in to_remove: needed = True; break
					if not needed and not dep in unneeded: unneeded.append(dep)
		if len(unneeded):
			recurse = to_remove[:]; recurse.extend(unneeded)
			for r in self.remove_unneeded_deps(recurse):
				if not r in unneeded: unneeded.append(r)
		return unneeded

	def remove_unneeded(self):
		all_unneeded = []
		for package in self.installed_packages():
			if package.auto():
				unneeded = self.remove_unneeded_deps([package])
				if len(unneeded):
					all_unneeded.append(package)
					for unneeded in self.remove_unneeded_deps([package]):
						if not unneeded in all_unneeded: all_unneeded.append(unneeded)
		return all_unneeded

	def remove_reverse_deps(self, packages):
		result = []
		for package in packages:
			for reverse_dep in self.recursed_reverse_deps(package):
				if not reverse_dep in result: result.append(reverse_dep)
			if not package in result: result.append(package)
		return result
	
	def remove_no_act(self, package_names):
		to_remove = []
		for package in self.remove_reverse_deps([self.find_package(package_name) for package_name in package_names]):
			if not package.installed(): print 'package is not installed:', package.name()
			else: to_remove.append(package)
		print 'would remove:', ', '.join([p.name() for p in to_remove])
		unneeded = self.remove_unneeded_deps(to_remove)
		for package in self.remove_unneeded():
			if not package in unneeded: unneeded.append(package)
		print 'would remove no-more used:', ', '.join([p.name() for p in unneeded])

	def remove(self, package_names, verbose = False):
		to_remove = []
		for package in self.remove_reverse_deps([self.find_package(package_name) for package_name in package_names]):
			if not package.installed(): print 'package is not installed:', package.name()
			else: to_remove.append(package)
		to_remove.extend(self.remove_unneeded_deps(to_remove))
		for package in self.remove_unneeded():
			if not package in to_remove: to_remove.append(package)
		for package in to_remove:
			print 'removing', package.name(), package.version()
			self.remove_one(package)

	def remove_one(self, package, verbose = False):
			if not package.installed(): raise Exception('package ' + package.name() + 'not an installed one')
			save = os.getcwd()
			os.chdir(package.state_dir())
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
				package.remove_state()
			finally: os.chdir(save)
			try:
				del self._packages[package.name()]
				del self._installed_packages[package.name()]
			except KeyError: pass
			try: del self._all_installed_packages
			except AttributeError: pass
	
	def clean_build(self, package_names, all, dest_dir, download):
		for package_recipee in [self.find_package_recipee(package_name) for package_name in package_names]:
			built_package = BuiltPackage(self, package_recipee.name())
			if all: built_package.remove_state(verbose = True)
			else:
				if download: built_package.remove_state('build', verbose = True)
				elif built_package.state_exists('build'):
					print 'cleaning', built_package.state_dir('build')
					os.chdir(built_package.state_dir('build'))
					package_recipee.clean_build()
				if dest_dir:
					built_package.remove_state('built', verbose = True)
					built_package.remove_state('dest', verbose = True)
				built_package.remove_state_dir_if_empty(verbose = True)

class BuiltDep:
	def __init__(self, name, version):
		self._name = name
		self._version = version
	def name(self): return self._name
	def version(self): return self._version

class Package:
	def __init__(self, packages, name):
		self._packages = packages
		self._name = name
	def packages(self): return self._packages
	def name(self): return self._name
	def version(self): pass
	def description(self): pass
	def deps(self): pass
	def recursed_deps(self): pass
	def installed(self): pass

class PackageRecipee(Package):
	def __init__(self, packages, name, version = None):
		Package.__init__(self, packages, name)
		self._version = version
		self._deps = []
		
	def version(self): return self._version
	def description(self): return '(no description)'
	def installed(self): return False

	def deps(self): return self._deps
	def recursed_deps(self):
		try: return self._recursed_deps
		except AttributeError:
			self._recursed_deps = []
			for dep in self.deps():
				for recursed_dep in dep.recursed_deps():
					if not recursed_dep in self._recursed_deps: self._recursed_deps.append(recursed_dep)
				if not dep in self._recursed_deps: self._recursed_deps.append(dep)
			return self._recursed_deps
	
	def add_dep(self, package_name): self._deps.append(self.packages().find_package(package_name))
	def download(self): pass
	def build(self): pass
	def continue_build(self): self.build()
	def clean_build(self): pass

	def mirror(self, name): return self._packages.mirror(name)
	def http_get(self, url): self.shell('wget -c http://' + url)
	def target(self): return self._packages.target()
	def prefix(self): return self._packages.prefix()
	def dest_dir(self): return self._packages.dest_dir()
	def gmake(self): return self._packages.gmake()
	def gsed(self): return self._packages.gsed()
	def shell(self, script): return self._packages.shell(script)

class BuiltPackage(Package):
	def installed(self): return False
	def state_dir(self, state_name = None):
		state_dir = self.packages().build_state_dir(self)
		if state_name is None: return state_dir
		else: return os.path.join(state_dir, state_name)
	def state_exists(self, state_name):
			if state_name is None: path = self.state_dir()
			else: path = os.path.join(self.state_dir(), state_name)
			return os.path.exists(path)
	def make_state_dir(self, state_name = None):
			if state_name is None: path = self.state_dir()
			else: path = os.path.join(self.state_dir(), state_name)
			if not self.state_exists(path): os.mkdir(path)
	def read_state(self, state_name): return read_file(os.path.join(self.state_dir(), state_name))
	def write_state(self, state_name, text): write_file(os.path.join(self.state_dir(), state_name), text)
	def remove_state(self, state_name = None, verbose = False):
		if self.state_exists(state_name):
			if state_name is None: path = self.state_dir()
			else: path = os.path.join(self.state_dir(), state_name)
			if verbose: print 'removing', path
			if state_name is None or os.path.isdir(path): shutil.rmtree(path)
			else: os.unlink(path)
	def remove_state_dir_if_empty(self, state_name = None, verbose = False):
			if state_name is None: path = self.state_dir()
			else: path = os.path.join(self.state_dir(), state_name)
			try: os.rmdir(path)
			except OSError: pass # directory not empty
			else:
				if verbose: print 'removed ', path

	def version(self):
		try: return self._version
		except AttributeError: self._version = self.read_state('version')[0]
		return self._version
	def description(self):
		try: return self._description
		except AttributeError: self._description = self.read_state('description')[0]
		return self._description
	def deps(self):
		try: return self._deps
		except AttributeError:
			self._deps = []
			for dep in self.read_state('direct-dependencies'):
				dep = dep.split(' ')
				self._deps.append(BuiltDep(dep[0], dep[1]))
			return self._deps
	def recursed_deps(self):
		try: return self._recursed_deps
		except AttributeError:
			self._recursed_deps = []
			for dep in self.read_state('recursed-dependencies'):
				dep = dep.split(' ')
				self._recursed_deps.append(BuiltDep(dep[0], dep[1]))
			return self._recursed_deps

class InstalledPackage(BuiltPackage):
	def installed(self): return True
	def state_dir(self, state_name = None):
		state_dir = self.packages().install_state_dir(self)
		if state_name is None: return state_dir
		else: return os.path.join(state_dir, state_name)
	def auto(self):
		try: return self._auto
		except AttributeError: self._auto = self.read_state('installed')[0] == 'auto'
		return self._auto

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

def write_file(file_name, text):
	f = file(file_name, 'w')
	try:
		if(not text is None): f.write(text); f.write('\n')
	finally: f.close()

def read_file(file_name):
	result = []
	f = file(file_name)
	try:
		while True:
			l = f.readline().rstrip()
			if not l: break
			result.append(l)
	finally: f.close()
	return result
