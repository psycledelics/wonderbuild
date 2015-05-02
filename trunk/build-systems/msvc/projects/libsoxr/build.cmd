@echo off

%~d0
cd %~p0

set pkgdir=..\..\..\..\external-packages\libsoxr
set srcdirname=soxr-%1-Source

if not exist %pkgdir%\%srcdirname% (
	pushd %pkgdir% || exit /b 1
	..\7za\7z.exe x -y %srcdirname%.tar.xz || exit /b 1
	..\7za\7z.exe x -y %srcdirname%.tar || exit /b 1
	del /q %srcdirname%.tar || exit /b 1
	popd || exit /b 1
)
