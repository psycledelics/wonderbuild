# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006-2007 johan boule <bohan@jabber.org>
# copyright 2006-2007 psycledelics http://psycle.pastnotecut.org

_template = {}

def template(base):
	try: return _template[base]
	except KeyError:
	
		class result(base):
			def execute(self):
				if not base.execute(self): return False
				
				if not self.project()._scons().Clone is None:
					scons = self.project()._scons().Clone()
				else:
					scons = self.project()._scons().Copy()
					
				self.execute_env()._scons(scons)
				import SCons.SConf
				scons_sconf = SCons.SConf.SConf(
					env = scons,
					conf_dir = self.project().check_dir(),
					log_file = self.project().check_log(),
					config_h = None
				)
				scons_sconf.AddTest('packageneric__execute', lambda scons_sconf_context, self = self: self._execute_(scons_sconf_context))
				result = scons_sconf.packageneric__execute()
				scons_sconf.Finish()
				return result
			
			def _execute_(self, scons_sconf_context):
				scons_sconf_context.Message(self.project().root().message('packageneric: ', 'checking for ' + self.name() + ' ... ', font = '1;34'))
				result, output = self._scons_sconf_execute(scons_sconf_context)
				if result:
					if not output: output = 'yes'
					font = '1;32'
				else:
					if not output: output = 'no'
					font = '1;31'
				from packageneric.scons.tty_font import tty_font
				scons_sconf_context.Result(tty_font(font, output))
				return result
				
			def _scons_sconf_execute(self, scons_sconf_context):
				'to be overridden in derived classes'
				return True, 'ok'
				
		_template[base] = result
		return result
