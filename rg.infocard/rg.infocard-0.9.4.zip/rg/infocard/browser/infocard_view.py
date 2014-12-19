# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from plone import api
from plone.app.textfield.interfaces import ITransformer
from plone.memoize.view import memoize


class View(BrowserView):
    ''' Custom view and methods for infocard
    '''
    @property
    @memoize
    def authors(self):
        ''' Show the authors for this infocard
        '''
        return ", ".join(
            sorted(getattr(self.context, 'infocard_authors', ''))
        )

    @property
    @memoize
    def servicetypes(self):
        ''' Show the authors for this infocard
        '''
        return ", ".join(sorted(self.context.servicetypes))

    @property
    @memoize
    def recipients(self):
        ''' Show the authors for this infocard
        '''
        return ", ".join(sorted(self.context.recipients))

    @property
    @memoize
    def modified(self):
        ''' Show the authors for this infocard
        '''
        return self.context.modified()

    @property
    @memoize
    def public_infos(self):
        ''' Return all the infos that are public
        '''
        return [
            info for info in self.context.informations
            if info['arg_public']
        ]

    @property
    @memoize
    def private_infos(self):
        ''' Return all the infos that are public
        '''
        return [
            info for info in self.context.informations
            if not info['arg_public']
        ]

    @property
    @memoize
    def allowed_infos(self):
        ''' Return all the infos that are public
        '''
        if api.user.is_anonymous():
            return self.public_infos
        else:
            return self.context.informations

    @property
    @memoize
    def searched_text(self):
        ''' The text searched
        '''
        parts = [
            self.context.title,
            self.context.description
        ]
        transformer = ITransformer(self.context)
        parts.extend([
            transformer(x['arg_value'], 'text/plain')
            for x in self.allowed_infos
            if x['arg_value']
        ])
        return u" ".join(set(u" ".join(parts).lower().split()))
