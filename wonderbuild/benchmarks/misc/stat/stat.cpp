#include <sys/stat.h>
#include <iostream>
#include <sstream>
#include <errno.h>

int main() {
	time_t max_time;
	struct stat st;
	for(unsigned int i(0); i < 200; ++i)
		for(unsigned int lib(0); lib < 50; ++lib)
			for(unsigned int cpp(0); cpp < 100; ++cpp) {
				std::ostringstream s;
				s << "../../bench/lib_" << lib << "/class_" << cpp << ".cpp";
				if(stat(s.str().c_str(), &st) != 0) {
					std::cerr << errno << '\n';
					return errno;
				}
				if(st.st_mtime > max_time) max_time = st.st_mtime;
	}
	std::cout << max_time << '\n';
	return 0;
}
