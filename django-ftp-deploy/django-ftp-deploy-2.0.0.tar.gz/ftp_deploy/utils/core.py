
import json
import pycurl

from .ftp import ftp_check
from .decorators import check
from .curl import curl_connection
from ftp_deploy.conf import *


class bitbucket_check(curl_connection):

    """Bitbucket check class contain all checking points for bitbucket,
        return True if fail"""

    def __init__(self, username, password, service):
        super(bitbucket_check, self).__init__(username, password)
        self.service = service

    @check('Bitbucket')
    def check_authentication(self):
        self.authenticate()
        self.perform('https://bitbucket.org/api/1.0/user/repositories')
        if self.curl.getinfo(pycurl.HTTP_CODE) != 200:
            raise Exception("Login Fail")

    @check('Bitbucket')
    def check_repo_exist(self):
        self.authenticate()
        repos = json.loads(self.perform('https://bitbucket.org/api/1.0/user/repositories'))
        for repo in repos:
            if repo['slug'] == self.service.repo_slug_name:
                return False, ''
        raise Exception("Repository %s doesn't exist" %
                        self.service.repo_slug_name)

    @check('Bitbucket')
    def check_branch_exist(self):
        self.authenticate()
        url = 'https://bitbucket.org/api/1.0/repositories/%s/%s/branches' % (
            self.username, self.service.repo_slug_name)
        branches = json.loads(self.perform(url))
        try:
            branches[self.service.repo_branch]
        except KeyError:
            raise Exception("Branch %s doesn't exist" %
                            self.service.repo_branch)

    @check('Bitbucket')
    def check_hook_exist(self):
        self.authenticate()
        url = 'https://bitbucket.org/api/1.0/repositories/%s/%s/services' % (
            self.username, self.service.repo_slug_name)
        hooks = json.loads(self.perform(url))

        if type(hooks) == list:
            for hook in hooks:
                if len(hook['service']['fields']) > 0:
                    value = hook['service']['fields'][0]['value']
                    if (value.find(str(self.service.hook_url())) != -1
                            and hook['service']['type'] == 'POST'):
                        return False, ''
        raise Exception("Hook is not set up")

    def check_all(self):
        status = self.check_authentication()
        if status[0] is True:
            return status

        status = self.check_repo_exist()
        if status[0] is True:
            return status

        status = self.check_branch_exist()
        if status[0] is True:
            return status

        return False, ''


class github_check(curl_connection):

    """Bitbucket check class contain all checking points for bitbucket,
        return True if fail"""

    def __init__(self, username, password, service):
        super(github_check, self).__init__(username, password)
        self.service = service

    @check('Github')
    def check_authentication(self):
        self.authenticate()
        self.perform('https://api.github.com/user/repos')
        if self.curl.getinfo(pycurl.HTTP_CODE) != 200:
            raise Exception("Login Fail")

    @check('Github')
    def check_repo_exist(self):
        self.authenticate()
        repos = json.loads(self.perform('https://api.github.com/user/repos'))
        for repo in repos:
            if repo['name'] == self.service.repo_slug_name:
                return False, ''
        raise Exception("Repository %s doesn't exist" %
                        self.service.repo_slug_name)

    @check('Github')
    def check_branch_exist(self):
        self.authenticate()
        url = 'https://api.github.com/repos/%s/%s/branches' % (
            self.username, self.service.repo_slug_name)
        branches = json.loads(self.perform(url))
        for branch in branches:
            if branch['name'] == self.service.repo_branch:
                return False, ''
        raise Exception("Branch %s doesn't exist" % self.service.repo_branch)

    @check('Github')
    def check_hook_exist(self):
        self.authenticate()
        url = 'https://api.github.com/repos/%s/%s/hooks' % (
            self.username, self.service.repo_slug_name)
        hooks = json.loads(self.perform(url))

        if type(hooks) == list:
            for hook in hooks:
                value = hook['config']['url']
                if (value.find(str(self.service.hook_url())) != -1
                        and hook['name'] == "web"):
                    return False, ''

        raise Exception("Hook is not set up")

    def check_all(self):
        status = self.check_authentication()
        if status[0] is True:
            return status

        status = self.check_repo_exist()
        if status[0] is True:
            return status

        status = self.check_branch_exist()
        if status[0] is True:
            return status

        return False, ''


class service_check(object):

    """Service check class, what group together all checking points.
       Return 'fails' and 'message' lists"""

    def __init__(self, service):
        self.service = service
        self.message = list()
        self.fails = [False, False, False, False]

    def check_log(self):
        """Check logs"""
        if self.service.pk is not None:
            log_fail = self.service.log_set.all().filter(
                status=False).filter(skip=False).count()
            if log_fail:
                self.message.append('<b>Log</b>: Deploy Fails(%d)' % log_fail)
                self.fails[0] = True

    def check_repo(self):
        """Check repositories connection, along with POST Hook"""
        if self.service.repo_source == 'bb':
            repo = bitbucket_check(
                BITBUCKET_SETTINGS['username'], BITBUCKET_SETTINGS['password'],
                self.service)
        elif self.service.repo_source == 'gh':
            repo = github_check(
                GITHUB_SETTINGS['username'], GITHUB_SETTINGS['password'],
                self.service)

        repo_fail, repo_fail_message = repo.check_all()
        if repo_fail:
            self.message.append(repo_fail_message)
            self.fails[1] = True

        hook_fail, hook_fail_message = repo.check_hook_exist()
        if hook_fail:
            self.message.append(hook_fail_message)
            self.fails[2] = True

    def check_ftp(self):
        """Check FTP connection"""
        ftp = ftp_check(self.service.ftp_host, self.service.ftp_username,
                        self.service.ftp_password, self.service.ftp_path)
        ftp_fail, ftp_fail_message = ftp.check_all()
        ftp.quit()

        if ftp_fail:
            self.message.append(ftp_fail_message)
            self.fails[3] = True

    def check_all(self):
        self.check_log()
        self.check_repo()
        self.check_ftp()

        return self.fails, self.message


class absolute_url(object):

    """Build absolute url to root url without trailing slash"""

    def __init__(self, request):
        self.request = request

    def build(self):
        return self.request.build_absolute_uri('/')[:-1]


class LockError(Exception):

    """Exception if service is locked"""

    def __str__(self):
        return 'Deploy failed because service is Locked!'
