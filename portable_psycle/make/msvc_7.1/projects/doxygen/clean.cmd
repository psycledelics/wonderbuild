%~d0
cd %~p0

pushd ..\..\..\doxygen\ && (
	clean || exit 1
	popd
)
