#ifndef WRAPPER__WRAPPER_HPP
#define WRAPPER__WRAPPER_HPP
#pragma once

#if !defined _WIN32 || WRAPPER < 0
	#define WRAPPER__LINK
#elif WRAPPER
	#define WRAPPER__LINK __declspec(dllexport)
#else
	#define WRAPPER__LINK __declspec(dllimport)
#endif

WRAPPER__LINK void wrapper();

#endif
