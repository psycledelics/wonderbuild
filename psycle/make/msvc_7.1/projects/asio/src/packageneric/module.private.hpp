///\file
///\brief packageneric configuration for module asio
#pragma once
#include <packageneric/configuration.private.hpp>

#undef  PACKAGENERIC__PACKAGE__ORIGIN
#define PACKAGENERIC__PACKAGE__ORIGIN "Steinberg Media Technologies GmbH http://steinberg.de"
#undef  PACKAGENERIC__PACKAGE__COPYRIGHT
#define PACKAGENERIC__PACKAGE__COPYRIGHT "Copyright (C) 1992-2005 Steinberg Media Technologies GmbH"
#undef  PACKAGENERIC__PACKAGE__LICENSE
#define PACKAGENERIC__PACKAGE__LICENSE "Steinberg ASIO SDK licensing agreement"

#define PACKAGENERIC__MODULE__NAME "asio"
#define PACKAGENERIC__MODULE__VERSION__INTERFACE 2
#define PACKAGENERIC__MODULE__VERSION__INTERFACE__MININUM_COMPATIBLE 0
#define PACKAGENERIC__MODULE__VERSION__IMPLEMENTATION 1
#define PACKAGENERIC__MODULE__DESCRIPTION "steinberg audio stream input/output"
#define PACKAGENERIC__MODULE__SOURCE__ASIO 1
