# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006-2007 johan boule <bohan@jabber.org>
# copyright 2006-2007 psycledelics http://psycle.pastnotecut.org

_template = {}

def template(mixin):
	try: return _template[mixin]
	except KeyError:
		import static_shared, flags, paths
		base = \
			static_shared.template(
			flags.template(
			paths.template(
			mixin)))
		
		class result(base):
			def __init__(self, project, *args, **kw): base.__init__(*(self, project) + args, **kw)
			
			pass # ...
					
		_template[mixin] = result
		return result
