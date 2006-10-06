# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006 johan boule <bohan@jabber.org>
# copyright 2006 psycledelics http://psycle.pastnotecut.org

class pkg_config_package:
	def __init__(
		self,
		packageneric,
		name = None,
		version = None,
		description = '',
		modules = None,
	):
		self._packageneric = packageneric
		self._name = name
		self._version = version
		self._description = description
		if modules is None: self._modules = []
		else: self._modules = modules
		self.packageneric().add_builder(self)
		
	def packageneric(self): return self._packageneric
		
	def name(self): return self._name
		
	def version(self): return self._version
	
	def description(self): return self._description
	
	def add_include_path(self, path, uninstalled = False, installed = False):
		if uninstalled: self.add_uninstalled_include_path(path)
		if installed: self.add_installed_include_path(path)
	
	def add_define(self, name, value, build = False, uninstalled = False, installed = False):
		if uninstalled: self.add_uninstalled_define(name, value)
		if installed: self.add_installed_define(name, value)

	def uninstalled_include_path(self):
		try: return  self._uninstalled_include_path
		except AttributeError:
			self._uninstalled_include_path = []
			return self._uninstalled_include_path
	def add_uninstalled_include_path(self, path): self.uninstalled_include_path().append(path)
	
	def uninstalled_defines(self):
		try: return self._uninstalled_defines
		except AttributeError:
			self._uninstalled_defines = {}
			return self._uninstalled_defines
	def add_uninstalled_define(self, name, value): self.uninstalled_defines()[name] = value
		
	def installed_include_path(self):
		try: return self._installed_include_path
		except AttributeError:
			self._installed_include_path = []
			return self._installed_include_path
	def add_installed_include_path(self, path): self.installed_include_path().append(path)
	
	def installed_defines(self):
		try: return self._installed_defines
		except AttributeError:
			self._installed_defines = {}
			return self._installed_defines
	def add_installed_define(self, name, value): self.installed_defines()[name] = value
		
	def modules(self): return self._modules
		
	def build_depends(self):
		try: return self._build_depends
		except AttributeError:
			self._build_depends = []
			for module in self.modules():
				for package in module.build_depends() + module.depends():
					if not package in self._build_depends: self._build_depends.append(package)
			return self._build_depends

	def string(self, uninstalled):
		string = 'Name: ' + self.name()
		if uninstalled: string += ' (uninstalled)'
		string += '\n'
		string += 'Description: ' + self.description() + '\n'
		string += 'Version: ' + str(self.version()) + '\n'
		if uninstalled: environment = self.uninstalled_environment()
		else: environment = self.installed_environment()
		D_prefix = environment.subst('$CPPDEFPREFIX')
		D_suffix = environment.subst('$CPPDEFSUFFIX')
		def D(k, v): return " %s%s='%s'%s" % (D_prefix, k, v, D_suffix)
		I_prefix = environment.subst('$INCPREFIX')
		I_suffix = environment.subst('$INCSUFFIX')
		def I(I): return ' ' + I_prefix + environment.Dir(I).get_abspath() + I_suffix
		L_prefix = environment.subst('$LIBDIRPREFIX')
		L_suffix = environment.subst('$LIBDIRSUFFIX')
		def L(L): return ' ' + L_prefix + environment.Dir(L).get_abspath() + L_suffix
		l_prefix = environment.subst('$LIBLINKPREFIX')
		l_suffix = environment.subst('$LIBLINKSUFFIX')
		def l(l): return ' ' + l_prefix + l + l_suffix
		string += 'CFlags:'
		for path in environment.Split(environment.subst('$CPPPATH')): string += I(path)
		try:
			for (k, v) in environment['CPPDEFINES'].items(): string += D(k, environment.subst(v))
		except KeyError: pass
		string += ' ' + environment.subst('$CXXFLAGS') + '\n'
		string += 'Libs:'
		for module in self.modules(): string += l(module.name())
		for path in environment.Split(environment.subst('$LIBPATH')): string += L(path)
		for library in environment.Split(environment.subst('$LIBS')): string += l(library)
		string += ' ' + environment.subst('$LINKFLAGS') + '\n'
		string += 'Libs.private:'
		for module in self.modules(): string += l(module.name())
		for path in environment.Split(environment.subst('$LIBPATH')): string += L(path)
		for library in environment.Split(environment.subst('$LIBS')): string += l(library)
		string += ' ' + environment.subst('$LINKFLAGS') + '\n'
		string += 'Requires:'
		for package in self.build_depends():
			if package.pkg_config(): string += ' ' + package.pkg_config()
		string += '\n'
		return string
	
	def uninstalled_environment(self):
		try: return self._uninstalled_environment
		except AttributeError:
			self._uninstalled_environment = self.packageneric().uninstalled_environment().Copy()
			for module in self.modules(): module.merge_uninstalled_environment(self._uninstalled_environment)
			import os.path
			for i in self.uninstalled_include_path(): self._uninstalled_environment.AppendUnique(CPPPATH = [os.path.join(self.packageneric().build_directory(), i)])
			self._uninstalled_environment.AppendUnique(CPPPATH = self.uninstalled_include_path())
			self._uninstalled_environment.Append(CPPDEFINES = self.uninstalled_defines())
			return self._uninstalled_environment

	def installed_environment(self):
		try: return self._installed_environment
		except AttributeError:
			self._installed_environment = self.packageneric().installed_environment().Copy()
			for module in self.modules(): module.merge_installed_environment(self._installed_environment)
			self._installed_environment.AppendUnique(CPPPATH = self.installed_include_path())
			self._installed_environment.Append(CPPDEFINES = self.installed_defines())
			return self._installed_environment

	def target_name(self): return self.name() + '.pc'

	def targets(self):
		try: return self._targets
		except AttributeError:
			depends = []
			for depend_lists in map(lambda module: module.targets(), self.modules()):
				for depend_list in depend_lists: depends.extend(depend_list)
			import os.path
			import SCons.Node.Python
			self._targets = [
				self.uninstalled_environment().WriteToFile(os.path.join(self.packageneric().build_directory(), self.name() + '-uninstalled.pc'), SCons.Node.Python.Value(self.string(uninstalled = True))),
				self.installed_environment().WriteToFile(os.path.join(self.packageneric().build_directory(), self.target_name()), SCons.Node.Python.Value(self.string(uninstalled = False)))
			]
			for target_list in self._targets:
				for target in target_list:
					target.add_dependency(depends)
			return self._targets
