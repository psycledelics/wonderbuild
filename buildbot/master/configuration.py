import os

try: del os.environ['TERM']
except KeyError: pass

BuildmasterConfig = {}

project_name = 'psycle'
BuildmasterConfig['projectName'] = project_name
BuildmasterConfig['projectURL'] = 'http://' + project_name + '.sourceforge.net'

domain = 'retropaganda.info'
master_port = 8010
from socket import getfqdn
master_host_fqdn = getfqdn()
if not master_host_fqdn.endswith(domain):
	from socket import gethostname
	host = gethostname()
	if host in ('factoid', 'anechoid'): master_host_fqdn = host + '.' + domain
BuildmasterConfig['buildbotURL'] = 'http://' + master_host_fqdn + ':' + str(master_port) + '/'

BuildmasterConfig['sources'] = []

from buildbot.changes.pb import PBChangeSource
BuildmasterConfig['sources'].append(PBChangeSource()) # prefix = branch_filter

branch = 'trunk'
svn_url = 'https://' + project_name + '.svn.sourceforge.net/svnroot/' + project_name + '/' + branch
svn_dir = project_name + '-' + branch + os.sep
poll_interval = 5 * 60
bunch_timer = poll_interval + 60

try: # only available since buildbot 0.7.5
	from buildbot.changes.svnpoller import SVNPoller
	BuildmasterConfig['sources'].append(SVNPoller(svnurl = svn_url, pollinterval = poll_interval, histmax = poll_interval  * 2 // 60))
	branch_filter = '' # the branch is stripped automatically from paths in changset notifications
except: branch_filter = '/' + branch + '/'

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

BuildmasterConfig['builders'] = []
BuildmasterConfig['schedulers'] = []

from buildbot.scheduler import Scheduler as BaseScheduler
class Scheduler(BaseScheduler):
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

from buildbot.process import factory, step
from buildbot.status.builder import SUCCESS, WARNINGS, FAILURE, SKIPPED, EXCEPTION

class PolicyCheck(step.Test):
	name = 'policy-check'
	description = ['checking policy']
	descriptionDone = ['policy']
	command = ['./tools/check-policy']

	def evaluateCommand(self, cmd):
		if cmd.rc != 0: return WARNINGS
		return SUCCESS

class LintCheck(step.Test):
	name = 'lint-check'
	description = ['checking lint']
	descriptionDone = ['lint']
	command = ['true']

class Upload(step.ShellCommand):
	name = 'upload'
	description = ['uploading']
	descriptionDone = ['uploaded']
	command = ['echo download the package at http://psycle.sourceforge.net/packages']

if False:
	BuildmasterConfig['builders'].append(
		{
			'name': 'dummy',
			'category': None,
			'slavenames': slaves + microsoft_slaves,
			'builddir': svn_dir + 'dummy',
			'factory': factory.BuildFactory(
				[
					factory.s(step.SVN, retry = (600, 3), mode = 'update', svnurl = svn_url, locks = [svn_lock])
				]
			)
		}
	)
	BuildmasterConfig['schedulers'].append(
		Scheduler(
			name = 'dummy',
			branch = None,
			treeStableTimer = bunch_timer,
			builderNames = ['dummy']
		)
	)

BuildmasterConfig['builders'].append(
	{
		'name': 'universalis',
		'category': 'psycle',
		'slavenames': slaves,
		'builddir': svn_dir + 'universalis',
		'factory': factory.BuildFactory(
			[
				factory.s(step.SVN, retry = (600, 3), mode = 'update', svnurl = svn_url, locks = [svn_lock]),
				factory.s(PolicyCheck, command = './tools/check-policy diversalis universalis', locks = [compile_lock]),
				factory.s(step.Compile, command = 'scons --directory=universalis packageneric__debug=1', locks = [compile_lock]),
				factory.s(step.Test, command = './++packageneric/variants/default/stage-install/usr/local/bin/universalis_unit_tests --log_level=test_suite --report_level=detailed', locks = [compile_lock])
			]
		)
	}
)
BuildmasterConfig['schedulers'].append(
	Scheduler(
		name = 'universalis',
		branch = None,
		treeStableTimer = bunch_timer,
		builderNames = ['universalis'],
		fileIsImportant = lambda change: filter(change, ['universalis/', 'diversalis/', 'packageneric/'])
	)
)

BuildmasterConfig['builders'].append(
	{
		'name': 'universalis.mingw',
		'category': 'psycle',
		'slavenames': microsoft_slaves,
		'builddir': svn_dir + 'universalis.mingw',
		'factory': factory.BuildFactory(
			[
				factory.s(step.SVN, retry = (600, 3), mode = 'update', svnurl = svn_url, locks = [svn_lock]),
				factory.s(PolicyCheck, command = 'call ..\\..\\..\\dev-pack && python .\\tools\\check-policy diversalis universalis', locks = [compile_lock]),
				factory.s(step.Compile, command = 'call ..\\..\\..\\dev-pack && scons --directory=universalis packageneric__debug=1', locks = [compile_lock]),
				factory.s(step.Test, command = 'call ..\\..\\..\\dev-pack && .\\++packageneric\\variants\\default\\stage-install\\usr\\local\\bin\\universalis_unit_tests --log_level=test_suite --report_level=detailed', locks = [compile_lock])
			]
		)
	}
)
BuildmasterConfig['schedulers'].append(
	Scheduler(
		name = 'universalis.mingw',
		branch = None,
		treeStableTimer = bunch_timer,
		builderNames = ['universalis.mingw'],
		fileIsImportant = lambda change: filter(change, ['universalis/', 'diversalis/', 'packageneric/'])
	)
)

BuildmasterConfig['builders'].append(
	{
		'name': 'freepsycle',
		'category': 'psycle',
		'slavenames': slaves,
		'builddir': svn_dir + 'freepsycle',
		'factory': factory.BuildFactory(
			[
				#factory.s(step.SVN, retry = (600, 3), mode = 'update', baseURL = svn_url, defaultBranch = 'trunk', locks = [svn_lock]),
				factory.s(step.SVN, retry = (600, 3), mode = 'update', svnurl = svn_url, locks = [svn_lock]),
				factory.s(PolicyCheck, command = './tools/check-policy diversalis universalis freepsycle', locks = [compile_lock]),
				factory.s(step.Compile, command = 'scons --directory=freepsycle packageneric__debug=1', locks = [compile_lock])
			]
		)
	}
)
BuildmasterConfig['schedulers'].append(
	Scheduler(
		name = 'freepsycle',
		branch = None,
		treeStableTimer = bunch_timer,
		builderNames = ['freepsycle'],
		fileIsImportant = lambda change: filter(change, ['freepsycle/', 'universalis/', 'diversalis/', 'packageneric/'])
	)
)

BuildmasterConfig['builders'].append(
	{
		'name': 'freepsycle.mingw',
		'category': 'psycle',
		'slavenames': microsoft_slaves,
		'builddir': svn_dir + 'freepsycle.mingw',
		'factory': factory.BuildFactory(
			[
				factory.s(step.SVN, retry = (600, 3), mode = 'update', svnurl = svn_url, locks = [svn_lock]),
				factory.s(PolicyCheck, command = 'call ..\\..\\..\\dev-pack && python .\\tools\\check-policy diversalis universalis freepsycle', locks = [compile_lock]),
				factory.s(step.Compile, command = 'call ..\\..\\..\\dev-pack && scons --directory=freepsycle packageneric__debug=1', locks = [compile_lock])
			]
		)
	}
)
BuildmasterConfig['schedulers'].append(
	Scheduler(
		name = 'freepsycle.mingw',
		branch = None,
		treeStableTimer = bunch_timer,
		builderNames = ['freepsycle.mingw'],
		fileIsImportant = lambda change: filter(change, ['freepsycle/', 'universalis/', 'diversalis/', 'packageneric/'])
	)
)

BuildmasterConfig['builders'].append(
	{
		'name': 'psycle-core',
		'category': 'psycle',
		'slavenames': slaves,
		'builddir': svn_dir + 'psycle-core',
		'factory': factory.BuildFactory(
			[
				factory.s(step.SVN, mode = 'update', svnurl = svn_url, locks = [svn_lock]),
				factory.s(PolicyCheck, command = './tools/check-policy psycle-core', locks = [compile_lock]),
				factory.s(step.Compile, command = 'cd psycle-core && qmake && make', locks = [compile_lock]),
			]
		)
	}
)
BuildmasterConfig['schedulers'].append(
	Scheduler(
		name = 'psycle-core',
		branch = None,
		treeStableTimer = bunch_timer,
		builderNames = ['psycle-core'],
		fileIsImportant = lambda change: filter(change, ['psycle-core/', 'psycle-audiodrivers/'])
	)
)

BuildmasterConfig['builders'].append(
	{
		'name': 'psycle-core.mingw',
		'category': 'psycle',
		'slavenames': microsoft_slaves,
		'builddir': svn_dir + 'psycle-core.mingw',
		'factory': factory.BuildFactory(
			[
				factory.s(step.SVN, mode = 'update', svnurl = svn_url, locks = [svn_lock]),
				factory.s(PolicyCheck, command = 'call ..\\..\\..\\dev-pack && python .\\tools\\check-policy psycle-core', locks = [compile_lock]),
				factory.s(step.Compile, command = 'call ..\\..\\..\\dev-pack && cd psycle-core && qmake && mingw32-make', locks = [compile_lock])
			]
		)
	}
)
BuildmasterConfig['schedulers'].append(
	Scheduler(
		name = 'psycle-core.mingw',
		branch = None,
		treeStableTimer = bunch_timer,
		builderNames = ['psycle-core.mingw'],
		fileIsImportant = lambda change: filter(change, ['psycle-core/', 'psycle-audiodrivers/'])
	)
)

BuildmasterConfig['builders'].append(
	{
		'name': 'psycle-player',
		'category': 'psycle',
		'slavenames': slaves,
		'builddir': svn_dir + 'psycle-player',
		'factory': factory.BuildFactory(
			[
				factory.s(step.SVN, mode = 'update', svnurl = svn_url, locks = [svn_lock]),
				factory.s(PolicyCheck, command = './tools/check-policy psycle-player', locks = [compile_lock]),
				factory.s(step.Compile, command = 'cd psycle-player && qmake && make', locks = [compile_lock])
			]
		)
	}
)
BuildmasterConfig['schedulers'].append(
	Scheduler(
		name = 'psycle-player',
		branch = None,
		treeStableTimer = bunch_timer,
		builderNames = ['psycle-player'],
		fileIsImportant = lambda change: filter(change, ['psycle-player/', 'psycle-core/', 'psycle-audiodrivers/'])
	)
)

BuildmasterConfig['builders'].append(
	{
		'name': 'psycle-player.mingw',
		'category': 'psycle',
		'slavenames': microsoft_slaves,
		'builddir': svn_dir + 'psycle-player.mingw',
		'factory': factory.BuildFactory(
			[
				factory.s(step.SVN, mode = 'update', svnurl = svn_url, locks = [svn_lock]),
				factory.s(PolicyCheck, command = 'call ..\\..\\..\\dev-pack && python .\\tools\\check-policy psycle-player', locks = [compile_lock]),
				factory.s(step.Compile, command = 'call ..\\..\\..\\dev-pack && cd psycle-player && qmake && mingw32-make', locks = [compile_lock])
			]
		)
	}
)
BuildmasterConfig['schedulers'].append(
	Scheduler(
		name = 'psycle-player.mingw',
		branch = None,
		treeStableTimer = bunch_timer,
		builderNames = ['psycle-player.mingw'],
		fileIsImportant = lambda change: filter(change, ['psycle-player/', 'psycle-core/', 'psycle-audiodrivers/'])
	)
)

BuildmasterConfig['builders'].append(
	{
		'name': 'qpsycle',
		'category': 'psycle',
		'slavenames': slaves,
		'builddir': svn_dir + 'qpsycle',
		'factory': factory.BuildFactory(
			[
				factory.s(step.SVN, mode = 'update', svnurl = svn_url, locks = [svn_lock]),
				factory.s(PolicyCheck, command = './tools/check-policy qpsycle', locks = [compile_lock]),
				factory.s(step.Compile, command = 'cd qpsycle && qmake && make', locks = [compile_lock])
			]
		)
	}
)
BuildmasterConfig['schedulers'].append(
	Scheduler(
		name = 'qpsycle',
		branch = None,
		treeStableTimer = bunch_timer,
		builderNames = ['qpsycle'],
		fileIsImportant = lambda change: filter(change, ['qpsycle/', 'psycle-core/', 'psycle-audiodrivers/'])
	)
)

BuildmasterConfig['builders'].append(
	{
		'name': 'qpsycle.mingw',
		'category': 'psycle',
		'slavenames': microsoft_slaves,
		'builddir': svn_dir + 'qpsycle.mingw',
		'factory': factory.BuildFactory(
			[
				factory.s(step.SVN, mode = 'update', svnurl = svn_url, locks = [svn_lock]),
				factory.s(PolicyCheck, command = 'call ..\\..\\..\\dev-pack && python .\\tools\\check-policy qpsycle', locks = [compile_lock]),
				factory.s(step.Compile, command = 'call ..\\..\\..\\dev-pack && cd qpsycle && qmake && mingw32-make', locks = [compile_lock])
			]
		)
	}
)
BuildmasterConfig['schedulers'].append(
	Scheduler(
		name = 'qpsycle.mingw',
		branch = None,
		treeStableTimer = bunch_timer,
		builderNames = ['qpsycle.mingw'],
		fileIsImportant = lambda change: filter(change, ['qpsycle/', 'psycle-core/', 'psycle-audiodrivers/'])
	)
)

BuildmasterConfig['builders'].append(
	{
		'name': 'qpsycle.mingw.pkg',
		'category': 'psycle',
		'slavenames': microsoft_slaves,
		'builddir': svn_dir + 'qpsycle.mingw.pkg',
		'factory': factory.BuildFactory(
			[
				factory.s(step.SVN, mode = 'update', svnurl = svn_url, locks = [svn_lock]),
				factory.s(step.Compile, command = 'call ..\\..\\..\\dev-pack && cd qpsycle && sh -c ./make-microsoft-raw-package', locks = [compile_lock]),
				factory.s(Upload, command = 'scp -F ../../../../.ssh/config qpsycle/++build/install/qpsycle.tar.bz2 upload.buildborg.retropaganda.info:psycle/htdocs/packages/microsoft/ && echo download the package at http://psycle.sourceforge.net/packages/microsoft/qpsycle.tar.bz2', locks = [svn_lock])
			]
		)
	}
)

BuildmasterConfig['builders'].append(
	{
		'name': 'psycle-plugins',
		'category': 'psycle',
		'slavenames': slaves,
		'builddir': svn_dir + 'psycle-plugins',
		'factory': factory.BuildFactory(
			[
				factory.s(step.SVN, mode = 'update', svnurl = svn_url, locks = [svn_lock]),
				factory.s(step.Compile, command = 'scons --directory=psycle-plugins packageneric__debug=1', locks = [compile_lock])
			]
		)
	}
)
BuildmasterConfig['schedulers'].append(
	Scheduler(
		name = 'psycle-plugins',
		branch = None,
		treeStableTimer = bunch_timer,
		builderNames = ['psycle-plugins'],
		fileIsImportant = lambda change: filter(change, ['psycle-plugins/', 'universalis/', 'diversalis/', 'packageneric/'])
	)
)

BuildmasterConfig['builders'].append(
	{
		'name': 'psycle-plugins.mingw',
		'category': 'psycle',
		'slavenames': microsoft_slaves,
		'builddir': svn_dir + 'psycle-plugins.mingw',
		'factory': factory.BuildFactory(
			[
				factory.s(step.SVN, mode = 'update', svnurl = svn_url, locks = [svn_lock]),
				factory.s(step.Compile, command = 'call ..\\..\\..\\dev-pack && scons --directory=psycle-plugins packageneric__debug=1', locks = [compile_lock])
			]
		)
	}
)
BuildmasterConfig['schedulers'].append(
	Scheduler(
		name = 'psycle-plugins.mingw',
		branch = None,
		treeStableTimer = bunch_timer,
		builderNames = ['psycle-plugins.mingw'],
		fileIsImportant = lambda change: filter(change, ['psycle-plugins/', 'universalis/', 'diversalis/', 'packageneric/'])
	)
)

BuildmasterConfig['builders'].append(
	{
		'name': 'psycle-helpers',
		'category': 'psycle',
		'slavenames': slaves,
		'builddir': svn_dir + 'psycle-helpers',
		'factory': factory.BuildFactory(
			[
				factory.s(step.SVN, mode = 'update', svnurl = svn_url, locks = [svn_lock]),
				factory.s(PolicyCheck, command = './tools/check-policy diversalis universalis psycle-helpers', locks = [compile_lock]),
				factory.s(step.Compile, command = 'scons --directory=psycle-helpers packageneric__debug=0 packageneric__test=1', locks = [compile_lock]),
				factory.s(step.Test, command = './++packageneric/variants/default/stage-install/usr/local/bin/psycle-helpers_unit_tests --log_level=test_suite --report_level=detailed', locks = [compile_lock])
			]
		)
	}
)
BuildmasterConfig['schedulers'].append(
	Scheduler(
		name = 'psycle-helpers',
		branch = None,
		treeStableTimer = bunch_timer,
		builderNames = ['psycle-helpers'],
		fileIsImportant = lambda change: filter(change, ['psycle-helpers/', 'universalis/', 'diversalis/', 'packageneric/'])
	)
)

BuildmasterConfig['builders'].append(
	{
		'name': 'psycle-helpers.mingw',
		'category': 'psycle',
		'slavenames': microsoft_slaves,
		'builddir': svn_dir + 'psycle-helpers.mingw',
		'factory': factory.BuildFactory(
			[
				factory.s(step.SVN, mode = 'update', svnurl = svn_url, locks = [svn_lock]),
				factory.s(PolicyCheck, command = 'call ..\\..\\..\\dev-pack && python .\\tools\\check-policy diversalis universalis psycle-helpers', locks = [compile_lock]),
				factory.s(step.Compile, command = 'call ..\\..\\..\\dev-pack && scons --directory=psycle-helpers packageneric__debug=0 packageneric__test=1', locks = [compile_lock]),
				factory.s(step.Test, command = 'call ..\\..\\..\\dev-pack && .\\++packageneric\\variants\\default\\stage-install\\usr\\local\\bin\\psycle-helpers_unit_tests --log_level=test_suite --report_level=detailed', locks = [compile_lock])
			]
		)
	}
)
BuildmasterConfig['schedulers'].append(
	Scheduler(
		name = 'psycle-helpers.mingw',
		branch = None,
		treeStableTimer = bunch_timer,
		builderNames = ['psycle-helpers.mingw'],
		fileIsImportant = lambda change: filter(change, ['psycle-helpers/', 'universalis/', 'diversalis/', 'packageneric/'])
	)
)

BuildmasterConfig['builders'].append(
	{
		'name': 'psycle.msvc',
		'category': 'psycle',
		'slavenames': microsoft_slaves_msvc,
		'builddir': svn_dir + 'psycle.msvc',
		'factory': factory.BuildFactory(
			[
				factory.s(step.SVN, retry = (600, 3), mode = 'update', svnurl = svn_url, locks = [svn_lock]),
				factory.s(step.Compile, command = 'call ..\\..\\..\\dev-pack _ msvc-solution && call .\\psycle\\make\\msvc_8.0\\build debug', locks = [compile_lock])
			]
		)
	}
)
BuildmasterConfig['schedulers'].append(
	Scheduler(
		name = 'psycle.msvc',
		branch = None,
		treeStableTimer = bunch_timer,
		builderNames = ['psycle.msvc'],
		fileIsImportant = lambda change: filter(change, ['psycle/', 'psycle-helpers/', 'psycle-core/', 'psycle-audiodrivers/', 'universalis/', 'diversalis/', 'packageneric/'])
	)
)

BuildmasterConfig['status'] = []

categories = None #['psycle', 'zzub']

from buildbot.status.html import Waterfall
BuildmasterConfig['status'].append(Waterfall(http_port = 8010, css = 'waterfall.css', robots_txt = 'robots.txt', categories = categories))

from buildbot.status.words import IRC as BaseIRC, IrcStatusBot as BaseIrcStatusBot, IrcStatusFactory

class IrcStatusBot(BaseIrcStatusBot):
	def __init__(self, *args, **kw):
		BaseIrcStatusBot.__init__(self, *args, **kw)
		self.quiet = {}
	
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
		def msg(message):
			for channel in self.channelMap(builderName):
				if not self.irc().quiet.get(channel, False): self.irc().msg(channel, message.encode('ascii', 'replace'))
		watched = self.watched[builderName]
		from buildbot.status.builder import SUCCESS, WARNINGS, FAILURE, SKIPPED, EXCEPTION
		if build.getResults() == FAILURE:
	   		if not watched.responsibles:
	   			for responsible in build.getResponsibleUsers():
	   				if not responsible in watched.responsibles: watched.responsibles.append(responsible)
				msg('%s: Your recent commit(s) might have broken the build of %s!' % (
					', '.join(watched.responsibles),
					builderName))
	   		else:
	   			old_responsibles = []
	   			new_responsibles = []
	   			for responsible in build.getResponsibleUsers():
	   				if responsible in watched.responsibles: old_responsibles.append(responsible)
	   				else: new_responsibles.append(responsible)
	   			if old_responsibles: msg('%s: You broke the build of %s even more!' % (
	   				', '.join(old_responsibles),
	   				builderName))
	   			if new_responsibles: msg('%s: Your recent commit(s) did not manage to repair what %s broke in the build of %s...' % (
	   				', '.join(new_responsibles),
	   				' and '.join(watched.responsibles), 
	   				builderName))
	   			watched.responsibles.extend(new_responsibles)
		elif watched.results == FAILURE and build.getResults() in (SUCCESS, WARNINGS):
			msg('%s: You managed to repair the build of %s!' % (
				', '.join(build.getResponsibleUsers()),
				builderName))
			watched.responsibles = []
		watched.results = build.getResults()
		if watched.results in (FAILURE, WARNINGS, EXCEPTION):
			if watched.results == WARNINGS: msg('Some warnings occured while building %s.' % builderName)
			elif watched.results == EXCEPTION: msg('An exception occured while trying to build %s!' % builderName)
			url = self._parent_status.getURLForThing(build)
			if not url: url = self._parent_status.getBuildbotURL()
			if url: msg('Build details are at %s' % url)

	def channelMap(self, builderName):
		if builderName.startswith('libzzub'): return self.irc().channels
		else: return ['#psycle']

decent_efnet_irc_server = 'irc.efnet.net'
#decent_efnet_irc_server = 'irc.choopa.ca'
BuildmasterConfig['status'].append(IRC(host = decent_efnet_irc_server, nick = 'buildborg', channels = ['#psycle'], categories = categories))
BuildmasterConfig['status'].append(IRC(host = 'irc.freenode.net', nick = 'buildborg', channels = ['#psycle', '#aldrin'], categories = categories))

BuildmasterConfig['debugPassword'] = 'debugpassword'

##################################### non-psycle stuff below ######################################
if True:

	microsoft_slaves_zzub = ['winux']

	zzub_exclude_prefixes = [
		'branches/', 'tags/',
		'/trunk/dependencies.dot', '/trunk/dependencies.png', '/README', 'tools/', 'freepsycle/', 'qpsycle/', 'psycle-core/',
		'psycle-player/', 'psycle-helpers', 'psycle-audiodrivers/', 'psycle-plugins/', 'psycle/',
		'universalis/', 'diversalis/', 'packageneric/', 'buildbot/', 'external-packages/', 'www/'
	]

	BuildmasterConfig['builders'].append(
		{
			'name': 'libzzub',
			'category': 'zzub',
			'slavenames': slaves,
			'builddir': os.path.join('zzub-trunk', 'libzzub'),
			'factory': factory.BuildFactory(
				[
					factory.s(step.SVN, mode = 'update', svnurl = 'http://svn.zeitherrschaft.org/zzub/trunk', locks = [svn_lock]),
					factory.s(step.Compile, command = 'scons configure && scons', locks = [compile_lock])
				]
			)
		}
	)
	BuildmasterConfig['schedulers'].append(
		Scheduler(
			name = 'libzzub',
			branch = None,
			treeStableTimer = bunch_timer,
			builderNames = ['libzzub'],
			fileIsImportant = lambda change: filter(change,
				include_prefixes = [''],
				exclude_prefixes = zzub_exclude_prefixes
			)
		)
	)


	BuildmasterConfig['builders'].append(
		{
			'name': 'libzzub.mingw',
			'category': 'zzub',
			'slavenames': microsoft_slaves_zzub,
			'builddir': os.path.join('zzub-trunk', 'libzzub.mingw'),
			'factory': factory.BuildFactory(
				[
					factory.s(step.SVN, mode = 'update', svnurl = 'http://svn.zeitherrschaft.org/zzub/trunk', locks = [svn_lock]),
					factory.s(step.Compile, command = 'call ..\\..\\..\\dev-pack && scons TOOLS=mingw configure && scons', locks = [compile_lock])
				]
			)
		}
	)
	BuildmasterConfig['schedulers'].append(
		Scheduler(
			name = 'libzzub.mingw',
			branch = None,
			treeStableTimer = bunch_timer,
			builderNames = ['libzzub.mingw'],
			fileIsImportant = lambda change: filter(change,
				include_prefixes = [''],
				exclude_prefixes = zzub_exclude_prefixes
			)
		)
	)

	BuildmasterConfig['builders'].append(
		{
			'name': 'libzzub.msvc',
			'category': 'zzub',
			'slavenames': microsoft_slaves_zzub,
			'builddir': os.path.join('zzub-trunk', 'libzzub.msvc'),
			'factory': factory.BuildFactory(
				[
					factory.s(step.SVN, mode = 'update', svnurl = 'http://svn.zeitherrschaft.org/zzub/trunk', locks = [svn_lock]),
					factory.s(step.Compile, command = 'call ..\\..\\..\\dev-pack && scons configure && scons', locks = [compile_lock])
				]
			)
		}
	)
	BuildmasterConfig['schedulers'].append(
		Scheduler(
			name = 'libzzub.msvc',
			branch = None,
			treeStableTimer = bunch_timer,
			builderNames = ['libzzub.msvc'],
			fileIsImportant = lambda change: filter(change,
				include_prefixes = [''],
				exclude_prefixes = zzub_exclude_prefixes
			)
		)
	)
