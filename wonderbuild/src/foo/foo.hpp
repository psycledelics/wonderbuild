#if !defined _WIN32 || FOO < 0
	#define FOO_LINK
#elif FOO
	#define FOO_LINK __declspec(dllexport)
#else
	#define FOO_LINK __declspec(dllimport)
#endif

#include "bong.hpp"

FOO_LINK void foo();
