%~d0
cd %~p0
set configuration=%1
if "%configuration%" == "" (
	set configuration=release
)
call "%VS90ComnTools%\VSVars32" || exit /b 1
rem msbuild psycle-solution-186-msvc9.0.sln -property:configuration=%configuration% || exit /b 1
vcbuild psycle-solution-186-msvc9.0.sln "%configuration%|Win32" || exit /b 1
rem DevEnv psycle-solution-186-msvc9.0.sln /useenv /build %configuration% || exit /b 1
