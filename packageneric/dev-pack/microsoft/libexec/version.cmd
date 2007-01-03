@echo off

rem ###########################################################################
rem #
rem # This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
rem # copyright 2004-2007 psycledelics http://psycle.pastnotecut.org : johan boule
rem #
rem # Sets the version of the dev-pack
rem #
rem ###########################################################################

pushd %~dp0.. || goto :failed

echo %~n0: Setting up PACKAGENERIC__DEV_PACK__VERSION env var ... || goto :failed
rem (
	set PACKAGENERIC__DEV_PACK__VERSION=21
	echo %~n0: PACKAGENERIC__DEV_PACK__VERSION env var: %PACKAGENERIC__DEV_PACK__VERSION% || goto :failed
rem )

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
