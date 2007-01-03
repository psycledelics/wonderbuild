@echo off

rem ###########################################################################
rem #
rem # This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
rem # copyright 2004-2007 psycledelics http://psycle.pastnotecut.org : johan boule
rem #
rem # Download script for source packages
rem #
rem ###########################################################################

pushd %~dp0.. || goto :failed

call libexec\settings || goto :failed

set remote__url=%1
set package=%2

sh -c /dev-pack/libexec/automate

if not exist working-dir (
	mkdir working-dir || goto :failed
)

pushd working-dir || goto :failed

if not exist source-packages (
	mkdir source-packages || goto :failed
)

rem (
	rem microsoft's state of the art script engine has no late evaluation by default... don't put that inside parenthesis.
	set stamp=%date%.%time%
	set stamp=%stamp: =.%
	set stamp=%stamp:/=.%
	set stamp=%stamp:\=.%
	set stamp=%stamp::=.%
	set stamp=%stamp:-=.%
	set stamp=%stamp%
	set tarball=%TMP%\%~n0.%package%.%stamp%
	echo %~n0: Downloading %remote__url%/%package%.tar.gz to temporary %tarball% ... || goto :failed
	rm --force --recursive %tarball% || goto :failed
	mkdir %tarball% || goto :failed
	pushd %tarball% || goto :failed
		wget %remote__url%/%package%.tar.gz || goto :failed
	popd || goto :failed
rem )

echo %~n0: Checking GPG signature %tarball%/%package%.tar.gz.sig || goto :failed
rem (
	pushd %tarball% || goto :failed
		wget --non-verbose %remote__url%/%package%.tar.gz.sig || goto :failed
		gpgv --homedir %~dp0..\.gnupg %package%.tar.gz.sig || goto :failed
	popd || goto :failed
rem )

echo %~n0: Unpacking %tarball%/%package%.tar.gz in temporary %tarball% || goto :failed
rem (
	pushd %tarball% || goto :failed
		tar --extract --touch --gzip < %package%.tar.gz || goto :failed
	popd || goto :failed
rem )

echo %~n0: Making a backup of the source package directory working-dir/source-packages/%package% ... || goto :failed
rem (
	rem microsoft's state of the art script engine has no late evaluation by default... don't put that inside parenthesis.
	set stamp=%date%.%time%
	set stamp=%stamp: =.%
	set stamp=%stamp:/=.%
	set stamp=%stamp:\=.%
	set stamp=%stamp::=.%
	set stamp=%stamp:-=.%
	set stamp=timestamp-%stamp%
	if exist source-packages\%package% (
		mv source-packages/%package% source-packages/.~%package%~backup~%stamp%~ || (
			echo %~n0: renaming failed. Maybe the directory %CD%/%package% is opened by some process.
			goto :failed
		)
	)
rem )

echo %~n0: Moving %tarball%/%package%-*.*.* to working-dir/source-packages/%package% || goto :failed
rem (
	mv %tarball%/%package%-*.*.* source-packages/%package% 2>nul || (
		rem argh :-( ... copy instead of moving because of problem accross different filesystems (if %TMP% is on a different filesystem)
		cp --recursive %tarball%/%package%-*.*.* source-packages/%package% || goto :failed
	)
	start explorer source-packages\%package%
rem )

echo %~n0: Removing temporary %tarball% || goto :failed
rem (
	rm --force --recursive %tarball% || goto :failed
rem )

echo %~n0: Updating eclipse.workspace with %package%/eclipse/workspace ... || goto :failed
rem (
	if exist source-packages\%package%\eclipse\workspace (
		if not exist eclipse.workspace (
			mkdir eclipse.workspace || goto :failed
		)
		pushd source-packages\%package%\eclipse\workspace || goto :failed
			find . -type f -exec cp --force {} ../../../../eclipse.workspace/{} \; || goto :failed
		popd || goto :failed
	)
rem )

echo %~n0: Configuring %package% ... || goto :failed
(
	pushd source-packages\%package% || goto :failed
		rem fixes for differing verions of autotools
		rem (
			rem just bootstrap everything and we'll be sure
			sh -c "cd $(pwd) && ./autotools-bootstrap" || goto :failed
		rem )
		sh -c "echo" || goto :failed
		sh -c "cd $(pwd) && ./configure.wrapper --with-gui" || goto :failed
	popd || goto :failed
)

rem pop from working-dir
popd || goto :failed
 
echo %~n0: Completed sucessfully.

popd || goto :failed
goto :eof

rem ------
rem failed
rem ------
:failed
	set return_code=%ErrorLevel%
	echo %~n0: Failed with return code: %return_code%
	pause
	set failed=true
	if "%return_code%" == "0" (
		exit /b 1
	) else (
		exit /b %return_code%
	)
