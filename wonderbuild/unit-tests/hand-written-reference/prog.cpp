#include <foo.hpp>

int main() {
	class foo foo;
	foo.say_hello();
	return 0;
}

#include <iostream>

void foo::undefined() {
	std::cout << "defined!" << std::endl;
}
