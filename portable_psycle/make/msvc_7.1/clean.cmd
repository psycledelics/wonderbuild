rem ===================================
rem cleans all compiler-generated files
rem ===================================

del/s/q "*.pch" || goto :failed
del/s/q "*.obj" || goto :failed
del/s/q "*.res" || goto :failed
del/s/q "*.aps" || goto :failed
del/s/q "..\..\src\*.aps" || goto :failed
del/s/q "*.idb" || goto :failed
del/s/q "*.ilk" || goto :failed
del/s/q "*.sbr" || goto :failed
del/s/q "*.bsc" || goto :failed
del/s/q "*.exp" || goto :failed

rename .\release.g7\lib\boost_thread.lib boost_thread.lib.preserve || goto :failed
rename .\release.g6\lib\boost_thread.lib boost_thread.lib.preserve || goto :failed
rename .\debug\lib\boost_threadd.lib boost_threadd.lib.preserve || goto :failed
del/s/q "*.lib" || goto :failed
del/s/q/ar "*.lib" || goto :failed
rename .\release.g7\lib\boost_thread.lib.preserve boost_thread.lib || goto :failed
rename .\release.g6\lib\boost_thread.lib.preserve boost_thread.lib || goto :failed
rename .\debug\lib\boost_threadd.lib.preserve boost_threadd.lib || goto :failed

rename .\release.g7\bin\boost_thread.dll boost_thread.dll.preserve || goto :failed
rename .\release.g6\bin\boost_thread.dll boost_thread.dll.preserve || goto :failed
rename .\debug\bin\boost_threadd.dll boost_threadd.dll.preserve || goto :failed
del/s/q "*.dll" || goto :failed
del/s/q/ar "*.dll" || goto :failed
rename .\release.g7\bin\boost_thread.dll.preserve boost_thread.dll || goto :failed
rename .\release.g6\bin\boost_thread.dll.preserve boost_thread.dll || goto :failed
rename .\debug\bin\boost_threadd.dll.preserve boost_threadd.dll || goto :failed

del/s/q "*.pdb" || goto :failed
del/s/q "*.exe" || goto :failed
del/s/q "*.opt" || goto :failed
del/s/q "*.ncb" || goto :failed
del/s/q/ah "*.suo" || goto :failed
del/s/q "*.log" || goto :failed
del/s/q "BuildLog.htm*" || goto :failed

rem =================================
rem cleans all psycle-generated files
rem =================================

del/s/q plugin-scan* || goto :failed
del/s/q output.log.txt || goto :failed

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
goto :eof

:failed
echo %~n0 failed.
pause
