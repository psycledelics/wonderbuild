// -*- mode:c++; indent-tabs-mode:t -*-
///\file
///\brief description of a fake source package (there's no notion of source package in msvc).
#pragma once
#include <packageneric/project.private.hpp>

///\name source package meta information
///\{
	/// name of the source package
	#define PACKAGENERIC__PACKAGE__NAME "psycle"
	/// description of the source package
	#define PACKAGENERIC__PACKAGE__DESCRIPTION "psycle modular music creation studio"
	/// major version number of the source package
	#define PACKAGENERIC__PACKAGE__VERSION__MAJOR 1
	/// minor version number of the source package
	#define PACKAGENERIC__PACKAGE__VERSION__MINOR 8
	/// patch version number of the source package
	#define PACKAGENERIC__PACKAGE__VERSION__PATCH 5
	/// distribution archive (e.g., unstable, testing, stable)
	#define PACKAGENERIC__PACKAGE__ARCHIVE "unstable"
	/// origin
	#define PACKAGENERIC__PACKAGE__ORIGIN "psycle project http://psycle.sourceforge.net"
	/// copyright
	#define PACKAGENERIC__PACKAGE__COPYRIGHT "copyright 2000-2008 members of the psycle project http://psycle.sourceforge.net ; see the AUTHORS file"
///\}
