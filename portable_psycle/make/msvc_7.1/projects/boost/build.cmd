pushd ..\..\..\..\include\ && (
	if not exist boost (
		boost -y
	)
	popd
) && (
	pushd ..\..\ && (
		output.boost.exe -y
	)
)
