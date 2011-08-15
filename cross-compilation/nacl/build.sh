#! /bin/sh
set -x &&
cd $(dirname $0) &&

depot_tools=$(pwd)/depot_tools &&

mkdir -p native_client_sdk &&
cd native_client_sdk &&
test -f .gclient || $depot_tools/gclient config http://nativeclient-sdk.googlecode.com/svn/trunk/src
$depot_tools/gclient sync

cd src &&
./scons installer

