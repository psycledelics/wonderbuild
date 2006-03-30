@echo off

rem ###########################################################################
rem #
rem # This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
rem # Copyright (C) 2004-2005 Psycledelics http://psycle.pastnotecut.org : Johan Boule
rem #
rem # Startup script chaining all the other startup scrips in the correct order
rem #
rem ###########################################################################

pushd %~dp0 || goto :failed

call version || goto :failed
rem call paths || goto :failed
call fstab || goto :failed
call http_proxy || goto :failed

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
