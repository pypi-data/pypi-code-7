# -*- coding: utf-8 -*-

from collective.tinymceplugins.advfilelinks import logger
from Products.CMFCore.utils import getToolByName


def migrateTo_0_2_0(context):
    setup_tool = getToolByName(context, 'portal_setup')
    setup_tool.runAllImportStepsFromProfile('profile-collective.tinymceplugins.advfilelinks:to_0_2_0')
    setup_tool.runImportStepFromProfile('profile-collective.tinymceplugins.advfilelinks:default', 'browserlayer')
    logger.info("Migrated to version 0.2")

def migrateTo_1_3_0(context):
    setup_tool = getToolByName(context, 'portal_setup')
    setup_tool.runAllImportStepsFromProfile('profile-collective.mtrsetup:default')
    setup_tool.runAllImportStepsFromProfile('profile-collective.mtrsetup:example')
    setup_tool.runImportStepFromProfile('profile-collective.tinymceplugins.advfilelinks:default', 'mimetypes')
    logger.info("Migrated to version 1.3.0")

def migrateTo_1_3_1(context):
    setup_tool = getToolByName(context, 'portal_setup')
    # this below it's not exactly fair, but meanwhile versione 1.5.2 or mtrsetup has been released
    setup_tool.runAllImportStepsFromProfile('profile-collective.mtrsetup:example')
    setup_tool.runImportStepFromProfile('profile-collective.tinymceplugins.advfilelinks:default', 'mimetypes')
    logger.info("Migrated to version 1.3.1")
