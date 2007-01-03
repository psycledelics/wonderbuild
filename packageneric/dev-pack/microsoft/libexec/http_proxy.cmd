@echo off

rem ###########################################################################
rem #
rem # This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
rem # copyright 2004-2007 psycledelics http://psycle.pastnotecut.org : johan boule
rem #
rem # Reads the HTTP proxy setting and sets the env var accordingly
rem #
rem ###########################################################################

pushd %~dp0.. || goto :failed

if "%HTTP_PROXY%" == "" (
	echo %~n0: Reading HTTP proxy configuration via proxycfg ... || goto :failed
	rem (
		for /f "usebackq delims=#" %%x in (`sh -c "proxycfg | grep 'Proxy Server' | sed 's/.*=//' | sed 's/^ *//' | sed 's/ *$//' | sed 's/^-.*-$//'"`) do set HTTP_PROXY=%%x || goto :failed
	rem )
)
if "%HTTP_PROXY%" == "" (
	echo %~n0: No HTTP proxy set. || goto :failed
) else (
	echo %~n0: HTTP_PROXY env var set to: %HTTP_PROXY% || goto :failed
	rem late evaluation !HTTP_PROXY! doesn't even work.
)

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
