# -*- coding: utf-8 -*-
# Copyright 2014 Powerleader, PLCLOUD
# Author: Joe Lei <jiaomin.lei@powerleader.com.cn>
import os

from keystoneclient import utils

from plcloudclient.v1_0 import client as plcloud_client


def env_client():
    username = os.environ.get('OS_USERNAME')
    password = os.environ.get('OS_PASSWORD')
    auth_url = os.environ.get('OS_AUTH_URL')
    tenant_name = os.environ.get('OS_TENANT_NAME')
    region_name = os.environ.get('OS_REGION_NAME')
    endpoint = os.environ.get('PLCLOUD_SERVICE_ENDPOINT')
    token = os.environ.get('OS_TOKEN')
    if endpoint:
        c = plcloud_client.Client(endpoint=endpoint,
                                  token=token)
    else:
        c = plcloud_client.Client(username=username,
                                  password=password,
                                  tenant_name=tenant_name,
                                  auth_url=auth_url,
                                  region_name=region_name)
    return c

client = env_client()


def do_notification_list(kc, args):
    notification = client.notification.list()
    show_items = ['id', 'name', 'create_time']
    if notification and 'user_id' in notification[0].to_dict():
        show_items.extend(['user_id', 'user_name'])
    utils.print_list(notification, show_items, order_by='id')


@utils.arg('--name', metavar='<name>', required=True,
           help='New notification name.')
def do_notification_create(kc, args):
    notification = client.notification.create(args.name)
    utils.print_dict(notification._info)


@utils.arg('--id', metavar='<id>', required=True,
           help='notification id.')
def do_notification_delete(kc, args):
    client.notification.delete(args.id)
    print 'Delete notification list "%s" success.' % args.id


@utils.arg('--id', metavar='<id>', required=True,
           help='notification id.')
def do_notification_show(kc, args):
    notification = client.notification.get(args.id).fix_items
    show_items = ['id', 'type', 'context', 'verified',
                  'create_time', 'remarks']
    if notification and 'user_id' in notification[0].to_dict():
        show_items.extend(['user_id', 'user_name', 'verified_time'])
    utils.print_list(notification, show_items, order_by='id')


def do_notification_tpl_list(kc, args):
    tpl = client.notification.list_template()
    show_items = ['id', 'name', 'type', 'create_time', 'update_time',
                  'remarks']
    utils.print_list(tpl, show_items, order_by='id')


@utils.arg('--id', metavar='<id>', required=True,
           help='notification template id.')
def do_notification_tpl_show(kc, args):
    tpl = client.notification.get_template(args.id)
    context = tpl.context
    del tpl._info['context']
    utils.print_dict(tpl._info)
    print '-------------- context --------------'
    print context
    print '-------------------------------------'


@utils.arg('--name', metavar='<name>', required=True,
           help='New notification template name.')
@utils.arg('--type', metavar='<ype>', required=True,
           help='New notification template type.')
@utils.arg('--context', metavar='<context>', required=True,
           help='New notification template context.')
@utils.arg('--remarks', metavar='<remarks>', required=False,
           help='New notification template remarks.')
def do_notification_tpl_create(kc, args):
    tpl = client.notification.create_template(
        args.name, args.type, args.context, args.remarks)
    context = tpl.context
    del tpl._info['context']
    utils.print_dict(tpl._info)
    print '-------------- context --------------'
    print context
    print '-------------------------------------'


@utils.arg('--id', metavar='<id>', required=True,
           help='New notification template name.')
def do_notification_tpl_delete(kc, args):
    client.notification.delete_template(args.id)
    print 'Delete notification template "%s" success.' % args.id


@utils.arg('--id', metavar='<tid>', required=True,
           help='New notification template id.')
@utils.arg('--context', metavar='<context>', required=False,
           help='New notification template context.')
@utils.arg('--remarks', metavar='<remarks>', required=False,
           help='New notification template remarks.')
def do_notification_tpl_update(kc, args):
    tpl = client.notification.update_template(
        args.id, args.context, args.remarks)
    context = tpl.context
    del tpl._info['context']
    utils.print_dict(tpl._info)
    print '-------------- context --------------'
    print context
    print '-------------------------------------'


def do_cdn_list(kc, args):
    cdn = client.cdn.list()
    formatters = {'domainId': lambda x: getattr(x, 'domainId', ''),
                  'domainName': lambda x: getattr(x, 'domainName', ''),
                  'serviceType': lambda x: getattr(x, 'serviceType', '')}
    show_items = ['domainId', 'domainName', 'cname', 'areas', 'origin_ips',
                  'serviceType', 'status']
    if cdn and 'project_id' in cdn[0].to_dict():
        show_items.extend(['project_id', 'project_name'])
    utils.print_list(cdn, show_items, formatters, order_by='domainId')


@utils.arg('--domain', metavar='<domain>', required=True,
           help='New notification name.')
@utils.arg('--areas', metavar='<areas>', required=True,
           help='New notification areas.')
@utils.arg('--origin_ips', metavar='<origin_ips>', required=True,
           help='New notification origin_ips.')
def do_cdn_create(kc, args):
    cdn = client.cdn.create(domain=args.domain,
                            origin_ips=args.origin_ips,
                            areas=args.areas)
    utils.print_dict(cdn._info)
