call "%VS71ComnTools%\VSVars32"
DevEnv solution.sln /clean release /out clean.log || ( echo clean failed, aborting. & goto :pause )
rem del/q clean.log
DevEnv solution.sln /build release /out release.log || ( echo build failed, aborting. & goto :pause )

call upx || ( echo upx failed, aborting. & goto :pause )

rmdir/s/q .\psycle\
mkdir .\psycle\
xcopy .\release.bin.upx.nrv2d\psycle.exe .\psycle\ || ( echo copy failed, aborting. & goto :pause )
rem mkdir .\psycle\plugins\
rem xcopy .\release.bin\psycle__plugins\*.dll .\psycle\plugins\ || ( echo copy failed, aborting. & goto :pause )
mkdir .\psycle\doc\
xcopy/s ..\..\doc\for-end-users\* .\psycle\doc\ || ( echo copy failed, aborting. & goto :pause )
for /r .\psycle\doc\ %%i in (*.txt) do unix2dos "%%i"

del/q .\psycle.bin.rar
rar a -s -m5 -md4096 -ep1 -r0 .\psycle.bin.rar .\psycle 1>> .\release.log 2>&1 || ( echo rar failed, aborting. & goto :pause )

scp ./psycle.bin.rar johan-boule@shell.sourceforge.net:psycle/htdocs/ || ( echo scp failed, aborting. && goto :pause )
ssh johan-boule@shell.sourceforge.net psycle/htdocs.update.bash || ( echo ssh failed, aborting. && goto :pause )

:pause
pause
rmdir/s/q .\psycle\
del/q .\psycle.bin.rar
