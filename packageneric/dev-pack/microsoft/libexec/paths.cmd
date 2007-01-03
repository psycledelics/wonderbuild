@echo off

rem ###########################################################################
rem #
rem # This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
rem # copyright 2004-2007 psycledelics http://psycle.pastnotecut.org : johan boule
rem #
rem # Sets the paths
rem #
rem ###########################################################################

pushd %~dp0.. || goto :failed

echo %~n0: Setting up paths with base dir %CD% ... || goto :failed

call %~dp0paths.gtk || goto :failed

echo %~n0: Setting up PATH env var ... || goto :failed
rem (
	set PATH=%SYSTEMROOT%\system32|| goto :failed
	set PATH=%CD%\opt\msys\bin;%PATH%|| goto :failed
	set PATH=%CD%\opt\msys\local\bin;%PATH%|| goto :failed
	set PATH=%CD%\opt\mingw\bin;%PATH%|| goto :failed
	set PATH=%CD%\opt\boost\lib;%PATH%|| goto :failed
	set PATH=%GTK_BASEPATH%\bin;%PATH%|| goto :failed
	set PATH=%CD%\opt\gnomecanvas\bin;%PATH%|| goto :failed
	set PATH=%CD%\opt\doxygen\bin;%PATH%|| goto :failed
	set PATH=%CD%\opt\graphviz\bin;%PATH%|| goto :failed
	set PATH=%CD%\opt\pkg-config\bin;%PATH%|| goto :failed
	set PATH=%CD%\opt\cygcheck\bin;%PATH%|| goto :failed
	set PATH=%CD%\opt\listdlls\bin;%PATH%|| goto :failed
	set PATH=%CD%\opt\junction\bin;%PATH%|| goto :failed
	set PATH=%CD%\opt\7-zip\bin;%PATH%|| goto :failed
	set PATH=%CD%\opt\wget\bin;%PATH%|| goto :failed
	set PATH=%CD%\opt\gnupg\bin;%PATH%|| goto :failed
	set PATH=%CD%\opt\kdiff3\bin;%PATH%|| goto :failed
	set PATH=%CD%\opt\eclipse;%PATH%|| goto :failed
	set PATH=%CD%\opt\jre\bin;%PATH%|| goto :failed
	rem echo %~n0: PATH env var: %PATH% || goto :failed
rem )

echo %~n0: Setting up PKG_CONFIG_PATH env var ... || goto :failed
rem (
	set PKG_CONFIG_PATH= || goto :failed
	set PKG_CONFIG_PATH=%CD%\opt\boost\lib\pkgconfig;%PKG_CONFIG_PATH%|| goto :failed
	set PKG_CONFIG_PATH=%GTK_BASEPATH%\lib\pkgconfig;%PKG_CONFIG_PATH%|| goto :failed
	set PKG_CONFIG_PATH=%CD%\opt\gnomecanvas\lib\pkgconfig;%PKG_CONFIG_PATH%|| goto :failed
	rem echo %~n0: PKG_CONFIG_PATH env var: %PKG_CONFIG_PATH% || goto :failed
rem )

echo %~n0: Setting up GNUPGHOME env var ... || goto :failed
rem (
	set GNUPGHOME=/dev-pack/.gnupg || goto :failed
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
