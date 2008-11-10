#include

#include 0

#include no

#include ""

#include <>

# include "yes-space"
#	include "yes-tab"

#include <yes-normal>
#include <yes-normal> // subsequent times not reported by gcc

#include </tmp/>
#include <tmp/yes>

//#include "no" "/foo" "/bar"

#define FOO "yes-foo"
#include FOO

#define STRINGIZED(x) STRINGIZED_(x)
#define STRINGIZED_(x) #x

#define BAR yes-bar
#include STRINGIZED(BAR)
#include STRINGIZED(BAR/bong)
#include STRINGIZED_(BAR/bong)

#define TOKEN(x) TOKEN_(x)
#define TOKEN_(x) x
#define TOKENIZED(a, b) TOKENIZED_(a, b)
#define TOKENIZED_(a, b) a##b

#define BONG_BANG_0(f) yes-bong-bang-0/f
#define BONG_BANG_1(f) yes-bong-bang-1/f
#define BONG_BANG_X(x, f) TOKENIZED(BONG_BANG_, x)(f)
#include STRINGIZED(BONG_BANG_X(0, ping))
#include STRINGIZED(BONG_BANG_X(1, pong))

#include "yes-foo\"
#include "yes-fo\\o"

#include "yes-fo/*o" /**///
#include <yes-fo//o> /**/
#include   "yes-a" //
#include	"yes-b"

\/*
*/
	#include "yes-c"

/*
\*/
#include \
	"yes-d"

\// /*
#include "yes-e"
// */

/* // */ #include "yes-f"

#include /* */ "yes-g"

"/*\""
#include "yes-h"
"*/\\"

'/*'
#include "yes-i"
'*/'

\"xxx"
#include "yes-j"
\"xxx"

//#include "no-a"

// \
#include "no-b"

// \
	\
#include "no-c"

/*
#include "no-d"
*/

xxx /* */ #include "no-e"

"xxx \
" \
#include "no-f"
