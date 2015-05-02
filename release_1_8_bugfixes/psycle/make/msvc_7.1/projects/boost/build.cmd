pushd ..\..\..\..\include\ && (
	if not exist boost (
		boost -y
	)
	popd
) && (
	if not exist ..\..\output\boost_stamp (
		pushd ..\..\ && (
			output.boost -y
			echo boost extracted > output\boost_stamp
		)
	)
)
