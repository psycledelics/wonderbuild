@echo off

%~d0
cd %~p0

SETLOCAL

set pkgdir=..\..\..\..\external-packages\stk-%1
set deldir=0

if not exist %pkgdir%\stk (
	pushd %pkgdir% || exit /b 1
	mkdir stk
	..\7za\7z.exe x -y stk-%1.tar.bz2 || exit /b 1
	..\7za\7z.exe x -y stk-%1.tar || exit /b 1
	xcopy stk-%1\include\* stk || exit /b 1
	xcopy stk-%1\src\* stk || exit /b 1
	rmdir /S /Q stk-%1 || exit /b 1
	del /q stk-%1.tar || exit /b 1
	popd || exit /b 1
)


ENDLOCAL