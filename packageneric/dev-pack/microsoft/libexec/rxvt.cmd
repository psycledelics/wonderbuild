@echo off

rem ###########################################################################
rem #
rem # This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
rem # Copyright (C) 2004-2005 Psycledelics http://psycle.pastnotecut.org : Johan Boule
rem #
rem # Startup script for rxvt terminal (cygwin or msys),
rem # using the value of the SHELL env var for the shell program
rem #
rem ###########################################################################

pushd %~dp0.. || goto :failed

echo %~n0: Starting rxvt terminal ... || goto :failed
rem (
	if "%TERM%" == "" (
		if "%1" == "" (
			set TERM=rxvt
		) else (
			set PATH=%PATH%;%~dp1
			set TERM=%~n1
		)
	)
	
	if "%DISPLAY%" == "" (
		if "%FONT%" == "" (
			if exist "%SYSTEMROOT%\fonts\lucon.ttf" (
				set FONT=Lucida Console-11
			) else (
				set FONT=Courier-12
			)
		)
	)
	
	if "%COLUMNS%" == "" set COLUMNS=140
	if "%LINES%" == "" set LINES=60

	rem Setup colors for rxvt.
	rem (
		rem Default colors.
		rem (
			if "%MSYSTEM%" == "MSYS" (
				if "%BGCOLOR%" == "" set BGCOLOR=LightYellow
				if "%FGCOLOR%" == "" set FGCOLOR=Navy
			) else if "%MSYSTEM%" == "MINGW32" (
				if "%BGCOLOR%" == "" set BGCOLOR=#fffff8
				if "%FGCOLOR%" == "" set FGCOLOR=#000055
			) else (
				if "%BGCOLOR%" == "" set BGCOLOR=#fafff8
				if "%FGCOLOR%" == "" set FGCOLOR=#000055
			)
		rem )
		rem Other colors.
		rem (
			set COLORS=--scrollColor "#aabbcc" --background "%BGCOLOR%" --foreground "%FGCOLOR%" --cursorColor "#00ff88" --cursorColor2 "#884400" --color0 "#000000" --color1 "#880000" --color2 "#008800" --color3 "#666600" --color4 "#0000aa" --color5 "#770077" --color6 "#006666" --color7 "#bbbbbb" --color8 "#444444" --color9 "#ff0000" --color10 "#00aa00" --color11 "#aaaa00" --color12 "#0000ff" --color13 "#aa00aa" --color14 "#00aaaa" --color15 "#ded0ba"
		rem )
	
	if "%SHELL%" == "" (
		rem set ENV=/etc/profile
		rem set SHELL=sh -i
		set SHELL=bash --login -i
	)
	
	if "%TITLE%" == "" (
		set TITLE=%SHELL%
	)

	start %TERM% --termName %TERM% --backspacekey   --font "%FONT%" --geometry %COLUMNS%x%LINES% --saveLines 10000 --mapAlert --scrollTtyOutput ++scrollTtyKeypress %COLORS% -title "%TITLE%" -e %SHELL%
	
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
