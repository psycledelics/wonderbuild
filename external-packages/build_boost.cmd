rem Index
rem ======
rem - Build with MinGW (using windows console).
rem - Build with Visual C++
rem
rem Worth reading: http://stackoverflow.com/questions/2629421/how-to-use-boost-in-visual-studio-2010

%~d0%
cd %~p0

rem The 'bootstrap' script builds bjam.exe in the source dir.
if not exist bootstrap.bat ( echo This file has to be placed in boost 1.50.0 root source dir (i.e. where bootstrap.bat is)
	goto :eof
)
if not exist bjam.exe call bootstrap

set bjam=%cd%\bjam -j%NUMBER_OF_PROCESSORS% --debug-configuration ^
 --build-dir=%src%\.build --prefix=%src%\.install ^
 link=shared runtime-link=shared threading=multi variant=release,debug

if "%1" NEQ "" ( call %1
	goto :eof
)
echo Please, enter one of: msvc32 msvc64 mingw

goto :eof

:mingw
rem -----------------------------------------------------------------------------------------------------------------
rem The following commands can be used to build boost using the MinGW compiler.
rem The target platform, architecture and address model depends entirely on the variant of mingw.
rem -----------------------------------------------------------------------------------------------------------------

%bjam% toolset=gcc install

goto :eof

:msvc64
rem -----------------------------------------------------------------------------------------------------------------
rem The following commands can be used to build boost for the 64-bit Windows platform, using the Visual C++ compiler.
rem -----------------------------------------------------------------------------------------------------------------

%bjam% toolset=msvc define=_SECURE_SCL=0 define=_HAS_ITERATOR_DEBUGGING=0 ^
 address-model=64 --stagedir=%src%\.stage64 stage

goto :eof

:msvc32
rem -----------------------------------------------------------------------------------------------------------------
rem The following commands can be used to build boost for the 32-bit Windows platform, using the Visual C++ compiler.
rem -----------------------------------------------------------------------------------------------------------------

%bjam% toolset=msvc define=_SECURE_SCL=0 define=_HAS_ITERATOR_DEBUGGING=0 ^
 address-model=32 --stagedir=%src%\.stage32 stage

goto :eof
