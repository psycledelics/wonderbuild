# !/usr/bin/m4

##############################################################################
#
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# Copyright (C) 1999-2005 Psycledelics http://psycle.pastnotecut.org : Johan Boule
# Some macro are Copyright (C) Alexandre Duret-Lutz <duret_g@epita.fr> and Guiodo Draheim <guidod@gmx.de>
#
# m4 macros for autoconf included by ./configure.ac
# \meta hook ./configure.ac
# \meta generic
# \meta standard posix
#
##############################################################################



###############################################################################################
###############################################################################################
###############################################################################################
# modules



# This macro is called by configure.ac and sets PKG_CONFIG_PATH so it contains paths to nested source packages.
AC_DEFUN([PACKAGENERIC__MODULE__EXTERNAL__PATH],
	[
		if PACKAGENERIC__CONFIGURATION__OPTION__WITH(nested_source_packages)
		then
			. $srcdir/packageneric/generic/detail/libexec/find &&
			packageneric__module__external__path()
			{
				local packages package__modules
				packages=[$]1
				echo $packages/ ...
				for package in $(cd $srcdir/$packages && eval find . -maxdepth 1 $(packageneric__find__dir__no_arch))
				do
					echo $packages/$package
					package__modules=$packages/$package/packageneric/package/modules
					PACKAGENERIC__MODULE__EXTERNAL__PATH__INCLUDES="-I$packages/$package/src -I\$(top_srcdir)/$packages/$package/src $PACKAGENERIC__MODULE__EXTERNAL__PATH__INCLUDES"
					case $build in
						*-*-mingw* | *-*-windows* )
							package__modules=$(cmd //c cd)$(echo /$package__modules | sed 's:/:\\:g')
							case $host in
								*-*-mingw* | *-*-windows* )
									PACKAGENERIC__MODULE__EXTERNAL__PATH__PATH=$packages/$package\\.libs\;$PACKAGENERIC__MODULE__EXTERNAL__PATH__PATH
								;;
							esac
							package__modules=$package__modules\\pkgconfig\;
						;;
						* )
							package__modules=$(pwd)/$package__modules/pkgconfig$PATH_SEPARATOR
						;;
					esac
					PACKAGENERIC__MODULE__EXTERNAL__PATH__PKG_CONFIG_PATH=$package__modules$PACKAGENERIC__MODULE__EXTERNAL__PATH__PKG_CONFIG_PATH
					if test -d $(cd $srcdir/$packages && pwd)/$package/packageneric/package/nested
					then
						packageneric__module__external__path $packages/$package/packageneric/package/nested
					fi
				done
			}
			packageneric__echo module: external: path ...
			packageneric__module__external__dir=
			if test $(basename $(dirname $(pwd))) = nested
			then
				while test $(basename $(cd ${packageneric__module__external__dir:-.}/.. && pwd)) = nested
				do
					packageneric__module__external__dir=${packageneric__module__external__dir:-.}/../../../..
				done
				packageneric__module__external__dir=${packageneric__module__external__dir:-.}/packageneric/package/nested
			elif test -d $srcdir/packageneric/package/nested
			then
				packageneric__module__external__dir=packageneric/package/nested
			fi
			if test -n "$packageneric__module__external__dir"
			then
				PACKAGENERIC__MODULE__EXTERNAL__PATH__INCLUDES=
				PACKAGENERIC__MODULE__EXTERNAL__PATH__PKG_CONFIG_PATH=$PKG_CONFIG_PATH
				case $host in
					*-*-mingw* | *-*-windows* )
						PACKAGENERIC__MODULE__EXTERNAL__PATH__PATH=
						for dir in $(echo $PATH | sed "s/$PATH_SEPARATOR/ /g") # IFS
						do
							PACKAGENERIC__MODULE__EXTERNAL__PATH__PATH=$PACKAGENERIC__MODULE__EXTERNAL__PATH__PATH\;$(cd $dir && cmd //c cd)
						done
					;;
				esac
				echo $packageneric__module__external__dir/ = $(cd $srcdir/$packageneric__module__external__dir && pwd)
				packageneric__module__external__path $packageneric__module__external__dir
			fi
			#packageneric__echo module: external: path: path: $PACKAGENERIC__MODULE__EXTERNAL__PATH__PATH
			packageneric__echo module: external: path: pkg-config: path: $PACKAGENERIC__MODULE__EXTERNAL__PATH__PKG_CONFIG_PATH
			#packageneric__echo module: external: path: includes: $PACKAGENERIC__MODULE__EXTERNAL__PATH__INCLUDES
			AC_SUBST(PACKAGENERIC__MODULE__EXTERNAL__PATH__PATH)
			AC_SUBST(PACKAGENERIC__MODULE__EXTERNAL__PATH__PKG_CONFIG_PATH)
			AC_SUBST(PACKAGENERIC__MODULE__EXTERNAL__PATH__INCLUDES)
		fi
	]
)

# Call this in the modules.external.ac file to get the needed flags to link against a lib which provides a pkg-config file (.pc) ; man (8) pkg-config.
# The supplied informations will be used for:
# - the compilation of your translation units (source files) to object files.
# - the link phase of the compilation of your binaries.
# - the creation of pkg-config files (.pc) for your libraries, which describing their dependencies ; man (8) pkg-config.
# - the creation of the dependency graph (graphviz dot) of libraries.
AC_DEFUN([PACKAGENERIC__MODULE__EXTERNAL],
	[
		# dnl # AC_REQUIRE([PACKAGENERIC__MODULE__EXTERNAL__PATH])
		# dnl # AC_REQUIRE([PKG_CHECK_MODULES])
		packageneric__echo module: external: [$1]  '$2'
		packageneric__module__external__found=false
		if test -n "$packageneric__module__external__dir"
		then
			for dependency in $(echo "$2")
			do
				if $(echo $dependency | cut --characters 1 | grep --silent $(echo -e "\133")a-zA-Z$(echo -e "\135"))
				then
					packageneric__module__external=$(cd $srcdir/$packageneric__module__external__dir && eval find . $(packageneric__find__file__no_arch \\\( -path \\\*/packageneric/package/modules/lib.$dependency.am -or -path \\\*/packageneric/package/modules/hpp.$dependency.am \\\)) | sort)
					if test -n "$packageneric__module__external"
					then
						dirname $packageneric__module__external 1>/dev/null 2>&1 ||
						{
							packageneric__echo module: external: nested-source-package: module $dependency appears several times in nested source packages under $(cd $srcdir/$packageneric__module__external__dir && pwd), possibly duplicated source package:
							packageneric__echo module: external: nested-source-package; $packageneric__module__external
							AC_MSG_ERROR([packageneric.module.external.nested-source-package: nested source package found several times])
						}
						packageneric__echo module: external: nested-source-package: $(pwd)/$packageneric__module__external__dir/$(dirname $packageneric__module__external)/pkgconfig
						$1__CFLAGS="$[$1__CFLAGS] \`PKG_CONFIG_PATH='\$(PACKAGENERIC__MODULE__EXTERNAL__PATH__PKG_CONFIG_PATH)' \$(PKG_CONFIG) --cflags $dependency\`"
						$1__LIBS="$[$1__LIBS] \`PKG_CONFIG_PATH='\$(PACKAGENERIC__MODULE__EXTERNAL__PATH__PKG_CONFIG_PATH)' \$(PKG_CONFIG) --libs $dependency\`"
						packageneric__module__external__found=true
					fi
					unset packageneric__module__external
				fi
			done
		fi
		if test "$packageneric__module__external__found" != true
		then
			packageneric__echo module: external: pkg-config
			PKG_CHECK_MODULES([$1_], [$2])
		fi
		$1__REQUIRED="$2"
		echo $1__CFLAGS = "$[$1__CFLAGS]"
		echo $1__LIBS = "$[$1__LIBS]"
		unset packageneric__module__external__found
	]
)

# Call this in the modules.external.ac file when you need to link against a lib which doesn't provide a pkg-config file (.pc) ; man (8) pkg-config.
# The supplied informations will be used for:
# - the compilation of your translation units (source files) to object files.
# - the link phase of the compilation of your binaries.
# - the creation of pkg-config files (.pc) for your libraries, which describe their dependencies ; man (8) pkg-config.
# - the creation of the dependency graph (graphviz dot) of libraries.
AC_DEFUN([PACKAGENERIC__MODULE__EXTERNAL__DEFINE],
	# 1: the prefixes of variables where we want to put the needed compiler (xxx__CFLAGS) and linker (xxx__LIBS) options for the libraries you depends on (e.g FOO, for FOO__CFLAGS FOO__LIBS)
	# 2: xxx__LIBS options (e.g -l-lib-foo)
	# 3: xxx__CFLAGS options (e.g. -I/usr/include/foo-2.1.0)
	# 4: the libraries you depend on, as a pkg-config requirement expression (e.g. foo >= 2.0 bar = 1.0.1)
	[
		packageneric__echo module: external: define: '$1  $4'
		$1__MISSING_PKG_CONFIG=true
		$1__LIBS="$2"
		$1__CFLAGS="$3"
		$1__REQUIRED="$4"
		packageneric__echo module: external: define: $1__CFLAGS = "$[$1__CFLAGS]"
		packageneric__echo module: external: define: $1__LIBS = "$[$1__LIBS]"
	]
)

# called once by configure.ac before it includes the modules.internal.ac file.
# This writes the start of the dependency graph (graphviz dot) of libraries.
AC_DEFUN([PACKAGENERIC__MODULE__INTERNAL__LIST__BEGIN],
	[
		packageneric__echo module: internal: list: begin:
		packageneric__modules__pkgconfig=packageneric/package/modules/pkgconfig
		#AC_REQUIRE([AS_MKDIR_P])
		AS_MKDIR_P($packageneric__modules__pkgconfig)
		packageneric__modules__dependencies__dot=packageneric/package/modules/dependencies.dot
		echo -e "digraph dependencies" > $packageneric__modules__dependencies__dot
		echo -e "{" >> $packageneric__modules__dependencies__dot
		echo -e "\tlabel = \"module dependencies, transitive graph\" rankdir = TB labelloc = t fontname = helvetica fontsize = 14 bgcolor = palegoldenrod concentrate = true ratio = auto" >> $packageneric__modules__dependencies__dot
		echo -e "\tnode \133 shape = record style = rounded fillcolor = lemonchiffon1 fontname = helvetica fontsize = 10 \135" >> $packageneric__modules__dependencies__dot
		echo -e "\tsubgraph cluster__$PACKAGENERIC__PACKAGE__NAME" >> $packageneric__modules__dependencies__dot
		echo -e "\t{" >> $packageneric__modules__dependencies__dot
		echo -e "\t\tlabel = \"$PACKAGENERIC__PACKAGE__NAME $PACKAGENERIC__PACKAGE__VERSION - $PACKAGENERIC__PACKAGE__DESCRIPTION\" bgcolor = khaki3" >> $packageneric__modules__dependencies__dot
		echo -e "\t\tnode \133 style = filled \135" >> $packageneric__modules__dependencies__dot
	]
)

# called once by configure.ac after it has included the modules.internal.ac file.
# This writes the end of the dependency graph (graphviz dot) of libraries.
AC_DEFUN([PACKAGENERIC__MODULE__INTERNAL__LIST__END],
	[
		echo -e "\t}" >> $packageneric__modules__dependencies__dot
		echo -en "$packageneric__modules__dependencies__dot__graph" >> $packageneric__modules__dependencies__dot
		echo -e "}" >> $packageneric__modules__dependencies__dot
		packageneric__echoing "module: dependencies:" cat $packageneric__modules__dependencies__dot
		unset packageneric__modules__dependencies__dot__graph
		unset packageneric__modules__dependencies__dot
		unset packageneric__modules__pkgconfig
		packageneric__echo module: internal: list: end.
	]
)

# Call this macro in the modules.internal.ac file to declare your own libraries or programs.
# For libraries, this creates a pkg-config file (.pc) which describing their dependencies ; man (8) pkg-config.
# It also adds nodes to the dependency graph (graphviz dot) of libraries and programs.
AC_DEFUN([PACKAGENERIC__MODULE__INTERNAL],
	# 1: the type of the module, either lib, hpp, or bin
	# 2: the name of your library (without the 'lib' prefix) or program (e.g.: foo.bar)
	# 3: the libtool version information (libtool's -version-info option) for your library (e.g.: 10:55:3)
	# 4: the prefixes of variables where we can find the needed compiler (xxx__CFLAGS) and linker (xxx__LIBS) options for the libraries your library or program depends on, and the pkg-config requirements (xxx__REQUIRED) (e.g FOO BAR, for FOO__CFLAGS FOO__LIBS FOO__REQUIRED BAR__CFLAGS BAR__LIBS BAR__REQUIRED)
	# 5: a one-line decription of your library or program
	# 6: compiler options
	# 7: linker options
	[
		packageneric__module__type=$1
		packageneric__module=$2
		packageneric__module__libtool__version_info=$3 # not for programs
		packageneric__module__dependencies__prefixes="$4"
		packageneric__module__description="$5"
		packageneric__module__description=$(echo $packageneric__module__description | sed 's: $::g')
		packageneric__module__cflags="$6"
		packageneric__module__libs="$7"

		packageneric__echo__no_new_line module: internal: "$packageneric__module$(if test $packageneric__module__type = bin ; then echo ' (leaf-program)' ; fi), dependencies: $packageneric__module__requires"

		for dependency_prefix in $packageneric__module__dependencies__prefixes
		do
			packageneric__module__dependencies__libs__internal="$packageneric__module__dependencies__libs__internal $(eval echo \'\$${dependency_prefix}__LIBS__INTERNAL\')"
			packageneric__module__dependencies__libs="$packageneric__module__dependencies__libs $(eval echo \'\$${dependency_prefix}__LIBS\')"
			packageneric__module__dependencies__cflags="$packageneric__module__dependencies__cflags $(eval echo \'\$${dependency_prefix}__CFLAGS\')"
			if test -z "$(eval echo \$${dependency_prefix}__REQUIRED)"
			then
				packageneric__echo__no_new_line__inline "$packageneric__module__dependencies__prefixes"
				echo
				packageneric__echo "modules: internal: $packageneric__module: requires the group $dependency_prefix, which is not defined."
				AC_MSG_ERROR([packageneric: module: internal: missing definition for internal module dependency])
			fi
			if test "$(eval echo \$${dependency_prefix}__MISSING_PKG_CONFIG)" = true
			then
				packageneric__module__required__missing_pkg_config="$packageneric__module__required__missing_pkg_config $(eval echo \$${dependency_prefix}__REQUIRED)"
				packageneric__module__dependencies__libs__missing_pkg_config="$packageneric__module__dependencies__libs__missing_pkg_config $(eval echo \$${dependency_prefix}__LIBS)"
				packageneric__module__dependencies__cflags__missing_pkg_config="$packageneric__module__dependencies__cflags__missing_pkg_config $(eval echo \$${dependency_prefix}__CFLAGS)"
			else
				packageneric__module__required="$packageneric__module__required $(eval echo \$${dependency_prefix}__REQUIRED)"
			fi
		done

		if test $packageneric__module__type != bin
		then
			{
				cat <<-eof > $packageneric__modules__pkgconfig/${packageneric__module}-uninstalled.pc
					src=$(cd $srcdir && pwd)
					build=$(pwd)
					
					Name: $packageneric__module $packageneric__module__libtool__version_info $host
					Description: $packageneric__module__description
					Version: $PACKAGENERIC__PACKAGE__VERSION
					Cflags: -I\${src}/src -I\${build}/src $packageneric__module__dependencies__cflags__missing_pkg_config $packageneric__module__cflags
					Libs: $(if test $packageneric__module__type = lib ; then echo "\${build}/lib-$packageneric__module.la" ; fi) $packageneric__module__dependencies__libs__missing_pkg_config $packageneric__module__libs
					Requires: $packageneric__module__required
				eof
			}
			{
				cat <<-eof > $packageneric__modules__pkgconfig/$packageneric__module.pc
					prefix=$prefix
					exec_prefix=$(if test "$exec_prefix" = NONE ; then echo \${prefix} ; else echo $exec_prefix ; fi)
					pkgversion=$PACKAGENERIC__PACKAGE__VERSION
					pkgnameversion=$PACKAGENERIC__PACKAGE__NAME-\${pkgversion}
					pkgversionlibdir=$libdir/\${pkgnameversion}
					pkgversionincludedir=$includedir/\${pkgnameversion}
					pkgversionsharedincludedir=$datadir/$(basename $includedir)\${pkgnameversion}
					
					Name: $packageneric__module $packageneric__module__libtool__version_info $host
					Description: $packageneric__module__description
					Version: \${pkgversion}
					Cflags: -I\${pkgversionincludedir} $packageneric__module__dependencies__cflags__missing_pkg_config $packageneric__module__cflags
					Libs: $(if test $packageneric__module__type = lib ; then echo "-L\${pkgversionlibdir} -l-$packageneric__module" ; fi) $packageneric__module__dependencies__libs__missing_pkg_config $packageneric__module__libs
					Requires: $packageneric__module__required
				eof
			}
		fi

		for dependency in $packageneric__module__dependencies__libs__missing_pkg_config $packageneric__module__libs
		do
			if $(echo $dependency | cut --characters 1-2 | grep --silent '^-l')
			then
				packageneric__module__dependencies="$packageneric__module__dependencies $(echo $dependency | sed 's/^-l//' | sed 's/^-//')"
			fi
		done

		for dependency in $packageneric__module__required $packageneric__module__required__missing_pkg_config
		do
			if $(echo $dependency | cut --characters 1 | grep --silent $(echo -e "\133")a-zA-Z$(echo -e "\135"))
			then
				packageneric__module__dependencies="$packageneric__module__dependencies $dependency"
			else
				:
				# would be good to output the version constraint too
			fi
		done

		packageneric__echo__no_new_line__inline " $packageneric__module__dependencies"
		echo

		echo -e "\t\t\"$packageneric__module$(if test $packageneric__module__type = bin ; then echo " (leaf-program)"; fi)\" \133 label = \"{$packageneric__module$(if test $packageneric__module__type = bin ; then echo " (leaf-program)"; fi) | $packageneric__module__description}\" \135;" >> $packageneric__modules__dependencies__dot
		for dependency in $packageneric__module__dependencies
		do
			packageneric__modules__dependencies__dot__graph="$packageneric__modules__dependencies__dot__graph\t\"$packageneric__module$(if test $packageneric__module__type = bin ; then echo " (leaf-program)"; fi)\" -> \"$dependency\" ;\n"
		done

		packageneric__module__prefix=$(if test $packageneric__module__type = bin ; then echo BIN__ ; fi)PACKAGENERIC__NORMALIZED_NAME($packageneric__module)
		eval ${packageneric__module__prefix}__CFLAGS=\"$packageneric__module__dependencies__cflags $packageneric__module__cflags\"
		eval ${packageneric__module__prefix}__LIBS__NO_SELF=\"$packageneric__module__dependencies__libs $packageneric__module__libs\"
		eval ${packageneric__module__prefix}__LIBS__NO_SELF__INTERNAL=\"$packageneric__module__dependencies__libs__internal\"
		if test $packageneric__module__type != bin
		then
			if test $packageneric__module__type = lib
			then
				eval ${packageneric__module__prefix}__LIBS__INTERNAL=\"lib-$packageneric__module.la\"
			fi
			eval ${packageneric__module__prefix}__LIBS=\"\$${packageneric__module__prefix}__LIBS__INTERNAL \$${packageneric__module__prefix}__LIBS__NO_SELF\"
		fi
		eval ${packageneric__module__prefix}__REQUIRED=\"$packageneric__module = $PACKAGENERIC__PACKAGE_META_INFORMATION__VERSION\"
		eval ${packageneric__module__prefix}__VERSION=$packageneric__module__libtool__version_info # not for programs
		eval ${packageneric__module__prefix}__DESCRIPTION=\"$packageneric__module__description\"
		
		#AC_MSG_NOTICE()
		echo ${packageneric__module__prefix}__CFLAGS = $(eval echo \$${packageneric__module__prefix}__CFLAGS)
		echo ${packageneric__module__prefix}__LIBS__NO_SELF = $(eval echo \$${packageneric__module__prefix}__LIBS__NO_SELF)

		unset packageneric__module
		unset packageneric__module__type
		unset packageneric__module__libtool__version_info
		unset packageneric__module__dependencies__prefixes
		unset packageneric__module__description
		unset packageneric__module__cflags
		unset packageneric__module__libs

		unset packageneric__module__prefix
		unset packageneric__module__dependencies
		unset packageneric__module__dependencies__cflags
		unset packageneric__module__dependencies__cflags__missing_pkg_config
		unset packageneric__module__dependencies__libs
		unset packageneric__module__dependencies__libs__missing_pkg_config
		unset packageneric__module__dependencies__libs__internal
		unset packageneric__module__required
		unset packageneric__module__required__missing_pkg_config
	]
)
