pushd ..\..\..\..\include\ && (
	del/s/q boost
	call :prune boost
	rmdir boost
	popd
)

goto :eof

rem ============================================
rem safely recursively removes empty directories
rem ============================================
:prune
for /d %%i in (%1\*) do (
	call :prune "%%i"
	rmdir "%%i"
)
goto :eof
