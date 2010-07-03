#! /bin/sh

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

for lib in Foundation CoreFoundation CoreGraphics UIKit OpenGLES
do
	path=System/Library/Frameworks/$lib.framework &&
	ln -s \
		../../../../../../$sdk/$path/$lib \
		$sys/$path/ || :
done

