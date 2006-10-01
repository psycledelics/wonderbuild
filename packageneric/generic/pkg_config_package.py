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
		modules = None
	):
		self._packageneric = packageneric
		self._name = name
		self._version = version
		self._description = description
		if modules is None: self._modules = []
		else: self._modules = modules
		self._build_depends = None
		self._uninstalled_environment = None
		self._installed_environment = None
		self._targets = None
		self.packageneric().add_target(self.name() + '.pc', self)
		
	def packageneric(self): return self._packageneric
		
	def name(self): return self._name
		
	def version(self): return self._version
	
	def description(self): return self._description
		
	def modules(self): return self._modules
		
	def build_depends(self):
		if self._build_depends is None:
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
		for (k, v) in environment['CPPDEFINES'].items(): string += D(k, environment.subst(v))
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
		if self._uninstalled_environment is None: self._uninstalled_environment = self.packageneric().uninstalled_environment().Copy()
		return self._uninstalled_environment

	def installed_environment(self):
		if self._installed_environment is None: self._installed_environment = self.packageneric().installed_environment().Copy()
		return self._installed_environment

	def targets(self):
		if self._targets is None:
			for module in self.modules():
				module.targets()
				module.merge_uninstalled_environment(self.uninstalled_environment())
				module.merge_installed_environment(self.installed_environment())
			import os.path
			import SCons.Node.Python
			self._targets = [
				self.uninstalled_environment().WriteToFile(os.path.join(self.packageneric().build_directory(), self.name() + '-uninstalled.pc'), SCons.Node.Python.Value(self.string(uninstalled = True))),
				self.installed_environment().WriteToFile(os.path.join(self.packageneric().build_directory(), self.name() + '.pc'), SCons.Node.Python.Value(self.string(uninstalled = False)))
			]
			depends = []
			for depend_list in map(lambda x: x.targets(), self.modules()):
				depends.extend(depend_list)
			for target_list in self._targets:
				for target in target_list:
					target.add_dependency(depends)
		return self._targets
