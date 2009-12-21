#! /bin/sh

set -x &&

cd $(dirname $0)/../.. &&

# where everything is going to be installed
dest=/tmp/psycle-player-test &&

# build the plugins separately so that we can use different compiler flags
psycle-plugins/wonderbuild_script.py --install-dest-dir=$dest --install-prefix-dir=/ --cxx-flags='-O1 -ggdb3' &&
psycle-player/wonderbuild_script.py  --install-dest-dir=$dest --install-prefix-dir=/ --cxx-flags='-O3 -ggdb3' &&

# choose either gdb, valgrind, alleyoop ...
cmd=valgrind &&
cmd="alleyoop --recursive $(pwd) --" &&
cmd='gdb --ex run --ex bt --args' &&

# choose the audio driver (gstreamer, alsa ...)
driver=gstreamer &&

# song to play (passed as argument or default to a demo)
song=${1:-psycle/doc/Example - classic sounds demo.psy} &&

# LD_LIBRARY_PATH is needed for valgrind.
# PSYCLE_PATH makes sure we don't get the path from the user config file in the home dir.
LD_LIBRARY_PATH=$dest/lib:$LD_LIBRARY_PATH \
PSYCLE_PATH=$dest/lib \
	$cmd $dest/bin/psycle-player --output-driver $driver --input-file "$song"
