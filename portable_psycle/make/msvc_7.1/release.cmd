@echo off

rem ====================================
rem creating temporary working directory
rem ====================================

	set work=%0.work
	if exist %work% rmdir/s/q %work%
	mkdir %work%
	pushd %work%
	echo %0: temporary working directory is %work%

rem ============
rem calling main
rem ============

	call :main && echo %0: all operations completed successfully.

rem ====================================================
echo %0: removing temporary working directory %work% ...
rem ====================================================

	popd
	echo %0: press any key to remove temporary working directory %work%, or break to keep it.
	pause
	rmdir/s/q %work%
	echo %0: removed temporary working directory %work%

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
	rem =======
	rem targets
	rem =======
	
		set targets=amd-k7-and-intel-pentium-3 intel-pentium-4
	
	rem ===============
	rem clean and build
	rem ===============
	
		echo %0: sourcing mircosoft visual studio 7.1 environement ...
			rem microsoft made a dumb script that keeps appending things to the env vars,
			rem so, when invoke many times, we ends up with "too long line", sic. they can rot in hell.
			rem so, we're saving the env to restore it after.
			call :save_env
			call "%VS71ComnTools%\VSVars32" || goto :failed
		
		for %%t in (%targets%) do (
			call :rebuild release.%%t || goto :failed
		)
		
		call :restore_env
	
	rem ===============================================
	echo %0: making the directory to be distributed ...
	rem ===============================================
	
		set timestamp=%date%.%time%
		set timestamp=%timestamp: =.%
		set timestamp=%timestamp:/=.%
		set timestamp=%timestamp:\=.%
		set timestamp=%timestamp::=.%
		set timestamp=%timestamp:-=.%
		
		set distribution=.\psycle.bin.timestamp-%timestamp%\
		
		mkdir "%distribution%"
		echo %0: directory %distribution% created
		
		rem ---------------------------------------
		echo %0: copying libraries and programs ...
		rem ---------------------------------------
		
			for %%t in (%targets%) do (
				call :copy_binaries %%t || goto :failed
			)
		
		rem ---------------------------------------
		echo %0: copying end-user documentation ...
		rem ---------------------------------------
		
			mkdir "%distribution%\doc\"
			xcopy/s ..\..\..\doc\for-end-users\* "%distribution%\doc\" || goto :failed
		
		rem ---------------------------------------------
		echo %0: removing cvs files from distribution ...
		rem ---------------------------------------------
		
			for /r "%distribution%" %%i in (CVS) do rmdir/s/q "%%i"
			for /r "%distribution%" %%i in (.cvsignore) do del/q "%%i"
		
		rem --------------------------------------------------------
		echo %0: converting text files to microsoft end-of-lines ...
		rem unix2dos is distributed with cygwin
		rem --------------------------------------------------------
		
			for /r "%distribution%" %%i in (*.txt *.text) do unix2dos "%%i"
		
	rem ===========================
	echo %0: making the archive ...
	rem ===========================
		
		rar a -s -m5 -md4096 -ep1 -r0 .\psycle.bin.rar "%distribution%" 1>> .\psycle.bin.rar.log 2>&1 || goto :failed
	
	rem =================================================
	rem uploading the archive and updating the site
	rem scp and ssh are cygwin/unix commands, use / not \
	rem =================================================
	
		rem ------------------------------------------------------------------------
		echo %0: maping local user account name to sourceforge user account name ...
		rem ------------------------------------------------------------------------
		
			if "%USERNAME%" == "bohan" (
				set sourceforge_user_account=johan-boule
			) else if "%USERNAME%" == "x" (
				rem in the meanwhile alk fixes his account, he uses bohan's.
				rem set sourceforge_user_account=alkenstein
				set sourceforge_user_account=johan-boule
			) else (
				set sourceforge_user_account=%USERNAME%
			)
			
			echo %0: sourceforge user account: %sourceforge_user_account%
		
		rem ------------------------------
		rem sourceforge group account
		rem ------------------------------

			set sourceforge_group_account=/home/groups/p/ps/psycle/
			echo %0: sourceforge group account: %sourceforge_group_account%
		
		rem ---------------------------------------------
		echo %0: uploading the archive to sourceforge ...
		rem ---------------------------------------------
		
			scp ./psycle.bin.rar "%sourceforge_user_account%@shell.sourceforge.net:%sourceforge_group_account%/htdocs/" || goto :failed
		
		rem ------------------------------------------
		echo %0: updating the sourceforge ht pages ...
		rem ------------------------------------------
		
			ssh "%sourceforge_user_account%@shell.sourceforge.net" "%sourceforge_group_account%/htdocs.update.bash" || goto :failed
goto :eof

rem ---------------
rem upx sub routine
rem ---------------
:upx
	upx.exe --overlay=strip --force --strip-relocs=1 --compress-icons=1 --best --crp-ms=999999 --nrv2d --no-backup -o %~p1%~n1.upx%~x1 %1
goto :eof

rem --------------------
rem save env sub routine
rem --------------------
:save_env
	set old_path=%PATH%
	set old_include=%INCLUDE%
	set old_lib=%LIB%
goto :eof

rem -----------------------
rem restore env sub routine
rem -----------------------
:restore_env
	set PATH=%old_path%
	set INCLUDE=%old_include%
	set LIB=%old_lib%
goto :eof

rem -------------------------------------
rem rebuild (clean and build) sub routine
rem -------------------------------------
:rebuild
	set configuration=%1
	rem for %%o in (clean build) do (
	for %%o in (build) do (
		echo %0: %%oing %configuration% ...
		DevEnv ..\solution.sln /%%o %configuration% /out %configuration%.%%o.log || ( call :restore_path && goto :failed )
	)
goto :eof

rem -------------
rem copy binaries
rem -------------
:copy_binaries
	set target=%1
	echo %0: copying %target% ...
	set source=..\release.%target%\bin\
	set destination=%distribution%\%target%\
	rem <bohan> well i think microsoft's documentation about microsoft's xcopy is wrong.
	rem <bohan> xcopy/f <-- shows what files are being copied.
	rem <bohan> it turns out it also does something else, like allowing copy of files whose name ends with ".exe".
	echo %0: copying built libraries and programs ...
	xcopy/f/i "%source%\*.exe" "%destination%" || goto :failed
	xcopy/i "%source%\psycle.plugins\*.dll" "%destination%\plugins\" || goto :failed
	echo %0: copying microsoft c/c++/gdi+/mfc runtime libraries ...
	xcopy "%SYSTEMROOT%\system32\msvcr71.dll" "%destination%" || goto :failed
	xcopy "%SYSTEMROOT%\system32\msvcp71.dll" "%destination%" || goto :failed
	xcopy "%SYSTEMROOT%\system32\mfc71.dll" "%destination%" || goto :failed
	rem xcopy/f/i "%SYSTEMROOT%\WinSxS\x86_Microsoft.Windows.GdiPlus_*_1.0.10.0_*\GDIPlus.dll" "%destination%" || goto :failed
	xcopy "%SYSTEMROOT%\WinSxS\x86_Microsoft.Windows.GdiPlus_6595b64144ccf1df_1.0.10.0_x-ww_712befd8\GDIPlus.dll" "%destination%" || goto :failed
goto :eof

rem ------
rem failed
rem ------
:failed
	set return_code=%ERRORLEVEL%
	echo %0: failed with return code: %return_code%
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
		echo %0: failed with return code: %return_code%
		if "%return_code%" == "0" (
			exit /b 1
		) else (
			exit /b %return_code%
		)
	) else (
		goto :eof
	)
