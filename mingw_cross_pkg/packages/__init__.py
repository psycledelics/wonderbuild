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
		
	def state_dir(self, package): return os.path.join(self._state_dir, package.name())
	def build_dir(self, package): return os.path.join(self._build_dir, package.name())

	def mirror(self, name): return self._mirrors[name]
	def target(self): return self._target
	def prefix(self): return self._prefix
	def dest_dir(self): return self._dest_dir
	def gmake(self): return self._gmake
	def gsed(self): return self._gsed
	
	def shell(self, script, verbose = True): shell(script, verbose)

	def state_file_exists(self, package_name, file_name):
		return os.path.exists(os.path.join(self._state_dir, package_name, file_name))
		
	def read_state_file(self, package_name, file_name):
		f = file(os.path.join(self._state_dir, package_name, file_name))
		try:
			result = []
			while True:
				l = f.readline().rstrip()
				if not l: break
				result.append(l)
		finally: f.close()
		return result
	
	def find(self, package_name):
		try: return self._packages[package_name]
		except KeyError:
			if os.path.exists(os.path.join(self._state_dir, package_name)): package = self.find_installed(package_name)
			else: package = self.find_recipee(package_name)
			self._packages[package_name] = package
			return package
	
	def find_installed(self, package_name):
		try: return self._installed_packages[package_name]
		except KeyError:
			package = InstalledPackage(self, package_name)
			self._installed_packages[package_name] = package
			return package
		
	def find_recipee(self, package_name):
		try: return self._package_recipees[package_name]
		except KeyError:
			package = import_package(package_name).package(self)
			self._package_recipees[package_name] = package
			return package

	def installed_packages(self):
		try: return self._all_installed_packages
		except AttributeError:
			self._all_installed_packages = []
			for package_name in os.listdir(self._state_dir): self._all_installed_packages.append(self.find_installed(package_name))
			return self._all_installed_packages

	def package_recipees(self):
		try: return self._all_package_recipees
		except AttributeError:
			self._all_package_recipees = []
			for path in __path__:
				for p in os.listdir(path):
					if fnmatch.fnmatch(p, '*.py') and p != '__init__.py' and not fnmatch.fnmatch(p, '.*'):
						self._all_package_recipees.append(self.find_recipee(p[:-2])) # name without .py extension
			return self._all_package_recipees

	def list(self):
		flag_width = 3; name_width = 35; version_width = 27; description_width = 40
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
			for package in packages:
				if not package.installed(): installed = 'n '
				elif package.auto(): installed = 'ia'
				else: installed = 'iu'
				print installed.ljust(flag_width) + \
					package.name().ljust(name_width) + \
					package.version().ljust(version_width) + \
					package.description().ljust(description_width)
				
	def direct_reverse_deps(self, package_name, installed_only = True):
		result = []
		for package in self.installed_packages():
			for dep_name in package.deps():
				if dep_name == package_name: result.append(package)
		if not installed_only:
			for package in self.recipees():
				if package.name() in [p.name() for p in result]: continue # already listed as installed package
				for dep_name in package.deps():
					if dep_name == package_name: result.append(package)
		return result

	def recursive_reverse_deps(self, package_name, installed_only):
		result = []
		for package in self.installed_packages():
			for dep_name in package.deps():
				if dep_name == package_name: result.append((package, self.recursive_reverse_deps(package.name(), installed_only)))
		if not installed_only:
			for package in self.package_recipees():
				if package.name() in [p[0].name() for p in result]: continue # already listed as installed package
				for dep_name in package.deps():
					if dep_name == package_name: result.append((package, self.recursive_reverse_deps(package.name(), installed_only)))
		return result

	def print_reverse_deps(self, package_names, installed_only):
		for package_name in package_names:
			def recurse(packages, t = 0):
				for package in packages:
					print '\t' * t + package[0].name()
					recurse(package[1], t + 1)
			recurse([(self.find(package_name), self.recursive_reverse_deps(package_name, installed_only))])
			
	def flatten_reverse_deps(self, package_name, installed_only = True):
		result = []
		def recurse(packages):
			for package in packages:
				if not package[0] in result: result.append(package[0])
				recurse(package[1])
		recurse(self.recursive_reverse_deps(package_name, installed_only))
		return result
	
	def flatten_deps(self, package_names):
		result = []
		for package in [self.find(package_name) for package_name in package_names]:
			for package_dep_recursed in self.flatten_deps(package.deps()):
				if not package_dep_recursed in result: result.append(package_dep_recursed)
			if not package in result: result.append(package)
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
			print 'Direct-depends:', ', '.join(package.deps())
			print 'Recursed-depends:', ', '.join([dep.name() for dep in self.flatten_deps(package.deps())])
			print 'Installed-direct-reverse-depends:', ', '.join([p.name() for p in self.direct_reverse_deps(package.name())])
			print 'Installed-recursed-reverse-depends:', ', '.join([p.name() for p in self.flatten_reverse_deps(package.name())])
			print
		for package in [self.find(package_name) for package_name in package_names]:
			show_package(package)
			if package.installed():
				try: recipee = self.find_recipee(package.name())
				except: pass # the recipee of an installed package may not exist anymore
				else:
					if recipee.version() != package.version(): show_package(recipee)
	
	def install_no_act(self, package_names):
		done = []; todo = []
		for package in self.flatten_deps(package_names):
			if package.installed(): done.append(package)
			else: todo.append(package)
		print 'would install:', ', '.join([package.name() for package in todo])
		print 'already installed:', ', '.join([package.name() for package in done])

	def install(self, package_names, continue_build = False, rebuild = False, skip_download = False):
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

						print 'building ', package.name(), package.version()
						
						if built: os.unlink('built')
						os.chdir('build')
						if not continue_build:
							if not skip_download: package.download()
							package.build()
						else: 
							package.continue_build()
							continue_build = False
					file(os.path.join(build_dir, 'built'), 'w').close()
					if not os.path.exists(self._dest_dir): raise Exception('no dest dir after building package: ' + package.name())

					print 'installing', package.name(), package.version()

					if not os.path.exists(state_dir): os.mkdir(state_dir)
					os.chdir(self._dest_dir + self._prefix)
					verbose = False
					self.shell('find . ! -type d -exec md5sum {} \\; > ' + os.path.join(state_dir, 'files'), verbose)
					self.shell('find . -mindepth 1 -type d | sort -r > ' + os.path.join(state_dir, 'dirs'), verbose)
					self.shell('cp -R * ' + self._prefix, verbose)
					write_state_file('name', package.name())
					write_state_file('version', package.version())
					write_state_file('description', package.description())
					write_state_file('direct-dependencies', '\n'.join([d.name() + ' ' + d.version() for d in [self.find_installed(n) for n in package.deps()]]))
					write_state_file('recursed-dependencies', '\n'.join([d.name() + ' ' + d.version() for d in self.flatten_deps(package.deps())]))
					if package.name() in package_names: installed = 'user'
					else: installed = 'auto'
					write_state_file('installed', installed)
					try: del self._packages[package.name()]
					except KeyError: pass

				elif package.name() in package_names: print 'already installed:', package.name()
				
				if not rebuild and package.name() in package_names: write_state_file('installed', 'user')
			finally: os.chdir(save)

	def remove_unneeded_deps(self, to_remove):
		unneeded = []
		for package in to_remove:
			for dep_name in package.deps():
				dep = self.find_installed(dep_name)
				if dep in to_remove: continue
				if dep.auto():
					needed = False
					for reverse_dep in self.direct_reverse_deps(dep_name):
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

	def remove_no_act(self, package_names):
		to_remove = []
		for package in [self.find(package_name) for package_name in package_names]:
			if not package.installed(): print 'package is not installed:', package.name()
			else: to_remove.append(package)
		for package_name in package_names:
			for reverse_dep in self.flatten_reverse_deps(package_name):
				if not reverse_dep in to_remove: to_remove.append(reverse_dep)
		print 'would remove:', ', '.join([p.name() for p in to_remove])
		unneeded = []
		for package in self.remove_unneeded_deps(to_remove):
			if not package in unneeded: unneeded.append(package)
		for package in self.remove_unneeded():
			if not package in unneeded: unneeded.append(package)
		print 'would remove no-more used:', ', '.join([p.name() for p in unneeded])

	def remove(self, package_names, verbose = False):
		to_remove = []
		for package in [self.find(package_name) for package_name in package_names]:
			if not package.installed(): print 'package is not installed:', package.name()
			else: to_remove.append(package)
		for package in to_remove:
			for reverse_dep in self.flatten_reverse_deps(package_name):
				if not reverse_dep in to_remove: to_remove.append(reverse_dep)
		to_remove.extend(self.remove_unneeded_deps(to_remove))
		for package in self.remove_unneeded():
			if not package in to_remove: to_remove.append(package)
		for package in to_remove:
			print 'removing', package.name(), package.version()
			state_dir = self.state_dir(package)
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
			try:
				del self._packages[package.name()]
				del self._installed_packages[package.name()]
			except KeyError: pass
			try: del self._all_installed_packages
			except AttributeError: pass

	def clean_build(self, package_names, all, dest_dir, download):
		for package in [self.find(package_name) for package_name in package_names]:
			build_dir = self.build_dir(package)
			if all:
				if os.path.exists(build_dir):
					print 'removing', build_dir
					shutil.rmtree(build_dir)
			else:
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
					built = os.path.join(build_dir, 'built')
					if os.path.exists(built):
						print 'removing', built
						os.unlink(built)
					dest = os.path.join(build_dir, 'dest')
					if os.path.exists(dest):
						print 'removing', dest
						shutil.rmtree(dest)
				try: os.rmdir(build_dir)
				except OSError: pass # directory not empty
				else: print 'removed ', build_dir

class Package:
	def __init__(self, packages, name):
		self._packages = packages
		self._name = name
	def packages(self): return self._packages
	def name(self): return self._name
	def version(self): pass
	def description(self): pass
	def deps(self): pass

class InstalledPackage(Package):
	def installed(self): return True
	def read_state_file(self, f): return self._packages.read_state_file(self.name(), f)
	def version(self):
		try: return self._version
		except AttributeError: self._version = self.read_state_file('version')[0]
		return self._version
	def description(self):
		try: return self._description
		except AttributeError: self._description = self.read_state_file('description')[0]
		return self._description
	def auto(self):
		try: return self._auto
		except AttributeError: self._auto = self.read_state_file('installed')[0] == 'auto'
		return self._auto
	def deps(self):
		try: return self._deps
		except AttributeError:
			self._deps = []
			for dep in self.read_state_file('direct-dependencies'): self._deps.append(dep.split(' ')[0])
			return self._deps

class PackageRecipee(Package):
	def installed(self): return False
	def __init__(self, packages, name, version = None):
		Package.__init__(self, packages, name)
		self._version = version
		self._deps = []

	def version(self): return self._version
	def description(self): return '(no description)'
	def deps(self): return self._deps
	def add_dep(self, package_name): self._deps.append(package_name)
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

