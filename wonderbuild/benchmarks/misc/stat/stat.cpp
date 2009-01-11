#include <sys/stat.h>
#include <iostream>
#include <errno.h>

int main() {
	time_t max_time;
	struct stat st;
	for(unsigned int i(0); i < 1000000; ++i) {
		if(stat(".", &st) != 0) {
			std::cerr << errno << '\n';
			return errno;
		}
		if(st.st_mtime > max_time) max_time = st.st_mtime;
	}
	std::cout << max_time << '\n';
	return 0;
}
