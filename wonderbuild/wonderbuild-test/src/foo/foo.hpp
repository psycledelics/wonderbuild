#if !defined _WIN32 || FOO < 0
	#define FOO_LINK
#elif FOO
	#define FOO_LINK __declspec(dllexport)
#else
	#define FOO_LINK __declspec(dllimport)
#endif

#if 0
	#include "bar.hpp"
#endif

FOO_LINK void foo();
