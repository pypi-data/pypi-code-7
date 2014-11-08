
from paste.script import templates, command, create_distro
from gae_command.config import *
import tempfile
import shutil
import os


class GAETemplate(templates.Template):

	egg_plugins = ['gae']
	summary = 'Template for creating a basic GAE package'
	_template_dir = 'templates'

	def pre(self, command, output_dir, vars):
		vars['package'] = ''
		if os.path.exists(vars['project']):
			raise Exception('%(project)s already exists' % vars)
		self._template_dir = tempfile.mkdtemp()
		package_dir = os.path.join(self._template_dir, '+package+')
		config = config_read()
		local_sdk = config.get('globals', 'GAE_SDK_DIR')
		shutil.copytree(
			os.path.join(local_sdk, 'new_project_template'), package_dir)
		app_yaml = os.path.join(package_dir, 'app.yaml')
		app_yaml_txt = open(app_yaml, 'r').read()
		app_yaml_txt = app_yaml_txt.replace(
			'new-project-template', '${project}')
		open('%s_tmpl' % app_yaml, 'w').write(app_yaml_txt)
		os.unlink(app_yaml)

	def post(self, command, output_dir, vars):
		shutil.rmtree(self._template_dir)


class GAETemplateApply(GAETemplate):

	summary = 'Template for applying a GAE info to current directory'

	def pre(self, command, output_dir, vars):
		if os.path.exists('app.yaml'):
			raise Exception('template already applied' % vars)
		self._temp_cwd = os.getcwd()
		os.chdir(tempfile.mkdtemp())
		if self._temp_cwd == os.getcwd():
			raise Exception('couldn\'t create temporary directory')
		super(GAETemplateApply, self).pre(command, output_dir, vars)
	
	def post(self, command, output_dir, vars):
		app_yaml = os.path.join(vars['project'], 'app.yaml')
		app_yaml_txt = open(app_yaml, 'r').read()
		tmpcwd = os.getcwd()
		os.chdir(self._temp_cwd)
		open('app.yaml', 'w').write(app_yaml_txt)
		shutil.rmtree(tmpcwd)
		shutil.rmtree(self._template_dir)


class GAETemplateCommand(command.Command):

	summary = 'Create a template for a basic GAE package'
	group_name = "Google Application Engine"
	template = "--template=gae"
	parser = command.Command.standard_parser(verbose=False)

	def command(self):
		config = config_read()
		if get_local_version(config) == 'missing':
			print 'gae sdk not innstalled'
			print 'to install, run paster gae install.'
			return
		command = create_distro.CreateDistroCommand("create")
		cmd_args = []
		cmd_args.append(self.template)
		cmd_args.append("-q")
		try:
			command.run(cmd_args)
		except Exception as e:
			print e


class GAETemplateApplyCommand(GAETemplateCommand):

	summary = 'Apply a GAE template to the current directory'
	template = "--template=gae-apply"

