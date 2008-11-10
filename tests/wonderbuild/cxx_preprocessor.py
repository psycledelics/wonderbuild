#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2008-2008 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

import os.path, re, cPickle, signature #, dircache

class Cache:
	def __init__(self, cache_path):
		self._cache_path = cache_path
		self._not_found = set() # of unique_path
		if os.path.exists(cache_path): self.load()
		else:
			self._deps = {} # { unique_path: (rel_includes, abs_includes) }
		
	def deps(self): return self._deps
	def not_found(self): return self._not_found
	
	def load(self):
		if not os.path.exists(self._cache_path): return
		f = file(self._cache_path)
		try:
			self._deps = cPickle.load(f)
			sigs = cPickle.load(f)
		finally: f.close()
		for path in self._deps.keys(): # copy because we remove some elements in the loop
			sig = signature.Sig()
			try: signature.file_sig(sig, path)
			except: self._not_found.add(path)
			else:
				if sig.digest() != sigs[path]: del self._deps[path]

	def save(self):
		f = file(self._cache_path, 'wb')
		try:
			p = cPickle.HIGHEST_PROTOCOL
			cPickle.dump(self._deps, f, p)
			sigs = {}
			for path in self._deps:
				sig = signature.Sig()
				signature.file_sig(sig, path)
				sigs[path] = sig.digest()
			cPickle.dump(sigs, f, p)
		finally: f.close()

_cache = Cache('/tmp/scanner-deps.cache')

_line_continuations = re.compile(r'\\\r*\n', re.MULTILINE)
_cpp = re.compile(r'''(/\*[^*]*\*+([^/*][^*]*\*+)*/)|//[^\n]*|("(\\.|[^"\\])*"|'(\\.|[^'\\])*'|.[^/"'\\]*)''', re.MULTILINE)
_include = re.compile(r'^[ \t]*#[ \t]*include[ \t]*(["<])([^">]*)[">].*$', re.MULTILINE)

class CppDumbIncludeScanner:
	'C/C++ scanner for #include statements, and nothing else (dumb)'
	
	def __init__(self, paths = None):
		if paths is not None: self._paths = paths
		else: self._paths = []
	
	def _cache(self):
		global _cache
		return _cache
	
	def _unique_path(self, file_name):
		return os.path.abspath(file_name)
		#try: return os.path.realpath(file_name)
		#except: return os.path.abspath(file_name)

	def add_path(self, path): self._paths.append(path)
	
	def scan(self, file_name):
		u = self._unique_path(file_name)

		if u in self._cache().deps():
			#print 'cached:', u
			return

		print 'scanning:', u

		try: f = file(file_name)
		except:
			self._cache().not_found().add(u)
			return
		try: s = f.read()
		finally: f.close()

		r = self.parse_string_fast(s)
		self._cache().deps()[u] = r
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
		if os.path.isabs(include):
			u = self._unique_path(include)
			if u in self._cache().not_found(): return None
			if os.path.exists(f): return f
			#else: print >> sys.stderr, 'not found:', '#include "' + u + '"'
		else:
			f = os.path.join(dir, include)
			u = self._unique_path(f)
			if u in self._cache().not_found(): return None
			if os.path.exists(f): return f
			#else: print >> sys.stderr, 'not found:', '#include "' + u + '"'
			if  not include.startswith(os.pardir + os.sep) \
			and not include.startswith(os.curdir + os.sep):
				abs = self.search_abs(include)
				if abs: return abs
		self._cache().not_found().add(u)
		return None
		
	def search_abs(self, include):
		global _not_found_cache
		if include in self._cache().not_found(): return None
		for dir in self._paths:
			f = os.path.join(dir, include)
			if os.path.exists(f): return f
		#print >> sys.stderr, 'not found:', '#include <' + include + '>'
		self._cache().not_found().add(include)
		return None

	def parse_string_fast(self, s):

		s = _line_continuations.sub('', s)

		def repl(m):
			s = m.group(1)
			if s is not None: return ' '
			s = m.group(3)
			if s is None: return ''
			return s
		s = _cpp.sub(repl, s)

		#for l in s.split('\n'): print '[' + l + ']'
		#return

		rel_includes = []
		abs_includes = []
		for m in _include.finditer(s):
			kind = m.group(1)
			if kind == '"':   rel_includes.append(m.group(2))
			elif kind == '<': abs_includes.append(m.group(2))
		return rel_includes, abs_includes
	
	def parse_string_slow(self, s):
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
				elif c != ' ' or (token_string[-1] != ' ' and token_string[-1] != '#'): token_string += c

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
	#sys.path.insert(0, os.path.dirname(__file__))

	dirs = []
	files = []
	for arg in sys.argv[1:]:
		if os.path.isdir(arg): dirs.append(arg)
		else: files.append(arg)

	scanner = CppDumbIncludeScanner(dirs)
	for f in files: scanner.scan(f)
	scanner._cache().save()
	
	#for path, includes in scanner._cache().deps().iteritems():
	#	print path, includes
