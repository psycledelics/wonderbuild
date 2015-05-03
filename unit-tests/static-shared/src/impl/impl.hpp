#ifndef IMPL__IMPL_HPP
#define IMPL__IMPL_HPP
#pragma once

#if !defined _WIN32 || IMPL < 0
	#define IMPL__DECL
#elif IMPL
	#define IMPL__DECL __declspec(dllexport)
#else
	#define IMPL__DECL __declspec(dllimport)
#endif

IMPL__DECL void impl();

#endif
