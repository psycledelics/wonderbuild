#! /bin/sh
set -x &&
cd $(dirname $0)/llvm &&
./configure --prefix=/tmp/install --enable-optimized --disable-assertions --enable-threads "$@"
make -j8 install
