%~d0
cd %~p0

pushd ..\..\..\doxygen\ && (
	build || exit 1
	popd
)
