#ifndef FOO__FOO2_HPP
#define FOO__FOO2_HPP
#pragma once

#include "foo.hpp"

typedef void (*foo_func)();

FOO_LINK void foo2(foo_func = foo);

#endif
