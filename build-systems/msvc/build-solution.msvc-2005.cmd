%~d0
cd %~p0
set configuration=%1
if "%configuration%" == "" (
	set configuration=release
)
call "%VS80ComnTools%\VSVars32" || exit /b 1
rem msbuild solution.msvc-2005.sln -property:configuration=%configuration% || exit /b 1
rem vcbuild solution.msvc-2005.sln "%configuration%|Win32" || exit /b 1
DevEnv solution.msvc-2005.sln /useenv /build %configuration% || exit /b 1
