#include "foo.hpp"

void foo::say_hello() {
	bar.say_hello();
	undefined();
}
