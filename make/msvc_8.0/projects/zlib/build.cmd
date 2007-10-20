@echo off

%~d0
cd %~p0

set pkgdir=..\..\..\..\external-packages\zlib-1.2.3
set libdir=lib-mswindows-cabi

if not exist ..\..\output\zlib_stamp (

	if not exist ..\..\output\debug\bin (
		mkdir ..\..\output\debug\bin || exit /b 1
	)
	xcopy/f %pkgdir%\%libdir%\zlib1.dll ..\..\output\debug\bin\ || exit /b 1

	if not exist ..\..\output\debug\lib (
		mkdir ..\..\output\debug\lib || exit /b 1
	)
	xcopy/f %pkgdir%\%libdir%\zlib.lib ..\..\output\debug\lib\ || exit /b 1

	if not exist ..\..\output\release\bin (
		mkdir ..\..\output\release\bin || exit /b 1
	)
	xcopy/f %pkgdir%\%libdir%\zlib1.dll ..\..\output\release\bin\ || exit /b 1

	if not exist ..\..\output\release\lib (
		mkdir ..\..\output\release\lib || exit /b 1
	)
	xcopy/f %pkgdir%\%libdir%\zlib.lib ..\..\output\release\lib\ || exit /b 1

	echo zlib copied > ..\..\output\zlib_stamp || exit /b 1
)
