#! /bin/sh

#set -x &&

toolchain=$(cd $(dirname $0) && pwd)/native_client_sdk_0_5_1031/toolchain/linux_x86 && test -d $toolchain &&
pre=$toolchain/bin && test -d $pre &&
#export SYSROOT=$toolchain/sys && test -d $SYSROOT &&
bin_prefix=$pre/x86_64-nacl- &&
export AS=${bin_prefix}as && test -x $AS &&
export CPP=${bin_prefix}cpp && test -x $CPP &&
export CC=${bin_prefix}gcc && test -x $CC &&
export CXX=${bin_prefix}c++ && test -x $CXX &&
export AR=${bin_prefix}ar && test -x $AR &&
export RANLIB=${bin_prefix}ranlib && test -x $RANLIB &&
#export LD=${bin_prefix}ld && test -x $LD &&
export STRIP=${bin_prefix}strip && test -x $STRIP &&

exec "$@"
