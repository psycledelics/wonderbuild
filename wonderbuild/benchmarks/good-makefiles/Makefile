# http://books.google.ch/books?id=fp45FtyUNQ4C&pg=PA11&lpg=PA11&dq=gnu+make+vpath&source=bl&ots=QEdI3VV9jo&sig=ru8LGzdTWxs4rxcDSrREcYtXHEI&hl=en&sa=X&oi=book_result&resnum=2&ct=result#PPA37,M1

#  -r, --no-builtin-rules      Disable the built-in implicit rules.
#  -R, --no-builtin-variables  Disable the built-in variable settings.

# http://make.paulandlesley.org/multi-arch.html

.SUFFIXES:

ifndef _ARCH
 _ARCH := $(shell print_arch)
 export _ARCH
endif

OBJDIR := _$(_ARCH)

MAKETARGET = $(MAKE) --no-print-directory -C $@ -f $(CURDIR)/Makefile \
	SRCDIR=$(CURDIR) $(MAKECMDGOALS)

.PHONY: $(OBJDIR)

$(OBJDIR):
	+@ test -d $@ || mkdir -p $@
	+@$(MAKETARGET)
	
Makefile : ;
%.mk :: ;
% :: $(OBJDIR) ; :

.PHONY: clean

clean: rm -Rf $(OBJDIR)
