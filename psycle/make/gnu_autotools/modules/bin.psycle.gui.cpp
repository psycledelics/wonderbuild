// This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
// Copyright © 1999-2005 Psycledelics http://psycle.pastnotecut.org : Johan Boule

///\file
///\brief
#include PACKAGENERIC__PRE_COMPILED
#include PACKAGENERIC
#include <psycle/detail/project.private.hpp>
#include <psycle/front_ends/gui/main.hpp>
extern "C" int main(int /*const*/ argument_count, char /*const*/ * /*const*/ arguments[]) throw()
{
	return psycle::front_ends::gui::main(argument_count, arguments);
}
