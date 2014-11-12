import os
import time
import json
import urllib2
import markdown2
import click
from datetime import datetime
from github3 import login as ghlogin
from selenium import webdriver


class Form(object):

    def __init__(self, tplname, repo, tracker, pull):
        self.gh = ghlogin(token=repo.token)
        self.tplname = tplname
        self.tplpath = tracker.get_tpl_path(tplname)
        self.formdir = tracker.path
        self.formname = '{}-{}-{}-{}'.format(repo.owner, repo.name,
                                             pull.number, tplname)
        self.jsonname = self.formname + '.json'
        self.mdname = self.formname + '.md'
        self.htmlname = self.formname + '.html'
        self.pngname = self.formname + '.png'
        self.jsonpath = os.path.join(self.formdir, self.jsonname)
        self.mdpath = os.path.join(self.formdir, self.mdname)
        self.htmlpath = os.path.join(self.formdir, self.htmlname)
        self.pngpath = os.path.join(self.formdir, self.pngname)
        if os.path.exists(self.jsonpath):
            datapath = self.jsonpath
        else:
            datapath = self.tplpath
        with open(datapath, 'r') as f:
            self.data = json.loads(f.read())

    def get_responses(self, pull):
        for field in self.data['fields']:
            self.get_field_response(field, pull)
            click.echo()
        for group in self.data['groups']:
            for field in group['fields']:
                self.get_field_response(field, pull)
                click.echo()

    def write_json(self):
        with open(self.jsonpath, 'w') as f:
            json.dump(self.data, f, indent=4, separators=(',', ': '),
                      sort_keys=True)

    def to_md(self):
        mdstr = '# {}\n\n'.format(self.data['name'])
        for field in self.data['fields']:
            mdstr = mdstr + self.field_to_md(field)
        for group in self.data['groups']:
            mdstr = mdstr + '## {}\n\n'.format(group['name'])
            for field in group['fields']:
                mdstr = mdstr + self.field_to_md(field)
        mdstr = mdstr.rstrip()
        return mdstr

    def write_md(self):
        with open(self.mdpath, 'w') as f:
            f.write(self.to_md())

    def to_html(self):
        return markdown2.markdown(self.to_md())

    def write_html(self):
        with open(self.htmlpath, 'w') as f:
            f.write(self.to_html())

    def write_png(self):
        driver = webdriver.Firefox()
        driver.set_window_size(800, 600)
        driver.get('file://' + self.htmlpath)
        driver.execute_script("document.body.bgColor = 'white'")
        driver.save_screenshot(self.pngpath)
        driver.quit()

    def pngurl(self, tracker):
        return 'https://github.com/{}/blob/{}/{}'.format(tracker.ghname,
                                                         tracker.sha(),
                                                         self.pngname)

    def prepare_field_prompt_kwargs(self, field, pull):
        text = '{}\n\t{}\n'.format(field['name'], field['description'])
        default = field.get('default', None)
        show_default = False
        if field['type'] in ('choice', 'username') and 'options' in field:
            opt_list = [opt['name'] for opt in field['options']]
            opt_txt = ', '.join(opt_list)
            text = text + '\toptions: {}\n'.format(opt_txt)
            default = default or opt_list[0]
            show_default = True
        if field['type'] == 'username':
            if field.get('default', '') == 'submitter':
                default = pull.api.to_json()['user']['login']
                show_default = True
        text = text + '\t' + field['type']
        if 'response' in field:
            default = field['response']
            show_default = True
        return {'text': text, 'default': default,
                'show_default': show_default}

    def get_field_response(self, field, pull):
        prompt_kwargs = self.prepare_field_prompt_kwargs(field, pull)
        field['response'] = click.prompt(**prompt_kwargs)
        valid, msg = self.validate_field_response(field)
        while not valid:
            click.echo(click.style(msg, fg='red'))
            field['response'] = click.prompt(**prompt_kwargs)
            valid, msg = self.validate_field_response(field)

    def validate_field_response(self, field):
        valid = True
        msg = ''
        if field['type'] in ('choice', 'username') and 'options' in field:
            opt_list = [opt['name'] for opt in field['options']]
            if field['response'] not in opt_list:
                msg = 'please pick one of the options'
                valid = False
        if field['type'] == 'url/text':
            parts = field['response'].split()
            if len(parts) == 1 and not self.url_exists(parts[0]):
                msg = 'please enter a valid url'
                valid = False
        if field['type'] == 'time':
            try:
                dt = datetime.strptime(field['response'], '%H:%M')
            except ValueError:
                msg = 'please use HH:MM format'
                valid = False
        if field['type'] == 'datetime':
            try:
                dt = datetime.strptime(field['response'], '%m-%d-%y %H:%M')
            except ValueError:
                msg = 'please use MM-DD-YY HH:MM format'
                valid = False
        if field['type'] == 'username':
            usr = self.gh.user(field['response'])
            if not usr:
                msg = 'please enter a valid github username'
                valid = False
        return valid, msg

    def field_to_md(self, field):
        response = field.get('response', '')
        mdstr = '**{}:**'.format(field['name'])
        if field['type'] == 'url/text':
            parts = response.split()
            url = parts[0]
            if len(parts) == 1 and url.endswith(('.png', '.jpg', '.gif',
                                                 '.psd', '.svg')):
                mdstr = mdstr + '\n\n![{}]({})\n\n'.format(field['name'],
                                                           response)
            else:
                mdstr = mdstr + '\n\n{}\n\n'.format(response)
        elif field['type'] == 'text':
            mdstr = mdstr + '\n\n{}\n\n'.format(response)
        elif field['type'] == 'username':
            usr = self.gh.user(response)
            mdstr = mdstr + ' {} (@{})\n\n'.format(usr.name, response)
        else:
            mdstr = mdstr + ' {}\n\n'.format(response)
        return mdstr

    @staticmethod
    def url_exists(url):
        try:
            response = urllib2.urlopen(url)
        except (ValueError, urllib2.URLError, urllib2.HTTPError):
            return False
        return True
