#! /bin/sh

set -x &&

cd $(dirname $0) &&

./wonderbuild_script.py --cxx-flags='-O0 -ggdb3 -Wall'
