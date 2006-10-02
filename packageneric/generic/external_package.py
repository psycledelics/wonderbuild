# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006 johan boule <bohan@jabber.org>
# copyright 2006 psycledelics http://psycle.pastnotecut.org

class external_package:
	
	def __init__(
		self,
		packageneric,
		distribution_packages,
		url = None,
		pkg_config = None,
		depends = None,
		builds = None,
		calls = None,
	):
		self._packageneric = packageneric
		self._distribution_packages = distribution_packages
		self._url = url
		self._pkg_config = pkg_config
		if not depends is None: self._depends = depends
		else: self._depends = []
		self._builds = []
		if not builds is None:
			for x in builds: self.add_build(x[0], x[1], x[2])
		if not calls is None: self._calls = calls
		else: self._calls = []
		self._found = None
		self._environment = None
		self._configure = None
		
	def packageneric(self): return self._packageneric
	
	def distribution_packages(self): return self._distribution_packages
	
	def url(self): return self._url
		
	def pkg_config(self): return self._pkg_config
	def recursed_pkg_config(self): pass # todo
	def _check_pkg_config(self):
		return_code, output = self.configure().packageneric__pkg_config(self, self.pkg_config(), 'exists')
		return return_code

	def depends(self):
		packages = []
		for package in self._depends:
			if not package in packages: packages.append(package)
			for package in package.depends():
				if not package in packages:
					packages.append(package)
		return packages
	def add_depend(self, depend): self._depends.append(depend)
	def add_depends(self, depends):
		for x in depends: self.add_depend(x)

	def builds(self): return self._builds
	def add_build(self, description, libraries, text = 'int main() { return 0; }', extension = '.cpp'):
		class build:
			def __init__(self):
				self._description = description
				self._libraries = libraries
				self._text = text
				self._extension = extension
			def description(self): return self._description
			def libraries(self): return self._libraries
			def text(self): return self._text
			def extension(self): return self._extension
		self._builds.append(build())
	def _check_build(self, description, libraries, text = 'int main() { return 0; }', extension = '.cpp'): return self.configure().packageneric__try_build(self, description, libraries, text, extension)

	def calls(self): return self._calls
	def add_call(self, call): self._calls.append(call)
	def add_call(self, calls):
		for x in calls: self.add_call(x)
	def _check_call(self, call, detail): return self.configure().packageneric__call(self, call, detail)
	
	def __str__(self):
		line = '____________________'
		separator = '\n|' + line + '\n|'
		string = '\n ' + line + '\n| '
		if self.pkg_config(): string += '\n| pkg-config: ' + self.pkg_config()
		for x in self.builds(): string += '\n| ' + x.description() + ': libraries '"'" + ' '.join(x.libraries()) + "'"' and their associated headers '
		for x in self.calls(): string += '\n| ' + str(x)
		if self.distribution_packages():
			string += separator
			for (k, v) in self.distribution_packages().items(): string += '\n| -> on ' + k + ' distributions, the package names are ' + v
		if not self.url() is None:
			if not self.distribution_packages(): string += separator
			string += '\n| -> '
			if self.distribution_packages(): string += 'otherwize, '
			string += 'the source of this package can be downloaded from ' + self.url()
		string += '\n|' + line + '\n'
		return string
	
	def found(self):
		if self._found is None:
			self._found = True
			for package in self.depends():
				self._found &= package.found()
				if package.found(): package.merge_environment(self.environment())
			if self.pkg_config(): self._found &= self._check_pkg_config()
			for x in self.builds(): self._found &= self._check_build(x.description(), x.libraries(), x.text(), x.extension())
			for x in self.calls(): self._found &= self._check_call(x, detail = False)
			self.finish_configure()
		return self._found
		
	def environment(self):
		if not self._environment:
			self._environment = self.packageneric().common_environment().Copy()
			if not self.found():
				message = 'the following external packages:'
				depends_not_found = []
				for package in self.depends():
					if not package.found(): depends_not_found.append(str(package))
				for depend_not_found in depends_not_found: message += str(depend_not_found) + '\n'
				message += 'are needed for the external package:' + str(self)
				self.packageneric().error(message)
		return self._environment
	
	def merge_environment(self, destination):
		import packageneric.generic
		packageneric.generic._merge_environment(self.environment(), destination)
		
	def configure(self):
		if self._configure is None:
			import os.path
			import SCons.SConf
			self._configure = SCons.SConf.SConf(
				env = self.environment(),
				conf_dir = os.path.join('$packageneric__build_directory', 'configure'),
				log_file = os.path.join('$packageneric__build_directory', 'configure.log'),
				config_h = os.path.join('$packageneric__build_directory', 'configure.hpp'),
				custom_tests =
				{
					'packageneric__pkg_config' : lambda context, self, name, what: _pkg_config(self, context, name, what),
					'packageneric__try_build' : lambda context, self, description, libraries, text, extension: _try_build(self, context, description, libraries, text, extension),
					'packageneric__call' : lambda context, self, call, detail: _call(self, context, call, detail)
				}
			)
		return self._configure
	
	def finish_configure(self):
		if not self._configure is None:
			self.configure().Finish()
			self._configure = None

#@staticmethod
def _pkg_config(self, context, name, what):
	import os
	try: context.env.AppendUnique(ENV = {'PKG_CONFIG_PATH': os.environ['PKG_CONFIG_PATH']})
	except KeyError: pass
	context.Message(self.packageneric().message('packageneric: ', 'checking for ' + name + ' ... '))
	result, output = context.TryAction("pkg-config --%s '%s'" % (what, name))
	context.Result(_result(self, result))
	return result, output

#@staticmethod
def _try_build(self, context, description, libraries, text, extension):
	context.Message(self.packageneric().message('packageneric: ', 'checking for ' + description + ' ... '))
	old_libs = context.AppendLIBS(libraries)
	result = context.TryBuild(context.env.Program, text, extension)
	if not result: context.SetLIBS(old_libs)
	context.Result(_result(self, result))
	return result

#@staticmethod
def _call(self, context, call, detail):
	context.Display(self.packageneric().message('packageneric: ', 'checking for ' + str(call) + ' ... '))
	if detail: context.Display('\n')
	else:
		class nullout:
			def __init__(self, underlying_out):
				self._underlying_out = underlying_out
			def underlying_out(self):
				return self._underlying_out
			def __getattr__(self, attr):
				return getattr(self._underlying_out, attr)
			def write(self, *args, **kw): pass
		import sys
		sys.stdout = nullout(sys.stdout)
	self.packageneric().push_indentation()
	result = call()
	if detail: context.Message(self.packageneric().message('packageneric: ', 'result: '))
	else:
		sys.stdout = sys.stdout.underlying_out()
		context.Message('')
	context.Result(_result(self, result))
	self.packageneric().pop_indentation()
	return result

#@staticmethod
def _result(self, result):
	if result:
		font = '1;32'
		text = 'yes'
	else:
		font = '1;31'
		text = 'no'
	import packageneric.generic
	return packageneric.generic.tty_font(font, text)
