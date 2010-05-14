#! /bin/sh

####################################################
# http://code.google.com/p/iphone-dev/wiki/Building
####################################################

set -x &&

cd $(dirname $0) &&

export PREFIX=$(pwd)/install &&

# llvm
if ! test -d llvm-svn
then
	svn checkout -r42498 http://llvm.org/svn/llvm-project/llvm/trunk llvm-svn
fi &&
cd llvm-svn &&
./configure --prefix=$PREFIX --enable-optimized &&
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
	svn checkout http://iphone-dev.googlecode.com/svn/trunk iphone-dev
fi &&
cd iphone-dev &&

# ???
mkdir $PREFIX/arm-apple-darwin &&

# iphone-dev odcctools
mkdir -p build/odcctools &&
cd build/odcctools &&
CFLAGS='-g -O2 -m32' LDFLAGS=-m32 ../../odcctools/configure --prefix=$PREFIX --target=arm-apple-darwin --disable-ld64
make &&
make install &&
cd ../.. &&

# iphone headers installation
cd include &&
./configure --prefix=$PREFIX --with-macosx-sdk=$SDK &&
bash install-headers.sh &&
cd .. &&

# iphone-dev csu
mkdir -p build/csu &&
cd build/csu &&
../../csu/configure --prefix=$PREFIX --host=arm-apple-darwin
make install &&
cd ../.. &&

# iphone-dec llvm-gcc
mkdir -p build/llvm-gcc-4.0-iphone &&
cd build/llvm-gcc-4.0-iphone &&
../../llvm-gcc-4.0-iphone/configure --prefix=$PREFIX --enable-llvm=$LLVMOBJDIR --with-heavenly=$HEAVENLY \
	--enable-languages=c,c++,objc,obj-c++ --target=arm-apple-darwin --enable-sjlj-exceptions --enable-wchar_t=no \
	--with-as=$PREFIX/bin/arm-apple-darwin-as \
	--with-ld=$PREFIX/bin/arm-apple-darwin-ld &&
make LLVM_VERSION_INFO=2.0-svn-iphone-dev-0.3-svn &&
make install &&
cd ../.. &&

cd .. &&
:

