@echo off


rem ================================================================================================
rem Sometimes this does not work. remove the rem from the following line in that case. (file locked)
rem goto :eof
rem ================================================================================================



%~d0
cd %~p0

set output=..\..\output\%1

pushd %output% && (
	rem [bohan] delete the stamp file in any case, because the rest sometimes fails for unknown reasons
	del /q boost-*-stamp || exit /b 1
	popd
) && (
	if exist %output% (
		pushd %output% && (
			del /s/q boost_* || exit /b 1
			del /s/q libboost_* || exit /b 1
			popd
		)
	)
)
