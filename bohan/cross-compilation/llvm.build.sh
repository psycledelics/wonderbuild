#! /bin/sh

set -x &&

cd $(dirname $0)/llvm &&

svn up &&

prefix=$(pwd)/++install &&

mkdir -p ++build &&
cd ++build &&

../configure --prefix=$prefix --enable-optimized --disable-assertions --enable-threads "$@"

make -j8 install
