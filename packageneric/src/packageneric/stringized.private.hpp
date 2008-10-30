// This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
// copyright 2002-2008 members of the psycle project http://psycle.pastnotecut.org ; johan boule <bohan@jabber.org>

///\file

#pragma once

/// Interprets argument as a string litteral.
/// The indirection in the call to # lets the macro expansion on the argument be done first.
#define PACKAGENERIC__STRINGIZED(tokens) PACKAGENERIC__STRINGIZED__DETAIL__NO_EXPANSION(tokens)

///\internal
/// Don't call this macro directly ; call PACKAGENERIC__STRINGIZED, which calls this macro after macro expansion is done on the argument.
///\relates PACKAGENERIC__STRINGIZED
#define PACKAGENERIC__STRINGIZED__DETAIL__NO_EXPANSION(tokens) #tokens
