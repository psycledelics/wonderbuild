#ifndef IMPL__IMPL_HPP
#define IMPL__IMPL_HPP
#pragma once

#if !defined _WIN32 || FOO < 0
	#define IMPL__LINK
#elif FOO
	#define IMPL__LINK __declspec(dllexport)
#else
	#define IMPL__LINK __declspec(dllimport)
#endif

IMPL__LINK void impl();

#endif
