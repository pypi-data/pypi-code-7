from functools import partial
from flask import url_for, redirect, session, Blueprint, render_template, flash
from flask.ext.babel import gettext as t, ngettext as nt


class View:
    endpoint = None
    url = None
    messages = {}
    templates = {}


    def __init__(self, bp):
        if not self.endpoint:
            raise Exception('`{!s}.endpoint` is not defined'.format(self))
        self.bp = bp
        self.url = self.endpoint if self.url is None else self.url
        self.session = session.setdefault(self.endpoint, {})


    # HELPERS ------------------------------------------------------------------
    def render(self, template_name, **context):
        if '.' not in template_name:
            template_name = self.templates[template_name]
        context['view'] = self
        return render_template(template_name, **context)


    def flash(self, message, num=None, **kwargs):
        if num :
            try:
                message, category = nt(message[0], message[1], num=num), self.messages[message[0], message[1]]
            except KeyError:
                message, category = nt(message, message, num=num), self.messages[message, message]
        else:
            message, category = t(message), self.messages[message]
        return flash(message.format(**kwargs), category)


    def redirect(self, endpoint, **kwargs):
        return redirect(self.url_for(endpoint, **kwargs))


    def url_for(self, endpoint, **values):
        if isinstance(self.bp, Blueprint):
            return url_for('{bp}.{self.endpoint}:{endpoint}'.format(
                bp=self.bp.name, self=self, endpoint=endpoint), **values
            )
        else:
            return url_for('{self.endpoint}:{endpoint}'.format(
                self=self, endpoint=endpoint), **values
            )


    def lazy_url_for(self, endpoint, **values):
        if isinstance(self.bp, Blueprint):
            return partial(url_for, '{bp}.{self.endpoint}:{endpoint}'.format(
                bp=self.bp.name, self=self, endpoint=endpoint), **values
            )
        else:
            return partial(url_for, '{self.endpoint}:{endpoint}'.format(
                self=self, endpoint=endpoint), **values
            )
