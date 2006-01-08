#! /bin/bash
# cygwin's sh not posix
#! /bin/sh

set -u &&

main()
{
	local from=$1 && shift &&
	local to=$1 &&
	dirname $0 && # first test there's no space in the path
	cd $(dirname $0) &&
	(
		cd $from &&
		find . -name \*.sln -or -name \*.vcproj
	) |
	(
		local file &&
		while read file
		do
			echo $file &&
			mkdir -p $to/$(dirname "$file") &&
			cp $from/"$file" $to/"$file" ||
			return
		done
	)
} &&

main "$@"
