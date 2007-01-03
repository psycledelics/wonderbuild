@echo off

rem ###########################################################################
rem #
rem # This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
rem # copyright 2004-2007 psycledelics http://psycle.pastnotecut.org : johan boule
rem #
rem # Startup script for rxvt terminal (msys),
rem # using the value of the SHELL env var for the shell program (or if not set, setting it to interactive bash shell)
rem #
rem ###########################################################################

pushd %~dp0 || goto :failed

rem set DISPLAY to nothing, otherwise, msys' rxvt won't start (it has no support for the X Window protocol, unlike cygwin's).
set DISPLAY=

if "%DISPLAY%" == "" (
	if "%FONT%" == "" (
		if exist "%SYSTEMROOT%\fonts\lucon.ttf" (
			set FONT=Lucida Console-11
		) else (
			set FONT=Courier-12
		)
	)
)

set COLUMNS=140
set LINES=60

if "%SHELL%" == "" (
	call libexec\settings || goto :failed
	set SHELL=bash --login -i
)

if "%MSYSTEM%" == "" set MSYSTEM=MINGW32

call libexec\rxvt %1 || goto :failed

popd || goto :failed
goto :eof

rem ------
rem failed
rem ------
:failed
	set return_code=%ErrorLevel%
	echo %~n0: Failed with return code: %return_code%
	pause
	set failed=true
	if "%return_code%" == "0" (
		exit /b 1
	) else (
		exit /b %return_code%
	)
