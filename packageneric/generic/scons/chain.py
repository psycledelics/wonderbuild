# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006-2007 johan boule <bohan@jabber.org>
# copyright 2006-2007 psycledelics http://psycle.pastnotecut.org

_template = {}

def template(base): # projected, attachable, env
	try: return _template[base]
	except KeyError:

		class result(base):
			class target_types:
				loadable = 0
				shared = 1
				static = 2
				program = 3
				
			def __init__(self, project,
				target_type = target_types.loadable,
				archiver = None,
				archiver_flags = None,
				archive_indexer = None,
				archive_indexer_flags = None,
				linker = None,
				library_paths = None,
				libraries = None,
				linker_flags = None,
				debug = None,
				*args, **kw
			):
				base.__init__(*(self, project) + args, **kw)
				self._target_type = target_type
				if archiver is not None: self.archiver().command().set(archiver)
				if archiver_flags is not None: self.archiver().flags().add(archiver_flags)
				if archive_indexer is not None: self.archiver().indexer().command().set(archive_indexer)
				if archive_indexer_flags is not None: self.archiver().indexer().flags().add(archive_indexer_flags)
				if linker is not None: self.linker().command().set(linker)
				if library_paths is not None: self.linker().paths().add(library_paths)
				if libraries is not None: self.linker().libraries().add(libraries)
				if linker_flags is not None: self.linker().flags().add(linker_flags)
				if debug is not None: self.debug().set(debug)
				if target_type in (result.target_types.shared, result.target_types.loadable): self.link_library().set(True)
				else: self.link_library().set(False)

			def target_type(self): return self._target_type
			
			def compilers(self):
				try: return self._compilers
				except AttributeError:
					from compilers import compilers
					self._compilers = compilers()
					return self._compilers

			def archiver(self):
				try: return self._archiver
				except AttributeError:
					#assert self.target_type() == result.target_types.static
					import archiver
					self._archiver = archiver.template(base)(self.project())
					for attached in self._attached:
						if isinstance(attached, result): self._archiver.attach(attached.archiver())
					return self._archiver
					
			def linker(self):
				try: return self._linker
				except AttributeError:
					#assert self.target_type() != result.target_types.static
					import linker
					self._linker = linker.template(base)(self.project())
					for attached in self._attached:
						if isinstance(attached, result): self._linker.attach(attached.linker())
					return self._linker

			def debug(self):
				try: return self._debug
				except AttributeError:
					from value import value
					self._debug = value()
					for attached in self._attached:
						if isinstance(attached, result): self._debug.attach(attached.debug())
					return self._debug

			def multi_threading(self):
				try: return self._multi_threading
				except AttributeError:
					from value import value
					self._multi_threading = value()
					for attached in self._attached:
						if isinstance(attached, result): self._multi_threading.attach(attached.multi_threading())
					return self._multi_threading
			
			def pre_compile(self):
				try: return self._pre_compile
				except AttributeError:
					from value import value
					self._pre_compile = value()
					for attached in self._attached:
						if isinstance(attached, result): self._pre_compile.attach(attached.pre_compile())
					return self._pre_compile
			
			def link_library(self):
				'whether to link the objects into a shared or loadable library or just archive them in a static library (or link a program)'
				try: return self._link_library
				except AttributeError:
					from value import value
					self._link_library = value()
					for attached in self._attached:
						if isinstance(attached, result): self._link_library.attach(attached.link_library())
					return self._link_library
			
			def link_with_static_libraries(self):
				try: return self._link_with_static_libraries
				except AttributeError:
					from value import value
					self._link_with_static_libraries = value()
					for attached in self._attached:
						if isinstance(attached, result): self._link_with_static_libraries.attach(attached.link_with_static_libraries())
					return self._link_with_static_libraries
			
			def _implementation(self):
				try: return self._implementation_
				except AttributeError:
					from value import value
					self._implementation_ = value()
					for attached in self._attached:
						if isinstance(attached, result): self._implementation_.attach(attached._implementation())
					return self._implementation_
			
			def attach(self, source):
				base.attach(self, source)
				if isinstance(source, result):
					for self_compiler in self.compilers():
						for source_compiler in source.compilers(): self_compiler.attach(source_compiler)
					
					try: archiver = self._archiver
					except AttributeError: pass
					else: archiver.attach(source.archiver())

					try: linker = self._linker
					except AttributeError: pass
					else: linker.attach(source.linker())

					try: implementation = self._implementation_
					except AttributeError: pass
					else: implementation.attach(source._implementation())

					try: debug = self._debug
					except AttributeError: pass
					else: debug.attach(source.debug())
					
					try: multi_threading = self._multi_threading
					except AttributeError: pass
					else: multi_threading.attach(source.multi_threading())
					
					try: pre_compile = self._pre_compile
					except AttributeError: pass
					else: pre_compile.attach(source.pre_compile())
					
					try: link_library = self._link_library
					except AttributeError: pass
					else: link_library.attach(source.link_library())
					
					try: link_with_static_libraries = self._link_with_static_libraries
					except AttributeError: pass
					else: link_with_static_libraries.attach(source.link_with_static_libraries())
					
			def _scons(self, scons):
				implementation = self._implementation().get()
				if implementation is not None:
					self = self.attached()
					implementation(self)

				base._scons(self, scons)
				for compiler in self.compilers(): compiler._scons(scons)
				self.archiver()._scons(scons)
				self.linker()._scons(scons)
				
		_template[base] = result
		return result
