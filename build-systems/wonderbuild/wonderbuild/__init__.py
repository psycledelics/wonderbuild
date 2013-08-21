#! /usr/bin/env python
# This source is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2, or (at your option) any later version.
# copyright 2008-2013 members of the psycle project http://psycle.sourceforge.net ; johan boule <bohan@jabber.org>

version = (1, 0)
abi_sig = '6'

class UserReadableException(Exception): pass

if False: # summary of modules

	# main
	def main(): pass
	def run(options, option_collector): pass

	# options
	class OptionDecl(): pass
	class OptionCollector(): pass
	def parse_args(args=None): pass
	def validate_options(options, known_options): pass
	def print_help(help, out, cols): pass
	
	# option_cfg
	class OptionCfg(OptionDecl): pass
	
	# scheduler
	class Scheduler(OptionDecl): pass

	# task
	class task(): pass # @task decorator
	class Task(): pass
	class PurgeablePersistentDict(dict): pass
	class Persistent(): pass
	class SharedTaskHolder(): pass
	class SharedTask(Task, Persistent): pass
	
	# project
	class Project(Task, SharedTaskHolder, OptionDecl): pass

	# script
	class ScriptLoaderTask(Task): pass
	class ScriptTask(Task): pass
	def import_module(node): pass
	
	# filesystem
	class FileSystem(): pass
	class Node(): pass
	def ignore(name): pass

	# signature
	class Sig(): pass

	# fhs
	class FHS(OptionCfg, Persistent): pass

	# install
	class InstallTask(Task, Persistent, OptionDecl): pass

	# check_task
	class DepTask(Task): pass # @property result, def __bool__(self), @property help
	class CheckTask(DepTask, SharedTask, OptionCfg): pass

	# cxx_tool_chain
	class ModDepPhases(DepTask): pass
	class _PreCompileTask(ModDepPhases, Persistent): pass
	class PreCompileTasks(ModDepPhases): pass
	class ModTask(ModDepPhases, Persistent): pass
	class _PkgConfigTask(CheckTask): pass
	class PkgConfigCheckTask(ModDepPhases, _PkgConfigTask): pass
	class MultiBuildCheckTask(ModDepPhases, CheckTask): pass
	class BuildCheckTask(MultiBuildCheckTask): pass
	
	# std_checks
	class ValidCfgCheckTask(BuildCheckTask): pass
	class DestPlatformCheckTask(BuildCheckTask): pass
	class PicFlagDefinesPicCheckTask(BuildCheckTask): pass
	class AutoLinkSupportCheckTask(BuildCheckTask): pass
	class ClangCheckTask(BuildCheckTask): pass
	class MingwCheckTask(BuildCheckTask): pass
	# std_checks.multithreading_spport
	class MultithreadingSupportCheckTask(BuildCheckTask): pass
	class PThreadCheckTask(BuildCheckTask): pass
	# std_checks.dynamic_loading_support
	class DynamicLoadingSupportCheckTask(MultiBuildCheckTask): pass
	class DlfcnCheckTask(MultiBuildCheckTask): pass
	# std_checks.math
	class StdMathCheckTask(MultiBuildCheckTask): pass
	# std_checks.cxx11
	class StdCxx11CheckTask(BuildCheckTask): pass
	# std_checks.cxx1y
	class StdCxx1yCheckTask(BuildCheckTask): pass
	# std_checks.boost
	class BoostCheckTask(MultiBuildCheckTask): pass
	# std_checks.openmp
	class OpenMPCheckTask(BuildCheckTask): pass
	# std_checks.opengl
	class OpenGLCheckTask(BuildCheckTask): pass
	class OpenGLUCheckTask(BuildCheckTask): pass
	class OpenGLUTCheckTask(BuildCheckTask): pass
	# std_checks.dsound
	class DSoundCheckTask(BuildCheckTask): pass
	# std_checks.winmm
	class WinMMCheckTask(BuildCheckTask): pass
	# std_checks.zlib
	class ZLibCheckTask(BuildCheckTask): pass
	
	# logger
	known_options = None # OptionDecl
	def generate_option_help(help): pass # OptionDecl
	def use_options(options): pass
	silent = None
	is_debug = None
	def debug(s): pass
	out = None
	out_is_dumb = None
	def multicolumn_format(list, max_width): pass
	def fold(s, width): pass
	def colored(color, s): pass
	def color_bg_fg_rgb(bg, fg): pass
