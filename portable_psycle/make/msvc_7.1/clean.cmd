rem ===========================================
rem cleans all IDE and compiler generated files
rem ===========================================

rmdir/s/q output || goto failed

call projects\boost\clean.cmd
call projects\doxygen\clean.cmd

del/s/q "*.ncb" || goto :failed
del/s/q/ah "*.suo" || goto :failed

rem ============================================
rem safely recursively removes empty directories
rem ============================================

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
