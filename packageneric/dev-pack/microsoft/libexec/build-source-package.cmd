@echo off

rem ###########################################################################
rem #
rem # This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
rem # copyright 2004-2007 psycledelics http://psycle.pastnotecut.org : johan boule
rem #
rem # Build wrapper script for source packages
rem #
rem ###########################################################################

pushd %~dp0.. || goto :failed

set package=%1|| goto :failed

call libexec\settings || goto :failed
set SHELL=sh --login -c '~/working-dir/source-packages/%package%/build --retry ; echo press enter to close ; read'
set TITLE=%~n0 %package%
set BGCOLOR=#fafaff
call terminal || goto :failed

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
