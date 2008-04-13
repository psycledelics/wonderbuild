#if !defined _WIN32 || FOO == -1
	#define FOO_LINK
#elif FOO
	#define FOO_LINK __declspec(dllexport)
#else
	#define FOO_LINK __declspec(dllimport)
#endif

FOO_LINK void f();
