#include "foo2.hpp"

void foo2(foo_func foo) {
	for(int i = 0; i < 2; ++i) foo();
	#if defined __GNUG__
		#warning foo2
	#endif
}
