@echo off

rem ###########################################################################
rem #
rem # This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
rem # copyright 2004-2007 psycledelics http://psycle.pastnotecut.org : johan boule
rem #
rem # Startup script for the eclipse workbench
rem #
rem ###########################################################################

pushd %~dp0 || goto :failed

call libexec\settings || goto :failed

if not exist working-dir\source-packages (
	call libexec\download-source-package http://psycle.sourceforge.net/packages/standard-source-tarball universalis || goto :failed
)

echo %~n0: Workspace resource preferences, 'packageneric' path variable ... || goto :failed
rem (
	set settings=working-dir\eclipse.workspace\.metadata\.plugins\org.eclipse.core.runtime\.settings
	rem sh -c "mkdir --parents $(echo '%settings%' | sed 's:\\:/:g')" || goto :failed
	sh -c 'mkdir --parents working-dir/eclipse.workspace/.metadata/.plugins/org.eclipse.core.runtime/.settings' || goto :failed
	set prefs=%settings%\org.eclipse.core.resources.prefs
	set settings=
	sh -c 'echo \#$(date)' > %prefs% || goto :failed
	echo pathvariable.packageneric=%CD%/working-dir/source-packages| sed 's:\\:/:g' | sed 's/:/\\\:/' >> %prefs% || goto :failed
	sh -c 'echo eclipse.preferences.version=1' >> %prefs% || goto :failed
	sh -c 'echo encoding=US-ASCII' >> %prefs% || goto :failed
	sh -c 'echo description.autobuilding=false' >> %prefs% || goto :failed
	set prefs=
rem )

echo %~n0: Project cdt include paths ... || goto :failed
rem (
	sh --login -c "for package in $(find $(pwd)/working-dir/source-packages -mindepth 1 -maxdepth 1 -follow -type d ! -name .) ; do cd $package && if test -f .cdtproject ; then /dev-pack/libexec/eclipse.cdt.update-include-paths || { failed=true ; break ; } fi ; done && test \"$failed\" != true" || goto :failed
rem )

echo %~n0: Starting eclipse ... || goto :failed
rem (
	set eclipse__parameters=-data working-dir/eclipse.workspace -showlocation -vmargs -Xmx256M || goto :failed
	echo eclipse %eclipse__parameters% || goto :failed
	start eclipse.exe %eclipse__parameters% || goto :failed
rem )

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
