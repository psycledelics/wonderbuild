rem ===================================
rem cleans all compiler-generated files
rem ===================================

del/s/q "*.pch"
del/s/q "*.obj"
del/s/q "*.res"
del/s/q "*.aps"
del/s/q "*.idb"
del/s/q "*.pdb"
del/s/q "*.ilk"
del/s/q "*.sbr"
del/s/q "*.bsc"
del/s/q "*.lib"
del/s/q "*.exp"

rename .\release\bin\unicows.dll unicows.dll.preserve
rename .\debug\bin\unicows.dll unicows.dll.preserve
del/s/q "*.dll"
del/s/q/ar "*.dll"
rename .\release\bin\unicows.dll.preserve unicows.dll
rename .\debug\bin\unicows.dll.preserve unicows.dll

del/s/q "*.exe"
del/s/q "*.opt"
del/s/q "*.ncb"
del/s/q/ah "*.suo"
del/s/q "*.log"
del/s/q "BuildLog.htm*"

rem =================================
rem cleans all psycle-generated files
rem =================================

del/s/q cache.map
del/s/q pluginlog.txt

rem ===========================================
rem safely recursively remove empty directories
rem ===========================================

call :prune .
goto :eof
:prune
for /d %%i in (%1\*) do (
	call :prune "%%i"
	rmdir "%%i"
)
