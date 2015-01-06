# -*- coding: utf-8 -*-

def upgrade_1_to_2(context):
    setup = getToolByName(context, 'portal_setup')
    setup.runAllImportStepsFromProfile('profile-collective.directory:default')