@echo off

rem ###########################################################################
rem #
rem # This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
rem # Copyright (C) 2004-2005 Psycledelics http://psycle.pastnotecut.org : Johan Boule
rem #
rem # Sets the paths
rem #
rem ###########################################################################

pushd %~dp0..\opt\gtk || goto :failed

echo %~n0: Setting up GTK_BASEPATH env var ... || goto :failed
rem (
	set GTK_BASEPATH=%CD%|| goto :failed
	rem echo %~n0: GTK_BASEPATH env var: %GTK_BASEPATH% || goto :failed
rem )

pushd bin || goto :failed

echo %~n0: modules: gdk pixbuf loaders ... || goto :failed
rem (
	gdk-pixbuf-query-loaders.exe > ..\etc\gtk-2.0\gdk-pixbuf.loaders || goto :failed
rem )
echo %~n0: modules: gtk im ... || goto :failed
rem (
	gtk-query-immodules-2.0.exe > ..\etc\gtk-2.0\gtk.immodules || goto :failed
rem )
echo %~n0: modules: pango ... || goto :failed
rem (
	pango-querymodules.exe > ..\etc\pango\pango.modules || goto :failed
rem )

popd || goto :failed

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
