@echo off

%~d0
cd %~p0

pushd ..\..\..\..\include\ && (
	if not exist boost (
		boost-1.33.1 -y || exit /b 1
	)
	popd
) && (
	if not exist ..\..\output\boost_stamp (
		pushd ..\..\ && (
			output.boost -y || exit /b 1
			echo boost extracted > output\boost_stamp || exit /b 1
			popd
		)
	)
)
