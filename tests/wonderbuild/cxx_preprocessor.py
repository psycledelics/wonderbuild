#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2008-2008 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

import os

class CppDumbIncludeScanner:
	'C/C++ scanner for #include statements, and nothing else (dumb)'
	
	def __init__(self, paths = None):
		if paths is not None: self._paths = paths
		else: self._paths = []
	
	def add_path(self, path): self._paths.append(path)
	
	def scan(self, file_name):
		f = file(file_name)
		try: s = f.read()
		finally: f.close()
		
		normal = 0
		single_line_comment = 1
		multi_line_comment = 2
		single_quoted_string = 3
		double_quoted_string = 4
		token = 5
		token_quote = 6
		other = 7
		
		prev_state = state = normal; prev = '\0'
		
		relative_includes = []
		absolute_includes = []
		for c in s:
			if c == '\r': continue
			if c == '\t': c = ' '

			new_state = state

			if state == single_line_comment:
				if c == '\n' and prev != '\\':
					if prev_state == other: new_state = normal
					else: new_state = prev_state
			elif state == multi_line_comment:
				if prev == '*' and c == '/': new_state = prev_state
			elif state == single_quoted_string:
				if c == "'" and prev != '\\': new_state = prev_state
			elif state == double_quoted_string:
				if c == '"' and prev != '\\': new_state = prev_state
			elif state == normal or state == other:
				if prev == '/' and c == '/': new_state = single_line_comment
				elif prev == '/' and c == '*': new_state = multi_line_comment
				elif c == "'": new_state = single_quoted_string
				elif c == '"': new_state = double_quoted_string
				elif state == normal:
					if c == '#' and prev != '/':
						new_state = token
						token_string = c
						token_quote = False
					elif c != ' ' and c != '\n' and c != '/': new_state = other
				elif state == other:
					if c == '\n' and prev != '\\': new_state = normal
			elif state == token:
				if c == '\\':
					if token_quote: token_string += c
				elif prev == '/' and c == '/': new_state = single_line_comment
				elif prev == '/' and c == '*': new_state = multi_line_comment
				elif c == '\n':
					if prev != '\\':
						search = '#include '
						if token_string.startswith(search):
							l = len(search)
							kind = token_string[l]
							if kind == '"': relative_includes.append(token_string[l + 1 : token_string.rfind('"')])
							elif kind == '<': absolute_includes.append(token_string[l + 1 : token_string.rfind('>')])
						new_state = normal
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

			if new_state != state:
				prev_state = state
				state = new_state
			prev = c;
		return relative_includes, absolute_includes

if __name__ == '__main__':
	import sys
	
	scanner = CppDumbIncludeScanner()
	for f in sys.argv[1:]:
		includes = scanner.scan(f)
		print f, includes
