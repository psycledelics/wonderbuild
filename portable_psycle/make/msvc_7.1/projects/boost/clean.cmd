pushd ..\..\..\..\include\ && (
	if exist boost (
		rmdir/s/q boost
	)
	popd
)
