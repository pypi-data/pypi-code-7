# -*- coding: utf-8 -*-
from plone.contentrules.rule.interfaces import IRuleAction, IRuleCondition
from plone.contentrules.engine.interfaces import IRuleStorage,\
    IRuleAssignmentManager
from plone.app.contentrules.rule import Rule, get_assignments
from plone.contentrules.engine.assignments import RuleAssignment
from Products.CMFCore.interfaces._events import IActionSucceededEvent
from zope import component
from zope.globalrequest import getRequest


def isNotCurrentProfile(context):
    return context.readDataFile("blogpolicy_marker.txt") is None


def post_install(context):
    """Post install script"""
    if isNotCurrentProfile(context):
        return
    portal = context.getSite()
    request = getRequest()
    initialize_archive_rules(portal, request)


def initialize_archive_rules(portal, request):
    RULE_ID = 'archivepost'
    rule = _create_rule(portal,
                        RULE_ID,
                        "Archive Post",
                        IActionSucceededEvent)

    # add condition & action
    data = {'wf_transitions': ['publish']}
    _add_rule_condition(request,
                        rule,
                        'plone.conditions.WorkflowTransition',
                        data)
    data = {'check_types': ['blog_post']}
    _add_rule_condition(request,
                        rule,
                        'plone.conditions.PortalType',
                        data)

    root_path = '/'.join(portal.getPhysicalPath())
    data = {'target_root_folder': root_path,
            'folderish_type': 'Folder',
            'transitions': ["publish"]}
    action = 'collective.contentrules.yearmonth.actions.Move'
    _add_rule_action(request, rule, action, data)

    # activate it on context
    _activate_rule(RULE_ID, portal)


def _add_rule_condition(request, rule, condition_id, data):
    condition = component.getUtility(IRuleCondition, name=condition_id)
    adding = component.getMultiAdapter((rule, request),
                                       name='+condition')
    addview = component.getMultiAdapter((adding, request),
                                        name=condition.addview)
    addview.createAndAdd(data=data)


def _add_rule_action(request, rule, action_id, data):
    action = component.getUtility(IRuleAction, name=action_id)
    adding = component.getMultiAdapter((rule, request),
                                       name='+action')
    addview = component.getMultiAdapter((adding, request),
                                        name=action.addview)
    addview.createAndAdd(data=data)


def _create_rule(portal, rule_id, title, event):
    storage = component.getUtility(IRuleStorage)
    if rule_id not in storage:
        storage[rule_id] = Rule()
    rule = storage.get(rule_id)
    rule.title = title
    rule.enabled = True
    # Clear out conditions and actions since we're expecting new ones
    del rule.conditions[:]
    del rule.actions[:]
    rule.event = event
    rule = rule.__of__(portal)
    return rule


def _activate_rule(rule_id, context=None):
    storage = component.getUtility(IRuleStorage)
    rule = storage.get(rule_id)
    assignable = IRuleAssignmentManager(context)
    assignment = assignable.get(rule_id, None)
    if not assignment:
        assignment = assignable[rule_id] = RuleAssignment(rule_id)
    assignment.enabled = True
    assignment.bubbles = True
    get_assignments(rule).insert('/'.join(context.getPhysicalPath()))
