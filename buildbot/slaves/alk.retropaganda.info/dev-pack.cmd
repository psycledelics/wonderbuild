set MAKEFLAGS=-j8
rem set SCONSFLAGS=-j8
set LIB=
set INCLUDE=

if "%2" neq "msvc-solution" (
	call %~dp0\..\psycle-dev-pack-for-mswindows\libexec\main %* || exit /b 1
	goto :msvc_extra
)

:msvc_hardcoded
	rem hardcoded paths for unintelligent .sln/.vcproj/.vcprops stuff

	set X=%~dp0\..\psycle-dev-pack-for-mswindows\opt\gtk

	set LIB=%LIB%;%X%\lib
	set INCLUDE=%INCLUDE%;%X%\include

	set INCLUDE=%INCLUDE%;%X%\include\libxml++-2.6
	set INCLUDE=%INCLUDE%;%X%\lib\libxml++-2.6\include

	set INCLUDE=%INCLUDE%;%X%\include\libxml2

	set INCLUDE=%INCLUDE%;%X%\include\glibmm-2.4
	set INCLUDE=%INCLUDE%;%X%\lib\glibmm-2.4\include

	set INCLUDE=%INCLUDE%;%X%\include\sigc++-2.0
	set INCLUDE=%INCLUDE%;%X%\lib\sigc++-2.0\include

	set INCLUDE=%INCLUDE%;%X%\include\glib-2.0
	set INCLUDE=%INCLUDE%;%X%\lib\glib-2.0\include
)

:msvc_extra
	rem msvc libs not in the dev-pack
	
	set INCLUDE=%INCLUDE%;x:\usr\lib\dx\include
	set LIB=%LIB%;x:\usr\lib\dx\lib
