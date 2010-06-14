#ifndef WRAPPER__WRAPPER_HPP
#define WRAPPER__WRAPPER_HPP
#pragma once

#if !defined _WIN32 || WRAPPER < 0
	#define WRAPPER__DECL
#elif WRAPPER
	#define WRAPPER__DECL __declspec(dllexport)
#else
	#define WRAPPER__DECL __declspec(dllimport)
#endif

WRAPPER__DECL void wrapper();

#endif
