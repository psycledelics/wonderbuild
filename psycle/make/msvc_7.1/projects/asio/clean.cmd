@echo off


rem ================================================================================================
rem disabled because there's no way to make it work on windows.. file and or dirs seems to be locked
goto :eof
rem ================================================================================================



%~d0
cd %~p0

pushd ..\..\..\..\include\ && (
	if exist asio (
		rem [bohan] i don't know why sometimes it fails
		rem [bohan] it seems we need to do it 5 times ...
		rmdir/s/q asio || exit /b 1
		rem [bohan] i don't know why sometimes it doesn't report the failure
		if exist asio exit /b 1
	)
	popd
)
