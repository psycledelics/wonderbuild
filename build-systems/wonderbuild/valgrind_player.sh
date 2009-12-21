#! /bin/sh

set -x &&

cd $(dirname $0) &&

prefix=++wonderbuild/staged-install/usr/local &&

# LD_LIBRARY_PATH is needed for valgrind.
LD_LIBRARY_PATH=$(pwd)/$prefix/lib:$LD_LIBRARY_PATH alleyoop --recursive $(cd ../.. && pwd) -- $prefix/bin/psycle-player "$@"
