
from twisted.application import service
from buildbot.master import BuildMaster
import os

basedir = os.getcwd()
configfile = r'configuration.py'

application = service.Application('buildmaster')
BuildMaster(basedir, configfile).setServiceParent(application)
