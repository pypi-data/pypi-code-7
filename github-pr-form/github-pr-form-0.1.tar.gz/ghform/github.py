import os
import shutil
import json
import click
import sh
from github3 import login as ghlogin
from pkg_resources import resource_filename


class Repo(object):

    def __init__(self, ghname, token):
        self.token = token
        self.owner, self.name = ghname.split('/')
        gh = ghlogin(token=token)
        self.api = gh.repository(self.owner, self.name)


class Pull(object):

    def __init__(self, number, repo):
        self.number = number
        gh = ghlogin(token=repo.token)
        self.api = gh.issue(repo.owner, repo.name, number)

    def add_form(self, form, tracker):
        self.api.create_comment(('Uploading a {} form in next comment...\n'
                                 'The PNG screenshot of it can be found'
                                 ' [here]({})').format(form.tplname,
                                                       form.pngurl(tracker)))
        self.api.create_comment(form.to_md())

    def do_form_actions(self, form, repo):
        for field in form.data['fields']:
            self.do_field_actions(field, repo)
        for group in form.data['groups']:
            for field in group['fields']:
                self.do_field_actions(field, repo)

    def do_field_actions(self, field, repo):
        lbl = None
        act = None
        response = field.get('response', None)
        if field['type'] == 'choice':
            for opt in field['options']:
                if opt['name'] == response:
                    lbl = opt.get('label', None)
                    break
        act = field.get('action', None)
        if lbl:
            for repo_lbl in repo.api.iter_labels():
                if repo_lbl.name == lbl:
                    break
            else:
                repo.api.create_label(lbl, 'fad8c7')
            self.api.add_labels(lbl)
        if act:
            if act == 'assign':
                self.api.assign(field['response'])


class Tracker(object):

    def __init__(self, ghname):
        self.ghname = ghname
        self.owner, self.name = ghname.split('/')
        self.url = 'https://github.com/{}'.format(ghname)
        self.path = os.path.join(resource_filename(__name__, ''), self.name)
        self.tpldir = os.path.join(self.path, 'tpl')
        self.git = sh.git.bake(_cwd=self.path, _tty_out=False)

    def clone(self):
        if not os.path.exists(self.path):
            sh.git.clone(self.url, self.path)

    def add_commit_push(self, msg):
        self.git.add(A=True)
        self.git.commit(m=msg)
        self.git.push()

    def add_tpl(self, tplpath):
        tplname = os.path.basename(tplpath)
        newtplpath = os.path.join(self.tpldir, tplname)
        ghtplpath = os.path.join('tpl', tplname)
        self.git.pull()
        if not os.path.exists(self.tpldir):
            os.mkdir(self.tpldir)
        shutil.copyfile(tplpath, newtplpath)
        msg = 'Add {} template'.format(tplname)
        self.add_commit_push(msg)

    def list_tpls(self):
        return [os.path.splitext(f)[0] for f in os.listdir(self.tpldir)]

    def get_tpl_path(self, tplname):
        if tplname not in self.list_tpls():
            raise RuntimeError(('{} template not found,'
                               ' please addtpl it').format(tpl))
        return os.path.join(self.tpldir, tplname) + '.json'

    def sha(self):
        return self.git.log(format='%H', n=1, _tty_out=False).strip()
