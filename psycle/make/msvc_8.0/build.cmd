%~d0
cd %~p0
call "%VS80ComnTools%\VSVars32"
vcbuild solution.sln "%1|Win32"
