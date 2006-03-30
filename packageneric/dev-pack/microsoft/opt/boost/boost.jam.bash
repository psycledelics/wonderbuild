#!/bin/bash

function main
{
	if test -z "$MINGW_ROOT_DIRECTORY"
	then
		echo "$(basename $0): MINGW_ROOT_DIRECTORY env var not set."
		false
		return
	fi &&
	if test -z "$PYTHON_ROOT"
	then
		echo "$(basename $0): PYTHON_ROOT env var not set."
		false
		return
	fi &&
	cd $(dirname $0) &&
	rm -rf boost.src.build boost.install &&
	cp -r boost.src boost.src.build &&
	cp boost.config.user.hpp boost.src.build/boost/config/user.hpp &&
	cd boost.src.build &&
	../boost.jam/bjam \
		-sTOOLS=${1:-mingw} \
		"-sBUILD=release <runtime-link>dynamic <threading>multi <optimization>full" \
		"-sGXX=g++ -O3 -Wl,-O3,--enable-runtime-pseudo-reloc" \
		--builddir=../boost.build \
		--prefix=../boost.install \
		install
}

#main "$@" | tee boost.log | grep error
#main "$@" > boost.log
main "$@"
