# Microsoft Developer Studio Project File - Name="foo_psy" - Package Owner=<4>
# Microsoft Developer Studio Generated Build File, Format Version 6.00
# ** DO NOT EDIT **

# TARGTYPE "Win32 (x86) Dynamic-Link Library" 0x0102

CFG=foo_psy - Win32 Debug
!MESSAGE This is not a valid makefile. To build this project using NMAKE,
!MESSAGE use the Export Makefile command and run
!MESSAGE 
!MESSAGE NMAKE /f "foo_psy.mak".
!MESSAGE 
!MESSAGE You can specify a configuration when running NMAKE
!MESSAGE by defining the macro CFG on the command line. For example:
!MESSAGE 
!MESSAGE NMAKE /f "foo_psy.mak" CFG="foo_psy - Win32 Debug"
!MESSAGE 
!MESSAGE Possible choices for configuration are:
!MESSAGE 
!MESSAGE "foo_psy - Win32 Debug" (based on "Win32 (x86) Dynamic-Link Library")
!MESSAGE "foo_psy - Win32 Release" (based on "Win32 (x86) Dynamic-Link Library")
!MESSAGE 

# Begin Project
# PROP AllowPerConfigDependencies 0
# PROP Scc_ProjName ""
# PROP Scc_LocalPath ""
CPP=cl.exe
MTL=midl.exe
RSC=rc.exe

!IF  "$(CFG)" == "foo_psy - Win32 Debug"

# PROP BASE Use_MFC 0
# PROP BASE Use_Debug_Libraries 1
# PROP BASE Output_Dir "Debug"
# PROP BASE Intermediate_Dir "Debug"
# PROP BASE Target_Dir ""
# PROP Use_MFC 2
# PROP Use_Debug_Libraries 1
# PROP Output_Dir "../Debug"
# PROP Intermediate_Dir "Debug"
# PROP Ignore_Export_Lib 0
# PROP Target_Dir ""
# ADD BASE CPP /nologo /MTd /W3 /Gm /GX /ZI /Od /D "WIN32" /D "_DEBUG" /D "_WINDOWS" /D "_MBCS" /D "_USRDLL" /D "foo_psy_EXPORTS" /YX /FD /GZ /c
# ADD CPP /nologo /MDd /W3 /Gm /GX /ZI /Od /I "../../foobar2000/sdk" /D "WIN32" /D "_DEBUG" /D "_WINDOWS" /D "_MBCS" /D "_USRDLL" /D "_WINAMP_PLUGIN_" /D "FOO_INPUT_STD_EXPORTS" /D "_WINDLL" /D "_AFXDLL" /Yu"stdafx.h" /FD /GZ /c
# ADD BASE MTL /nologo /D "_DEBUG" /mktyplib203 /win32
# ADD MTL /nologo /D "_DEBUG" /mktyplib203 /win32
# ADD BASE RSC /l 0x409 /d "_DEBUG"
# ADD RSC /l 0x409 /d "_DEBUG" /d "_AFXDLL"
BSC32=bscmake.exe
# ADD BASE BSC32 /nologo
# ADD BSC32 /nologo
LINK32=link.exe
# ADD BASE LINK32 kernel32.lib user32.lib gdi32.lib winspool.lib comdlg32.lib advapi32.lib shell32.lib ole32.lib oleaut32.lib uuid.lib odbc32.lib odbccp32.lib /nologo /dll /debug /machine:I386 /pdbtype:sept
# ADD LINK32 foobar2000_SDK.lib /nologo /dll /debug /machine:I386 /nodefaultlib:"MSVCRT" /out:"./Debug/foo_psy.dll" /pdbtype:sept
# SUBTRACT LINK32 /profile

!ELSEIF  "$(CFG)" == "foo_psy - Win32 Release"

# PROP BASE Use_MFC 0
# PROP BASE Use_Debug_Libraries 0
# PROP BASE Output_Dir "foo_psy___Win32_Release"
# PROP BASE Intermediate_Dir "foo_psy___Win32_Release"
# PROP BASE Ignore_Export_Lib 0
# PROP BASE Target_Dir ""
# PROP Use_MFC 2
# PROP Use_Debug_Libraries 0
# PROP Output_Dir "../Release"
# PROP Intermediate_Dir "Release"
# PROP Ignore_Export_Lib 0
# PROP Target_Dir ""
# ADD BASE CPP /nologo /MD /W3 /GX /O2 /I "../SDK" /I "../../vorbis/include" /I "../../ogg/include" /I "../../flac/include" /D "WIN32" /D "NDEBUG" /D "_WINDOWS" /D "_MBCS" /D "_USRDLL" /D "foo_psy_EXPORTS" /YX /FD /c
# ADD CPP /nologo /MD /W3 /GX /O2 /I "..\..\FOOBAR2000\SDK" /D "WIN32" /D "NDEBUG" /D "_WINDOWS" /D "_MBCS" /D "_USRDLL" /D "_WINAMP_PLUGIN_" /D "FOO_INPUT_STD_EXPORTS" /D "_WINDLL" /D "_AFXDLL" /Yu"stdafx.h" /FD /c
# ADD BASE MTL /nologo /D "NDEBUG" /mktyplib203 /win32
# ADD MTL /nologo /D "NDEBUG" /mktyplib203 /win32
# ADD BASE RSC /l 0x409 /d "NDEBUG"
# ADD RSC /l 0x417 /d "NDEBUG" /d "_WINAMP_PLUGIN_" /d "_AFXDLL"
BSC32=bscmake.exe
# ADD BASE BSC32 /nologo
# ADD BSC32 /nologo
LINK32=link.exe
# ADD BASE LINK32 kernel32.lib user32.lib gdi32.lib winspool.lib comdlg32.lib advapi32.lib shell32.lib ole32.lib oleaut32.lib uuid.lib odbc32.lib odbccp32.lib msacm32.lib /nologo /dll /machine:I386
# SUBTRACT BASE LINK32 /debug
# ADD LINK32 foobar2000_SDK.lib pfc.lib utf8api.lib foobar2000_component_client.lib /nologo /dll /machine:I386 /out:"./Release/foo_psy.dll" /libpath:"../../foobarSDK/foobar2000/SDK/Release" /libpath:"../../foobarSDK/pfc/Release_unicode" /libpath:"../../foobarSDK/foobar2000/foobar2000_component_client/Release" /libpath:"../../foobarSDK/foobar2000/Release"
# SUBTRACT LINK32 /debug

!ENDIF 

# Begin Target

# Name "foo_psy - Win32 Debug"
# Name "foo_psy - Win32 Release"
# Begin Group "Psycle"

# PROP Default_Filter ""
# Begin Group "Source"

# PROP Default_Filter ""
# Begin Source File

SOURCE=..\Configuration.cpp
# End Source File
# Begin Source File

SOURCE=..\DataCompression.cpp
# End Source File
# Begin Source File

SOURCE=..\Dsp.cpp
# End Source File
# Begin Source File

SOURCE=..\FileIO.cpp
# End Source File
# Begin Source File

SOURCE=..\Filter.cpp
# End Source File
# Begin Source File

SOURCE=..\Global.cpp
# End Source File
# Begin Source File

SOURCE=..\Helpers.cpp
# End Source File
# Begin Source File

SOURCE=..\Instrument.cpp
# End Source File
# Begin Source File

SOURCE=..\Machine.cpp
# End Source File
# Begin Source File

SOURCE=..\Player.cpp
# End Source File
# Begin Source File

SOURCE=..\Plugin.cpp
# End Source File
# Begin Source File

SOURCE=..\Registry.cpp
# End Source File
# Begin Source File

SOURCE=..\Sampler.cpp
# End Source File
# Begin Source File

SOURCE=..\Song.cpp
# End Source File
# Begin Source File

SOURCE=..\StdAfx.cpp
# ADD CPP /Yc"stdafx.h"
# End Source File
# Begin Source File

SOURCE=..\VstHost.cpp
# End Source File
# End Group
# Begin Group "Header"

# PROP Default_Filter ""
# Begin Source File

SOURCE=..\Vst\AEffect.h
# End Source File
# Begin Source File

SOURCE=..\Vst\AEffectx.h
# End Source File
# Begin Source File

SOURCE=..\Configuration.h
# End Source File
# Begin Source File

SOURCE=..\Constants.h
# End Source File
# Begin Source File

SOURCE=..\DataCompression.h
# End Source File
# Begin Source File

SOURCE=..\Ddc.h
# End Source File
# Begin Source File

SOURCE=..\Dsp.h
# End Source File
# Begin Source File

SOURCE=..\FileIO.h
# End Source File
# Begin Source File

SOURCE=..\Filter.h
# End Source File
# Begin Source File

SOURCE=..\Global.h
# End Source File
# Begin Source File

SOURCE=..\Helpers.h
# End Source File
# Begin Source File

SOURCE=..\Instrument.h
# End Source File
# Begin Source File

SOURCE=..\Machine.h
# End Source File
# Begin Source File

SOURCE=..\MachineInterface.h
# End Source File
# Begin Source File

SOURCE=..\Player.h
# End Source File
# Begin Source File

SOURCE=..\Plugin.h
# End Source File
# Begin Source File

SOURCE=..\Registry.h
# End Source File
# Begin Source File

SOURCE=.\resource.h
# End Source File
# Begin Source File

SOURCE=..\Sampler.h
# End Source File
# Begin Source File

SOURCE=..\Song.h
# End Source File
# Begin Source File

SOURCE=..\SongStructs.h
# End Source File
# Begin Source File

SOURCE=..\StdAfx.h
# End Source File
# Begin Source File

SOURCE=..\VstHost.h
# End Source File
# End Group
# Begin Source File

SOURCE=..\convert_internal_machines.h
# End Source File
# End Group
# Begin Source File

SOURCE=.\foo_input_psy.rc
# End Source File
# Begin Source File

SOURCE=.\foo_psy.cpp
# End Source File
# End Target
# End Project
