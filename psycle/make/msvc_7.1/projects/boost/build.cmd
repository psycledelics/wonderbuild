@echo off

%~d0
cd %~p0

set pkgdir=..\..\..\..\..\external-packages\boost-1.32
set libdir=lib-mswindows-msvc-7.1-cxxabi-1310

if not exist ..\..\..\..\include\boost (
	pushd %pkgdir% || exit /b 1
	..\7za\7za x -y include.tar.bz2 || exit /b 1
	..\7za\7za x -y include.tar || exit /b 1
	del/q include.tar || exit /b 1
	popd || exit /b 1

	if not exist ..\..\..\..\include\ (
		mkdir ..\..\..\..\include\ || exit /b 1
	)
	rem cmd's move command bugs with long paths, so we try cygwin's mv command first
	mv %pkgdir%\include\boost ..\..\..\..\include\boost || (
		echo "no mv command ... using cmd move builtin as fallback"
		move %pkgdir%\include\boost ..\..\..\..\include\boost || exit /b 1
	)
	rmdir/s/q %pkgdir%\include || exit /b 1
)

if not exist ..\..\output\boost_stamp (
	pushd %pkgdir% || exit /b 1
	..\7za\7za x -y %libdir%.tar.bz2 || exit /b 1
	..\7za\7za x -y %libdir%.tar || exit /b 1
	del/q %libdir%.tar || exit /b 1
	popd || exit /b 1

	if not exist ..\..\output\debug\bin (
		mkdir ..\..\output\debug\bin || exit /b 1
	)
	move %pkgdir%\%libdir%\*-gd-*.dll ..\..\output\debug\bin || exit /b 1

	if not exist ..\..\output\debug\lib (
		mkdir ..\..\output\debug\lib || exit /b 1
	)
	move %pkgdir%\%libdir%\*-gd-*.lib ..\..\output\debug\lib || exit /b 1

	if not exist ..\..\output\release.g6\bin (
		mkdir ..\..\output\release.g6\bin || exit /b 1
	)
	xcopy/f/i %pkgdir%\%libdir%\*.dll ..\..\output\release.g6\bin\ || exit /b 1

	if not exist ..\..\output\release.g6\lib (
		mkdir ..\..\output\release.g6\lib || exit /b 1
	)
	xcopy/f/i %pkgdir%\%libdir%\*.lib ..\..\output\release.g6\lib\ || exit /b 1

	if not exist ..\..\output\release.g7\bin (
		mkdir ..\..\output\release.g7\bin || exit /b 1
	)
	move %pkgdir%\%libdir%\*.dll ..\..\output\release.g7\bin\ || exit /b 1

	if not exist ..\..\output\release.g7\lib (
		mkdir ..\..\output\release.g7\lib || exit /b 1
	)
	move %pkgdir%\%libdir%\*.lib ..\..\output\release.g7\lib\ || exit /b 1

	echo boost extracted > ..\..\output\boost_stamp || exit /b 1
	rmdir/s/q %pkgdir%\%libdir% || exit /b 1
)
