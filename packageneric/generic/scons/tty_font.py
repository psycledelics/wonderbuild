# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2006 johan boule <bohan@jabber.org>
# copyright 2006 psycledelics http://psycle.pastnotecut.org

import sys

def tty_font(font = '0', text = None):
	if not sys.stdout.isatty():
		if text: return text
		else: return ''
	result = '\033[' + font + 'm'
	if text: result += text + tty_font()
	return result
