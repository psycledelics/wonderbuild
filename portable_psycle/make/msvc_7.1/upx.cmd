del /s /q "release\bin\*__upx*"
if "%1"=="clean" (
	goto :eof
) else (
	for /r release\bin %%i in (*.exe *.dll) do (
		rem call :upx nrv2b "%%i"
		call :upx nrv2d "%%i"
	)
)
goto :eof
:upx
upx.exe --overlay=strip --force --strip-relocs=1 --compress-icons=1 --best --crp-ms=999999 --%1 --no-backup -o %~p2%~n2__upx__%1%~x2 %2
rem -o %~p2%~n2__upx__%1%~x2
