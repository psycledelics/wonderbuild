call "%VS71ComnTools%\VSVars32"
DevEnv solution.sln /clean release /out clean.log
rem del/s/q clean.log
DevEnv solution.sln /build release /out release.log
call upx
rar a -s -m5 -md4096 softsynth__release__bin.rar release\bin ..\..\doc\history.text 1>> release.log 2>&1
pause
