# switches versions of .vcproj and .sln files
# License: GPL, http://fsf.org/licenses/gpl.html
# Copyright (C) 2005 Leonard "paniq" Ritter.

import sys
import os
import os.path
import re

if not "make\\msvc" in os.getcwd():
	print "Wrong current directory."
	sys.exit()
	
c = re.compile("^(\\s*Version\=\\\")([^\\\"]*)(\\\"\\s*)$")
csln = re.compile("^(Microsoft Visual Studio Solution File\\, Format Version )(\\S*)(\\s*)$")

mapSlnVersion = {"7.10":"8.00","8.00":"9.00"}

def switch_version(newVersion):
	for root, folders, files in os.walk("."):
		for name in files:
			base,ext = os.path.splitext(name)
			if ext in [".vcproj",".sln"]:
				fullpath = os.path.join(root,name)
				print "Changing %s..." % fullpath
				f = open(fullpath,"r")
				inlines = f.readlines()
				f.close()
				outlines = []
				for l in inlines:
					r = c.match(l)					
					if r:						
						nl = r.group(1) + newVersion + r.group(3)
						print "Changing"
						print repr(l)
						print "To"
						print repr(nl)
						l = nl
					else:
						r = csln.match(l)
						if r:
							nl = r.group(1) + mapSlnVersion[newVersion] + r.group(3)
							print "Changing"
							print repr(l)
							print "To"
							print repr(nl)
							l = nl
					outlines.append(l)
				f = open(fullpath,"w")
				f.writelines(outlines)
				f.close()

if __name__ == "__main__":
	if len(sys.argv) == 2:
		switch_version(sys.argv[1])
	else:
		print "usage: "
		print "    switch_version.py 7.10"
		print "or"
		print "    switch_version.py 8.00"
