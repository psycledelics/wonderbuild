pushd ..\..\..\..\include\ && (
	if exist boost (
		rem [bohan] i don't know why sometimes it fails
		rmdir/s/q boost || exit 1
		rem [bohan] i don't know why sometimes it doesn't report the failure
		if exist boost exit 1
	)
	popd
)
