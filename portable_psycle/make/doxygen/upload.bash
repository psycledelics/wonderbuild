#!/bin/bash

function main
{
	cd $(dirname $0)/../../doc/ &&
	tar cjf /tmp/doxygen.tar.bz2 doxygen &&
	# maps local user account names to sourceforge user account names
	case "$(logname)@$(hostname)" in
		bohan@*) local user=johan-boule ;;
		x@KABOOM) local user=alkenstein ;;
		*) local user=$(logname) ;;
	esac
	scp /tmp/doxygen.tar.bz2 $user@shell.sourceforge.net:/tmp/$(basename $0).$user.doxygen.tar.bz2 &&
	ssh $user@shell.sourceforge.net \
		"\
			set -vx && \
			cd /home/groups/p/ps/psycle/htdocs/ && \
			rm --force doxygen --recursive && \
			tar xjf /tmp/$(basename $0).$user.doxygen.tar.bz2 && \
			chmod ug+rw,o+r-w doxygen --recursive
			cd .. && \
			source htdocs.update.bash \
		"
}

set -vx &&
main
