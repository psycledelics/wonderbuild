
from twisted.application import service
from buildbot.slave.bot import BuildSlave
import os

basedir = os.getcwd()
host = 'factoid.retropaganda.info'
port = 9989
slavename = 'winux'
passwd = 'password'
keepalive = 600
usepty = 1
umask = None

application = service.Application('buildslave')
s = BuildSlave(host, port, slavename, passwd, basedir, keepalive, usepty,
               umask=umask)
s.setServiceParent(application)

