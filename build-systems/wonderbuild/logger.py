#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2008-2009 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

import sys, os

known_options = set(['silent', 'verbose'])

def generate_option_help(help):
	help['silent'] = (None, 'suppress printing of informative messages (errors and verbose messages are still printed)')
	help['verbose'] = ('[zone,...]', 'wonderbuild debugging trace zones, comma-separated list, or no list for all zones. (example values: exec,cfg,task,sched,fs,project,cpp,...)')

silent = True
is_debug = False
def debug(s): pass

def use_options(options):
	global silent
	silent = 'silent' in options

	if __debug__:
		global is_debug
		is_debug = 'verbose' in options

		if is_debug:
			zones = options['verbose'].split(',')
			global debug
			if len(zones) != 0:
				def debug(s):
					for z in zones:
						if s.startswith(z):
							print >> sys.stderr, colored('35', 'wonderbuild: dbg:') + ' ' + s
							break
			else:
				def debug(s): print >> sys.stderr, colored('35', 'wonderbuild: dbg:') + ' ' + s

out = sys.stdout

try: import curses
except ImportError: _curses = False
else:
	try: curses.setupterm()
	except: _curses = False
	else: _curses = True

def _get_cols():
	if _curses: return curses.tigetnum('cols')
	
	try: import struct, fcntl, termios
	except ImportError: pass
	else:
		if out.isatty():
			try: lines, cols = struct.unpack(
						'HHHH',
						fcntl.ioctl(
							out.fileno(),
							termios.TIOCGWINSZ,
							struct.pack('HHHH', 0, 0, 0, 0)
						)
				)[:2]
			except IOError: pass
			else: return cols

	e = os.environ.get('COLUMNS', None)
	if e is not None: return int(e)

	return 80
cols = _get_cols()

out_is_dumb = os.environ.get('TERM', 'dumb') in ('dumb', 'emacs') or not out.isatty()
if out_is_dumb:
	def colored(color, s): return s
	colors = 0
	def color_bg_fg_rgb(bg, fg): return ''
else:
	def colored(color, s): return '\33[' + color + 'm' + s + '\33[0m'
	if _curses:
		colors = curses.tigetnum('colors')
		if \
			colors == 8 and \
			os.environ.get('TERM', None) == 'xterm' and \
			os.environ.get('COLORTERM', None) == 'gnome-terminal': colors = 256
	else: colors = 8
	if colors == 8:
		def _merge_rgb(rgb):
			a = (rgb[0] + rgb[1] + rgb[2]) // 3
			return str(
				(rgb[0] >= a and 1 or 0) + \
				(rgb[1] >= a and 2 or 0) + \
				(rgb[2] >= a and 4 or 0)
			)
		def color_bg_fg_rgb(bg, fg):
			return '4' + _merge_rgb(bg) + ';3' + _merge_rgb(fg)
	elif colors == 16:
		def _merge_rgb(rgb):
			a = (rgb[0] + rgb[1] + rgb[2]) // 3
			c = \
				(rgb[0] >= a and 1 or 0) + \
				(rgb[1] >= a and 2 or 0) + \
				(rgb[2] >= a and 4 or 0)
			if max(rgb) >= 170: c += 8
			# TODO bright black is never used
			return str(c)
		def color_bg_fg_rgb(bg, fg):
			return '48;5;' + _merge_rgb(bg) + ';38;5;' + _merge_rgb(fg)
	elif colors == 88 or colors == 256:
		_map_r = []
		_map_g = []
		_map_b = []
		_map_grey = []
		def _fill_maps():
			# note: xterm and mrxvt support changing the palette: http://invisible-island.net/xterm/ctlseqs/ctlseqs.html
			#       gnome-terminal has a fixed palette.
			scale = {88: 4, 256: 6}[colors]
			scale_grey = {88: 8, 256: 24}[colors]
			offset_grey = {88: 80, 256: 232}[colors]
			for v in xrange(256):
				_map_grey.append(str(offset_grey + v * scale_grey // 256))
				# TODO there are also grey colors in the color cube (4 in 256-color mode, not counting black and white)
				v = v * scale // 256
				_map_b.append(v)
				v *= scale
				_map_g.append(v)
				_map_r.append(v * scale)
			_map_grey[0] = str(16)
			_map_grey[255] = str(offset_grey - 1)
		_fill_maps()
		def _merge_rgb(rgb):
			if rgb[0] == rgb[1] and rgb[1] == rgb[2]: return _map_grey[rgb[0]]
			else: return str(16 + _map_r[rgb[0]] + _map_g[rgb[1]] + _map_b[rgb[2]])
		def color_bg_fg_rgb(bg, fg):
			return '48;5;' + _merge_rgb(bg) + ';38;5;' + _merge_rgb(fg)
	else:
		def color_bg_fg_rgb(bg, fg): return ''

if __name__ == '__main__':
	s = [0] + [0x5f + (0x87 - 0x5f) * x for x in xrange(5)]
	i = 16
	for r in s:
		for g in s:
			for b in s:
				v = (r + g + b) // 3 < 128 and 255 or 0
				out.write(colored(color_bg_fg_rgb((r, g, b), (v, v, v)), '%02x/%02x/%02x        ' % (r, g, b)))
				out.write(colored('48;5;' + str(i) + ';38;5;' + (v != 0 and '231' or '0'), '         %03d' % i) + ' ')
				i += 1
			out.write('\n')
		out.write('\n')
	for l in xrange(3):
		i = 232
		for c in [0x8] + [0x12 + (0x12 - 0x8) * x for x in xrange(23)]:
			v = c < 128 and 255 or 0
			out.write(colored(color_bg_fg_rgb((c, c, c), (v, v, v)), l == 1 and '%02x ' % c or '   '))
			out.write(colored('48;5;' + str(i), l == 1 and '%03d' % i or '   ') + ' ')
			i += 1
		out.write('\n')
	if False:
		for i in xrange(255):
			out.write('\33]4;' + str(i) + ';?\33\\')
