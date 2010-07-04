#! /bin/sh
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2010-2010 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

# iphonedevonlinux/toolchain.sh forgets to copy some files from the iphone sdk to the sysroot tree,
# so this script adds the missing files afterwards.

set -x &&

cd $(dirname $0) &&

cd iphonedevonlinux &&

sdk=$(echo sdks/iPhoneOS*.sdk) &&
sys=toolchain/sys &&

for lib in System objc stdc++.6
do
	path=usr/lib &&
	ln -s \
		../../../../$sdk/$path/lib$lib.dylib \
		$sys/$path/ || :
done &&

for lib in Foundation CoreFoundation CoreGraphics UIKit OpenGLES QuartzCore
do
	path=System/Library/Frameworks/$lib.framework &&
	ln -s \
		../../../../../../$sdk/$path/$lib \
		$sys/$path/ || :
done

