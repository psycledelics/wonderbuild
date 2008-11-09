#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2008-2008 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

import os.path

def unique_path(file_name): return os.path.abspath(file_name)

_cache = {} # { unique_path: (rel_includes, abs_includes) }
_not_found_cache = set()

class CppDumbIncludeScanner:
	'C/C++ scanner for #include statements, and nothing else (dumb)'
	
	def __init__(self, paths = None):
		if paths is not None: self._paths = paths
		else: self._paths = []
	
	def add_path(self, path): self._paths.append(path)
	
	def scan(self, file_name):
		path = unique_path(file_name)

		global _cache
		if path in _cache: return

		f = file(file_name)
		try: s = f.read()
		finally: f.close()

		r = self.scan_string_slow(s)
		_cache[path] = r
		rel_includes, abs_includes = r
		
		if rel_includes:
			dir = os.path.dirname(file_name)
			for include in rel_includes:
				sub_file_name = self.search_rel(dir, include)
				if sub_file_name: self.scan(sub_file_name)
				#else: print >> sys.stderr, 'not found:', file_name + ': #include "' + include + '"'

		if abs_includes:
			for include in abs_includes:
				sub_file_name = self.search_abs(include)
				if sub_file_name: self.scan(sub_file_name)
				#else: print >> sys.stderr, 'not found:', file_name + ': #include <' + include + '>'

	def search_rel(self, dir, include):
		f = os.path.join(dir, include)
		u = unique_path(f)
		if u in _not_found_cache: return None
		if os.path.exists(f): return f
		else: print >> sys.stderr, 'not found:', '#include "' + u + '"'
		if not include.startswith(os.pardir + os.sep) and not include.startswith(os.curdir + os.sep):
			abs = self.search_abs(include)
			if abs: return abs
		_not_found_cache.add(u)
		return None
		
	def search_abs(self, include):
		global _not_found_cache
		if include in _not_found_cache: return None
		for dir in self._paths:
			f = os.path.join(dir, include)
			if os.path.exists(f): return f
		print >> sys.stderr, 'not found:', '#include <' + include + '>'
		_not_found_cache.add(include)
		return None

	def scan_string_fast(self, s):
		'^[ \t]*#[ \t]*(?:include|import)[ \t]*(<|")([^>"]+)(>|")'
	
	def scan_string_slow(self, s):
		normal = 0
		single_line_comment = 1
		multi_line_comment = 2
		single_quoted_string = 3
		double_quoted_string = 4
		token = 5
		token_quote = 6
		other = 7
	
		prev_state = state = normal; prev = '\0'
	
		rel_includes = []
		abs_includes = []
		for c in s:
			if c == '\r': continue
			if prev == '\\' and c == '\n': continue
			if c == '\t': c = ' '

			new_state = state

			if   state == single_line_comment:
				if c == '\n': new_state = normal
			elif state == multi_line_comment:
				if prev == '*' and c == '/': new_state = prev_state
			elif state == single_quoted_string:
				if prev != '\\' and c == "'": new_state = prev_state
				elif c == '\n': new_state = normal
			elif state == double_quoted_string:
				if prev != '\\' and c == '"': new_state = prev_state
				elif c == '\n': new_state = normal
			elif state == normal or state == other:
				if   prev == '/' and c == '/': new_state = single_line_comment
				elif prev == '/' and c == '*': new_state =  multi_line_comment
				elif c == "'": new_state = single_quoted_string
				elif c == '"': new_state = double_quoted_string
				elif state == normal:
					if c == '#' and prev != '/':
						new_state = token
						token_string = c
						token_quote = False
					elif c != ' ' and c != '\n' and c != '/': new_state = other
				elif state == other:
					if c == '\n': new_state = normal
			elif state == token:
				token_end = False
				if c == '\\':
					if token_quote: token_string += c
				elif prev == '/' and c == '/':
					new_state = single_line_comment
					token_end = True
				elif prev == '/' and c == '*': new_state = multi_line_comment
				elif c == '\n': token_end = True
				elif c == '"':
					token_quote = not token_quote
					token_string += c
				elif c == '<':
					token_quote = True
					token_string += c
				elif c == '>':
					token_quote = False
					token_string += c
				elif c == '/':
					if token_quote or prev_state == multi_line_comment: token_string += '/'
				elif c != ' ' or token_string[-1] != ' ': token_string += c

				if token_end:
					search = '#include '
					if token_string.startswith(search):
						l = len(search)
						kind = token_string[l]
						if kind == '"':   rel_includes.append(token_string[l + 1 : token_string.rfind('"')])
						elif kind == '<': abs_includes.append(token_string[l + 1 : token_string.rfind('>')])
					new_state = normal

			if new_state != state:
				prev_state = state
				state = new_state
			prev = c;
		return rel_includes, abs_includes

if __name__ == '__main__':
	import sys
	
	dirs = []
	files = []
	for arg in sys.argv[1:]:
		if os.path.isdir(arg): dirs.append(arg)
		else: files.append(arg)

	scanner = CppDumbIncludeScanner(dirs)
	for f in files: scanner.scan(f)
	
	for path, includes in _cache.iteritems():
		print path, includes
