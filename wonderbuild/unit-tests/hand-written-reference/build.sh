#! /bin/sh

set -x &&

cd $(dirname $0) &&

if test "$1" = "clean"
then
	rm -f *.o *.a *.so *.dbg prog prog-* &&
	exit
fi &&

##########
# dynamic

c++ -o bar.o -fPIC -c -ggdb3 -O0 bar.cpp -I. &&
c++ -o libbar.so -shared bar.o &&
objcopy --only-keep-debug libbar.so libbar.so.dbg &&
objcopy --strip-debug libbar.so &&
objcopy --add-gnu-debuglink=libbar.so.dbg libbar.so &&
readelf -d libbar.so | grep NEEDED &&

c++ -o foo.o -fPIC -c -ggdb3 -O0 foo.cpp -I. &&
c++ -o libfoo.so -shared foo.o -L. -Wl,-rpath-link=. -Wl,-rpath=\$ORIGIN -lbar && # -Wl,-no-undefined
objcopy --only-keep-debug libfoo.so libfoo.so.dbg &&
objcopy --strip-debug libfoo.so &&
objcopy --add-gnu-debuglink=libfoo.so.dbg libfoo.so &&
readelf -d libfoo.so | grep NEEDED &&

c++ -o prog.o -c -ggdb3 -O0 prog.cpp -I. &&
c++ -o prog prog.o -L. -Wl,-rpath-link=. -Wl,-rpath=\$ORIGIN -lfoo &&
objcopy --only-keep-debug prog prog.dbg &&
objcopy --strip-debug prog &&
objcopy --add-gnu-debuglink=prog.dbg prog &&
readelf -d prog | grep NEEDED &&
./prog &&

#########
# static

c++ -o bar-static.o -c -ggdb3 -O0 bar.cpp -I. &&
ar crs libbar.a bar-static.o &&

c++ -o foo-static.o -c -ggdb3 -O0 foo.cpp -I. &&
ar crs libfoo.a foo-static.o &&

c++ -o prog-static.o -c -ggdb3 -O0 prog.cpp -I. &&
c++ -o prog-static -static prog-static.o -L. -lfoo -lbar &&
./prog-static &&

objcopy --strip-unneeded prog-static prog-static-stripped &&

:
