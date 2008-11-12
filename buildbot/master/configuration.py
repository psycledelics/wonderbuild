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

BuildmasterConfig['debugPassword'] = 'debugpassword'

BuildmasterConfig['builders'] = []
BuildmasterConfig['schedulers'] = []

from buildbot.scheduler import Scheduler as BaseScheduler
class Scheduler(BaseScheduler):
	def __init__(self, *args, **kw):
		kw['branch'] = None,
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

from buildbot.process import factory, step
from buildbot.status.builder import SUCCESS, WARNINGS, FAILURE, SKIPPED, EXCEPTION

##################################### custom build steps ######################################

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

class SVNUpdate(step.SVN):
	def __init__(self, *args, **kw):
		kw['retry'] = (600, 3)
		kw['mode'] = 'update'
		kw['svnurl'] = svn_url
		if False: kw['defaultBranch'] = 'trunk'
		kw['locks'] = [svn_lock]
		step.SVN.__init__(self, *args, **kw)

class Test(step.Test):
	def __init__(self, *args, **kw):
		kw['locks'] = [compile_lock]
		handle_microsoft_kw(kw)
		step.Test.__init__(self, *args, **kw)

class PolicyCheck(Test):
	name = 'policy-check'
	description = ['checking policy']
	descriptionDone = ['policy']
	def __init__(self, *args, **kw):
		kw['command'] += 'python ./tools/check-policy ' + ' '.join(kw['dirs'])
		del kw['dirs']
		Test.__init__(self, *args, **kw)
	def evaluateCommand(self, cmd):
		if cmd.rc != 0: return WARNINGS
		return SUCCESS
	warnOnWarnings = True

class Compile(step.Compile):
	def __init__(self, *args, **kw):
		kw['locks'] = [compile_lock]
		handle_microsoft_kw(kw)
		step.Compile.__init__(self, *args, **kw)

class ShellCommand(step.ShellCommand):
	def __init__(self, *args, **kw):
		handle_microsoft_kw(kw)
		step.ShellCommand.__init__(self, *args, **kw)

class Upload(ShellCommand):
	name = 'upload'
	description = ['uploading']
	descriptionDone = ['uploaded']
	def __init__(self, *args, **kw):
		kw['locks'] = []
		kw['no_slash_inversion_command'] = 
			('scp -F ../../../../.ssh/config ' +
			'%(src)s/%(file)s upload.buildborg.retropaganda.info:psycle/htdocs/packages/%(dst)s/ && ' +
			'echo download the package at http://psycle.sourceforge.net/packages/%(dst)s') \
			% {'file': kw['file'], 'src': kw['src'], 'dst': kw['dst']}
		def kw['file']; del kw['src']; del kw['dst']
		ShellCommand.__init__(self, *args, **kw)

unit_test_log_level = ' --log_level=test_suite --report_level=detailed'

##################################### standard builder ##########################################

def append_standard_builder(
	category = 'psycle', name, trigger_dirs, update_step = factory.s(SVNUpdate), build_dir = svn_dir,
	policy_check_dirs, compile_command, test_command, mingw = True, msvc = False
):
	def append(name, variant, slaves, compile_command, microsoft = False, mingw = True, msvc = False):
		factory_steps = [update_step]
		if policy_check_dirs: factory_steps.append(factory.s(PolicyCheck, dirs = policy_check_dirs))
		if callable(compile_command): compile_command = compile_command(microsoft, mingw, msvc)
		factory_steps.append(factory.s(Compile, microsoft = microsoft, mingw = mingw, msvc = msvc, command = compile_command))
		if test_command: factory_steps.append(factory.s(Test, microsoft = microsoft, command = test_command))
		BuildmasterConfig['builders'].append({
			'category': category,
			'name': name + variant,
			'slavenames': slaves,
			'builddir': build_dir + name + variant,
			steps = 
			'factory': factory.BuildFactory(factory_steps)
		})
		BuildmasterConfig['schedulers'].append(Scheduler(
			name = name + variant,
			builderNames = [name + variant],
			fileIsImportant = lambda change: filter(change, trigger_dirs)
		))
	append(name, '', slaves)
	if mingw: append(name, '.mingw', microsoft_slaves, compile_command, microsoft = True)
	if msvc: append(name, '.msvc', microsoft_slaves, compiled_command, microsoft = True, msvc = True)

##################################### universalis builders ######################################

class universalis_dirs = ['universalis/', 'diversalis/', 'packageneric/']

append_standard_builder(
	category = 'psycle',
	name = 'universalis',
	trigger_dirs = universalis_dirs,
	policy_check_dirs, universalis_dirs,
	compile_command = 'scons --directory=universalis',
	test_command = './++packageneric/variants/default/stage-install/usr/local/bin/universalis_unit_tests' + unit_test_log_level
)

def append_universalis_builder(variant, slaves, microsoft = False):
	name = 'universalis'
	BuildmasterConfig['builders'].append({
		'category': 'psycle',
		'name': name + variant,
		'slavenames': slaves,
		'builddir': svn_dir + name + variant,
		'factory': factory.BuildFactory([
				factory.s(SVNUpdate),
				factory.s(PolicyCheck, dirs = universalis_dirs),
				factory.s(Compile, microsoft = microsoft, command = 'scons --directory=' + name),
				factory.s(Test, microsoft = microsoft, command =
					'./++packageneric/variants/default/stage-install/usr/local/bin/' + name + '_unit_tests' +
					unit_test_log_level)
	])})
	BuildmasterConfig['schedulers'].append(Scheduler(
		name = name + variant,
		builderNames = [name + variant],
		fileIsImportant = lambda change: filter(change, universalis_dirs)
	))

append_universalis_builder('', slaves)
append_universalis_builder('.mingw', microsoft_slaves, microsoft = True)

##################################### freepsycle builders ######################################

freepsycle_dirs = ['freepsycle/'] + universalis_dirs

def append_freepsycle_builder(variant, slaves, microsoft):
	name = 'freepsycle'
	BuildmasterConfig['builders'].append({
	'category': 'psycle',
	'name': name,
	'slavenames': slaves,
	'builddir': svn_dir + name + variant,
	'factory': factory.BuildFactory([
		factory.s(SVNUpdate),
		factory.s(PolicyCheck, dirs = [name]),
		factory.s(Compile, microsoft = microsoft, command = 'scons --directory=' + name)
	])})
	BuildmasterConfig['schedulers'].append(Scheduler(
			name = name,
			builderNames = [name],
			fileIsImportant = lambda change: filter(change, freepsycle_dirs)
	))
append_freepsycle_builder('', slaves)
append_freepsycle_builder('.mingw', microsoft_slaves, microsoft = True)

# mingw raw pkg + upload

BuildmasterConfig['builders'].append({
	'category': 'psycle',
	'name': 'freepsycle.mingw.pkg',
	'slavenames': microsoft_slaves,
	'builddir': svn_dir + 'freepsycle.mingw.pkg',
	'factory': factory.BuildFactory([
		factory.s(SVNUpdate),
		factory.s(Compile, command = 'cd freepsycle && sh -c make-microsoft-raw-package'),
		factory.s(Upload,
			file = 'freepsycle.tar.bz2'
			src = 'freepsycle/++packageneric/variants/default/install',
			dst = 'microsoft'
		)
])})

##################################### psycle-core builders ######################################

psycle_core_dirs = ['psycle-core/', 'psycle-audiodrivers/']

def append_psycle_core_builder(variant, slaves, microsoft):
	name = 'psycle-core.' + variant
	BuildmasterConfig['builders'].append({
		'category': 'psycle',
		'name': name,
		'slavenames': slaves,
		'builddir': svn_dir + name,
		'factory': factory.BuildFactory([
			factory.s(SVNUpdate),
			factory.s(PolicyCheck, dirs = ['psycle-core']),
			factory.s(Compile, microsoft = microsoft, command =
				'cd psycle-core && ' +
				'qmake -recursive CONFIG-=debug_and_release CONFIG-=debug && ' +
				microsoft and 'mingw32-make' or 'make', locks = [compile_lock]),
	])})
	BuildmasterConfig['schedulers'].append(Scheduler(
		name = 'psycle-core',
		builderNames = ['psycle-core'],
		fileIsImportant = lambda change: filter(change, psycle_core_dirs)
	))
append_psycle_core_builder('psycle-core', slaves)
append_psycle_core_builder('', microsoft_slaves, microsoft = True)

##################################### psycle-player builders ######################################

# gnu

BuildmasterConfig['builders'].append(
	{
		'name': 'psycle-player',
		'category': 'psycle',
		'slavenames': slaves,
		'builddir': svn_dir + 'psycle-player',
		'factory': factory.BuildFactory(
			[
				factory.s(SVNUpdate),
				factory.s(PolicyCheck, command = './tools/check-policy psycle-player', locks = [compile_lock]),
				factory.s(Compile, command = 'cd psycle-player && qmake -recursive CONFIG-=debug_and_release CONFIG-=debug && make', locks = [compile_lock])
			]
		)
	}
)
BuildmasterConfig['schedulers'].append(
	Scheduler(
		name = 'psycle-player',
		builderNames = ['psycle-player'],
		fileIsImportant = lambda change: filter(change, ['psycle-player/', 'psycle-core/', 'psycle-audiodrivers/'])
	)
)

# mingw

BuildmasterConfig['builders'].append(
	{
		'name': 'psycle-player.mingw',
		'category': 'psycle',
		'slavenames': microsoft_slaves,
		'builddir': svn_dir + 'psycle-player.mingw',
		'factory': factory.BuildFactory(
			[
				factory.s(SVNUpdate),
				factory.s(PolicyCheck, command = microsoft_dev_pack + 'python .\\tools\\check-policy psycle-player', locks = [compile_lock]),
				factory.s(Compile, command = microsoft_dev_pack + 'cd psycle-player && qmake -recursive CONFIG-=debug_and_release CONFIG-=debug && mingw32-make', locks = [compile_lock])
			]
		)
	}
)
BuildmasterConfig['schedulers'].append(
	Scheduler(
		name = 'psycle-player.mingw',
		builderNames = ['psycle-player.mingw'],
		fileIsImportant = lambda change: filter(change, ['psycle-player/', 'psycle-core/', 'psycle-audiodrivers/'])
	)
)

##################################### qpsycle builders ######################################

# gnu

BuildmasterConfig['builders'].append(
	{
		'name': 'qpsycle',
		'category': 'psycle',
		'slavenames': slaves,
		'builddir': svn_dir + 'qpsycle',
		'factory': factory.BuildFactory(
			[
				factory.s(SVNUpdate),
				factory.s(PolicyCheck, command = './tools/check-policy qpsycle', locks = [compile_lock]),
				factory.s(Compile, command = 'cd qpsycle && qmake -recursive CONFIG-=debug_and_release CONFIG-=debug && make', locks = [compile_lock])
			]
		)
	}
)
BuildmasterConfig['schedulers'].append(
	Scheduler(
		name = 'qpsycle',
		builderNames = ['qpsycle'],
		fileIsImportant = lambda change: filter(change, ['qpsycle/', 'psycle-core/', 'psycle-audiodrivers/'])
	)
)

# mingw

BuildmasterConfig['builders'].append(
	{
		'name': 'qpsycle.mingw',
		'category': 'psycle',
		'slavenames': microsoft_slaves,
		'builddir': svn_dir + 'qpsycle.mingw',
		'factory': factory.BuildFactory(
			[
				factory.s(SVNUpdate),
				factory.s(PolicyCheck, command = microsoft_dev_pack + 'python .\\tools\\check-policy qpsycle', locks = [compile_lock]),
				factory.s(Compile, command = microsoft_dev_pack + 'cd qpsycle && qmake -recursive CONFIG-=debug_and_release CONFIG-=debug && mingw32-make', locks = [compile_lock])
			]
		)
	}
)
BuildmasterConfig['schedulers'].append(
	Scheduler(
		name = 'qpsycle.mingw',
		builderNames = ['qpsycle.mingw'],
		fileIsImportant = lambda change: filter(change, ['qpsycle/', 'psycle-core/', 'psycle-audiodrivers/'])
	)
)

# mingw raw pkg + upload

BuildmasterConfig['builders'].append(
	{
		'name': 'qpsycle.mingw.pkg',
		'category': 'psycle',
		'slavenames': microsoft_slaves,
		'builddir': svn_dir + 'qpsycle.mingw.pkg',
		'factory': factory.BuildFactory(
			[
				factory.s(SVNUpdate),
				factory.s(Compile, command = microsoft_dev_pack + 'cd qpsycle && sh -c ./make-microsoft-raw-package', locks = [compile_lock]),
				factory.s(Upload, command =
					'scp -F ../../../../.ssh/config qpsycle/++install/qpsycle.tar.bz2 ' +
					'upload.buildborg.retropaganda.info:psycle/htdocs/packages/microsoft/ && ' +
					'echo download the package at http://psycle.sourceforge.net/packages/microsoft/qpsycle.tar.bz2'
				)
			]
		)
	}
)

##################################### psycle-plugins builders ######################################

# gnu

BuildmasterConfig['builders'].append(
	{
		'name': 'psycle-plugins',
		'category': 'psycle',
		'slavenames': slaves,
		'builddir': svn_dir + 'psycle-plugins',
		'factory': factory.BuildFactory(
			[
				factory.s(SVNUpdate),
				factory.s(Compile, command = 'scons --directory=psycle-plugins', locks = [compile_lock])
			]
		)
	}
)
BuildmasterConfig['schedulers'].append(
	Scheduler(
		name = 'psycle-plugins',
		branch = None,
		fileIsImportant = lambda change: filter(change, ['psycle-plugins/', 'universalis/', 'diversalis/', 'packageneric/'])
	)
)

# mingw

BuildmasterConfig['builders'].append(
	{
		'name': 'psycle-plugins.mingw',
		'category': 'psycle',
		'slavenames': microsoft_slaves,
		'builddir': svn_dir + 'psycle-plugins.mingw',
		'factory': factory.BuildFactory(
			[
				factory.s(SVNUpdate),
				factory.s(Compile, command = microsoft_dev_pack + 'scons --directory=psycle-plugins', locks = [compile_lock])
			]
		)
	}
)
BuildmasterConfig['schedulers'].append(
	Scheduler(
		name = 'psycle-plugins.mingw',
		builderNames = ['psycle-plugins.mingw'],
		fileIsImportant = lambda change: filter(change, ['psycle-plugins/', 'universalis/', 'diversalis/', 'packageneric/'])
	)
)

# mingw raw pkg + upload

BuildmasterConfig['builders'].append(
	{
		'name': 'psycle-plugins.mingw.pkg',
		'category': 'psycle',
		'slavenames': microsoft_slaves,
		'builddir': svn_dir + 'psycle-plugins.mingw.pkg',
		'factory': factory.BuildFactory(
			[
				factory.s(SVNUpdate),
				factory.s(Compile, command = microsoft_dev_pack + 'cd psycle-plugins && sh -c ./make-microsoft-raw-package', locks = [compile_lock]),
				factory.s(Upload, command =
					'scp -F ../../../../.ssh/config psycle-plugins/++packageneric/variants/default/install/psycle-plugins.tar.bz2 ' +
					'upload.buildborg.retropaganda.info:psycle/htdocs/packages/microsoft/ && ' +
					'echo download the package at http://psycle.sourceforge.net/packages/microsoft/psycle-plugins.tar.bz2'
				)
			]
		)
	}
)

##################################### psycle-helpers builders ######################################

# gnu

BuildmasterConfig['builders'].append(
	{
		'name': 'psycle-helpers',
		'category': 'psycle',
		'slavenames': slaves,
		'builddir': svn_dir + 'psycle-helpers',
		'factory': factory.BuildFactory(
			[
				factory.s(SVNUpdate),
				factory.s(PolicyCheck, command = './tools/check-policy diversalis universalis psycle-helpers', locks = [compile_lock]),
				factory.s(Compile, command = 'scons --directory=psycle-helpers', locks = [compile_lock]),
				factory.s(Test, command = './++packageneric/variants/default/stage-install/usr/local/bin/psycle-helpers_unit_tests --log_level=test_suite --report_level=detailed', locks = [compile_lock])
			]
		)
	}
)
BuildmasterConfig['schedulers'].append(
	Scheduler(
		name = 'psycle-helpers',
		builderNames = ['psycle-helpers'],
		fileIsImportant = lambda change: filter(change, ['psycle-helpers/', 'universalis/', 'diversalis/', 'packageneric/'])
	)
)

# mingw

BuildmasterConfig['builders'].append(
	{
		'name': 'psycle-helpers.mingw',
		'category': 'psycle',
		'slavenames': microsoft_slaves,
		'builddir': svn_dir + 'psycle-helpers.mingw',
		'factory': factory.BuildFactory(
			[
				factory.s(SVNUpdate),
				factory.s(PolicyCheck, command = microsoft_dev_pack + 'python .\\tools\\check-policy diversalis universalis psycle-helpers'),
				factory.s(Compile, command = microsoft_dev_pack + 'scons --directory=psycle-helpers'),
				factory.s(Test, command =
					microsoft_dev_pack +
					'.\\++packageneric\\variants\\default\\stage-install\\usr\\local\\bin\\psycle-helpers_unit_tests ' +
					'--log_level=test_suite --report_level=detailed')
			]
		)
	}
)
BuildmasterConfig['schedulers'].append(
	Scheduler(
		name = 'psycle-helpers.mingw',
		builderNames = ['psycle-helpers.mingw'],
		fileIsImportant = lambda change: filter(change, ['psycle-helpers/', 'universalis/', 'diversalis/', 'packageneric/'])
	)
)

##################################### psycle.msvc builder ######################################

# msvc

BuildmasterConfig['builders'].append(
	{
		'name': 'psycle.msvc',
		'category': 'psycle',
		'slavenames': microsoft_slaves_msvc,
		'builddir': svn_dir + 'psycle.msvc',
		'factory': factory.BuildFactory(
			[
				factory.s(SVNUpdate),
				factory.s(Compile, command = with_microsoft_dev_pack(
					'call .\\psycle\\make\\msvc_8.0\\build release',
					mingw = False, msvc = True)
			]
		)
	}
)
BuildmasterConfig['schedulers'].append(
	Scheduler(
		name = 'psycle.msvc',
		builderNames = ['psycle.msvc'],
		fileIsImportant = lambda change: filter(change, ['psycle/', 'psycle-helpers/', 'psycle-core/', 'psycle-audiodrivers/', 'universalis/', 'diversalis/', 'packageneric/'])
	)
)

##################################### statuses ######################################

BuildmasterConfig['status'] = []

categories = None #['psycle', 'sondar', 'armstrong']

##################################### waterfall http status ######################################

from buildbot.status.html import Waterfall
BuildmasterConfig['status'].append(Waterfall(http_port = 8010, css = 'waterfall.css', robots_txt = 'robots.txt', allowForce=False, categories = categories))
	# Note: Spam bots manage to trigger random builds with the "force build" button. It's annoying since they usually request the build of an inexistant revision
	#       by filling the form with random garbage, and we get irc/e-mail messages about the spurious build failure.
	#       When allowForce is set to False, the "force build" button is removed.

##################################### mail status ######################################

from buildbot.status.mail import MailNotifier
BuildmasterConfig['status'].append(MailNotifier(fromaddr = email, mode = 'problem', categories = ['psycle', 'sondar'], lookup = 'users.sourceforge.net'))

##################################### irc status ######################################

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
		result = []
		joined = self.irc().channels
		if '#psycle' in joined: result.append('#psycle') # we're able to see everything there
		if builderName.startswith('sondar') and 'sondar' in joined: result.append('#sondar')
		elif builderName.startswith('armstrong') and 'aldrin' in joined: result.append('#aldrin')
		return result

BuildmasterConfig['status'].append(IRC(host = 'irc.efnet.net'   , nick = 'buildborg', channels = ['#psycle']                      , categories = categories))
BuildmasterConfig['status'].append(IRC(host = 'irc.freenode.net', nick = 'buildborg', channels = ['#psycle', '#sondar', '#aldrin'], categories = categories))

##################################### non-psycle stuff ######################################

if True:
	##################################### sondar builders ######################################
	
	BuildmasterConfig['builders'].append({
		'category': 'sondar',
		'name': 'sondar',
		'slavenames': slaves,
		'builddir': 'sondar-trunk',
		'factory': factory.BuildFactory([
			factory.s(SVNUpdate, svnurl = 'https://sondar.svn.sourceforge.net/svnroot/sondar/trunk'),
			factory.s(Compile,
				name = 'compile-sondar',
				description = ['compiling sondar'],
				descriptionDone = ['compile sondar'],
				command =
					'cd sondar &&' +
					'sh autogen.sh --prefix=$(dirname $(pwd))/install &&' +
					'make install'),
			factory.s(Compile
				name = 'compile-gui',
				description = ['compiling gui'],
				descriptionDone = ['compile gui'],
				command =
					'export PKG_CONFIG_PATH=$(pwd)/install/lib/pkgconfig && ' +
					'cd host_gtk && ' +
					'sh autogen.sh --prefix=$(dirname $(pwd))/install && ' +
					'make install')
		])
	})
	BuildmasterConfig['schedulers'].append(Scheduler(
		name = 'sondar',
		builderNames = ['sondar'],
		fileIsImportant = lambda change: filter(change, ['sondar/', 'host_gtk/'])
	))

if False:
	##################################### armstrong builders ######################################
	
	# Note: These builders had to be disabled because the project is too much an unstable moving target.

	class HgUpdate(step.ShellCommand):
		name = 'update'
		description = ['updating']

	# armstrong repository lack subfolders.. we need to do crazy things to detect which repository it is
	armstrong_exclude_prefixes = [
		'branches/', 'tags/',
		'/trunk/dependencies.dot', '/trunk/dependencies.png', '/README', 'tools/', 'freepsycle/', 'qpsycle/', 'psycle-core/',
		'psycle-player/', 'psycle-helpers', 'psycle-audiodrivers/', 'psycle-plugins/', 'psycle/',
		'universalis/', 'diversalis/', 'packageneric/', 'buildbot/', 'external-packages/', 'www/'
	]

	def append_armstrong_builder(variant, slaves, microsoft = False, mingw = True, msvc = False):
		name = 'armstrong'
		BuildmasterConfig['builders'].append({
			'category': name,
			'name': name + variant,
			'slavenames': slaves,
			'builddir': os.path.join(name + '-trunk', name + variant),
			'factory': factory.BuildFactory([
				# todo factory.s(HgUpdate),
				factory.s(step.Compile, microsoft = microsoft, mingw = mingw, msvc = msvc,
					command = 'scons configure ' + (mingw and 'TOOLS=mingw ')+ '&& scons')
		])})
		BuildmasterConfig['schedulers'].append(Scheduler(
			name = name + variant,
			builderNames = [name + variant],
			fileIsImportant = lambda change: filter(change, include_prefixes = [''], exclude_prefixes = armstrong_exclude_prefixes)
		))
	
	append_armstrong_builder('', slaves)
	armstrong_microsoft_slaves = ['winux']
	append_armstrong_builder('.mingw', armstrong_microsoft_slaves, microsoft = True)
	append_armstrong_builder('.msvc' , armstrong_microsoft_slaves, microsoft = True, msvc = True)

##################################### clean builders ######################################

class Clean(step.ShellCommand):
	name = 'clean'
	description = ['cleaning']
	descriptionDone = ['cleaned']
	def __init__(self, *args, **kwargs):
		kwargs['workdir'] = '..'
		kwargs['locks'] = all_locks
		step.ShellCommand.__init__(self, *args, **kwargs)

clean_factory = factory.BuildFactory([factory.s(Clean,
	command = 'find . -ignore_readdir_race -name ++\\* -exec rm -Rf {} \\; ; sleep 5')]) # might be too fast!
clean_factory_microsoft = factory.BuildFactory([factory.s(Clean,
	command = 'del /s /q ++*')])

from buildbot.scheduler import Periodic as PeriodicScheduler

def append_clean_builder(slave_name, microsoft = False):
	if microsoft: factory = clean_factory_microsoft
	else: factory = clean_factory
	BuildmasterConfig['builders'].append({
		'name': 'clean.' + slave_name,
		'category': None,
		'slavenames': [slave_name],
		'builddir': 'clean.' + slave_name,
		'factory': factory
	})
	if not microsoft: # don't schedule it on microsoft slaves since these aren't stable enough
		BuildmasterConfig['schedulers'].append(PeriodicScheduler(
			name = 'clean.' + slave_name,
			branch = None,
			periodicBuildTimer = 60 * 60 * 24 * 30, # 30 days
			builderNames = ['clean.' + slave_name]
		))
	
for slave in slaves: append_clean_builder(slave)
for slave in microsoft_slaves: append_clean_builder(slave, microsoft = True)
