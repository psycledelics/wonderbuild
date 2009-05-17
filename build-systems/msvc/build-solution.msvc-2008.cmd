%~d0
cd %~p0
set configuration=%1
if "%configuration%" == "" (
	set configuration=release
)
call "%VS90ComnTools%\VSVars32" || exit /b 1
rem msbuild solution.msvc-2008.sln -property:configuration=%configuration% || exit /b 1
rem vcbuild solution.msvc-2008.sln "%configuration%|Win32" || exit /b 1
DevEnv solution.msvc-2008.sln /useenv /build %configuration% || exit /b 1
