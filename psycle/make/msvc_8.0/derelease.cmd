@echo off



rem ===================================================================================================
rem ===================================================================================================
rem ===================================================================================================
rem This script requires UNIX programs, such as distributed by cygwin.
rem It was technically impossible to use only microsoft's (non)standard tools ; they are too limited.
rem We should even rewrite this script in POSIX shell because cmd.exe's language is absolutely awfull.
rem ===================================================================================================
rem ===================================================================================================
rem ===================================================================================================



rem ====================================
rem creating temporary working directory
rem ====================================

	set work=%0.work
	if exist %work% rmdir/s/q %work%
	mkdir %work%
	pushd %work%
	echo %~n0: temporary working directory is %work%

rem ============
rem calling main
rem ============

	if exist ..\..\..\CVS\Tag (
		for /f %%i in (..\..\..\CVS\Tag) do (
			call :main %%i && echo %~n0: all operations completed successfully.
		)
	) else (
		call :main && echo %~n0: all operations completed successfully.
	)

rem ======================================================
echo %~n0: removing temporary working directory %work% ...
rem ======================================================

	popd
	echo %~n0: press any key to remove temporary working directory %work%, or break to keep it.
	pause
	rmdir/s/q %work%
	echo %~n0: removed temporary working directory %work%

rem ======================================
rem end of main flow, exiting or returning
rem ======================================
	
	goto :return



rem ===================================
rem sub routines, called via call :name
rem ===================================

rem ----------------
rem main sub routine
rem ----------------
:main

	rem ===
	rem tag
	rem ===

		set tag=%1
		if "%tag%" == "" (
			echo %~n0: tag: no tag
		) else (
			set tag=%tag:~1%
			echo %~n0: tag: %tag%
		)
		
	rem =================================================
	echo %~n0: making the directory to be distributed ...
	rem =================================================

		rem microsoft's state of the art script engine has no late evaluation by default ...  would need to use !stamp!
		set stamp=%date%.%time%
		set stamp=%stamp: =.%
		set stamp=%stamp:/=.%
		set stamp=%stamp:\=.%
		set stamp=%stamp::=.%
		set stamp=%stamp:-=.%
		set stamp=timestamp-%stamp%

		if "%tag%" == "" (
			rem microsoft's state of the art script engine has no late evalutation by default ... would need to use !tag!
		) else (
			set stamp=%tag%
		)
		
		set distribution=psycle.mfc.bin.%stamp%

		mkdir "%distribution%"
		echo %~n0: directory %distribution% created
	
		rem --------------------------------
		echo %~n0: writing sorry message ...
		rem --------------------------------
		
			echo %stamp% > %distribution%\README.txt || goto :failed
			echo. >> %distribution%\README.txt || goto :failed
			echo Sorry, alpha builds are currently too broken for distribution. >> %distribution%\README.txt || goto :failed
			echo You can use a stable build instead. >> %distribution%\README.txt || goto :failed
		
	rem =============================
	echo %~n0: making the archive ...
	rem =============================
		
		if "%tag%" == "" (
			set archive=psycle.mfc.bin.zip
		) else (
			set archive=psycle.mfc.bin.%tag%.zip
		)

		rem rar a -s -m5 -md4096 -r0 .\%archive% "%distribution%" 1>> %archive%.log 2>&1 || goto :failed
		rem 7za a -ms=on -mx=9 -m0=BCJ2 -m1=LZMA -m2=LZMA -m3=LZMA -mb0:1 -mb0s1:2 -mb0s2:3 %archive% "%distribution%" 1>> %archive%.log 2>&1 || goto :failed
		rem tar czf %archive% "%distribution%" || goto :failed
		zip -r %archive% "%distribution%" || goto :failed
	
	rem =================================================
	rem uploading the archive and updating the site
	rem scp and ssh are cygwin/unix commands, use / not \
	rem =================================================
	
		rem ---------------------------------------------------------------------------
		echo %~n0: mapping local user account name to sourceforge user account name ...
		rem ---------------------------------------------------------------------------
		
			if "%USERNAME%" == "JosepMa" (
				set sourceforge_user_account=jaz001
			) else if "%USERNAME%" == "Administrador" (
				set sourceforge_user_account=sampler
			) else if "%USERNAME%" == "bohan" (
				set sourceforge_user_account=johan-boule
			) else if "%USERNAME%" == "x" (
				set sourceforge_user_account=alkenstein
			) else (
				set sourceforge_user_account=%USERNAME%
			)
			
			echo %~n0: sourceforge user account: %sourceforge_user_account%
		
		rem -------------------------
		rem sourceforge group account
		rem -------------------------

			set sourceforge_group_account=/home/groups/p/ps/psycle/
			echo %~n0: sourceforge group account: %sourceforge_group_account%
		
		rem -----------------------------------------------
		echo %~n0: uploading the archive to sourceforge ...
		rem -----------------------------------------------
		
			scp %archive% "%sourceforge_user_account%@shell.sourceforge.net:%sourceforge_group_account%/htdocs/packages/microsoft/" || goto :failed
		
		rem ----------------------------------------
		echo %~n0: updating sourceforge ht pages ...
		rem ----------------------------------------
		
			ssh "%sourceforge_user_account%@shell.sourceforge.net" "%sourceforge_group_account%/htdocs/update-timestamps" || goto :failed
goto :eof

rem ------
rem failed
rem ------
:failed
	set return_code=%ErrorLevel%
	echo %~n0: failed with return code: %return_code%
	set failed=true
	if "%return_code%" == "0" (
		exit /b 1
	) else (
		exit /b %return_code%
	)

rem ------
rem return
rem ------
:return
	if "%failed%" == "true" (
		echo %~n0: failed with return code: %return_code%
		if "%return_code%" == "0" (
			exit /b 1
		) else (
			exit /b %return_code%
		)
	) else (
		goto :eof
	)
