rem ===============
rem clean and build
rem ===============

call "%VS71ComnTools%\VSVars32"
DevEnv solution.sln /clean release /out clean.log || ( echo clean failed, aborting. & goto :pause )
rem del/q clean.log
DevEnv solution.sln /build release /out release.log || ( echo build failed, aborting. & goto :pause )

rem ========
rem compress
rem ========

call upx || ( echo upx failed, aborting. & goto :pause )

rem ====================================
rem make the directory to be distributed
rem ====================================

rmdir/s/q .\psycle\
mkdir .\psycle\

rem ------------------------------
rem copy executables and libraries
rem ------------------------------

xcopy/f .\release.bin.upx.nrv2d\psycle.exe .\psycle\ || ( echo copy failed, aborting. & goto :pause )

rem mkdir .\psycle\plugins\
rem xcopy/f .\release.bin\psycle__plugins\*.dll .\psycle\plugins\ || ( echo copy failed, aborting. & goto :pause )

rem ------------------------------------------
rem copy microsoft c/c++/mfc runtime libraries
rem ------------------------------------------

xcopy/f "%SYSTEMROOT%\system32\msvcr71.dll" .\psycle\ || ( echo copy failed, aborting. & goto :pause )
xcopy/f "%SYSTEMROOT%\system32\msvcp71.dll" .\psycle\ || ( echo copy failed, aborting. & goto :pause )
xcopy/f "%SYSTEMROOT%\system32\mfc71.dll" .\psycle\ || ( echo copy failed, aborting. & goto :pause )

rem ---------------------------
rem copy end-user documentation
rem ---------------------------

mkdir .\psycle\doc\
xcopy/f/s ..\..\doc\for-end-users\* .\psycle\doc\ || ( echo copy failed, aborting. & goto :pause )

rem ----------------
rem remove cvs files
rem ----------------

for /r .\psycle\ %%i in (CVS) do rmdir/s/q "%%i"
for /r .\psycle\ %%i in (.cvsignore) do del/q "%%i"

rem ----------------------------------------------------------------------------------
rem convert text files to microsoft end-of-lines (unix2dos is distributed with cygwin)
rem ----------------------------------------------------------------------------------
for /r .\psycle\ %%i in (*.txt *.text) do unix2dos "%%i"

rem ================
rem make the archive
rem ================

del/q .\psycle.bin.rar
rar a -s -m5 -md4096 -ep1 -r0 .\psycle.bin.rar .\psycle 1>> .\release.log 2>&1 || ( echo rar failed, aborting. & goto :pause )

rem =====================================================================================
rem upload the archive and update the site (scp and ssh are cygwin commands, use / not \)
rem =====================================================================================

set user=johan-boule

scp ./psycle.bin.rar %user%@shell.sourceforge.net:psycle/htdocs/ || ( echo scp failed, aborting. && goto :pause )
ssh %user%@shell.sourceforge.net psycle/htdocs.update.bash || ( echo ssh failed, aborting. && goto :pause )

rem ================================
rem pause and remove temporary files
rem ================================

:pause
pause
rmdir/s/q .\psycle\
del/q .\psycle.bin.rar
