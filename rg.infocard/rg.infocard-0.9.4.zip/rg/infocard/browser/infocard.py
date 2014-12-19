# -*- coding: utf-8 -*-
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.dexterity.browser.add import DefaultAddForm, DefaultAddView
from plone.dexterity.browser.edit import DefaultEditForm, DefaultEditView
from rg.infocard import rg_infocard_msgfactory as _


class AddForm(DefaultAddForm):
    '''
    Add form for the server content type
    '''
    @property
    def description(self):
        ''' Overrride DexterityExtensibleForm description property
        '''
        return _(
            'edit_infocard_help',
            (
                u"Configure an infocard."
            )
        )


class EditForm(DefaultEditForm):
    '''
    Add form for the server content type
    '''
    @property
    def description(self):
        ''' Overrride DexterityExtensibleForm description property
        '''
        return _(
            'edit_infocard_help',
            (
                u"Configure an infocard."
            )
        )


class AddView(DefaultAddView):
    ''' Custom form for infocardcontainer add form
    '''
    index = ViewPageTemplateFile('templates/rg.infocard.layout.pt')
    form = AddForm


class EditView(DefaultEditView):
    ''' Custom form for infocardcontainer edit form
    '''
    index = ViewPageTemplateFile('templates/rg.infocard.layout.pt')
    form = EditForm
