#! /bin/sh
set -x &&
cd $(dirname $0)/llvm &&
svn up &&

mkdir -p ++build &&
cd ++build &&

../configure --prefix=/tmp/install --enable-optimized --disable-assertions --enable-threads "$@"

make -j8 install
