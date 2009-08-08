#include "foo2.hpp"

namespace foo {
	foo2::foo2() {}
	#if defined __GNUG__
		#warning foo2
	#endif
}
