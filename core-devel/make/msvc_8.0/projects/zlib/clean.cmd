@echo off


rem ================================================================================================
rem disabled because there's no way to make it work on windows.. file and or dirs seems to be locked
goto :eof
rem ================================================================================================



%~d0
cd %~p0

pushd ..\..\output && (
	rem [bohan] delete the stamp file in any case, because the rest sometimes fails for unknown reasons
	del/q zlib_stamp || exit /b 1
	popd
) && (
	if exist ..\..\output (
		pushd ..\..\output && (
			del/s/q zlib_stamp || exit /b 1
			del/s/q zlib.lib || exit /b 1
			del/s/q zlib1.dll || exit /b 1
			popd
		)
	)
) && (
	pushd ..\..\..\..\include\ && (
		if exist zlib.h (
			del/s/q zlib.h || exit /b 1
		)
		if exist zconf.h (
			del/s/q zconf.h || exit /b 1
		)
		popd
	)
)
