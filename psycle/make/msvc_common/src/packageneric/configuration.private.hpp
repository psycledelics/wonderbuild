// -*- mode:c++; indent-tabs-mode:t -*-

///\file \brief packageneric build configuration.

#pragma once
#include <packageneric/package.private.hpp>

#define BOOST_THREAD_USE_DLL

/// tool chain used to build the source package.
#define PACKAGENERIC__CONFIGURATION__COMPILER__BUILD "msvc"

/// host environment: platform for which the source package is built by the tool chain.
#define PACKAGENERIC__CONFIGURATION__COMPILER__HOST "msvc"

///\name installation paths
///\{
	/// relative path from the bin dir to the lib dir
	#define PACKAGENERIC__CONFIGURATION__INSTALL_PATH__BIN_TO_LIB     "."
	/// relative path from the bin dir to the libexec dir
 	#define PACKAGENERIC__CONFIGURATION__INSTALL_PATH__BIN_TO_LIBEXEC "../libexec"
	/// relative path from the bin dir to the share dir
	#define PACKAGENERIC__CONFIGURATION__INSTALL_PATH__BIN_TO_SHARE   "../share"
	/// relative path from the bin dir to the var dir
	#define PACKAGENERIC__CONFIGURATION__INSTALL_PATH__BIN_TO_VAR     "../var"
	/// relative path from the bin dir to the etc dir
	#define PACKAGENERIC__CONFIGURATION__INSTALL_PATH__BIN_TO_ETC     "../etc"
///\}

///\name stage paths (to be able to execute from the build dir without installing)
///\{
	/// relative path from the build dir to the source dir
	#define PACKAGENERIC__CONFIGURATION__STAGE_PATH__BUILD_TO_SOURCE "../../../../.."
///\}
