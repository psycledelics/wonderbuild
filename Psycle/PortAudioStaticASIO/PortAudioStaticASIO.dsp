# Microsoft Developer Studio Project File - Name="PortAudioStaticASIO" - Package Owner=<4>
# Microsoft Developer Studio Generated Build File, Format Version 6.00
# ** DO NOT EDIT **

# TARGTYPE "Win32 (x86) Static Library" 0x0104

CFG=PortAudioStaticASIO - Win32 Debug
!MESSAGE This is not a valid makefile. To build this project using NMAKE,
!MESSAGE use the Export Makefile command and run
!MESSAGE 
!MESSAGE NMAKE /f "PortAudioStaticASIO.mak".
!MESSAGE 
!MESSAGE You can specify a configuration when running NMAKE
!MESSAGE by defining the macro CFG on the command line. For example:
!MESSAGE 
!MESSAGE NMAKE /f "PortAudioStaticASIO.mak" CFG="PortAudioStaticASIO - Win32 Debug"
!MESSAGE 
!MESSAGE Possible choices for configuration are:
!MESSAGE 
!MESSAGE "PortAudioStaticASIO - Win32 Debug" (based on "Win32 (x86) Static Library")
!MESSAGE "PortAudioStaticASIO - Win32 Release" (based on "Win32 (x86) Static Library")
!MESSAGE "PortAudioStaticASIO - Win32 Release Cyrix" (based on "Win32 (x86) Static Library")
!MESSAGE 

# Begin Project
# PROP AllowPerConfigDependencies 0
# PROP Scc_ProjName ""
# PROP Scc_LocalPath ""
CPP=cl.exe
MTL=midl.exe
RSC=rc.exe

!IF  "$(CFG)" == "PortAudioStaticASIO - Win32 Debug"

# PROP BASE Use_MFC 0
# PROP BASE Use_Debug_Libraries 1
# PROP BASE Output_Dir ".\Debug"
# PROP BASE Intermediate_Dir ".\Debug"
# PROP BASE Target_Dir ""
# PROP Use_MFC 0
# PROP Use_Debug_Libraries 1
# PROP Output_Dir ".\Debug"
# PROP Intermediate_Dir ".\Debug"
# PROP Target_Dir ""
# ADD BASE CPP /nologo /MDd /I "..\..\asiosdk2\host\pc" /I "..\..\asiosdk2\host" /I "..\..\asiosdk2\common" /I "..\..\portaudio_v18\pa_common" /ZI /W3 /Od /Ot /D "WIN32" /D "_DEBUG" /D "_LIB" /D "_MBCS" /YX /GZ /c /GX 
# ADD CPP /nologo /MDd /I "..\..\asiosdk2\host\pc" /I "..\..\asiosdk2\host" /I "..\..\asiosdk2\common" /I "..\..\portaudio_v18\pa_common" /ZI /W3 /Od /Ot /D "WIN32" /D "_DEBUG" /D "_LIB" /D "_MBCS" /YX /GZ /c /GX 
# ADD BASE MTL /nologo /win32 
# ADD MTL /nologo /win32 
# ADD BASE RSC /l 1033 /d "_DEBUG" 
# ADD RSC /l 1033 /d "_DEBUG" 
BSC32=bscmake.exe
# ADD BASE BSC32 /nologo 
# ADD BSC32 /nologo 
LIB32=link.exe -lib
# ADD BASE LIB32 /nologo /out:".\Debug\PortAudioStaticASIO.lib" 
# ADD LIB32 /nologo /out:".\Debug\PortAudioStaticASIO.lib" 

!ELSEIF  "$(CFG)" == "PortAudioStaticASIO - Win32 Release"

# PROP BASE Use_MFC 0
# PROP BASE Use_Debug_Libraries 0
# PROP BASE Output_Dir ".\Release"
# PROP BASE Intermediate_Dir ".\Release"
# PROP BASE Target_Dir ""
# PROP Use_MFC 0
# PROP Use_Debug_Libraries 0
# PROP Output_Dir ".\Release"
# PROP Intermediate_Dir ".\Release"
# PROP Target_Dir ""
# ADD BASE CPP /nologo /MT /I "..\..\asiosdk2\host\pc" /I "..\..\asiosdk2\host" /I "..\..\asiosdk2\common" /I "..\..\portaudio_v18\pa_common" /W3 /O2 /Ob2 /Ot /G6 /D "WIN32" /D "NDEBUG" /D "_LIB" /D "_MBCS" /GF /Gy /YX /c /GX 
# ADD CPP /nologo /MT /I "..\..\asiosdk2\host\pc" /I "..\..\asiosdk2\host" /I "..\..\asiosdk2\common" /I "..\..\portaudio_v18\pa_common" /W3 /O2 /Ob2 /Ot /G6 /D "WIN32" /D "NDEBUG" /D "_LIB" /D "_MBCS" /GF /Gy /YX /c /GX 
# ADD BASE MTL /nologo /win32 
# ADD MTL /nologo /win32 
# ADD BASE RSC /l 1033 /d "NDEBUG" 
# ADD RSC /l 1033 /d "NDEBUG" 
BSC32=bscmake.exe
# ADD BASE BSC32 /nologo 
# ADD BSC32 /nologo 
LIB32=link.exe -lib
# ADD BASE LIB32 /nologo /out:".\Release\PortAudioStaticASIO.lib" 
# ADD LIB32 /nologo /out:".\Release\PortAudioStaticASIO.lib" 

!ELSEIF  "$(CFG)" == "PortAudioStaticASIO - Win32 Release Cyrix"

# PROP BASE Use_MFC 0
# PROP BASE Use_Debug_Libraries 0
# PROP BASE Output_Dir ".\Release Cyrix"
# PROP BASE Intermediate_Dir ".\Release Cyrix"
# PROP BASE Target_Dir ""
# PROP Use_MFC 0
# PROP Use_Debug_Libraries 0
# PROP Output_Dir ".\Release Cyrix"
# PROP Intermediate_Dir ".\Release Cyrix"
# PROP Target_Dir ""
# ADD BASE CPP /nologo /MT /I "..\..\asiosdk2\host\pc" /I "..\..\asiosdk2\host" /I "..\..\asiosdk2\common" /I "..\..\portaudio_v18\pa_common" /W3 /Ob2 /D "WIN32" /D "NDEBUG" /D "_LIB" /D "_CYRIX_PROCESSOR_" /D "_MBCS" /GF /Gy /c /GX 
# ADD CPP /nologo /MT /I "..\..\asiosdk2\host\pc" /I "..\..\asiosdk2\host" /I "..\..\asiosdk2\common" /I "..\..\portaudio_v18\pa_common" /W3 /Ob2 /D "WIN32" /D "NDEBUG" /D "_LIB" /D "_CYRIX_PROCESSOR_" /D "_MBCS" /GF /Gy /c /GX 
# ADD BASE MTL /nologo /win32 
# ADD MTL /nologo /win32 
# ADD BASE RSC /l 1033 
# ADD RSC /l 1033 
BSC32=bscmake.exe
# ADD BASE BSC32 /nologo 
# ADD BSC32 /nologo 
LIB32=link.exe -lib
# ADD BASE LIB32 /nologo /out:".\Release Cyrix\PortAudioStaticASIO.lib" 
# ADD LIB32 /nologo /out:".\Release Cyrix\PortAudioStaticASIO.lib" 

!ENDIF

# Begin Target

# Name "PortAudioStaticASIO - Win32 Debug"
# Name "PortAudioStaticASIO - Win32 Release"
# Name "PortAudioStaticASIO - Win32 Release Cyrix"
# Begin Group "ASIO SDK Files"

# PROP Default_Filter ""
# Begin Source File

SOURCE=..\..\asiosdk2\common\asio.cpp
# End Source File
# Begin Source File

SOURCE=..\..\asiosdk2\host\asiodrivers.cpp
# End Source File
# Begin Source File

SOURCE=..\..\asiosdk2\host\pc\asiolist.cpp
# End Source File
# End Group
# Begin Group "PortAudio SDK Files"

# PROP Default_Filter ""
# Begin Source File

SOURCE=..\..\portaudio_v18\pa_asio\pa_asio.cpp
# End Source File
# Begin Source File

SOURCE=..\..\portaudio_v18\pa_common\pa_host.h
# End Source File
# Begin Source File

SOURCE=..\..\portaudio_v18\pa_common\pa_lib.c
# End Source File
# Begin Source File

SOURCE=..\..\portaudio_v18\pa_common\portaudio.h
# End Source File
# End Group
# End Target
# End Project

