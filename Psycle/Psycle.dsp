# Microsoft Developer Studio Project File - Name="Psycle" - Package Owner=<4>
# Microsoft Developer Studio Generated Build File, Format Version 6.00
# ** DO NOT EDIT **

# TARGTYPE "Win32 (x86) Application" 0x0101

CFG=Psycle - Win32 Debug
!MESSAGE This is not a valid makefile. To build this project using NMAKE,
!MESSAGE use the Export Makefile command and run
!MESSAGE 
!MESSAGE NMAKE /f "Psycle.mak".
!MESSAGE 
!MESSAGE You can specify a configuration when running NMAKE
!MESSAGE by defining the macro CFG on the command line. For example:
!MESSAGE 
!MESSAGE NMAKE /f "Psycle.mak" CFG="Psycle - Win32 Debug"
!MESSAGE 
!MESSAGE Possible choices for configuration are:
!MESSAGE 
!MESSAGE "Psycle - Win32 Release" (based on "Win32 (x86) Application")
!MESSAGE "Psycle - Win32 Debug" (based on "Win32 (x86) Application")
!MESSAGE "Psycle - Win32 Release Cyrix" (based on "Win32 (x86) Application")
!MESSAGE 

# Begin Project
# PROP AllowPerConfigDependencies 0
# PROP Scc_ProjName ""
# PROP Scc_LocalPath ""
CPP=cl.exe
MTL=midl.exe
RSC=rc.exe

!IF  "$(CFG)" == "Psycle - Win32 Release"

# PROP BASE Use_MFC 6
# PROP BASE Use_Debug_Libraries 0
# PROP BASE Output_Dir "Release"
# PROP BASE Intermediate_Dir "Release"
# PROP BASE Target_Dir ""
# PROP Use_MFC 5
# PROP Use_Debug_Libraries 0
# PROP Output_Dir "Release"
# PROP Intermediate_Dir "Release"
# PROP Ignore_Export_Lib 0
# PROP Target_Dir ""
# ADD BASE CPP /nologo /MD /W3 /GX /O2 /D "WIN32" /D "NDEBUG" /D "_WINDOWS" /D "_AFXDLL" /Yu"stdafx.h" /FD /c
# ADD CPP /nologo /G6 /MT /W3 /GX /Zi /O2 /Ob2 /I "../portaudio_v18/pa_common" /D "WIN32" /D "NDEBUG" /D "_WINDOWS" /D "_MBCS" /Fr /Yu"stdafx.h" /FD /c
# ADD BASE MTL /nologo /D "NDEBUG" /mktyplib203 /win32
# ADD MTL /nologo /D "NDEBUG" /mktyplib203 /win32
# ADD BASE RSC /l 0x80a /d "NDEBUG" /d "_AFXDLL"
# ADD RSC /l 0x417 /d "NDEBUG"
BSC32=bscmake.exe
# ADD BASE BSC32 /nologo
# ADD BSC32 /nologo
LINK32=link.exe
# ADD BASE LINK32 /nologo /subsystem:windows /machine:I386
# ADD LINK32 winmm.lib dsound.lib /nologo /subsystem:windows /debug /machine:I386 /libpath:"./PortAudioStaticASIO/Release" /OPT:REF
# SUBTRACT LINK32 /pdb:none /incremental:yes

!ELSEIF  "$(CFG)" == "Psycle - Win32 Debug"

# PROP BASE Use_MFC 6
# PROP BASE Use_Debug_Libraries 1
# PROP BASE Output_Dir "Debug"
# PROP BASE Intermediate_Dir "Debug"
# PROP BASE Target_Dir ""
# PROP Use_MFC 6
# PROP Use_Debug_Libraries 1
# PROP Output_Dir "Debug"
# PROP Intermediate_Dir "Debug"
# PROP Ignore_Export_Lib 0
# PROP Target_Dir ""
# ADD BASE CPP /nologo /MDd /W3 /Gm /GX /ZI /Od /D "WIN32" /D "_DEBUG" /D "_WINDOWS" /D "_AFXDLL" /Yu"stdafx.h" /FD /GZ /c
# ADD CPP /nologo /MDd /W3 /Gm /Gi /GX /ZI /Od /I "../portaudio_v18/pa_common" /D "WIN32" /D "_DEBUG" /D "_WINDOWS" /D "_MBCS" /D "_AFXDLL" /FR /Yu"stdafx.h" /FD /GZ /c
# ADD BASE MTL /nologo /D "_DEBUG" /mktyplib203 /win32
# ADD MTL /nologo /D "_DEBUG" /mktyplib203 /win32
# ADD BASE RSC /l 0x80a /d "_DEBUG" /d "_AFXDLL"
# ADD RSC /l 0x417 /d "_DEBUG" /d "_AFXDLL"
BSC32=bscmake.exe
# ADD BASE BSC32 /nologo
# ADD BSC32 /nologo
LINK32=link.exe
# ADD BASE LINK32 /nologo /subsystem:windows /debug /machine:I386 /pdbtype:sept
# ADD LINK32 winmm.lib dsound.lib PortAudioStaticASIO.lib /nologo /subsystem:windows /map /debug /machine:I386 /libpath:"./PortAudioStaticASIO/Debug"
# SUBTRACT LINK32 /profile /pdb:none

!ELSEIF  "$(CFG)" == "Psycle - Win32 Release Cyrix"

# PROP BASE Use_MFC 5
# PROP BASE Use_Debug_Libraries 0
# PROP BASE Output_Dir "Psycle___Win32_Release_Cyrix"
# PROP BASE Intermediate_Dir "Psycle___Win32_Release_Cyrix"
# PROP BASE Ignore_Export_Lib 0
# PROP BASE Target_Dir ""
# PROP Use_MFC 5
# PROP Use_Debug_Libraries 0
# PROP Output_Dir "Release_Cyrix"
# PROP Intermediate_Dir "Release_Cyrix"
# PROP Ignore_Export_Lib 0
# PROP Target_Dir ""
# ADD BASE CPP /nologo /G6 /MT /W3 /GX /Zi /O2 /Ob2 /D "WIN32" /D "NDEBUG" /D "_WINDOWS" /D "_MBCS" /Yu"stdafx.h" /FD /c
# SUBTRACT BASE CPP /WX /Fr
# ADD CPP /nologo /MT /W3 /GX /Zi /O2 /Ob2 /I "../portaudio_v18/pa_common" /D "WIN32" /D "NDEBUG" /D "_WINDOWS" /D "_MBCS" /D "_CYRIX_PROCESSOR_" /Yu"stdafx.h" /FD /c
# SUBTRACT CPP /WX /Fr
# ADD BASE MTL /nologo /D "NDEBUG" /mktyplib203 /win32
# ADD MTL /nologo /D "NDEBUG" /mktyplib203 /win32
# ADD BASE RSC /l 0x417 /d "NDEBUG"
# ADD RSC /l 0x417 /d "NDEBUG"
BSC32=bscmake.exe
# ADD BASE BSC32 /nologo
# ADD BSC32 /nologo
LINK32=link.exe
# ADD BASE LINK32 winmm.lib dsound.lib htmlhelp.lib /nologo /subsystem:windows /debug /machine:I386 /OPT:REF
# SUBTRACT BASE LINK32 /pdb:none /incremental:yes
# ADD LINK32 winmm.lib dsound.lib PortAudioStaticASIO.lib /nologo /subsystem:windows /debug /machine:I386 /libpath:"./PortAudioStaticASIO/Release" /OPT:REF
# SUBTRACT LINK32 /pdb:none /incremental:yes

!ENDIF 

# Begin Target

# Name "Psycle - Win32 Release"
# Name "Psycle - Win32 Debug"
# Name "Psycle - Win32 Release Cyrix"
# Begin Group "Source Files"

# PROP Default_Filter ""
# Begin Group "Gear"

# PROP Default_Filter ""
# Begin Source File

SOURCE=.\DefaultVstGui.cpp
# End Source File
# Begin Source File

SOURCE=.\DefaultVstGui.h
# End Source File
# Begin Source File

SOURCE=.\Dsp.cpp
# End Source File
# Begin Source File

SOURCE=.\Dsp.h
# End Source File
# Begin Source File

SOURCE=.\Filter.cpp
# End Source File
# Begin Source File

SOURCE=.\Filter.h
# End Source File
# Begin Source File

SOURCE=.\FrameMachine.cpp
# End Source File
# Begin Source File

SOURCE=.\FrameMachine.h
# End Source File
# Begin Source File

SOURCE=.\GearDelay.cpp
# End Source File
# Begin Source File

SOURCE=.\GearDelay.h
# End Source File
# Begin Source File

SOURCE=.\GearDistort.cpp
# End Source File
# Begin Source File

SOURCE=.\GearDistort.h
# End Source File
# Begin Source File

SOURCE=.\Gearfilter.cpp
# End Source File
# Begin Source File

SOURCE=.\GearFilter.h
# End Source File
# Begin Source File

SOURCE=.\GearFlanger.cpp
# End Source File
# Begin Source File

SOURCE=.\GearFlanger.h
# End Source File
# Begin Source File

SOURCE=.\GearGainer.cpp
# End Source File
# Begin Source File

SOURCE=.\GearGainer.h
# End Source File
# Begin Source File

SOURCE=.\GearPsychOsc.cpp
# End Source File
# Begin Source File

SOURCE=.\GearPsychosc.h
# End Source File
# Begin Source File

SOURCE=.\GearTracker.cpp
# End Source File
# Begin Source File

SOURCE=.\GearTracker.h
# End Source File
# Begin Source File

SOURCE=.\Machine.cpp
# End Source File
# Begin Source File

SOURCE=.\Machine.h
# End Source File
# Begin Source File

SOURCE=.\MachineInterface.h
# End Source File
# Begin Source File

SOURCE=.\MasterDlg.cpp
# End Source File
# Begin Source File

SOURCE=.\MasterDlg.h
# End Source File
# Begin Source File

SOURCE=.\Plugin.cpp
# End Source File
# Begin Source File

SOURCE=.\Plugin.h
# End Source File
# Begin Source File

SOURCE=.\Sampler.cpp
# End Source File
# Begin Source File

SOURCE=.\Sampler.h
# End Source File
# Begin Source File

SOURCE=.\VstEditorDlg.cpp
# End Source File
# Begin Source File

SOURCE=.\VstEditorDlg.h
# End Source File
# Begin Source File

SOURCE=.\VstGui.cpp
# End Source File
# Begin Source File

SOURCE=.\VstGui.h
# End Source File
# Begin Source File

SOURCE=.\VstHost.cpp
# End Source File
# Begin Source File

SOURCE=.\VstHost.h
# End Source File
# End Group
# Begin Group "Instrument"

# PROP Default_Filter ""
# Begin Source File

SOURCE=.\EnvDialog.cpp
# End Source File
# Begin Source File

SOURCE=.\EnvDialog.h
# End Source File
# Begin Source File

SOURCE=.\InstrumentEditor.cpp
# End Source File
# Begin Source File

SOURCE=.\InstrumentEditor.h
# End Source File
# Begin Source File

SOURCE=.\WaveEdAmplifyDialog.cpp
# End Source File
# Begin Source File

SOURCE=.\WaveEdAmplifyDialog.h
# End Source File
# Begin Source File

SOURCE=.\WaveEdChildView.cpp
# End Source File
# Begin Source File

SOURCE=.\WaveEdChildView.h
# End Source File
# Begin Source File

SOURCE=.\WaveEdFrame.cpp
# End Source File
# Begin Source File

SOURCE=.\WaveEdFrame.h
# End Source File
# Begin Source File

SOURCE=.\WavFileDlg.cpp
# End Source File
# Begin Source File

SOURCE=.\WavFileDlg.h
# End Source File
# End Group
# Begin Group "Audio_Driver"

# PROP Default_Filter ""
# Begin Source File

SOURCE=.\AudioDriver.cpp
# End Source File
# Begin Source File

SOURCE=.\AudioDriver.h
# End Source File
# Begin Source File

SOURCE=.\DirectSound.cpp
# End Source File
# Begin Source File

SOURCE=.\DirectSound.h
# End Source File
# Begin Source File

SOURCE=.\PortAudioASIO.cpp
# End Source File
# Begin Source File

SOURCE=.\PortAudioASIO.h
# End Source File
# Begin Source File

SOURCE=.\WaveOut.cpp
# End Source File
# Begin Source File

SOURCE=.\WaveOut.h
# End Source File
# End Group
# Begin Group "Configuration"

# PROP Default_Filter ""
# Begin Source File

SOURCE=.\ConfigDlg.cpp
# End Source File
# Begin Source File

SOURCE=.\ConfigDlg.h
# End Source File
# Begin Source File

SOURCE=.\Configuration.cpp
# End Source File
# Begin Source File

SOURCE=.\Configuration.h
# End Source File
# Begin Source File

SOURCE=.\DirectoryDlg.cpp
# End Source File
# Begin Source File

SOURCE=.\DirectoryDlg.h
# End Source File
# Begin Source File

SOURCE=.\DSoundConfig.cpp
# End Source File
# Begin Source File

SOURCE=.\DSoundConfig.h
# End Source File
# Begin Source File

SOURCE=.\KeyConfigDlg.cpp
# End Source File
# Begin Source File

SOURCE=.\KeyConfigDlg.h
# End Source File
# Begin Source File

SOURCE=.\MidiInputDlg.cpp
# End Source File
# Begin Source File

SOURCE=.\MidiInputDlg.h
# End Source File
# Begin Source File

SOURCE=.\MidiLearn.cpp
# End Source File
# Begin Source File

SOURCE=.\MidiLearn.h
# End Source File
# Begin Source File

SOURCE=.\OutputDlg.cpp
# End Source File
# Begin Source File

SOURCE=.\OutputDlg.h
# End Source File
# Begin Source File

SOURCE=.\PortAudioASIOConfig.cpp
# End Source File
# Begin Source File

SOURCE=.\PortAudioASIOConfig.h
# End Source File
# Begin Source File

SOURCE=.\Registry.cpp
# End Source File
# Begin Source File

SOURCE=.\Registry.h
# End Source File
# Begin Source File

SOURCE=.\SkinDlg.cpp
# End Source File
# Begin Source File

SOURCE=.\SkinDlg.h
# End Source File
# Begin Source File

SOURCE=.\WaveOutDialog.cpp
# End Source File
# Begin Source File

SOURCE=.\WaveOutDialog.h
# End Source File
# End Group
# Begin Group "Legacy"

# PROP Default_Filter ""
# Begin Source File

SOURCE=.\Riff.cpp
# End Source File
# Begin Source File

SOURCE=.\Riff.h
# End Source File
# End Group
# Begin Group "VST SDK Files"

# PROP Default_Filter ""
# Begin Source File

SOURCE=.\Vst\AEffect.h
# End Source File
# Begin Source File

SOURCE=.\Vst\AEffectx.h
# End Source File
# Begin Source File

SOURCE=.\Vst\AEffEditor.h
# End Source File
# End Group
# Begin Group "Interface Dialogs"

# PROP Default_Filter ""
# Begin Source File

SOURCE=.\GearRackDlg.cpp
# End Source File
# Begin Source File

SOURCE=.\GearRackDlg.h
# End Source File
# Begin Source File

SOURCE=.\GreetDialog.cpp
# End Source File
# Begin Source File

SOURCE=.\GreetDialog.h
# End Source File
# Begin Source File

SOURCE=.\InfoDlg.cpp
# End Source File
# Begin Source File

SOURCE=.\InfoDlg.h
# End Source File
# Begin Source File

SOURCE=.\MacProp.cpp
# End Source File
# Begin Source File

SOURCE=.\MacProp.h
# End Source File
# Begin Source File

SOURCE=.\MidiMonitorDlg.cpp
# End Source File
# Begin Source File

SOURCE=.\MidiMonitorDlg.h
# End Source File
# Begin Source File

SOURCE=.\NewMachine.cpp
# End Source File
# Begin Source File

SOURCE=.\NewMachine.h
# End Source File
# Begin Source File

SOURCE=.\NewVal.cpp
# End Source File
# Begin Source File

SOURCE=.\NewVal.h
# End Source File
# Begin Source File

SOURCE=.\PatDlg.cpp
# End Source File
# Begin Source File

SOURCE=.\PatDlg.h
# End Source File
# Begin Source File

SOURCE=.\PresetsDlg.cpp
# End Source File
# Begin Source File

SOURCE=.\PresetsDlg.h
# End Source File
# Begin Source File

SOURCE=.\SaveWavDlg.cpp
# End Source File
# Begin Source File

SOURCE=.\SaveWavDlg.h
# End Source File
# Begin Source File

SOURCE=.\SongpDlg.cpp
# End Source File
# Begin Source File

SOURCE=.\SongpDlg.h
# End Source File
# Begin Source File

SOURCE=.\SwingFillDlg.cpp
# End Source File
# Begin Source File

SOURCE=.\SwingFillDlg.h
# End Source File
# Begin Source File

SOURCE=.\VolumeDlg.cpp
# End Source File
# Begin Source File

SOURCE=.\VolumeDlg.h
# End Source File
# Begin Source File

SOURCE=.\WireDlg.cpp
# End Source File
# Begin Source File

SOURCE=.\WireDlg.h
# End Source File
# End Group
# Begin Source File

SOURCE=.\ChildView.cpp
# End Source File
# Begin Source File

SOURCE=.\ChildView.h
# End Source File
# Begin Source File

SOURCE=.\Constants.h
# End Source File
# Begin Source File

SOURCE=.\FileIO.cpp
# End Source File
# Begin Source File

SOURCE=.\FileIO.h
# End Source File
# Begin Source File

SOURCE=.\FileXM.cpp
# End Source File
# Begin Source File

SOURCE=.\FileXM.h
# End Source File
# Begin Source File

SOURCE=.\Global.cpp
# End Source File
# Begin Source File

SOURCE=.\Global.h
# End Source File
# Begin Source File

SOURCE=.\Helpers.cpp
# End Source File
# Begin Source File

SOURCE=.\Helpers.h
# End Source File
# Begin Source File

SOURCE=.\InputHandler.cpp
# End Source File
# Begin Source File

SOURCE=.\InputHandler.h
# End Source File
# Begin Source File

SOURCE=.\MainFrm.cpp
# End Source File
# Begin Source File

SOURCE=.\MainFrm.h
# End Source File
# Begin Source File

SOURCE=.\MidiInput.cpp
# End Source File
# Begin Source File

SOURCE=.\MidiInput.h
# End Source File
# Begin Source File

SOURCE=.\Player.cpp
# End Source File
# Begin Source File

SOURCE=.\Player.h
# End Source File
# Begin Source File

SOURCE=.\Psycle.cpp
# End Source File
# Begin Source File

SOURCE=.\Psycle.rc
# End Source File
# Begin Source File

SOURCE=.\Psycle2.h
# End Source File
# Begin Source File

SOURCE=.\resource.h
# End Source File
# Begin Source File

SOURCE=.\Song.cpp
# End Source File
# Begin Source File

SOURCE=.\Song.h
# End Source File
# Begin Source File

SOURCE=.\SongStructs.h
# End Source File
# Begin Source File

SOURCE=.\StdAfx.cpp
# ADD CPP /Yc"stdafx.h"
# End Source File
# Begin Source File

SOURCE=.\StdAfx.h
# End Source File
# End Group
# Begin Group "Resource Files"

# PROP Default_Filter "ico;cur;bmp;dlg;rc2;rct;bin;rgs;gif;jpg;jpeg;jpe"
# Begin Source File

SOURCE=.\res\AsioLogo.bmp
# End Source File
# Begin Source File

SOURCE=.\res\bitmap1.bmp
# End Source File
# Begin Source File

SOURCE=.\res\bmp00001.bmp
# End Source File
# Begin Source File

SOURCE=.\res\bmp00002.bmp
# End Source File
# Begin Source File

SOURCE=.\res\bmp00003.bmp
# End Source File
# Begin Source File

SOURCE=.\res\bmp00004.bmp
# End Source File
# Begin Source File

SOURCE=.\res\bmp00005.bmp
# End Source File
# Begin Source File

SOURCE=.\res\bmp00006.bmp
# End Source File
# Begin Source File

SOURCE=.\res\bmp00009.bmp
# End Source File
# Begin Source File

SOURCE=.\res\bmp00010.bmp
# End Source File
# Begin Source File

SOURCE=.\res\bmp00011.bmp
# End Source File
# Begin Source File

SOURCE=.\res\bmp00012.bmp
# End Source File
# Begin Source File

SOURCE=.\res\bmp00013.bmp
# End Source File
# Begin Source File

SOURCE=.\res\dalaydelay.bmp
# End Source File
# Begin Source File

SOURCE=.\res\ico00001.ico
# End Source File
# Begin Source File

SOURCE=.\res\icon1.ico
# End Source File
# Begin Source File

SOURCE=.\res\idr_main.ico
# End Source File
# Begin Source File

SOURCE=.\res\idr_vstf.ico
# End Source File
# Begin Source File

SOURCE=.\res\less.bmp
# End Source File
# Begin Source File

SOURCE=.\res\lessless.bmp
# End Source File
# Begin Source File

SOURCE=.\res\littleleft.bmp
# End Source File
# Begin Source File

SOURCE=.\res\littleright.bmp
# End Source File
# Begin Source File

SOURCE=.\res\machine_skin.bmp
# End Source File
# Begin Source File

SOURCE=.\res\MasterMachine\masterbk.bmp
# End Source File
# Begin Source File

SOURCE=.\res\minus.bmp
# End Source File
# Begin Source File

SOURCE=.\res\minus1.bmp
# End Source File
# Begin Source File

SOURCE=.\res\more.bmp
# End Source File
# Begin Source File

SOURCE=.\res\moremore.bmp
# End Source File
# Begin Source File

SOURCE=.\res\MasterMachine\numbers.bmp
# End Source File
# Begin Source File

SOURCE=.\res\pattern_header_skin.bmp
# End Source File
# Begin Source File

SOURCE=.\res\plus.bmp
# End Source File
# Begin Source File

SOURCE=.\res\plus1.bmp
# End Source File
# Begin Source File

SOURCE=.\res\Psycle.ico
# End Source File
# Begin Source File

SOURCE=.\res\Psycle.rc2
# End Source File
# Begin Source File

SOURCE=.\res\MasterMachine\slider.bmp
# End Source File
# Begin Source File

SOURCE=".\res\splash copia.bmp"
# End Source File
# Begin Source File

SOURCE=.\res\stuff.bmp
# End Source File
# Begin Source File

SOURCE=.\res\TbMainKnob.bmp
# End Source File
# Begin Source File

SOURCE=.\res\Toolbar.bmp
# End Source File
# Begin Source File

SOURCE=.\res\vstfx.bmp
# End Source File
# Begin Source File

SOURCE=.\res\vsti.bmp
# End Source File
# End Group
# Begin Source File

SOURCE=".\Docs\how to skin psycle.txt"
# End Source File
# Begin Source File

SOURCE=".\DevelDocs\new sampler spec.txt"
# End Source File
# Begin Source File

SOURCE=.\Docs\todo.txt
# End Source File
# Begin Source File

SOURCE=".\Docs\tweakings and commands.txt"
# End Source File
# Begin Source File

SOURCE=.\Docs\whatsnew.txt
# End Source File
# End Target
# End Project
# Section Psycle : {D14B6218-78B9-456C-ACB2-39C372D178B2}
# 	2:16:Resource Include:resource.h
# 	2:10:ENUM: enum:enum
# 	2:21:IDD_VST_CUSTOM_EDITOR:IDD_VST_CUSTOM_EDITOR
# 	2:14:DlgVstCustom.h:DlgVstCustom1.h
# 	2:19:Application Include:psycle.h
# 	2:20:CLASS: CDlgVstCustom:CDlgVstCustom
# 	2:16:DlgVstCustom.cpp:DlgVstCustom1.cpp
# End Section
