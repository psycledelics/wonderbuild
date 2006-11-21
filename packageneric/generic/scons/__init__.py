# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006 johan boule <bohan@jabber.org>
# copyright 2006 psycledelics http://psycle.pastnotecut.org

def _merge_environment(source, destination): # todo remove
	try: destination.AppendUnique(CPPFLAGS = source['CPPFLAGS'])
	except KeyError: pass
	try: destination.Append(CPPDEFINES = source['CPPDEFINES'])
	except KeyError: pass
	try: destination.AppendUnique(CPPPATH = source['CPPPATH'])
	except KeyError: pass
	try: destination.AppendUnique(CXXFLAGS = source['CXXFLAGS'])
	except KeyError: pass
	try: destination.AppendUnique(LINKFLAGS = source['LINKFLAGS'])
	except KeyError: pass
	try: destination.AppendUnique(LIBPATH = source['LIBPATH'])
	except KeyError: pass
	try: destination.AppendUnique(LIBS = source['LIBS'])
	except KeyError: pass
	import os
	try: path = source['ENV']['PKG_CONFIG_PATH']
	except KeyError: path = ''
	else: path = source.subst(path)
	try: path = destination['ENV']['PKG_CONFIG_PATH'] + os.pathsep + path
	except KeyError: pass
	try: path = path + os.pathsep + os.environ['PKG_CONFIG_PATH']
	except KeyError: pass
	destination.AppendENVPath('PKG_CONFIG_PATH', path)
	
def _dump_environment(environment, all = False): # todo remove
	if all:
		if False: print environment.Dump()
		else:
			dictionary = environment.Dictionary()
			keys = dictionary.keys()
			keys.sort()
			for key in keys: print '%s = %s' % (key, dictionary[key])
	else:
		def show(key):
			try:
				environment[key]
				if len(environment[key]): print key, '->', environment[key], '->', environment.subst('$' + key)
				else: print key, '<- empty'
			except KeyError: pass
		for x in 'CPPFLAGS', 'CPPDEFINES', 'CPPPATH', 'CXXFLAGS', 'LINKFLAGS', 'LIBPATH', 'LIBS': show(x)
