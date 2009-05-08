#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2009-2009 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

def format(list, max_width):
	min_col_width = 3
	list_len = len(list)
	max_cols = min(max(1, max_width / min_col_width), list_len)

	class ColInfo(object): pass
	col_infos = []
	for i in xrange(max_cols):
		col_info = ColInfo()
		col_infos.append(col_info)
		col_info.valid_len = True;
		col_info.line_len = (i + 1) * min_col_width
		col_info.col_arr = []
		for j in xrange(i + 1): col_info.col_arr.append(min_col_width)

	# compute the maximum number of possible columns
	for f in xrange(list_len):
		e = list[f]
		name_len = len(e)
		for i in xrange(max_cols):
			col_info = col_infos[i]
			if col_info.valid_len:
				idx = f / ((list_len + i) / (i + 1))
				real_len = name_len + (idx != i and 2 or 0)
				if col_info.col_arr[idx] < real_len:
					col_info.line_len += real_len - col_info.col_arr[idx]
					col_info.col_arr[idx] = real_len
					col_info.valid_len = col_info.line_len < max_width

	# find maximum allowed columns
	cols = max_cols
	while 1 < cols:
		if col_infos[cols -1].valid_len: break
		cols -= 1
	#print cols

	# calculate the number of rows that will be in each column except possibly for a short column on the right
	rows = list_len / cols + (list_len % cols != 0)
	#print rows

	col_info = col_infos[cols - 1]
	result = []
	for row in xrange(rows):
		col = 0
		f = row
		line = ''
		while True: # print the next row
			e = list[f]
			name_len = len(e)
			max_name_len = col_info.col_arr[col]
			col += 1
			line += e.ljust(max_name_len)
			f += rows
			if f >= list_len: break
		result.append(line)
	return result
