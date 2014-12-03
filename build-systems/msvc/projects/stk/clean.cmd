@echo off

%~d0
cd %~p0

SETLOCAL

set pkgdir=..\..\..\..\external-packages\stk-%1

pushd %pkgdir% || exit /b 1
  if exist stk (
    rmdir /S /Q stk || exit /b 1
  )
popd || exit /b 1

ENDLOCAL
