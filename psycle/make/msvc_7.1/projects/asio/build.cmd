@echo off

%~d0
cd %~p0

pushd ..\..\..\..\include\ && (
	if not exist asio (
		asio-2.1 -y || exit /b 1
	)
	popd
)
