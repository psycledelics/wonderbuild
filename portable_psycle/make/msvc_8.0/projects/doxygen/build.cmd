%~d0
cd %~p0

pushd ..\..\..\doxygen\ && (
	build || exit /b 1
	popd
)
