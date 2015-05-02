#! /bin/sh

set -x &&

cd $(dirname $0) &&

prefix=++wonderbuild/staged-install/usr/local &&

# choose either gdb, valgrind, alleyoop ...
#cmd=valgrind &&
cmd="alleyoop --recursive $(cd ../.. && pwd) --" &&
#cmd='gdb --ex run --ex quit --args' &&

# LD_LIBRARY_PATH is needed for valgrind.
# PSYCLE_PATH makes sure we don't get the path from the user config file in the home dir.
LD_LIBRARY_PATH=$(pwd)/$prefix/lib:$LD_LIBRARY_PATH \
PSYCLE_PATH=$(pwd)/$prefix/lib \
	$cmd $prefix/bin/psycle-player "$@"
