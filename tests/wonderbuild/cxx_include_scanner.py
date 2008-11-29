#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2008-2008 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

import sys, os.path, re, cPickle, gc
from hashlib import md5 as Sig

_line_continuations = re.compile(r'\\\r*\n', re.MULTILINE)
_cpp = re.compile(r'''(/\*[^*]*\*+([^/*][^*]*\*+)*/)|//[^\n]*|("(\\.|[^"\\])*"|'(\\.|[^'\\])*'|.[^/"'\\]*)''', re.MULTILINE)
_include = re.compile(r'^[ \t]*#[ \t]*include[ \t]*(["<])([^">]*)[">].*$', re.MULTILINE)

class IncludeScanner(object):
	'C/C++ dependency scanner. #include statements, and nothing else, no #if, no #define (dumb)'
	
	def __init__(self, filesystem, paths = None, cache_path = '/tmp/dep-scanner.cache'):
		self.fs = filesystem
		if paths is not None: self.paths = paths
		else: self.paths = set()
		self.not_found = set() # of unique_path
		self.cache_path = cache_path
		self.load()

	def load(self):
		gc.disable()
		try:
			try:
				f = file(self.cache_path, 'rb')
				try:
					p = cPickle.Unpickler(f)
					self.deps = p.load()
				finally: f.close()
			except Exception, e:
				print >> sys.stderr, 'could not load pickle:', e
				self.deps = {} # { unique_path: (rel_includes, abs_includes) }
			else:
				for path in self.deps.keys(): # copy because we remove some elements in the loop
					print 'scanner: cached:', path
					try: changed = self.fs.node(path).changed()
					except OSError: self.not_found.add(path) ; print 'scanner: del not found:', path
					else:
						if changed: del self.deps[path] ;  print 'scanner: del changed:', changed
		finally: gc.enable()

	def dump(self):
		f = file(self.cache_path, 'wb')
		try:
			p = cPickle.Pickler(f, cPickle.HIGHEST_PROTOCOL)
			for path in self.deps: self.fs.node(path)
			p.dump(self.deps)
		finally: f.close()
	
	def _unique_path(self, file_name):
		return os.path.abspath(file_name)
		#try: return os.path.realpath(file_name)
		#except: return os.path.abspath(file_name)

	def scan_deps(self, file_name): return self._scan_deps(file_name)
	def _scan_deps(self, file_name, already_seen = None):
		u = self._unique_path(file_name)

		if already_seen is not None:
			if u in already_seen: return
 			already_seen.add(u)
		else: already_seen = set()
	
		try: r = self.deps[u]
		except KeyError:
			print 'parsing:', u

			try: f = file(file_name, 'rb')
			except:
				self.not_found.add(u)
				return already_seen
			try: s = f.read()
			finally: f.close()

			r = self.parse_string(s)
			self.deps[u] = r
		rel_includes, abs_includes = r

		if rel_includes:
			dir = os.path.dirname(file_name)
			for include in rel_includes:
				sub_file_name = self.search_rel(dir, include)
				if sub_file_name: self._scan_deps(sub_file_name, already_seen)
				#else: print >> sys.stderr, 'not found:', file_name + ': #include "' + include + '"'

		if abs_includes:
			for include in abs_includes:
				sub_file_name = self.search_abs(include)
				if sub_file_name: self._scan_deps(sub_file_name, already_seen)
				#else: print >> sys.stderr, 'not found:', file_name + ': #include <' + include + '>'
	
		return already_seen
	
	def search_rel(self, dir, include):
		if os.path.isabs(include):
			u = self._unique_path(include)
			if u in self.not_found: return None
			if os.path.exists(f): return f
			#else: print >> sys.stderr, 'not found:', '#include "' + u + '"'
		else:
			f = os.path.join(dir, include)
			u = self._unique_path(f)
			if u in self.not_found: return None
			if os.path.exists(f): return f
			#else: print >> sys.stderr, 'not found:', '#include "' + u + '"'
			if  not include.startswith(os.pardir + os.sep) \
			and not include.startswith(os.curdir + os.sep):
				abs = self.search_abs(include)
				if abs: return abs
		self.not_found.add(u)
		return None
		
	def search_abs(self, include):
		if include in self.not_found: return None
		for dir in self.paths:
			f = os.path.join(dir, include)
			if os.path.exists(f): return f
		#print >> sys.stderr, 'not found:', '#include <' + include + '>'
		self.not_found.add(include)
		return None

	def parse_string(self, s): return self._parse_string_fast(s)

	def _parse_string_fast(self, s):
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

		rel_includes = set()
		abs_includes = set()
		for m in _include.finditer(s):
			kind = m.group(1)
			if   kind == '"': rel_includes.add(m.group(2))
			elif kind == '<': abs_includes.add(m.group(2))
		return rel_includes, abs_includes
	
	def _parse_string_slow(self, s):
		normal = 0
		single_line_comment = 1
		multi_line_comment = 2
		single_quoted_string = 3
		double_quoted_string = 4
		token = 5
		token_quote = 6
		other = 7
	
		prev_state = state = normal; prev = '\0'
	
		rel_includes = set()
		abs_includes = set()
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
						if   kind == '"': rel_includes.add(token_string[l + 1 : token_string.rfind('"')])
						elif kind == '<': abs_includes.add(token_string[l + 1 : token_string.rfind('>')])
					new_state = normal

			if new_state != state:
				prev_state = state
				state = new_state
			prev = c;
		return rel_includes, abs_includes
		
	def display(self):
		print 'cpp dep scanner:'
		print 'include path:', self.paths
		for path, includes in self.deps.iteritems(): print path, includes
		print 'not found:', self.not_found

if __name__ == '__main__':
	import time
	
	import filesystem
	
	dirs = set()
	files = set()
	for arg in [x for x in sys.argv[1:] if not x.startswith('-')]:
		if os.path.isdir(arg): dirs.add(arg)
		else: files.add(arg)

	t0 = time.time()
	fs = filesystem.FileSystem()
	print >> sys.stderr, 'load time:', time.time() - t0

	t0 = time.time()
	scanner = IncludeScanner(fs, dirs)
	print >> sys.stderr, 'load time:', time.time() - t0

	for f in files:
		print 'scanning:', f
		deps = scanner.scan_deps(f)

	t0 = time.time()
	scanner.dump()
	print >> sys.stderr, 'dump time:', time.time() - t0
	
	t0 = time.time()
	fs.dump()
	print >> sys.stderr, 'dump time:', time.time() - t0
	
	scanner.display()
