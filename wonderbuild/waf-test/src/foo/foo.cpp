#if defined __unix__ || defined __APPLE__
	#include "foo.hpp"
#elif defined _WIN32
	#include "foo.hpp"
#endif
#include <iostream>

void foo() {
	std::cout << "foo\n";
}
