#!/bin/bash

function main
{
	cd $(dirname $0)/../../doc/ &&
	tar --create --bzip2 --file /tmp/$(logname).doxygen.tar.bz2 doxygen.microsoft &&
	# maps local user account names to sourceforge user account names
	case "$(logname)@$(hostname)" in
		bohan@*) local user=johan-boule ;;
		x@KABOOM) local user=alkenstein ;;
		*) local user=$(logname) ;;
	esac &&
	scp /tmp/$(logname).doxygen.tar.bz2 $user@shell.sourceforge.net:/tmp/$(logname).doxygen.tar.bz2 &&
	ssh $user@shell.sourceforge.net <<-eof
		set -vx &&
		cd /home/groups/p/ps/psycle/htdocs &&
		rm --force doxygen.microsoft --recursive &&
		tar --extract --bzip2 --file /tmp/$(logname).doxygen.tar.bz2 &&
		chmod ug+rw,o+r-w doxygen.microsoft --recursive &&
		./update-timestamps
	eof
}

set -vx &&
main
