%~d0
cd %~p0

pushd ..\..\..\doxygen\ && (
	clean || exit /b 1
	popd
)
