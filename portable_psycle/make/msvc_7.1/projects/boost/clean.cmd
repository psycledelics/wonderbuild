pushd ..\..\..\..\include\ && (
	if exist boost (
		rmdir/s/q boost
		rem [bohan] i don't know why sometimes it fails
		if exist boost (
			rmdir/s/q boost
			if exist boost (
				rmdir/s/q boost
				if exist boost (
					rmdir/s/q boost
					if exist boost (
						rmdir/s/q boost
						if exist boost (
							rmdir/s/q boost
							if exist boost (
								rmdir/s/q boost
							)
						)
					)
				)
			)
		)
	)
	popd
)
