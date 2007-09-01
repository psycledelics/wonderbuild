call %~dp0\..\psycle-dev-pack-for-mswindows\libexec\main no-msys || exit /b 1
if "%1" == "scons-tools-mingw" set SCONS_TOOLS=mingw || exit /b 1
