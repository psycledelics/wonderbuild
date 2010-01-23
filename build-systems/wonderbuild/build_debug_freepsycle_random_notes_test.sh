#! /bin/sh

set -x &&

cd $(dirname $0)/../.. &&

# where everything is going to be installed
dest=/tmp/freepsycle-random-notes-test &&

freepsycle/wonderbuild_script.py --install-dest-dir=/ --install-prefix-dir=$dest --cxx-flags='-O0 -ggdb3 -Wall' &&

# choose either gdb, valgrind, alleyoop ...
#cmd=valgrind &&
#cmd="alleyoop --recursive $(pwd) --" &&
cmd='gdb --ex run --ex quit --args' &&

# LD_LIBRARY_PATH is needed for valgrind.
LD_LIBRARY_PATH=$dest/lib:$LD_LIBRARY_PATH \
	$cmd $dest/bin/freepsycle-test-random-notes
