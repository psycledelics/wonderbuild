pushd ..\..\..\..\include\ && (
	if exist boost (
		rem [bohan] i don't know why sometimes it fails
		rem [bohan] it seems we need to do it 5 times ...
		rmdir/s/q boost || exit 1
		rem [bohan] i don't know why sometimes it doesn't report the failure
		if exist boost exit 1
	)
	popd
) && (
	if exist ..\..\output (
		pushd ..\..\output && (
			del/s/q boost_*
			popd
		)
	)
)
