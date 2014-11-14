from bobsleigh.conf.handlers import InstallationHandler


class LocalHandler(InstallationHandler):
    "For my local development setup."

    def get_required_kwargs(self):
        return ('sitename',)

    def get_optional_kwargs(self):
        optional_kwargs = super(LocalHandler, self).get_optional_kwargs()
        optional_kwargs.update({
            'host': 'lanky',
            'debug': True,
            'monitor': True,
            'email_host': 'smtp.gmail.com',
            'email_use_tls': True,
            'email_port': 587,
            'email_host_user': 'davidseddonis@gmail.com',
            'protocol': 'http',
        })
        return optional_kwargs

    def get_config_patterns(self):
        patterns = super(LocalHandler, self).get_config_patterns()
        patterns += (
            ('domain', '%(sitename)s.localhost'),
            ('base_url', '%(protocol)s://%(domain)s'),
            ('db_name', '%(sitename)s'),
            ('db_user', '%(sitename)s'),
            ('log_path', '/var/log/django/%(sitename)s'),
            ('static_path', '/home/david/var/www/%(sitename)s/static'),
            ('media_path', '/home/david/var/www/%(sitename)s/uploads'),
            ('virtualenv_path', '/home/david/.virtualenvs/%(sitename)s'),
            ('project_path', '/home/david/www/%(sitename)s'),
            ('server_email', 'contact@%(domain)s'),
        )
        return patterns

    def adjust(self):
        super(LocalHandler, self).adjust()
        self._settings['EMAIL_USE_TLS'] = self.config.email_use_tls
        self._settings['EMAIL_PORT'] = self.config.email_port
        self._settings['BASE_URL'] = self.config.base_url


class VagrantHandler(InstallationHandler):
    "Geared up towards Vagrant machines."

    def get_required_kwargs(self):
        return ('sitename',)

    def get_optional_kwargs(self):
        optional_kwargs = super(VagrantHandler, self).get_optional_kwargs()
        optional_kwargs.update({
            'host': 'precise32',
            'protocol': 'http',
            'debug': True,
            'monitor': True,
            'db_name': 'site',
            'db_user': 'site',
        })
        return optional_kwargs

    def get_config_patterns(self):
        patterns = super(VagrantHandler, self).get_config_patterns()
        patterns += (
            ('domain', '%(sitename)s.vagrant'),
            ('base_url', '%(protocol)s://%(domain)s'),
            ('log_path', '/var/log/django'),
            ('static_path', '/opt/site/static'),
            ('media_path', '/opt/site/uploads'),
            ('virtualenv_path', '/opt/site/.virtualenvs/site'),
            ('project_path', '/opt/site/django'),
        )
        return patterns

    def adjust(self):
        super(VagrantHandler, self).adjust()
        self._settings['BASE_URL'] = self.config.base_url
