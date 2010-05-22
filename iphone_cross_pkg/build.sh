#! /bin/sh

####################################################
# http://code.google.com/p/iphone-dev/wiki/Building
####################################################

set -x &&

cd $(dirname $0) &&

XPREFIX=/usr/local &&
#USE_XPREFIX="--prefix=$XPREFIX" &&

# llvm
if ! test -d llvm-svn
then
	svn checkout -r42498 http://llvm.org/svn/llvm-project/llvm/trunk llvm-svn
fi &&
cd llvm-svn &&
CC=gcc-4.1 CXX=g++-4.1 ./configure $USE_XPREFIX --enable-optimized &&
make ENABLE_OPTIMIZED=1 &&
make install &&
export LLVMOBJDIR=$(pwd) &&
cd .. &&

# xcode dmg
export SDK=$(pwd)/sdk-dmg/SDKs/MacOSX10.4u.sdk &&
if ! test -d $SDK
then
	cd sdk-dmg &&
	od -t x1 *.dmg | grep '^[0-7]*000 1f 8b' > offsets.txt &&
	dd if=*.dmg skip=$(awk '{ print $1 }' offsets.txt | while read x; do dd if=*.dmg skip=$((0$x / 512)) count=1 | gunzip | cpio -t | grep -q MacOSX10.4u.sdk && echo $((0$x / 512)); done 2>/dev/null) | gunzip | pax -r
	cd ..
fi &&
test -d $SDK &&

# iphone root filesystem
test -d heavenly &&
export HEAVENLY=$(pwd)/heavenly &&

# iphone-dev
if ! test -d iphone-dev
then
	svn checkout http://iphone-dev.googlecode.com/svn/trunk iphone-dev &&
	cd iphone-dev &&
	cd include &&
	svn switch http://iphone-dev.googlecode.com/svn/branches/include-1.2-sdk &&
	cd .. &&
	cd odcctools &&
	svn switch http://iphone-dev.googlecode.com/svn/branches/odcctools-9.2-ld &&
	cd ../..
fi &&
cd iphone-dev &&

# ???
if ! test -d $XPREFIX/arm-apple-darwin
then
	mkdir $XPREFIX/arm-apple-darwin
fi &&

# iphone-dev odcctools
mkdir -p build/odcctools &&
cd build/odcctools &&
../../odcctools/configure $USE_XPREFIX --target=arm-apple-darwin --disable-ld64
make &&
make install &&
cd ../.. &&

# iphone headers installation
cd include &&
./configure $USE_XPREFIX --with-macosx-sdk=$SDK &&
bash install-headers.sh &&
cd .. &&

# iphone-dev csu
mkdir -p build/csu &&
cd build/csu &&
../../csu/configure $USE_XPREFIX --host=arm-apple-darwin
make install &&
cd ../.. &&

# iphone-dev issue #145
if ! test -f lib1funcs.asm.diff
then
	wget 'http://iphone-dev.googlecode.com/issues/attachment?aid=-4811806783580725987&name=lib1funcs.asm.diff&token=9191c5c2ddd1a1cad1f8ddec6b288cb2' \
		--output-document=lib1funcs.asm.diff &&
	cd llvm-gcc-4.0-iphone/gcc/config/arm &&
	patch -p0 < ../../../../lib1funcs.asm.diff &&
	cd ../../../..
fi &&

# iphone-dev llvm-gcc
mkdir -p build/llvm-gcc-4.0-iphone &&
cd build/llvm-gcc-4.0-iphone &&
../../llvm-gcc-4.0-iphone/configure $USE_XPREFIX --enable-llvm=$LLVMOBJDIR --with-heavenly=$HEAVENLY \
	--enable-languages=c,c++,objc,obj-c++ --target=arm-apple-darwin --enable-sjlj-exceptions --enable-wchar_t=no \
	--with-as=$XPREFIX/bin/arm-apple-darwin-as \
	--with-ld=$XPREFIX/bin/arm-apple-darwin-ld &&
#ln -sf gcc/darwin/4.0/stdint.h $XPREFIX/arm-apple-darwin/include/ &&
####ln -s libSystem.B.dylib libSystem.dylib
####ln -s libSystem.dylib libc.dylib
make LLVM_VERSION_INFO=2.0-svn-iphone-dev-0.3-svn && #NM=$XPREFIX/bin/arm-apple-darwin-nm &&
make install &&
cd ../.. &&

cd .. &&
:

