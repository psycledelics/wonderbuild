#if !defined _WIN32 || defined __GNUC__ /*__MINGW32__*/ || FOO < 0
	#define FOO_LINK
	#if defined __GNUC__
		#if FOO < 0
			#warning static
		#else
			#warning auto import/export
		#endif
	#elif defined _MSC_VER
		#if FOO < 0
			#pragma message("static")
		#else
			#pragma message("auto import/export")
		#endif
	#endif
#elif FOO
	#define FOO_LINK __declspec(dllexport)
	#if defined __GNUC__
		#warning export
	#elif defined _MSC_VER
			#pragma message("export")
	#endif
#else
	#define FOO_LINK __declspec(dllimport)
	#if defined __GNUC__
		#warning import
	#elif defined _MSC_VER
			#pragma message("import")
	#endif
#endif

FOO_LINK void foo();
