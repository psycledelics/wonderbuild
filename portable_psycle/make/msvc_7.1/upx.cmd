for %%r in (.\release .\release_intel_pentium_4) do (
	for %%t in (nrv2b nrv2d) do (
		rmdir/s/q %%r.bin.upx.%%t\
		mkdir %%r.bin.upx.%%t\
		set r=%%r
		for /r %r%\bin %%i in (*.exe *.dll) do (
			call :upx %%r %%t "%%i" || ( echo upx failed, aborting. && goto :pause )
		)
	)
)
goto :eof

:upx
upx.exe --overlay=strip --force --strip-relocs=1 --compress-icons=1 --best --crp-ms=999999 --%2 --no-backup -o %1.bin.upx.%2\%~n3%~x3 %3
goto :eof

:pause
pause
goto :eof
