call "%VS71ComnTools%\VSVars32"
DevEnv solution.sln /clean release /out clean.log
rem del/s/q clean.log
DevEnv solution.sln /build release /out release.log
call upx
del/q .\psycle.bin.rar
rar a -s -m5 -md4096 -ep1 -r0 .\psycle.bin.rar .\release.bin.upx.nrv2b\*.exe .\release.bin.upx.nrv2b\*.dll ..\..\doc\for-end-users 1>> .\release.log 2>&1
scp ./psycle.bin.rar johan-boule@shell.sourceforge.net:~/psycle/htdocs/ || ( echo scp failed, continuing with next hosts... )
rem other hosts?
pause
rem del/q .\psycle.bin.rar
