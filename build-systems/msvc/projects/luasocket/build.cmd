@echo off

%~d0
cd %~p0

set pkgdir=..\..\..\..\external-packages\luasocket-%1
set srcdirname=luasocket-%1

if not exist %pkgdir%\src (
	pushd %pkgdir% || exit /b 1
	..\7za\7z.exe x -y %srcdirname%.tar.bz2 || exit /b 1
	..\7za\7z.exe x -y %srcdirname%.tar || exit /b 1
	del /q %srcdirname%.tar || exit /b 1
	popd || exit /b 1
)
