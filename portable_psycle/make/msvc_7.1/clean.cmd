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
del/s/q "*.dll"
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
