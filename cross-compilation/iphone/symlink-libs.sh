#! /bin/sh

set -x &&

cd $(dirname $0) &&

for lib in System objc
do
	ln -s \
		../../../../sdks/iPhoneOS*.sdk/usr/lib/lib$lib.dylib \
		iphonedevonlinux/toolchain/sys/usr/lib/ || :
done &&

for lib in Foundation CoreFoundation CoreGraphics UIKit
do
	ln -s \
		../../../../../../sdks/iPhoneOS*.sdk/System/Library/Frameworks/$lib.framework/$lib \
		iphonedevonlinux/toolchain/sys/System/Library/Frameworks/$lib.framework/ || :
done
