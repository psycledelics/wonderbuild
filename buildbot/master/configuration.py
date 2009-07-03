import os

try: del os.environ['TERM']
except KeyError: pass

BuildmasterConfig = {}

project_name = 'psycle'
BuildmasterConfig['projectName'] = project_name
BuildmasterConfig['projectURL'] = 'http://' + project_name + '.sourceforge.net'

master_port = 8010
from socket import getfqdn
master_host_fqdn = getfqdn()
try: domain = master_host_fqdn[master_host_fqdn.index('.') + 1:]
except: domain = ''
username = 'buildbot' # or use getent to get the effective username
email = username + '@' + domain
BuildmasterConfig['buildbotURL'] = 'http://' + master_host_fqdn + ':' + str(master_port) + '/'

BuildmasterConfig['sources'] = []

#from buildbot.changes.pb import PBChangeSource
#BuildmasterConfig['sources'].append(PBChangeSource()) # prefix = branch_filter

branch = 'trunk'
svn_url = 'https://' + project_name + '.svn.sourceforge.net/svnroot/' + project_name + '/' + branch
svn_dir = project_name + '-' + branch + os.sep
poll_interval = 5 * 60
bunch_timer = poll_interval + 15
hist_max = poll_interval * 2 // 60

from buildbot.changes.svnpoller import SVNPoller
BuildmasterConfig['sources'].append(SVNPoller(svnurl = svn_url, pollinterval = poll_interval, histmax = hist_max))
branch_filter = '' # the branch is stripped automatically from paths in changset notifications

BuildmasterConfig['slavePortnum'] = 9989

slaves = ['anechoid', 'factoid']
microsoft_slaves = ['winux', 'alk']
microsoft_slaves_msvc = ['winux']

BuildmasterConfig['bots'] = [
	('anechoid', 'password'),
	('factoid', 'password'),
	('winux', 'password'),
	('alk', 'alk')
]

BuildmasterConfig['debugPassword'] = 'debugpassword'

BuildmasterConfig['builders'] = []
BuildmasterConfig['schedulers'] = []

from buildbot.scheduler import Scheduler as BaseScheduler
class Scheduler(BaseScheduler):
	def __init__(self, *args, **kw):
		kw['branch'] = None
		kw['treeStableTimer'] = bunch_timer
		BaseScheduler.__init__(self, *args, **kw)

	def addUnimportantChange(self, change):
		from twisted.python import log
		log.msg("%s: change is not important, forgetting %s" % (self, change))

def filter(change, include_prefixes = None, exclude_prefixes = None):
	for file in change.files:
		if exclude_prefixes is not None:
			for prefix in exclude_prefixes:
				if file.startswith(branch_filter + prefix): return False
		if include_prefixes is not None:
			for prefix in include_prefixes:
				if file.startswith(branch_filter + prefix): return True
	return False

from buildbot import locks
svn_lock = locks.SlaveLock('svn')
compile_lock = locks.SlaveLock('compile')
upload_lock = locks.SlaveLock('upload')
all_locks = [svn_lock, compile_lock, upload_lock]

from buildbot.process import factory
from buildbot.steps.source import SVN
from buildbot.steps.shell import ShellCommand as BaseShellCommand, Compile as BaseCompile, Test as BaseTest
from buildbot.status.builder import SUCCESS, WARNINGS, FAILURE, SKIPPED, EXCEPTION

##################################### custom build steps ######################################

class SVNUpdate(SVN):
	def __init__(self, *args, **kw):
		kw['retry'] = (600, 3)
		kw['mode'] = 'update'
		kw['svnurl'] = svn_url
		if False: kw['defaultBranch'] = 'trunk'
		kw['locks'] = [svn_lock]
		SVN.__init__(self, *args, **kw)

def handle_microsoft_kw(kw):
	if 'microsoft' in kw:
		if kw['microsoft']:
			command = 'call ../../../dev-pack '
			if 'msvc' in kw:
				if kw['msvc']: command += '_ msvc_solution'
				del kw['msvc']
			command += ' && ' + kw.get('command', '')
			command = command.replace('/', '\\')
			if 'no_slash_inversion_command' in kw:
				command += ' && ' + kw['no_slash_inversion_command']
				del kw['no_slash_inversion_command']
			kw['command'] = command
		del kw['microsoft']

class Test(BaseTest):
	def __init__(self, *args, **kw):
		kw['locks'] = [compile_lock]
		handle_microsoft_kw(kw)
		BaseTest.__init__(self, *args, **kw)

class PolicyCheck(Test):
	name = 'policy-check'
	description = ['checking policy']
	descriptionDone = ['policy']
	def __init__(self, *args, **kw):
		kw['command'] = 'python ./tools/check-policy ' + ' '.join(kw['dirs'])
		del kw['dirs']
		Test.__init__(self, *args, **kw)
	def evaluateCommand(self, cmd):
		if cmd.rc != 0: return WARNINGS
		return SUCCESS
	warnOnWarnings = True

class Compile(BaseCompile):
	def __init__(self, *args, **kw):
		kw['locks'] = [compile_lock]
		handle_microsoft_kw(kw)
		BaseCompile.__init__(self, *args, **kw)

class BoostTest(Test):
	def __init__(self, *args, **kw):
		kw['command'] = kw['path'] + ' --log_level=test_suite --report_level=detailed'
		del kw['path']
		handle_microsoft_kw(kw)
		BaseTest.__init__(self, *args, **kw)

class ShellCommand(BaseShellCommand):
	def __init__(self, *args, **kw):
		handle_microsoft_kw(kw)
		BaseShellCommand.__init__(self, *args, **kw)

class Upload(ShellCommand):
	name = 'upload'
	description = ['uploading']
	descriptionDone = ['uploaded']
	command = ['echo download the package at http://psycle.sourceforge.net/packages']
	# call ..\\..\\..\\dev-pack && cd freepsycle && sh -c ./make-microsoft-raw-package
	# scp \
	#	-F ../../../../.ssh/config \
	#	freepsycle/++wonderbuild/freepsycle.tar.bz2 \
	#	upload.buildborg.retropaganda.info:psycle/htdocs/packages/microsoft/ && \
	#	echo download the package at http://psycle.sourceforge.net/packages/microsoft/freepsycle.tar.bz2

if False: # following not used yet. would help in having less repetitive build definitions

	class Upload(ShellCommand):
		name = 'upload'
		description = ['uploading']
		descriptionDone = ['uploaded']
		def __init__(self, *args, **kw):
			kw['locks'] = []
			kw['no_slash_inversion_command'] = (
				'scp -F ../../../../.ssh/config ' +
				'%(src)s/%(file)s upload.buildborg.retropaganda.info:psycle/htdocs/packages/%(dst)s/ && ' +
				'echo download the package at http://psycle.sourceforge.net/packages/%(dst)s'
				) % {'file': kw['file'], 'src': kw['src'], 'dst': kw['dst']}
			del kw['file']; del kw['src']; del kw['dst']
			ShellCommand.__init__(self, *args, **kw)

	def append_standard_builders(
		name, trigger_dirs,
		category = 'psycle', update_step = factory.s(SVNUpdate), build_dir = svn_dir,
		policy_check_dirs = None, compile_command = None, build_system = 'wonderbuild', test_command = None, boost_test = False,
		unix = True, mingw = True, mingw_pkg = None, mingw_pkg_command = None, msvc = True,
	):
		def append(name, variant, slaves, compile_command, mingw = False, msvc = False):
			microsoft = mingw or msvc

			factory_steps = [update_step]

			if policy_check_dirs is None: policy_check_dirs = [name]
			if policy_check_dirs: factory_steps.append(factory.s(PolicyCheck, microsoft = microsoft, dirs = policy_check_dirs))

			if not compile_command:
				if build_system == 'wonderbuild': compile_command = 'python ' + name + '/wonderbuild_script.py'
				elif build_system == 'waf': compile_command = 'waf --srcdir=' + name
				elif build_system == 'scons': compile_command = 'scons --directory=' + name
				elif build_system == 'autotools': compile_command = \
					'cd ' + name + ' &&' + \
					'if test -f autogen.sh; then sh autogen.sh --prefix=$(dirname $(pwd))/install ' + \
					'else sh configure --prefix=$(dirname $(pwd))/install; fi && ' + \
					'make install'
				elif build_system == 'qmake': compile_command = \
					'cd ' + name + ' && ' + \
					'qmake -recursive CONFIG-=debug_and_release CONFIG-=debug && ' + \
					(mingw and 'mingw32-make' or msvc and 'nmake' or 'make')
			elif callable(compile_command): compile_command = compile_command(microsoft, mingw, msvc)

			factory_steps.append(factory.s(Compile, microsoft = microsoft, mingw = mingw, msvc = msvc, command = compile_command))

			if boost_test and build_system == 'wonderbuild': test_command = \
				'./++wonderbuild/staged-install/usr/local/bin/' + name + '-unit-tests' + \
				' --log_level=test_suite --report_level=detailed'
			if test_command: factory_steps.append(factory.s(Test, microsoft = microsoft, command = test_command))

			BuildmasterConfig['builders'].append({
				'category': category,
				'name': name + variant,
				'slavenames': slaves,
				'builddir': build_dir + name + variant,
				'factory': factory.BuildFactory(factory_steps)
			})
			BuildmasterConfig['schedulers'].append(Scheduler(
				name = name + variant,
				builderNames = [name + variant],
				fileIsImportant = lambda change: filter(change, trigger_dirs)
			))
		if unix:  append(name, '', slaves, compile_command)
		if mingw: append(name, '.mingw', microsoft_slaves, compile_command, mingw = True)
		if msvc:  append(name, '.msvc', microsoft_slaves_msvc, compile_command, msvc = True)
		if mingw_pkg:
			if isinstance(ming_pkg, bool) and build_system:
				if   build_system == 'wonderbuild': mingw_pkg = '++wonderbuild/staged-install'
				elif build_system == 'qmake': mingw_pkg = '++install'
			mingw_pkg_command = mingw_pkg_command or ('cd ' + name + ' && sh -c make-microsoft-raw-package')
			BuildmasterConfig['builders'].append({
				'category': category,
				'name': name + variant + '.pkg',
				'slavenames': microsoft_slaves,
				'builddir': build_dir + name + variant + '.pkg',
				'factory': factory.BuildFactory([
					factory.s(update_step),
					factory.s(Compile, microsoft = True, command = mingw_pkg_command),
					factory.s(Upload, file = name + '.tar.bz2', src = name + '/' + mingw_pkg, dst = 'microsoft')
			])})

##################################### universalis builders ######################################

universalis_deps = ['universalis/', 'diversalis/', 'build-systems/']

if False: # following not used yet. would help in having less repetitive build definitions
	append_standard_builders(
		name = 'universalis',
		trigger_dirs = universalis_deps,
		policy_check_dirs = universalis_deps,
		boost_test = True
	)
else:
	BuildmasterConfig['builders'].append(
		{
			'name': 'universalis',
			'category': 'psycle',
			'slavenames': slaves,
			'builddir': svn_dir + 'universalis',
			'factory': factory.BuildFactory(
				[
					factory.s(SVNUpdate),
					factory.s(PolicyCheck, dirs = ['diversalis', 'universalis']),
					factory.s(Compile, command = './universalis/wonderbuild_script.py'),
					factory.s(BoostTest, path = './universalis/++wonderbuild/staged-install/usr/local/bin/universalis-unit-tests')
				]
			)
		}
	)
	BuildmasterConfig['schedulers'].append(
		Scheduler(
			name = 'universalis',
			builderNames = ['universalis'],
			fileIsImportant = lambda change: filter(change, universalis_deps)
		)
	)

##################################### psycle-helpers builders ######################################

psycle_helpers_deps = ['psycle-helpers/'] + universalis_deps

if False: # following not used yet. would help in having less repetitive build definitions
	append_standard_builders(
		name = 'psycle-helpers',
		trigger_dirs = psycle_helpers_deps,
		boost_test = True
	)
else:
	BuildmasterConfig['builders'].append(
		{
			'name': 'psycle-helpers',
			'category': 'psycle',
			'slavenames': slaves,
			'builddir': svn_dir + 'psycle-helpers',
			'factory': factory.BuildFactory(
				[
					factory.s(SVNUpdate),
					factory.s(PolicyCheck, dirs = ['psycle-helpers']),
					factory.s(Compile, command = './psycle-helpers/wonderbuild_script.py'),
					factory.s(BoostTest, path = './psycle-helpers/++wonderbuild/staged-install/usr/local/bin/psycle-helpers-unit-tests')
				]
			)
		}
	)
	BuildmasterConfig['schedulers'].append(
		Scheduler(
			name = 'psycle-helpers',
			builderNames = ['psycle-helpers'],
			fileIsImportant = lambda change: filter(change, psycle_helpers_deps)
		)
	)

##################################### freepsycle builders ######################################

freepsycle_deps = ['freepsycle/'] + psycle_helpers_deps

if False: # following not used yet. would help in having less repetitive build definitions
	append_standard_builders(
		name = 'freepsycle',
		trigger_dirs = freepsycle_deps,
		mingw_pkg = True
	)
else:
	BuildmasterConfig['builders'].append(
		{
			'name': 'freepsycle',
			'category': 'psycle',
			'slavenames': slaves,
			'builddir': svn_dir + 'freepsycle',
			'factory': factory.BuildFactory(
				[
					factory.s(SVNUpdate),
					factory.s(PolicyCheck, dirs = ['freepsycle']),
					factory.s(Compile, command = './freepsycle/wonderbuild_script.py')
				]
			)
		}
	)
	BuildmasterConfig['schedulers'].append(
		Scheduler(
			name = 'freepsycle',
			builderNames = ['freepsycle'],
			fileIsImportant = lambda change: filter(change, freepsycle_deps)
		)
	)

##################################### psycle-core builders ######################################

psycle_core_deps = ['psycle-core/', 'psycle-audiodrivers/'] + psycle_helpers_deps

if False: # following not used yet. would help in having less repetitive build definitions
	append_standard_builders(
		name = 'psycle-core',
		trigger_dirs = psycle_core_deps,
		policy_check_dirs = ['psycle-core', 'psycle-audiodrivers'],
	)
else:
	BuildmasterConfig['builders'].append(
		{
			'name': 'psycle-core',
			'category': 'psycle',
			'slavenames': slaves,
			'builddir': svn_dir + 'psycle-core',
			'factory': factory.BuildFactory(
				[
					factory.s(SVNUpdate),
					factory.s(PolicyCheck, dirs = ['psycle-core', 'psycle-audiodrivers']),
					factory.s(Compile, command = './psycle-core/wonderbuild_script.py')
				]
			)
		}
	)
	BuildmasterConfig['schedulers'].append(
		Scheduler(
			name = 'psycle-core',
			builderNames = ['psycle-core'],
			fileIsImportant = lambda change: filter(change, psycle_core_deps)
		)
	)

##################################### psycle-player builders ######################################

psycle_player_deps = ['psycle-player/'] + psycle_core_deps

if False: # following not used yet. would help in having less repetitive build definitions
	append_standard_builders(
		name = 'psycle-player',
		trigger_dirs = psycle_player_deps,
		policy_check_dirs = ['psycle-player']
	)
else:
	BuildmasterConfig['builders'].append(
		{
			'name': 'psycle-player',
			'category': 'psycle',
			'slavenames': slaves,
			'builddir': svn_dir + 'psycle-player',
			'factory': factory.BuildFactory(
				[
					factory.s(SVNUpdate),
					factory.s(PolicyCheck, dirs = ['psycle-player']),
					factory.s(Compile, command = './psycle-player/wonderbuild_script.py')
				]
			)
		}
	)
	BuildmasterConfig['schedulers'].append(
		Scheduler(
			name = 'psycle-player',
			builderNames = ['psycle-player'],
			fileIsImportant = lambda change: filter(change, psycle_player_deps)
		)
	)

##################################### qpsycle builders ######################################

qpsycle_deps = ['qpsycle/'] + psycle_core_deps

if False: # following not used yet. would help in having less repetitive build definitions
	append_standard_builders(
		name = 'qpsycle',
		trigger_dirs = qpsycle_deps,
		build_system = 'qmake',
		mingw_pkg = True
	)
else:
	BuildmasterConfig['builders'].append(
		{
			'name': 'qpsycle',
			'category': 'psycle',
			'slavenames': slaves,
			'builddir': svn_dir + 'qpsycle',
			'factory': factory.BuildFactory(
				[
					factory.s(SVNUpdate),
					factory.s(PolicyCheck, dirs = ['qpsycle']),
					factory.s(Compile, command = 'cd qpsycle && qmake -recursive CONFIG-=debug_and_release CONFIG-=debug && make')
				]
			)
		}
	)
	BuildmasterConfig['schedulers'].append(
		Scheduler(
			name = 'qpsycle',
			builderNames = ['qpsycle'],
			fileIsImportant = lambda change: filter(change, qpsycle_deps)
		)
	)

##################################### psycle-plugins builders ######################################

psycle_plugins_deps = ['psycle-plugins/'] + psycle_helpers_deps

if False: # following not used yet. would help in having less repetitive build definitions
	append_standard_builders(
		name = 'psycle-plugins',
		trigger_dirs = psycle_plugins_deps,
		mingw_pkg = True
	)
else:
	BuildmasterConfig['builders'].append(
		{
			'name': 'psycle-plugins',
			'category': 'psycle',
			'slavenames': slaves,
			'builddir': svn_dir + 'psycle-plugins',
			'factory': factory.BuildFactory(
				[
					factory.s(SVNUpdate),
					factory.s(Compile, command = './psycle-plugins/wonderbuild_script.py')
				]
			)
		}
	)
	BuildmasterConfig['schedulers'].append(
		Scheduler(
			name = 'psycle-plugins',
			builderNames = ['psycle-plugins'],
			fileIsImportant = lambda change: filter(change, psycle_plugins_deps)
		)
	)

##################################### psycle.msvc builder ######################################

psycle_msvc_deps = ['psycle/'] + psycle_core_deps + psycle_plugins_deps

if False: # following not used yet. would help in having less repetitive build definitions
	append_standard_builders(
		name = 'psycle.msvc',
		trigger_dirs = psycle_msvc_deps,
		compile_command = r'call build-systems/msvc/build release',
		unix = False, mingw = False, msvc = True
	)
elif False: # disabled
	BuildmasterConfig['builders'].append(
		{
			'name': 'psycle.msvc',
			'category': 'psycle',
			'slavenames': microsoft_slaves_msvc,
			'builddir': svn_dir + 'psycle.msvc',
			'factory': factory.BuildFactory(
				[
					factory.s(SVNUpdate),
					factory.s(Compile, command = r'call ..\..\..\dev-pack ms && call build-systems\msvc\build release')
				]
			)
		}
	)
	BuildmasterConfig['schedulers'].append(
		Scheduler(
			name = 'psycle.msvc',
			builderNames = ['psycle.msvc'],
			fileIsImportant = lambda change: filter(change, psycle_msvc_deps)
		)
	)

##################################### sondar builders ######################################

svn_sondar = 'https://sondar.svn.sourceforge.net/svnroot/sondar/trunk'
BuildmasterConfig['sources'].append(SVNPoller(svnurl = svn_sondar, pollinterval = poll_interval, histmax = hist_max))

class CompileSondar(Compile):
	name = 'compile-sondar'
	description = ['compiling sondar']
	descriptionDone = ['compile sondar']
	command = 'cd sondar && sh autogen.sh --prefix=$(cd .. && pwd)/install && make install'

class CompileSondarGUI(Compile):
	name = 'compile-gui'
	description = ['compiling gui']
	descriptionDone = ['compile gui']
	command = 'export PKG_CONFIG_PATH=$(pwd)/install/lib/pkgconfig && cd host_gtk && sh autogen.sh --prefix=$(cd .. && pwd)/install && make install'

BuildmasterConfig['builders'].append(
	{
		'name': 'sondar',
		'category': 'sondar',
		'slavenames': slaves,
		'builddir': 'sondar-trunk',
		'factory': factory.BuildFactory(
			[
				factory.s(SVN, mode = 'update', svnurl = svn_sondar, locks = [svn_lock]),
				factory.s(CompileSondar),
				factory.s(CompileSondarGUI)
			]
		)
	}
)
BuildmasterConfig['schedulers'].append(
	Scheduler(
		name = 'sondar',
		builderNames = ['sondar'],
		fileIsImportant = lambda change: filter(change, ['sondar/', 'host_gtk/'])
	)
)

##################################### clean builders ######################################

class Clean(ShellCommand):
	name = 'clean'
	description = ['cleaning']
	descriptionDone = ['cleaned']
	def __init__(self, *args, **kwargs):
		kwargs['workdir'] = '..'
		kwargs['locks'] = all_locks
		ShellCommand.__init__(self, *args, **kwargs)

clean_factory = factory.BuildFactory(
	[
		factory.s(Clean, command=r'find . -ignore_readdir_race -name ++\* -exec rm -Rf {} \; ; sleep 5') # might be too fast!
		# Note: The sleep command is because buildbot looses track of the process if it finishes too fast!
	]
)

clean_factory_microsoft = factory.BuildFactory(
	[
		factory.s(Clean, command='del /s /q ++* && ping -n 5 127.0.0.1 > nul')
		# Since there's no damn sleep command in standard on windows, we need to use, erm, a stupid ping :-(
	]
)

def append_clean_builder(slave_name, microsoft = False):
	BuildmasterConfig['builders'].append(
		{
			'name': 'clean.' + slave_name,
			'category': None,
			'slavenames': [slave_name],
			'builddir': 'clean.' + slave_name,
			'factory': microsoft and clean_factory_microsoft or clean_factory
		}
	)
	
for slave in slaves: append_clean_builder(slave)
for slave in microsoft_slaves: append_clean_builder(slave, microsoft=True)
from buildbot.scheduler import Periodic as PeriodicScheduler
BuildmasterConfig['schedulers'].append(
	PeriodicScheduler(
		name = 'clean',
		branch = None,
		periodicBuildTimer = 60 * 60 * 24 * 30, # 30 days
		builderNames = ['clean.' + slave for slave in slaves + microsoft_slaves]
	)
)

##################################### statuses ######################################

BuildmasterConfig['status'] = []

categories = None #['psycle', 'sondar', 'armstrong']

##################################### http status ######################################

from buildbot.status.html import WebStatus
BuildmasterConfig['status'].append(WebStatus(http_port = 8010, allowForce=False))

##################################### mail status ######################################

from buildbot.status.mail import MailNotifier
BuildmasterConfig['status'].append(MailNotifier(fromaddr = email, mode = 'problem', categories = ['psycle', 'sondar'], lookup = 'users.sourceforge.net'))

##################################### irc status ######################################

from buildbot.status.words import IRC as BaseIRC, IrcStatusBot as BaseIrcStatusBot, IrcStatusFactory

class IrcStatusBot(BaseIrcStatusBot):
	def __init__(self, *args, **kw):
		BaseIrcStatusBot.__init__(self, *args, **kw)
		self.quiet = {}
	
	if False: # used to work in previous buildbot versions, but not anymore
		def command_QUIET(self, user, reply, args):
			if reply.startswith('#'):
				if not reply in self.quiet: self.quiet[reply] = False
				args = args.split()
				if len(args) == 0: self.quiet[reply] = not self.quiet[reply]
				else: self.quiet[reply] = args[0] == 'on'
				if self.quiet[reply]: self.reply(reply, 'I am now quiet.')
				else: self.reply(reply, 'I will speak from now on!')
		command_QUIET.usage = "quiet - mutes/unmutes unsolicited reports"

		def build_commands(self):
			commands = []
			for k in self.__class__.__dict__.keys() + BaseIrcStatusBot.__dict__.keys():
				if k.startswith('command_'): commands.append(k[8:].lower())
			commands.sort()
			return commands

IrcStatusFactory.protocol = IrcStatusBot

class IRC(BaseIRC):
	def __init__(self, *args, **kw):
		BaseIRC.__init__(self, *args, **kw)
		self.watched = {}
	
	class Watched:
		def __init__(self, builder, results):
			self.builder = builder
			self.results = results
			self.responsibles = []
			
	def setServiceParent(self, parent):
		BaseIRC.setServiceParent(self, parent)
		self._parent_status = parent.getStatus()
		self._parent_status.subscribe(self)
		
	def disownServiceParent(self):
		self._parent_status.unsubscribe(self)
		for builderName, watched in self.watched.items(): watched.builder.unsubscribe(self)
		self.watched = {}
		return BaseIRC.disownServiceParent(self)
	
	def builderAdded(self, builderName, builder):
		self.watched[builderName] = IRC.Watched(builder, None)
		if False: builder.subscribe(self) # subscription to self is done automatically by returning self
		return self
	
	def builderRemoved(self, builderName):
		try: watched = self.watched[builderName]
		except KeyError: pass
		else: watched.builder.unsubscribe(self) ; del self.watched[builderName]

	def irc(self): return self.f.p
	
	def buildFinished(self, builderName, build, results):
		msg = []
		watched = self.watched[builderName]
		from buildbot.status.builder import SUCCESS, WARNINGS, FAILURE, SKIPPED, EXCEPTION
		if build.getResults() == FAILURE:
			if not watched.responsibles:
				for responsible in build.getResponsibleUsers():
					if not responsible in watched.responsibles: watched.responsibles.append(responsible)
				msg.append('%s: %s broken by your recent commits.' % (', '.join(watched.responsibles), builderName))
			else:
				old_responsibles = []
				new_responsibles = []
				for responsible in build.getResponsibleUsers():
					if responsible in watched.responsibles: old_responsibles.append(responsible)
					else: new_responsibles.append(responsible)
				if old_responsibles and not new_responsibles: append('%s: %s still broken.' % (', '.join(old_responsibles), builderName))
				elif new_responsibles: msg.append('%s: %s still broken (was broken by %s).' % (
					', '.join(old_responsibles + new_responsibles), builderName, ' and '.join(watched.responsibles)))
				else: msg.append('%s still broken.' % (builderName,))
				watched.responsibles.extend(new_responsibles)
		elif watched.results == FAILURE and build.getResults() in (SUCCESS, WARNINGS):
			msg.append('%s: %s repaired.' % (', '.join(build.getResponsibleUsers()), builderName))
			watched.responsibles = []
		watched.results = build.getResults()
		if watched.results in (FAILURE, WARNINGS, EXCEPTION):
			if watched.results == WARNINGS: msg.append('Some warnings occured while building %s.' % builderName)
			elif watched.results == EXCEPTION: msg.append('An exception occured while trying to build %s!' % builderName)
			url = self._parent_status.getURLForThing(build)
			if not url: url = self._parent_status.getBuildbotURL()
			if url: msg.append('Build details are at %s' % url)
		if len(msg) != 0:
			for channel in self.channelMap(builderName):
				if not self.irc().quiet.get(channel, False): self.irc().msg(channel, ' '.join(msg).encode('ascii', 'replace'))

	def channelMap(self, builderName):
		result = []
		joined = self.irc().channels
		if '#psycle' in joined: result.append('#psycle') # we're able to see everything there
		if builderName.startswith('sondar') and 'sondar' in joined: result.append('#sondar')
		elif builderName.startswith('armstrong') and 'aldrin' in joined: result.append('#aldrin')
		return result

BuildmasterConfig['status'].append(IRC(host = 'irc.efnet.net'   , nick = 'buildborg', channels = ['#psycle']                      , categories = categories))
BuildmasterConfig['status'].append(IRC(host = 'irc.freenode.net', nick = 'buildborg', channels = ['#psycle', '#sondar', '#aldrin'], categories = categories))
