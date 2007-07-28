#! /bin/bash

set -u &&

function main
{
	cd $(dirname $0)/../../doc/ &&
	tar --create --bzip2 --file /tmp/$(logname).doxygen.tar.bz2 doxygen.mfc &&
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
		rm --force doxygen.mfc --recursive &&
		umask ug=rwx,o=rx &&
		tar --extract --bzip2 --touch --file /tmp/$(logname).doxygen.tar.bz2 &&
		chmod ug=rwsx,o=rx doxygen.mfc &&
		find doxygen.mfc -type d -exec chmod ug=rwsx,o=rx {} \; &&
		find doxygen.mfc -type f -exec chmod ug+rw,o+r-w {} \; &&
		./update-timestamps
	eof
}

set -vx &&
main "$@"
