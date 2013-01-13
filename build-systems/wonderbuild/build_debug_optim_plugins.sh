#! /bin/sh

set -x &&

cd $(dirname $0)/../.. &&

# the only place where we write; nothing is touched outside of this dir
output=/tmp/psycle-player-test &&

# where everything is going to be built
build=$output/build &&

# where everything is going to be installed
prefix=$output/install &&

common_flags='-march=native -ggdb3 -Wall -Wstrict-aliasing=2 -Winit-self' && # -Wfloat-equal -Wpadded

# test whether compiler supports link-time optimisation (lto)
if cpp -P -xc++ /dev/null -flto; then optims="$optims -flto";  fi &&
# test whether compiler supports openmp
if cpp -P -xc++ /dev/null -fopenmp; then optims="$optims -fopenmp"; fi &&


# build the plugins separately so that we can use different compiler flags
psycle-plugins/wonderbuild_script.py --bld-dir=$build/optim --install-prefix-dir=$prefix \
	--cxx-flags="$common_flags -O3 -DNDEBUG $optims" --ld-flags="$optims" &&

psycle-player/wonderbuild_script.py  --bld-dir=$build/debug --install-prefix-dir=$prefix \
	--cxx-flags="$common_flags -O0 -UNDEBUG" &&

# merge the two staged-install dirs into one
rm -Rf $prefix &&
mkdir $prefix &&
# using hard links (-l) makes it pretty fast
cp -axl $build/optim/staged-install/$prefix/* $prefix &&
cp -axl $build/debug/staged-install/$prefix/* $prefix &&

# choose either gdb, valgrind, alleyoop ...
#cmd=valgrind &&
#cmd="alleyoop --recursive $(cd ../.. && pwd) --" &&
cmd='gdb --ex run --ex quit --args' &&

# choose the audio driver (gstreamer, alsa, esd ...)
driver=alsa &&
#driver=gstreamer &&
#driver=esd &&

# song to play (passed as argument or defaults to a demo)
song=${1:-psycle/doc/Example - classic sounds demo.psy} &&

# LD_LIBRARY_PATH is needed for valgrind.
# PSYCLE_PATH makes sure we don't get the path from the user config file in the home dir.
LD_LIBRARY_PATH=$prefix/lib:$LD_LIBRARY_PATH \
PSYCLE_PATH=$prefix/lib \
	$cmd $prefix/bin/psycle-player --output-driver $driver --input-file "$song"

