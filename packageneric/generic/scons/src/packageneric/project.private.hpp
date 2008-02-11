/* -*- mode:c++, indent-tabs-mode:t -*- */
// This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
// copyright 2002-2007 johan boule <bohan@jabber.org>
// copyright 2004-2007 psycledelics http://psycle.pastnotecut.org

///\file

#pragma once
#include <packageneric/stringized.private.hpp>

#define PACKAGENERIC__PACKAGE__VERSION \
	PACKAGENERIC__STRINGIZED(PACKAGENERIC__PACKAGE__VERSION__MAJOR) "." \
	PACKAGENERIC__STRINGIZED(PACKAGENERIC__PACKAGE__VERSION__MINOR) "." \
	PACKAGENERIC__STRINGIZED(PACKAGENERIC__PACKAGE__VERSION__PATCH)

#define PACKAGENERIC__MODULE__VERSION \
	PACKAGENERIC__STRINGIZED(PACKAGENERIC__MODULE__VERSION__INTERFACE__MININUM_COMPATIBLE) "." \
	PACKAGENERIC__STRINGIZED(PACKAGENERIC__MODULE__VERSION__INTERFACE) "." \
	PACKAGENERIC__STRINGIZED(PACKAGENERIC__MODULE__VERSION__IMPLEMENTATION)
