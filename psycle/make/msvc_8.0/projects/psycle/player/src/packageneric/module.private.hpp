///\file
///\brief packageneric configuration for module psycle.player
#pragma once
#include <packageneric/configuration.private.hpp>

#define PACKAGENERIC__MODULE__NAME "psycle.player"
#define PACKAGENERIC__MODULE__VERSION__INTERFACE 0
#define PACKAGENERIC__MODULE__VERSION__INTERFACE__MININUM_COMPATIBLE 0
#define PACKAGENERIC__MODULE__VERSION__IMPLEMENTATION 0
#define PACKAGENERIC__MODULE__DESCRIPTION "psycle player"
#define PACKAGENERIC__MODULE__SOURCE__PSYCLE__PLAYER 1
#define PACKAGENERIC__MODULE__LOGO "psycle"
#include <diversalis/compiler.hpp>
#if defined DIVERSALIS__COMPILER__RESOURCE && !defined DIVERSALIS__COMPILER__GNU // workaround for microsoft's rc.exe's preprocessor which doesn't expand the what we put after 1 ICON DISCARDABLE
	1 ICON DISCARDABLE "../../../../../../pixmaps/psycle.ico"
#endif
