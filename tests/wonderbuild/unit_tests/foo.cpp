# include "yes"
#	include "yes"

#include <yes>
#include </tmp/yes>

//#include "no" "/foo" "/bar"

#define FOO "yes-foo"
#include FOO

#define FOO_(x) x "/bar"
#include FOO_(FOO)

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
