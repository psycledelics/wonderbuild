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
		umask ug=rwx,o=rx &&
		tar --extract --bzip2 --file /tmp/$(logname).doxygen.tar.bz2 &&
		chmod ug=rwsx,o=rx doxygen.microsoft &&
		find doxygen.microsoft -type d -exec chmod ug=rwsx,o=rx {} \; &&
		find doxygen.microsoft -type f -exec chmod ug+rw,o+r-w {} \; &&
		./update-timestamps
	eof
}

set -vx &&
main
