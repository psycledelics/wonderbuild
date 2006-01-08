#! /bin/bash
# cygwin's sh not posix
# !/bin/sh

set -u &&

main()
{
	dirname $0 && # first test there's no space in the path
	cd $(dirname $0) &&
	../msvc_copy_projects.sh msvc_8.0 msvc_7.1 &&
	../msvc_switch_version.py 7.10
} &&

main "$@"
