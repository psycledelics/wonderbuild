#ifndef IMPL__IMPL_HPP
#define IMPL__IMPL_HPP
#pragma once

#if !defined _WIN32 || IMPL < 0
	#define IMPL__LINK
#elif IMPL
	#define IMPL__LINK __declspec(dllexport)
#else
	#define IMPL__LINK __declspec(dllimport)
#endif

IMPL__LINK void impl();

#endif
