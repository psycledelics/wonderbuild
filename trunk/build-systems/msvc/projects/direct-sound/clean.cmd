@echo off

%~d0
cd %~p0

set output=..\..\output\%1

pushd %output% && (
	rem [bohan] delete the stamp file in any case, because the rest sometimes fails for unknown reasons
	del /q %output%\direct-sound-stamp || exit /b 1
	popd
) && (
	if exist %output% (
		pushd %output% && (
			del /s/q dsound.lib || exit /b 1
			del /s/q dxguid.lib || exit /b 1
			popd
		)
	)
)
