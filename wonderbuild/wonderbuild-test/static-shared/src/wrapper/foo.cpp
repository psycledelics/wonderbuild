#include "foo.hpp"
#include <iostream>

void foo() {
	std::cout << "foo\n";
	#if defined __GNUG__
		#warning foo
	#endif
}
