@echo off

rem ###########################################################################
rem #
rem # This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
rem # Copyright (C) 2004-2005 Psycledelics http://psycle.pastnotecut.org : Johan Boule
rem #
rem # Startup script for rxvt terminal (msys),
rem # setting the MSYSTEM env var to MSYS,
rem # and forwarding to the normal terminal startup script
rem #
rem ###########################################################################

pushd %~dp0 || goto :failed

set MSYSTEM=MSYS
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
