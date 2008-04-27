isEmpty(platform_included) {
	platform_included = 1
	verbose: message("platform included")

	unix: include(platform-unix.pri)
	else: win32: include(platform-win32.pri)
}
