rem ===================================
rem cleans all compiler-generated files
rem ===================================

del/s/q "*.pch"
del/s/q "*.obj"
del/s/q "*.res"
del/s/q "*.aps"
del/s/q "..\..\src\*.aps"
del/s/q "*.idb"
del/s/q "*.pdb"
del/s/q "*.ilk"
del/s/q "*.sbr"
del/s/q "*.bsc"
del/s/q "*.lib"
del/s/q "*.exp"

rename .\release.g7\lib\boost_thread.lib boost_thread.lib.preserve
rename .\release.g6\lib\boost_thread.lib boost_thread.lib.preserve
rename .\debug\lib\boost_threadd.lib boost_threadd.lib.preserve
del/s/q "*.lib"
del/s/q/ar "*.lib"
rename .\release.g7\lib\boost_thread.lib.preserve boost_thread.lib
rename .\release.g6\lib\boost_thread.lib.preserve boost_thread.lib
rename .\debug\lib\boost_threadd.lib.preserve boost_threadd.lib

rename .\release.g7\bin\boost_thread.dll boost_thread.dll.preserve
rename .\release.g6\bin\boost_thread.dll boost_thread.dll.preserve
rename .\debug\bin\boost_threadd.dll boost_threadd.dll.preserve
del/s/q "*.dll"
del/s/q/ar "*.dll"
rename .\release.g7\bin\boost_thread.dll.preserve boost_thread.dll
rename .\release.g6\bin\boost_thread.dll.preserve boost_thread.dll
rename .\debug\bin\boost_threadd.dll.preserve boost_threadd.dll

del/s/q "*.exe"
del/s/q "*.opt"
del/s/q "*.ncb"
del/s/q/ah "*.suo"
del/s/q "*.log"
del/s/q "BuildLog.htm*"

rem =================================
rem cleans all psycle-generated files
rem =================================

del/s/q plugin-scan*
del/s/q output.log.txt

rem ===========================================
rem safely recursively removes empty directories
rem ===========================================

call :prune .
goto :eof
:prune
for /d %%i in (%1\*) do (
	call :prune "%%i"
	rmdir "%%i"
)
