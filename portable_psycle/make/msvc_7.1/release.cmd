rem ===============
rem clean and build
rem ===============

call "%VS71ComnTools%\VSVars32"

rem ######### amd k7 and intel p3 ##########

DevEnv solution.sln /clean release /out clean.log || ( echo clean failed, aborting. & goto :pause )
del/q clean.log
DevEnv solution.sln /build release /out release.log || ( echo build failed, aborting. & goto :pause )

rem ########## intel p4 ##########

DevEnv solution.sln /clean release_intel_pentium_4 /out clean.log || ( echo clean failed, aborting. & goto :pause )
del/q clean.log
DevEnv solution.sln /build release_intel_pentium_4 /out release.log || ( echo build failed, aborting. & goto :pause )

rem ====================================
rem make the directory to be distributed
rem ====================================

set timestamp=%date%.%time%
set timestamp=%timestamp: =.%
set timestamp=%timestamp:/=.%
set timestamp=%timestamp:\=.%
set timestamp=%timestamp::=.%
set timestamp=%timestamp:-=.%

set distribution=.\psycle.bin.timestamp-%timestamp%\

rmdir/s/q "%distribution%"
mkdir "%distribution%"

rem ------------------------------
rem copy executables and libraries
rem ------------------------------

rem ########## amd k7 and intel p3 ##########

mkdir "%distribution%\amd-k7-and-intel-pentium-3\"
xcopy/f/i ".\release\bin\psycle.exe" "%distribution%\amd-k7-and-intel-pentium-3\" || ( echo copy failed, aborting. & goto :pause )
rename "%distribution%\amd-k7-and-intel-pentium-3\psycle.exe" "psycle.timestamp-%timestamp%.exe" || ( echo rename failed, aborting. & goto :pause )
call :upx "%distribution%\amd-k7-and-intel-pentium-3\psycle.timestamp-%timestamp%.exe"

mkdir "%distribution%\amd-k7-and-intel-pentium-3\plugins\"
xcopy/f .\release\bin\psycle__plugins\*.dll "%distribution%\amd-k7-and-intel-pentium-3\plugins\" || ( echo copy failed, aborting. & goto :pause )

rem ########## intel p4 ##########

mkdir "%distribution%\intel-pentium-4\"
xcopy/f/i ".\release_intel_pentium_4\bin\psycle.exe" "%distribution%\intel-pentium-4\" || ( echo copy failed, aborting. & goto :pause )
rename "%distribution%\intel-pentium-4\psycle.exe" "psycle.timestamp-%timestamp%-intel-pentium-4.exe" || ( echo rename failed, aborting. & goto :pause )
call :upx "%distribution%\intel-pentium-4\psycle.timestamp-%timestamp%-intel-pentium-4.exe"

mkdir "%distribution%\intel-pentium-4\plugins\"
xcopy/f .\release_intel_pentium_4\bin\psycle__plugins\*.dll "%distribution%\intel-pentium-4\plugins\" || ( echo copy failed, aborting. & goto :pause )

rem ------------------------------------------
rem copy microsoft c/c++/mfc runtime libraries
rem ------------------------------------------

xcopy/f "%SYSTEMROOT%\system32\msvcr71.dll" "%distribution%" || ( echo copy failed, aborting. & goto :pause )
xcopy/f "%SYSTEMROOT%\system32\msvcp71.dll" "%distribution%" || ( echo copy failed, aborting. & goto :pause )
xcopy/f "%SYSTEMROOT%\system32\mfc71.dll" "%distribution%" || ( echo copy failed, aborting. & goto :pause )

rem ---------------------------
rem copy end-user documentation
rem ---------------------------

mkdir "%distribution%\doc\"
xcopy/f/s ..\..\doc\for-end-users\* "%distribution%\doc\" || ( echo copy failed, aborting. & goto :pause )

rem ----------------
rem remove cvs files
rem ----------------

for /r "%distribution%" %%i in (CVS) do rmdir/s/q "%%i"
for /r "%distribution%" %%i in (.cvsignore) do del/q "%%i"

rem ----------------------------------------------------------------------------------
rem convert text files to microsoft end-of-lines (unix2dos is distributed with cygwin)
rem ----------------------------------------------------------------------------------
for /r "%distribution%" %%i in (*.txt *.text) do unix2dos "%%i"

rem ================
rem make the archive
rem ================

del/q .\psycle.bin.rar
rar a -s -m5 -md4096 -ep1 -r0 .\psycle.bin.rar "%distribution%" 1>> .\release.log 2>&1 || ( echo rar failed, aborting. & goto :pause )

rem =====================================================================================
rem upload the archive and update the site (scp and ssh are cygwin commands, use / not \)
rem =====================================================================================

group=/home/groups/p/ps/psycle/

rem maps local user account names to sourceforge user account names

if "%USERPNAME%" == "bohan" (
	set user=johan-boule
) else if "%USERPNAME%" == "x" (
	set user=alkenstein
) else (
	set user="%USERPNAME%"
)

scp ./psycle.bin.rar "%user%@shell.sourceforge.net:%group%/htdocs/" || ( echo scp failed, aborting. && goto :pause )
ssh "%user%@shell.sourceforge.net" "%group%/htdocs.update.bash" || ( echo ssh failed, aborting. && goto :pause )

rem ================================
rem pause and remove temporary files
rem ================================

:pause
pause
rmdir/s/q "%distribution%"
del/q .\psycle.bin.rar
del/q .\release.log
goto :eof

rem ===============
rem upx sub routine
rem ===============

:upx
upx.exe --overlay=strip --force --strip-relocs=1 --compress-icons=1 --best --crp-ms=999999 --nrv2d --no-backup -o %~p1%~n1.upx%~x1 %1
goto :eof
