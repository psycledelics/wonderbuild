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
!MESSAGE 

# Begin Project
# PROP AllowPerConfigDependencies 0
# PROP Scc_ProjName ""
# PROP Scc_LocalPath ""
CPP=cl.exe
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
MTL=midl.exe
# ADD BASE MTL /nologo /win32
# ADD MTL /nologo /win32
# ADD BASE CPP /nologo /MDd /W3 /GX /ZI /Ot /I "..\..\asiosdk2\host\pc" /I "..\..\asiosdk2\host" /I "..\..\asiosdk2\common" /I "..\..\portaudio_v18\pa_common" /D "WIN32" /D "_DEBUG" /D "_LIB" /D "_MBCS" /YX /GZ /c
# ADD CPP /nologo /MTd /W3 /GX /ZI /Od /I "..\..\asiosdk2\host\pc" /I "..\..\asiosdk2\host" /I "..\..\asiosdk2\common" /I "..\..\portaudio_v18\pa_common" /D "WIN32" /D "_DEBUG" /D "_LIB" /D "_MBCS" /FR /YX /GZ /c
# ADD BASE RSC /l 0x409 /d "_DEBUG"
# ADD RSC /l 0x409 /d "_DEBUG"
BSC32=bscmake.exe
# ADD BASE BSC32 /nologo
# ADD BSC32 /nologo
LIB32=link.exe -lib
# ADD BASE LIB32 /nologo
# ADD LIB32 /nologo

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
MTL=midl.exe
# ADD BASE MTL /nologo /win32
# ADD MTL /nologo /win32
# ADD BASE CPP /nologo /G6 /MT /W3 /GX /Ot /Ob2 /Gy /I "..\..\asiosdk2\host\pc" /I "..\..\asiosdk2\host" /I "..\..\asiosdk2\common" /I "..\..\portaudio_v18\pa_common" /D "WIN32" /D "NDEBUG" /D "_LIB" /D "_MBCS" /YX /GF /c
# ADD CPP /nologo /G6 /MT /W3 /GX /Ot /Ob2 /Gy /I "..\..\asiosdk2\host\pc" /I "..\..\asiosdk2\host" /I "..\..\asiosdk2\common" /I "..\..\portaudio_v18\pa_common" /D "WIN32" /D "NDEBUG" /D "_LIB" /D "_MBCS" /YX /GF /c
# ADD BASE RSC /l 0x409 /d "NDEBUG"
# ADD RSC /l 0x409 /d "NDEBUG"
BSC32=bscmake.exe
# ADD BASE BSC32 /nologo
# ADD BSC32 /nologo
LIB32=link.exe -lib
# ADD BASE LIB32 /nologo
# ADD LIB32 /nologo

!ENDIF 

# Begin Target

# Name "PortAudioStaticASIO - Win32 Debug"
# Name "PortAudioStaticASIO - Win32 Release"
# Begin Group "ASIO SDK Files"

# PROP Default_Filter ""
# Begin Source File

SOURCE=..\..\asiosdk2\common\asio.cpp
DEP_CPP_ASIO_=\
	"..\..\asiosdk2\common\asio.h"\
	"..\..\asiosdk2\common\asiodrvr.h"\
	"..\..\asiosdk2\common\asiosys.h"\
	"..\..\asiosdk2\common\combase.h"\
	"..\..\asiosdk2\common\iasiodrv.h"\
	"..\..\asiosdk2\host\asiodrivers.h"\
	"..\..\asiosdk2\host\ginclude.h"\
	"..\..\asiosdk2\host\pc\asiolist.h"\
	
NODEP_CPP_ASIO_=\
	"..\..\asiosdk2\host\CodeFragments.hpp"\
	
# End Source File
# Begin Source File

SOURCE=..\..\asiosdk2\host\asiodrivers.cpp
DEP_CPP_ASIOD=\
	"..\..\asiosdk2\common\asio.h"\
	"..\..\asiosdk2\common\asiosys.h"\
	"..\..\asiosdk2\common\iasiodrv.h"\
	"..\..\asiosdk2\host\asiodrivers.h"\
	"..\..\asiosdk2\host\ginclude.h"\
	"..\..\asiosdk2\host\pc\asiolist.h"\
	
NODEP_CPP_ASIOD=\
	"..\..\asiosdk2\host\CodeFragments.hpp"\
	
# End Source File
# Begin Source File

SOURCE=..\..\asiosdk2\host\pc\asiolist.cpp
DEP_CPP_ASIOL=\
	"..\..\asiosdk2\common\asio.h"\
	"..\..\asiosdk2\common\asiosys.h"\
	"..\..\asiosdk2\common\iasiodrv.h"\
	"..\..\asiosdk2\host\pc\asiolist.h"\
	
# End Source File
# End Group
# Begin Group "PortAudio SDK Files"

# PROP Default_Filter ""
# Begin Source File

SOURCE=..\..\portaudio_v18\pa_asio\pa_asio.cpp
DEP_CPP_PA_AS=\
	"..\..\asiosdk2\common\asio.h"\
	"..\..\asiosdk2\common\asiosys.h"\
	"..\..\asiosdk2\host\asiodrivers.h"\
	"..\..\asiosdk2\host\ginclude.h"\
	"..\..\asiosdk2\host\pc\asiolist.h"\
	"..\..\portaudio_v18\pa_common\pa_host.h"\
	"..\..\portaudio_v18\pa_common\pa_trace.h"\
	"..\..\portaudio_v18\pa_common\portaudio.h"\
	
NODEP_CPP_PA_AS=\
	"..\..\asiosdk2\host\CodeFragments.hpp"\
	
# End Source File
# Begin Source File

SOURCE=..\..\portaudio_v18\pa_common\pa_host.h
# End Source File
# Begin Source File

SOURCE=..\..\portaudio_v18\pa_common\pa_lib.c
DEP_CPP_PA_LI=\
	"..\..\portaudio_v18\pa_common\pa_host.h"\
	"..\..\portaudio_v18\pa_common\pa_trace.h"\
	"..\..\portaudio_v18\pa_common\portaudio.h"\
	
# End Source File
# Begin Source File

SOURCE=..\..\portaudio_v18\pa_common\portaudio.h
# End Source File
# End Group
# End Target
# End Project
