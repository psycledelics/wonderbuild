#include <diversalis/operating_system.hpp>
#if !defined DIVERSALIS__OPERATING_SYSTEM__POSIX
	#error "sorry, but your operating system ain't standard"
#endif
#include <dlfcn.h>
#include <string>
#include <sstream>
#include <iostream>
#include <stdexcept>
#include <diversalis/compiler.hpp>

namespace psycle
{
	namespace plugin
	{
		namespace interface
		{
			int const version = 11;
			
			namespace info
			{
				class result
				{
					public:
						int version;
						int flags;
						int parameter_count;
						class parameter ; parameter const ** parameters;
						char const * description;
						char const * name;
						char const * author;
						char const * title;
						int columns;
						
						class parameter
						{
							public:
								char const * name;
								char const * description;
								int minimum_value;
								int maximum_value;
								int flags;
								int default_value;
						};
				};
				
				typedef result & (*function)();
				char const symbol[] = "GetInfo";
			}
		}
		

		void check(std::string const & lib_file_name, std::ostream & out) throw(std::exception)
		{
			out << "loading: " << lib_file_name << " ... " << std::endl;
			void * const lib(::dlopen(lib_file_name.c_str(), RTLD_NOW));
			if(!lib)
			{
				std::ostringstream s;
				s << "error: " << ::dlerror() << std::endl;
				out << s.str() << std::endl;
				out.flush();
				throw std::runtime_error(s.str().c_str());
			}
			try
			{
				out << "loaded fine." << std::endl;
				out << "resolving symbol " << interface::info::symbol << " ..." << std::endl;
				#if \
					defined DIVERSALIS__COMPILER__GNU && \
					( \
						DIVERSALIS__COMPILER__VERSION__MAJOR > 3 || \
						DIVERSALIS__COMPILER__VERSION__MAJOR == 3 && \
						DIVERSALIS__COMPILER__VERSION__MINOR >= 4 \
					)
					interface::info::function function(reinterpret_cast<interface::info::function>(::dlsym(lib, interface::info::symbol)));
				#else
					interface::info::function function((interface::info::function)(::dlsym(lib, interface::info::symbol)));
				#endif
				if(!function)
				{
					std::ostringstream s;
					s << "error: " << ::dlerror() << std::endl;
					out << s.str() << std::endl;
					out.flush();
					throw std::runtime_error(s.str().c_str());
				}
				out << "resolved fine." << std::endl;
				out << "obtaining info ... " << std::endl;
				interface::info::result & info(function());
				out << "interface version: " << info.version << std::endl;
				if(info.version != psycle::plugin::interface::version)
				{
					std::ostringstream s;
					s << "error: interface version missmatch ; expected: " << interface::version << std::endl;
					out << s.str() << std::endl;
					out.flush();
					throw std::runtime_error(s.str().c_str());
				}
				out << "name: " << info.name << std::endl;
				out << "description: " << info.description << std::endl;
				out << "author: " << info.author << std::endl;
				out << "flags: " << info.flags << std::endl;
				out << "columns: " << info.columns << std::endl;
				out << "parameters : " << info.parameter_count << std::endl;
				for(/*unsigned*/ int parameter_index(0) ; parameter_index < info.parameter_count ; ++parameter_index)
				{
					out << "\t" << parameter_index << ":" << std::endl;
					interface::info::result::parameter const & parameter(*info.parameters[parameter_index]);
					out << "\t\t name: " << parameter.name << std::endl;
					out << "\t\t description: " << parameter.description << std::endl;
					out << "\t\t flags: " << parameter.flags << std::endl;
					out << "\t\t minimum value: " << parameter.minimum_value << std::endl;
					out << "\t\t default value: " << parameter.default_value << std::endl;
					out << "\t\t maximum value: " << parameter.maximum_value << std::endl;
				}
			}
			catch(...)
			{
				out << "closing library ... " << std::endl;
				if(::dlclose(lib))
				{
					std::ostringstream s;
					s << "error: " << ::dlerror() << std::endl;
					out << s.str() << std::endl;
					out.flush();
				}
				else
				{
					out << "library closed." << std::endl;
				}
				throw;
			}
			out << "closing library ... " << std::endl;
			if(::dlclose(lib))
			{
				std::ostringstream s;
				s << "error: " << ::dlerror() << std::endl;
				out << s.str() << std::endl;
				out.flush();
				throw std::runtime_error(s.str().c_str());
			}
			out << "library closed." << std::endl;
		}
	}
}

int main(unsigned const int argument_count, char const * arguments[])
{
	if(argument_count != 2)
	{
		std::cerr << arguments[0] << ": " << "usage: " << arguments[0] << " <plugin-name>" << std::endl;
		return 1;
	}
	try
	{
		psycle::plugin::check(arguments[1], std::cout);
	}
	catch(std::exception const & e)
	{
		std::cerr << "caught exception: standard: " << e.what() << std::endl;
		throw;
	}
	catch(...)
	{
		std::cerr << "caught exception: unkown type of exception." << std::endl;
		throw;
	}
}
