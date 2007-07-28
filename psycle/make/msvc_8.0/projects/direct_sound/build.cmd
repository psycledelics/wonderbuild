@echo off

%~d0
cd %~p0

if not exist ..\..\output\direct_sound_stamp (
	pushd ..\..\ && (
		output.direct_sound -y || exit /b 1
		echo direct_sound extracted > output\direct_sound_stamp || exit /b 1
		popd
	)
)
