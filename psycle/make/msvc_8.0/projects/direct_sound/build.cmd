@echo off

%~d0
cd %~p0

set pkgdir=..\..\..\..\..\external-packages\dsound-9
set libdir=lib-mswindows-msvc-cxxabi

if not exist ..\..\output\direct_sound_stamp (

	if not exist ..\..\output\debug\lib (
		mkdir ..\..\output\debug\lib || exit /b 1
	)
	xcopy/f %pkgdir%\%libdir%\dsound.lib ..\..\output\debug\lib\ || exit /b 1

	if not exist ..\..\output\release\lib (
		mkdir ..\..\output\release\lib || exit /b 1
	)
	xcopy/f %pkgdir%\%libdir%\dsound.lib ..\..\output\release\lib\ || exit /b 1

	echo direct_sound copied > ..\..\output\direct_sound_stamp || exit /b 1
)
