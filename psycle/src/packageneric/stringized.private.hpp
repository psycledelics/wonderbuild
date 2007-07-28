// This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
// copyright 1999-2007 johan boule <bohan@jabber.org>
// copyright 2004-2007 psycledelics http://psycle.pastnotecut.org

///\file
#pragma once

//#region PACKAGENERIC
	/// Interprets argument as a string litteral.
	/// The indirection in the call to # lets the macro expansion on the argument be done first.
	#define PACKAGENERIC__STRINGIZED(tokens) PACKAGENERIC__STRINGIZED__DETAIL__NO_EXPANSION(tokens)

	//#region DETAIL
		///\internal
		/// Don't call this macro directly ; call PACKAGENERIC__STRINGIZED, which calls this macro after macro expansion is done on the argument.
		///\relates PACKAGENERIC__STRINGIZED
		#define PACKAGENERIC__STRINGIZED__DETAIL__NO_EXPANSION(tokens) #tokens
	//#endregion
//#endregion
