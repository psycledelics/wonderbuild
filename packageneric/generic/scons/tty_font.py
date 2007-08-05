# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006-2007 johan boule <bohan@jabber.org>
# copyright 2006-2007 psycledelics http://psycle.pastnotecut.org

def tty_font(font = '0', text = None):
	if not ansi_term():
		if text: return text
		else: return ''
	result = '\033[' + font + 'm'
	if text: result += text + tty_font()
	return result

_ansi_term = None

def ansi_term():
	global _ansi_term
	if not _ansi_term:
		# We check for both a tty and the TERM env var to exclude microsoft's non-ansi terminal.
		# On cygwin, the terminal may be a X Window terminal, or the native port of rxvt (also found with msys),
		# but it may also be microsoft's terminal.
		# It the latter case, cygwin emulates an ansi terminal by translating control sequences into calls to microsoft's api,
		# and the TERM env var is set to 'cygwin'. This means you get colors in this case too.
		import sys, os
		_ansi_term = sys.stdout.isatty() and 'TERM' in os.environ
	return _ansi_term
