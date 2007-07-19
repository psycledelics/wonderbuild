@echo off


rem ================================================================================================
rem disabled because there's no way to make it work on windows.. file and or dirs seems to be locked
goto :eof
rem ================================================================================================



%~d0
cd %~p0

pushd ..\..\output && (
	rem [bohan] delete the stamp file in any case, because the rest sometimes fails for unknown reasons
	del/q direct_sound_stamp || exit /b 1
	popd
) && (
	if exist ..\..\output (
		pushd ..\..\output && (
			del/s/q direct_sound_stamp || exit /b 1
			del/s/q dsound.lib || exit /b 1
			popd
		)
	)
) && (
	pushd ..\..\..\..\include\ && (
		if exist dsound.h (
			rem [bohan] i don't know why sometimes it fails
			rem [bohan] it seems we need to do it 5 times ...
			rmdir/s/q dsound.h || exit /b 1
			rem [bohan] i don't know why sometimes it doesn't report the failure
			if exist dsound.h exit /b 1
		)
		popd
	)
)
