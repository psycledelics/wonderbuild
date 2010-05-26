#! /bin/sh

set -x &&

cd $(dirname $0) &&

root=$(pwd)/iphonedevonlinux/toolchain &&
toolset_root=$root/pre/bin &&
prefix=$root/sys/usr &&

cd boost/boost_* &&

cat > tools/build/v2/user-config.jam <<eof
using gcc
	: arm
	: $toolset_root/arm-apple-darwin9-g++
	: <archiver>$toolset_root/arm-apple-darwin9-ar
	;
eof

# http://www.boost.org/doc/libs/1_43_0/doc/html/bbv2/overview.html#bbv2.overview.invocation

# workaround for 7z's stupidness
chmod +x bootstrap.sh tools/jam/src/build.sh &&

# using bjam --prefix directly gives errors o_O`
sh bootstrap.sh --prefix=$prefix &&

# --help (also see Jamroot!)
# --build-dir=bin.v2 (this is the default)
# --stage-dir=./stage (this is the default)
# --prefix=$prefix
# --show-libraries
# --with-<library>
# --without-<library>
# link=shared,static
# runtime-link=shared,static

./bjam \
	--without-python \
	--toolset-root=$toolset_root \
	--layout=system \
	--toolset=gcc-arm \
	--target-os=darwin \
	define=_LITTLE_ENDIAN \
	threading=multi \
	variant=release \
	"$@"

