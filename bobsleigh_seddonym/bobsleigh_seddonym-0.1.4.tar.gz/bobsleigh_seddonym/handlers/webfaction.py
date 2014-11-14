from bobsleigh.conf.handlers import InstallationHandler
from collections import OrderedDict
import socket


class WebfactionHandler(InstallationHandler):

    def get_required_kwargs(self):
        required_kwargs = super(WebfactionHandler, self).get_required_kwargs()
        required_kwargs += (
           # Name of the webfaction user
           'webfaction_user',
           'server_email',
        )
        return required_kwargs

    def get_optional_kwargs(self):
        optional_kwargs = super(WebfactionHandler, self).get_optional_kwargs()
        optional_kwargs.update({
            'email_host': 'smtp.webfaction.com',
            'protocol': 'http',
        })
        return optional_kwargs

    def get_config_patterns(self):
        # Because some of the items depend on the setting of ones before,
        # this needs to be an OrderedDict.
        return (
            ('log_path', '/home/%(webfaction_user)s/logs/user/%(sitename)s'),
            ('static_path', '/home/%(webfaction_user)s/webapps/%(sitename)s_static'),
            ('media_path', '/home/%(webfaction_user)s/webapps/%(sitename)s_uploads'),
            ('virtualenv_path', '/home/%(webfaction_user)s/.virtualenvs/%(sitename)s'),
            ('project_path', '/home/%(webfaction_user)s/webapps/%(sitename)s/project'),
            # Set the ability to have a prefixed name - this will
            # be used in place of the sitename for email and database creds
            ('prefixed_name', '%(sitename)s'),
            ('email_host_user', '%(prefixed_name)s'),
            ('db_name', '%(prefixed_name)s'),
            ('db_user', '%(prefixed_name)s'),
            ('base_url', '%(protocol)s://%(domain)s'),
        )

    def adjust(self):
        super(WebfactionHandler, self).adjust()
        self._settings['BASE_URL'] = self.config.base_url

    def is_current(self):
        """Webfaction-specific way of detecting whether this
        is the current installation, since several installations
        running on one host."""
        if self.config.host == socket.gethostname():
            # Check if virtualenv matches
            virtualenv_path = '/'.join(__file__.split('/')[:5])
            return virtualenv_path == self.config.virtualenv_path
        return False


class DevHandler(WebfactionHandler):
    def get_optional_kwargs(self):
        optional_kwargs = super(DevHandler, self).get_optional_kwargs()
        optional_kwargs.update({
            'debug': True,
        })
        return optional_kwargs


class LiveHandler(WebfactionHandler):
    pass
