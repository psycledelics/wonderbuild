#! /bin/sh

# This script converts msvc 2008 projects and solutions to msvc-2005

cd $(dirname $0)/../.. &&

# converts the projects
for f in $(find . -name \*.vcproj)
do
	sed \
		-e s/msvc-2008/msvc-2005/g \
		-e 's/Version=\"9\.00\"/Version=\"8\.00\"/' \
		< $f > $(echo $f | sed s/msvc-2008/msvc-2005/) ||
	break
done &&

# converts the solutions
for f in  $(find . -name \*.sln)
do
	sed \
		-e s/msvc-2008/msvc-2005/g \
		-e 's/^Microsoft Visual Studio Solution File, Format Version 10.00$/Microsoft Visual Studio Solution File, Format Version 9.00/' \
		-e 's/^# Visual Studio 2008$/# Visual Studio 2008/' \
		< $f > $(echo $f | sed s/msvc-2008/msvc-2005/) ||
	break
done
