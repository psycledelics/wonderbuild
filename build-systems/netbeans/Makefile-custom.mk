dir = ../wonderbuild

all:
	$(dir)/wonderbuild_script.py --source-abs-paths=yes --cxx-flags='-g3 -gdwarf-2'

clean:
	rm -Rfv $(dir)/++wonderbuild
