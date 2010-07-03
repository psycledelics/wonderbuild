#! /bin/sh

#set -x &&

toolchain=$(cd $(dirname $0) && pwd)/iphonedevonlinux/toolchain && test -d $toolchain &&
pre=$toolchain/pre && test -d $pre &&
sys=$toolchain/sys && test -d $sys &&
bin_prefix=$pre/bin/arm-apple-darwin9- &&
export AS=${bin_prefix}as && test -x $AS &&
export CPP=${bin_prefix}cpp && test -x $CPP &&
export CC=${bin_prefix}gcc && test -x $CC &&
export CXX=${bin_prefix}c++ && test -x $CXX &&
export AR=${bin_prefix}ar && test -x $AR &&
export RANLIB=${bin_prefix}ranlib && test -x $RANLIB &&
#export LD=${bin_prefix}ld && test -x $LD &&
export STRIP=${bin_prefix}strip && test -x $STRIP &&

exec "$@"
