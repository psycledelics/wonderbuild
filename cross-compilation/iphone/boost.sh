#! /bin/sh

cd $(dirname $0) &&

toolset_root=$(pwd)/iphonedevonlinux/toolchain/pre/bin

cd boost/boost_* &&

cat > tools/build/v2/user-config.jam <<eof
using gcc
	: arm
	: $toolset_root/arm-apple-darwin9-g++
	: <archiver>$toolset_root/arm-apple-darwin9-ar
	;
eof

bjam \
	--toolset-root=$toolset_root \
	toolset=gcc-arm \
	target-os=iphone \
	threading=multi \
	release

