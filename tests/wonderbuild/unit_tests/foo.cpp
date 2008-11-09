#include <absolute>

//#include "relative" "foo"

#define FOO "relative" "foo"
#define FOO_(x) FOO__(x)
#define FOO__(x) #x
#include FOO_(FOO)

#include "foo\"
#include "fo\\o"

#include "fo/o" /**///
#include <fo/o> /**/
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

/* */ #include "yes-f"

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
