pushd ..\..\..\..\include\ && (
	if not exist boost (
		boost-1.33.1 -y
	)
	popd
) && (
	if not exist ..\..\output\boost_stamp (
		pushd ..\..\ && (
			output.boost.exe -y
			echo boost extracted > output\boost_stamp
		)
	)
)
