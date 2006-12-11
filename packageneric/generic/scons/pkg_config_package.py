# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006 johan boule <bohan@jabber.org>
# copyright 2006 psycledelics http://psycle.pastnotecut.org

import os.path
from builder import builder

class pkg_config_package(builder):
	def __init__(self, project,
		name,
		version,
		description,
		modules = None,
	):
		self._project = project
		self._name = name
		self._version = version
		self._description = description
		if modules is None: self._modules = []
		else: self._modules = modules
		self.project().add_builder(self)
		
	def project(self): return self._project
		
	def name(self): return self._name
	
	def local_package(self):
		from local_package import local_package
		return local_package(self)
	
	def version(self): return self._version
	
	def description(self): return self._description
	
	def modules(self): return self._modules

	def dependencies(self):
		try: return self._build_dependencies
		except AttributeError:
			self._build_dependencies = []
			for module in self.modules():
				for package in module.build_dependencies() + module.dependencies():
					if not package in self._build_dependencies: self._build_dependencies.append(package)
			return self._build_dependencies

	def string(self, uninstalled):
		string = 'Name: ' + self.name()
		if uninstalled: string += ' (uninstalled)'
		string += '\n'
		string += 'Description: ' + self.description() + '\n'
		string += 'Version: ' + str(self.version()) + '\n'
		if uninstalled: env = self.uninstalled_env()
		else: env = self.installed_env()

		scons = self.project()._scons()

		D_prefix = scons.subst('$CPPDEFPREFIX')
		D_suffix = scons.subst('$CPPDEFSUFFIX')
		def D(name, value): return D_prefix + name + "='" + scons.subst(value) + "'" + D_suffix

		I_prefix = scons.subst('$INCPREFIX')
		I_suffix = scons.subst('$INCSUFFIX')
		def I(path): return I_prefix + scons.subst(path) + I_suffix

		L_prefix = scons.subst('$LIBDIRPREFIX')
		L_suffix = scons.subst('$LIBDIRSUFFIX')
		def L(path): return L_prefix + scons.subst(path) + L_suffix

		l_prefix = scons.subst('$LIBLINKPREFIX')
		l_suffix = scons.subst('$LIBLINKSUFFIX')
		def l(library): return l_prefix + scons.subst(library) + l_suffix

		string += 'CFlags: ' + \
			' '.join([D(name, value) for name, value in env.compilers().cxx().defines().get().items()]) + ' ' + \
			' '.join([I(path) for path in env.compilers().cxx().paths()]) + ' ' + \
			' '.join([flag for flag in env.compilers().cxx().flags()]) + '\n'
		string += 'Libs: ' + \
			' '.join([L(path) for path in env.linker().paths()]) + ' ' + \
			' '.join([l(path) for path in env.linker().libraries()]) + ' ' + \
			' '.join([flag for flag in env.linker().flags()]) + '\n'
		string += 'Libs.private: ' + \
			' '.join([l(path) for path in env.linker().libraries()]) + '\n'
		string += 'Requires: '
		import check.pkg_config
		string += ' '.join([pkg_config.name() for pkg_config in filter(lambda x: isinstance(x, check.pkg_config.pkg_config), self.dependencies())])
		string += '\n'
		return string
	
	def uninstalled_env(self):
		try: return self._uninstalled_env_
		except AttributeError:
			env = self._uninstalled_env_ = self.project().contexes().client().uninstalled().attached()
			for module in self.modules(): env.attach(module.contexes().client().uninstalled())
			return env

	def installed_env(self):
		try: return self._installed_env_
		except AttributeError:
			env = self._installed_env_ = self.project().contexes().client().installed().attached()
			for module in self.modules(): env.attach(module.contexes().client().installed())
			return env

	def alias_names(self): return ['packageneric:pkg-config-package', self.name()]

	def targets(self):
		try: return self._targets
		except AttributeError:
			uninstalled_file_name = os.path.join(self.project().build_variant_intermediate_dir(), 'pkgconfig', self.name() + '-uninstalled.pc')
			installed_file_name = os.path.join('$packageneric__install__stage_destination', '$packageneric__install__lib', 'pkgconfig', self.name() + '.pc')

			dependencies = []
			for dependency_lists in [module.targets() for module in self.modules()]:
				for dependency_list in dependency_lists: dependencies.extend(dependency_list)
			
			env = self.uninstalled_env()
			
			paths = []
			for path in env.compilers().cxx().paths(): paths.append(os.path.join(self.project().intermediate_target_dir(), path))
			env.compilers().cxx().paths().add(paths)
			
			paths = []
			for path in env.compilers().cxx().paths(): paths.append(self.project()._scons().Dir(path).get_abspath())
			env.compilers().cxx().paths().add(paths)
			
			env.linker().paths().add([os.path.join('$packageneric__install__stage_destination', '$packageneric__install__lib')])

			paths = []
			for path in env.linker().paths(): paths.append(self.project()._scons().Dir(path).get_abspath())
			env.linker().paths().add(paths)
			
			for module in self.modules(): env.linker().libraries().add([module.name()])

			scons = self.project()._scons()
			self._targets = [
				scons.Alias(uninstalled_file_name, [scons.FileFromValue(uninstalled_file_name, self.string(uninstalled = True))] + dependencies),
				scons.Alias(installed_file_name, [scons.FileFromValue(installed_file_name, self.string(uninstalled = False))] + dependencies),
			]
			return self._targets
