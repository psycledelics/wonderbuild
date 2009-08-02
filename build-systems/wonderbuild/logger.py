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
			def m(v, scale):
				_map_b.append(v)
				v *= scale
				_map_g.append(v)
				_map_r.append(v * scale)
			if colors == 88:
				scale = 4
				for v in xrange(0x8b): m(0, scale)
				for v in xrange(0x8b, 0xcd): m(1, scale)
				for v in xrange(0xcd, 0xff): m(2, scale)
				m(3, scale)
			
				c1 = 0x2e
				for x in xrange(0, c1): _map_grey.append('16')
				i = 80
				for c2 in (0x5c, 0x73, 0x8b, 0xa2, 0xb9, 0xd0, 0xe7):
					for v in xrange(c1, c2): _map_grey.append(str(i))
					i += 1; c1 = c2
				for x in xrange(c2, 256): _map_grey.append('79')
				# there are also 2 grey colors in the 4x4x4 color cube, not counting black and white
				#for x in xrange(0x?? - ?, 0x?? + ?): _map_grey[x] = '?'
				#for x in xrange(0x?? - ?, 0x?? + ?): _map_grey[x] = '?'
			elif colors == 256:
				scale = 6
				for v in xrange(0x5f): m(0, scale);
				for i in xrange(1, 5):
					for x in xrange(40): m(i, scale)
				m(5, scale)

				c1 = 8
				for x in xrange(0, c1): _map_grey.append('16')
				i = 231
				for c2 in xrange(c1, 256, 10):
					for v in xrange(c1, c2): _map_grey.append(str(i))
					i += 1; c1 = c2
				for x in xrange(c2, 256): _map_grey.append('231')
				# there are also 4 grey colors in the 6x6x6 color cube, not counting black and white
				for x in xrange(0x5f, 0x5f + 5): _map_grey[x] = '59'
				for x in xrange(0x87, 0x87 + 5): _map_grey[x] = '102'
				for x in xrange(0xaf, 0xaf + 5): _map_grey[x] = '145'
				for x in xrange(0xd7, 0xd7 + 5): _map_grey[x] = '188'
		_fill_maps()
		def _merge_rgb(rgb):
			if rgb[0] == rgb[1] and rgb[1] == rgb[2]: return _map_grey[rgb[0]]
			else: return str(16 + _map_r[rgb[0]] + _map_g[rgb[1]] + _map_b[rgb[2]])
		def color_bg_fg_rgb(bg, fg):
			return '48;5;' + _merge_rgb(bg) + ';38;5;' + _merge_rgb(fg)
	else:
		def color_bg_fg_rgb(bg, fg): return ''

if __name__ == '__main__':
	# 8 colors (3-bit: bgr with 1 on bit per channel)
	for i in xrange(8):
		bg = '4' + str(i)
		fg = 7 - i
		c = bg + ';3' + str(fg)
		out.write(colored(c, '%02d/%02d' % (fg, i)))
		for x in ('1', '2', '5', '6'): out.write(colored(c + ';' + x, ' ' + x + ' '))
		out.write(colored(bg + ';37', '07'))
		out.write(colored(bg + ';30', '00'))
		out.write(' ')
	out.write('\n')
	# 16 colors (4-bit: bgr with 1 on bit per channel, and 1 bit for highlight)
	for i in xrange(16):
		bg = '48;5;' + str(i)
		fg = (i + 8) % 16
		c = bg + ';38;5;' + str(fg)
		out.write(colored(c, '%02d/%02d' % (fg, i)))
		for x in ('1', '2', '5', '6'): out.write(colored(c + ';' + x, ' ' + x + ' '))
		out.write(colored(bg + ';38;5;15', '15'))
		out.write(colored(bg + ';38;5;0', '00'))
		out.write(' ')
		if i == 7: out.write('\n')
	out.write('\n\n')
	if colors == 256:
		# 6x6x6 color cube (rgb with 6 values per channel)
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
		# 24-values grey ramp, without black and white
		for l in xrange(3):
			i = 232
			for c in [0x8] + [0x12 + (0x12 - 0x8) * x for x in xrange(23)]:
				v = c < 128 and 255 or 0
				out.write(colored(color_bg_fg_rgb((c, c, c), (v, v, v)), l == 0 and '%02x:' % c or '   '))
				out.write(colored('48;5;' + str(i) + ';38;5;' + (v != 0 and '231' or '0'), l == 0 and '%03d' % i or '   ') + ' ')
				i += 1
			out.write('\n')
		for l in xrange(2):
			for c in [0x8] + [0x12 + (0x12 - 0x8) * x for x in xrange(23)]:
				for x in (0, 1, 3, 4, 6, 8, 9): out.write(colored(color_bg_fg_rgb((c + x, c + x, c + x), (0, 0, 0)), ' '))
			out.write('\n')
		# palette querying (xterm only)
		# default 256-color palette:
		# - color cube starts at index 16 with intensity 95 (0x5f) and increments by 40 (0x87 - 0x5f)
		# - grey ramp starts at index 232 with intensity 8 (0x8) and increments by 10 (0x12 - 0x8)
		# xterm and mrxvt support changing the palette: http://invisible-island.net/xterm/ctlseqs/ctlseqs.html
		# gnome-terminal has a fixed palette.
		if False:
			out.write('\33]4')
			for i in xrange(256): out.write(';' + str(i) + ';?')
			out.write('\33\\')
