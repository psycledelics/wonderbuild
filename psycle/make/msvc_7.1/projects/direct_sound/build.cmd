@echo off

%~d0
cd %~p0

set pkgdir=..\..\..\..\..\external-packages\dsound-9
set libdir=lib-mswindows-msvc-cxxabi

if not exist ..\..\..\..\include\dsound.h (
	if not exist ..\..\..\..\include (
		mkdir ..\..\..\..\include || exit /b 1
	)
	xcopy/f %pkgdir%\include\dsound.h ..\..\..\..\include\ || exit /b 1
)

if not exist ..\..\output\direct_sound_stamp (

	if not exist ..\..\output\debug\lib (
		mkdir ..\..\output\debug\lib || exit /b 1
	)
	xcopy/f %pkgdir%\%libdir%\dsound.lib ..\..\output\debug\lib\ || exit /b 1

	if not exist ..\..\output\release.g7\lib (
		mkdir ..\..\output\release.g7\lib || exit /b 1
	)
	xcopy/f %pkgdir%\%libdir%\dsound.lib ..\..\output\release.g7\lib\ || exit /b 1

	if not exist ..\..\output\release.g6\lib (
		mkdir ..\..\output\release.g6\lib || exit /b 1
	)
	xcopy/f %pkgdir%\%libdir%\dsound.lib ..\..\output\release.g6\lib\ || exit /b 1

	echo direct_sound copied > ..\..\output\direct_sound_stamp || exit /b 1
)
