#! /bin/sh

set -x &&

cd $(dirname $0)/../.. &&

# where everything is going to be build/installed
dest=/tmp/psycle-player-test &&

# test whether compiler supports link-time optimisation (lto)
{ cpp -P 2>/dev/null << EOF
        #if (__GNUC__ * 10000 + __GNUC_MINOR__ * 100 + __GNUC_PATCHLEVEL__) < 40500
                #error version too low
        #endif
EOF
} && lto=-flto

common_flags='-march=native -ggdb3 -Wall -Wstrict-aliasing=2 -Winit-self' && # -Wfloat-equal -Wpadded

# build the plugins separately so that we can use different compiler flags
psycle-plugins/wonderbuild_script.py --install-dest-dir=/ --install-prefix-dir=$dest/optim --cxx-flags="$common_flags -O3 -DNDEBUG -fno-strict-aliasing $lto" &&
psycle-player/wonderbuild_script.py  --install-dest-dir=/ --install-prefix-dir=$dest/debug --cxx-flags="$common_flags -O0 -UNDEBUG" &&

rm -Rf $dest/merge &&
mkdir $dest/merge &&
# using hard links (-l) makes it pretty fast
cp -axl $dest/optim/* $dest/merge &&
cp -axl $dest/debug/* $dest/merge &&

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
LD_LIBRARY_PATH=$dest/merge/lib:$LD_LIBRARY_PATH \
PSYCLE_PATH=$dest/merge/lib \
	$cmd $dest/merge/bin/psycle-player --output-driver $driver --input-file "$song"
