#!/bin/bash

###########################################################################
#
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2004-2007 psycledelics http://psycle.pastnotecut.org : johan boule
# copyright 2001,2002 Earnie Boyd  <earnie@users.sf.net>
#
# Environment initialization script for interactive login shells
# note: this should be explicitely executed by /etc/profile for bash shells when both the login and interactive options are on.
#
###########################################################################

# if the shell is interactive:
if test -n "$PS1"
then

	##############
	# window size

	# check the window size on both WINCH signal and after each command,
	# and, if necessary, update the values of LINES and COLUMNS.
	shopt -s checkwinsize
	# dunno why but just after startup of msys's rxvt, LINES and COLUMNS are not set according to the geometry settings passed to rxvt's command line.
	# Sending a SIGWINCH signal to bash didn't help either,
	# but clsb works and triggers bash.
	clsb


	#####################
	# message of the day

	if test -n "$PACKAGENERIC__DEV_PACK__VERSION"
	then
		if test -f /etc/motd
		then
			cat /etc/motd
		fi
		echo -e "\033[1;36mpsycledelics packageneric dev-pack - version $PACKAGENERIC__DEV_PACK__VERSION, $OSTYPE\033[0m"
	fi


	###############
	# mount points

	echo -e "\033[36mtype 'mount' to list the mount points of the file system tree.\033[0m"
	if test "$OSTYPE" = msys
	then
		echo -e "\033[36mtype 'cmd //c cd' to view microsoft's syntax of the current dir.\033[0m"
	fi


	######################
	# initial current dir

	if test -d ~/working-dir
	then
		cd ~/working-dir
	fi


	############
	# read line

	if test ! -f ~/.inputrc
	then
		export INPUTRC=/etc/readline.inputrc
	fi


	##############################################
	# Don't wait for job termination notification
	#set -o notify


	#######################
	# Don't use ^D to exit
	#set -o ignoreeof

	
	#############
	# completion

	# enable bash completion in interactive shells
	if test -f /etc/bash_completion
	then
		source /etc/bash_completion 2>/dev/null
	fi


	##########
	# history

	# don't put duplicate lines in the history.
	export HISTCONTROL=ignoredups
	export HISTSIZE=10000
	unset HISTFILESIZE


	#####################
	# ls and tree colors	

	# enable color support of ls and tree
	#eval `dircolors --bourne-shell`


	##########
	# aliases

	alias l='command ls --color=auto --almost-all --format=vertical --indicator-style=classify --ignore-backups'
	alias ls='l --size --human-readable'
	alias ll='lh'
	alias lb='l --format=long'
	alias lh='lb --human-readable'
	alias la='lb --all'

	#alias dir='tree -pugilasDAFL 1'

	#alias tree='tree -AF -I {arch}'
	
	alias less='less --raw-control-chars'

	#alias grep='grep --color=auto --with-filename --line-number'

	alias diff='colordiff --no-banner'

	alias rm='rm --interactive'
	alias cp='cp --interactive'
	alias mv='mv --interactive'
	alias ln='ln --interactive'

	alias clear=clsb

	########
	# pompt

	# We are in interactive mode, so, set a fancy prompt
	case $TERM in
	xterm*|rxvt*)
		ps_color="\e[1m"
		ps_color_user="${ps_color}"
		ps_color_host="${ps_color}"
		ps_color_dir="\e[0m \e[1;34m"
		# set the window title.
		PROMPT_COMMAND='echo -ne "\e]0;$LOGNAME@$HOSTNAME:$PWD $0\a"'
		;;
	linux)
		ps_color="\e[1m"
		ps_color_user="${ps_color}"
		ps_color_host="${ps_color}"
		ps_color_dir="\e[0m \e[1;34m"
		;;
	dumb)
		ps_color=""
		ps_color_user=""
		ps_color_host=""
		ps_color_dir=" "
		;;
	*)
		ps_color="\e[1m"
		ps_color_user="${ps_color}"
		ps_color_host="${ps_color}"
		ps_color_dir="\e[0m \e[1;34m"
		;;
	esac
	ps="\s \W"
	if test "$(id --user)" -eq 0 # no group on msys -o "$(id --group)" -eq 544
	then
		ps_color_user_id_0="\e[1;31m"
		user="${ps_color_user_id_0}${USER}\e[0m${ps_color_user}"
		if [ "$(echo $SU_STACK | sed 's/.*->//')" != "$user" ]; then
			export SU_STACK="${SU_STACK:+${SU_STACK}->}${user}"
		fi
		#ps="\s${ps_color_id_0}%\e[0m "
		#ps="${ps}%"
		ps="${ps}#"
		unset user ps_color_user_id_0
	else
		if [ "$(echo $SU_STACK | sed 's/.*->//')" != $USER ]; then
			export SU_STACK="${SU_STACK:+${SU_STACK}->}${USER}"
		fi
		#ps="\s\e[1m#\e[0m "
		#ps="\e[1m${ps}#\e[0m"
		ps="${ps}#"
	fi
	ps="$ps "
	for i in $(id --name --groups)
	do
		if test ! "$i" = "$USER"
		then
			groups="${groups:+$groups+}$i"
		fi
	done
	if test $groups
	then
		groups="($groups)"
	fi
	#PS1="${ps_color_user}${SU_STACK}${groups}${ps_color_host}@\H:\l \j \A${ps_color_dir}\w"
	#PS1="${ps_color_user}${SU_STACK}${groups}${ps_color_host}@\H:\l \j \t${ps_color_dir}\w"
	# no group on msys
	PS1="${ps_color_user}${SU_STACK}${ps_color_host}@\H:\l \j \t${ps_color_dir}\w" &&
	PS1="${PS1}\$(test \$? -eq 0 || echo -e \" \033[1;31m\007(command failed with return code \$?)\")" &&	
	
	PS1="${PS1}\e[0m\n$ps" &&
	unset ps ps_color ps_color_user ps_color_host ps_color_dir groups


	#######
	# bell

	# low frequency
	#setterm -bfreq 21 -blength 25

	# high frequency, strident => short duration
	#setterm -bfreq 10000 -blength 5

	# average
	#setterm -bfreq 200 -blength 25
fi
