
from paste.script import command
from gae_command.config import *
import os, sys
import zipfile
import urllib2
import shutil
from cStringIO import StringIO


def download_sdk(url, version):
	url = url.format(version)
	archive = StringIO()
	for line in urlget(url):
		archive.write(line)
	return archive

def install_sdk(archive, dest):
	archive.seek(0)
	zf = zipfile.ZipFile(archive)
	zf.extractall(path=dest)

def clean_local(destdir):
	if os.path.isdir(destdir):
		try:
			shutil.rmtree(destdir, ignore_errors=True)
		except:
			pass
	else:
		try:
			os.unlink(destdir)
		except:
			pass
	if os.path.exists(destdir):
		print 'no way to clean local sdk. "%s" still exists' % destdir
		return False
	return True

class GAEGlobalCommand(command.Command):

	max_args = None
	min_args = None

	#usage = "GAEGlobal"
	summary = "Commands to manipulate and invoke gae sdk"
	group_name = "Google Application Engine"

	parser = PassThroughOptionParser()
	parser.add_option('--version',
					  dest='version',
					  help="remote sdk version to download. default to last")
	parser.add_option('--force',
					  dest='force',
					  action='store_true',
					  help="upgrade should overwrite current sdk, even with same version")

	config = config_read()

	gae_sdk_root = os.path.abspath(config.get('globals', 'GAE_SDK_ROOT'))
	os.environ['GAE_SDK_ROOT'] = gae_sdk_root

	remote_last_version = get_remote_last_version(config)
	local_version = get_local_version(config)
	local_sdk = config.get('globals', 'GAE_SDK_DIR')
	remote_sdk = config.get('globals', 'DOWNLOAD_URL')

	files = [
		f for f in os.listdir(local_sdk) \
		if os.path.isfile(os.path.join(local_sdk, f))
	]
	firstlines = [
		(f, open(os.path.join(local_sdk, f), 'r').readline().strip()) \
		for f in files
	]
	commands = [
		f for f, l in firstlines if l.split() == ['#!/usr/bin/env', 'python']]

	def sdk_install(self, version):
		try:
			print version
			archive = download_sdk(url=self.remote_sdk, version=version)
			if archive.tell() and clean_local(self.local_sdk):
				install_sdk(archive, self.gae_sdk_root)
				print 'done'
		except:
			print 'failed'

	def command(self):
		cmd = self.args[0] if self.args else None
		if cmd == 'install':
			version = getattr(self.options, 'version') or self.remote_last_version
			if 'missing' != self.local_version and not getattr(self.options, 'force'):
				print "version %s already installed" % self.local_version
			else:
				print "installing..."
				self.sdk_install(version)
		if cmd == 'upgrade':
			version = getattr(self.options, 'version') or self.remote_last_version
			if version == self.local_version and not getattr(self.options, 'force'):
				print "version %s already installed" % version
			else:
				print "upgrading..."
				self.sdk_install(version)
		elif cmd == 'clean-local':
			clean_local(self.local_sdk)
			print 'done'
		elif cmd == 'save-local-config':
			config_save_local()
			print 'done'
		elif cmd == 'remote-last-version':
			print self.remote_last_version
		elif cmd == 'local-version':
			print self.local_version
		else:
			args = sys.argv[2:]
			cmd = args[0] if args else None
			projpath = None
			cwd = os.getcwd()+os.path.sep
			while os.path.sep in cwd:
				pos = cwd.rindex(os.path.sep)
				path = cwd[:pos+1]
				app_yaml = os.path.join(path, u'app.yaml')
				if os.path.isfile(app_yaml):
					projpath = path
					break
				cwd = cwd[:pos]
			if projpath:
				if cmd not in self.commands:
					cmd +='.py'
				if cmd in self.commands:
					cmd = os.path.join(self.local_sdk, cmd)
					runargs = [cmd] + args[1:]
					stdout = self.run_command(
						sys.executable, 
						*runargs, 
						cwd=projpath, 
						capture_stderr=True, 
						expect_returncode=True
					)
					print stdout
