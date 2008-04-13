#include <iostream>

__attribute__((dllexport)) void f() {
	std::cout << "f\n";
}
