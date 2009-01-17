#ifdef WINDOW_OS
	#ifdef PRINT_EXPORTS
		#define PRINT_API __declspec(dllexport)
	#else
		#define PRINT_API __declspec(dllimport)
	#endif
#else
	#define PRINT_API
#endif

PRINT_API void print_msg();
