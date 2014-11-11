#!/usr/bin/env python

'''
ElasticBox Confidential
Copyright (c) 2014 All Right Reserved, ElasticBox Inc.

NOTICE:  All information contained herein is, and remains the property
of ElasticBox. The intellectual and technical concepts contained herein are
proprietary and may be covered by U.S. and Foreign Patents, patents in process,
and are protected by trade secret or copyright law. Dissemination of this
information or reproduction of this material is strictly forbidden unless prior
written permission is obtained from ElasticBox
'''

import argparse
import httplib
import inspect
import json
import keyring
import os
import requests
import sys
import traceback
import urlparse

from mimetypes import types_map


REQUESTS_TIMEOUT_SECONDS = 30

EBX_CREDENTIALS_NAME = 'ElasticBox Token'
EBX_CREDENTIALS_ACCOUNT = 'elasticbox'

SCHEMA_VERSION = '2014-10-09'
DEPLOY_SERVICE_REQUEST_SCHEMA = 'http://elasticbox.net/schemas/{0}/deploy-instance-request'.format(SCHEMA_VERSION)

TOKEN_URL = '/services/security/token'

# It is provisional until we find a way to specify a default URL to connect
DEFAULT_URL = 'https://elasticbox.com'

# These are URL templates that are used to reach different controllers in the web services.
# Instances
START_INSTANCE_TEMPLATE = '{instance_id}/poweron'
STOP_INSTANCE_TEMPLATE = '{instance_id}/shutdown'
RECONFIGURE_INSTANCE_TEMPLATE = '{instance_id}/reconfigure'
REINSTALL_INSTANCE_TEMPLATE = '{instance_id}/reinstall'

UPLOAD_BOX_BLOB_TEMPLATE = 'services/blobs/upload/{0}'

# Workspaces
INSTANCES_TEMPLATE = '{workspace_id}/instances'
PROFILES_TEMPLATE = '{workspace_id}/profiles'
BOXES_TEMPLATE = '{workspace_id}/boxes'

USER_AGENT_HEADER = 'user-agent'
EB_TOKEN_HEADER = 'ElasticBox-Token'
USER_AGENT_EB = 'elasticbox-cli/2014-05-23'

SCRIPT_EVENTS = ['install', 'post_install', 'configure', 'post_configure', 'start', 'post_start', 'stop', 'post_stop',
                 'dispose', 'post_dispose']

TERMINATE_INSTANCE_REST_TYPE = 'terminate'
FORCE_TERMINATE_INSTANCE_REST_TYPE = 'force_terminate'
DELETE_INSTANCE_REST_TYPE = 'delete'

EXIT_CODES = {
    400: 3,
    401: 4,
    403: 5,
    404: 6,
    409: 7,
    500: 8,
    503: 9
}

SERVICE_ID_PARAM = (
    ['-s', '--service'],
    {'help': 'Service ID', 'required': False}
)
TAGS_PARAM = (
    ['-t', '--tags'],
    {'help': 'Tags',
     'nargs': '*',
     'required': False}
)
SCRIPT_NAME_PARAM = (
    ['-s', '--script-name'],
    {'help': 'Event script name', 'required': True}
)
INPUT_FILE_PARAM = (
    ['-f', '--file'],
    {'help': 'Input file', 'required': True}
)
PROFILE_NAME_PARAM = (
    ['-p', '--profile-name'],
    {'help': 'Profile Name', 'required': True}
)
JSON_OUTPUT_PARAM = (
    ['-j', '--json'],
    {'help': 'JSON Output',
     'action': 'store_true',
     'required': False}
)
VARIABLE_PARAM = (
    ['-v', '--variable'],
    {'help': 'Variable',
     'nargs': 2,
     'required': True}
)
ADDRESS_PARAM = (
    ['--address'],
    {'help': 'Host to connect',
     'required': False,
     'default': DEFAULT_URL}
)
TOKEN_PARAM = (
    ['--token'],
    {'help': 'Authentication Token'}
)
BOX_ID_PARAM = (
    ['-b', '--box-id'],
    {'help': 'Box Id',
     'required': False}
)
WORKSPACE_ID_PARAM = (
    ['-w', '--workspace-id'],
    {'help': 'Workspace Id',
     'required': True}
)
NO_KEYCHAIN_PARAM = (
    ['--no-keychain'],
    {'action': 'store_true',
     'required': False,
     'help': 'Disable the use of keychain service to store your Authentication Token'}
)


def _generate_resource_id_param(required, help_text):
    return (
        ['-i', '--id'],
        {'help': help_text,
         'required': required}
    )


def _generate_resource_name_param(required, help_text):
    return (
        ['-n', '--name'],
        {'help': help_text,
         'required': required}
    )


def _generate_tag_param(required):
    return (
        ['-t', '--tag'],
        {'help': 'Tag',
         'required': required}
    )


def _generate_field_param(help_text):
    return (
        ['-f', '--fields'],
        {'help': help_text,
         'nargs': '*',
         'required': False}
    )


class UnexpectedFieldsException(Exception):
    pass


class ResourceNotFound(Exception):
    pass


class ArgumentException(Exception):
    pass


class AuthTokenException(Exception):
    pass


class AmbigousResourceFilterException(Exception):
    pass


class _BaseCommand(object):
    """Base class for all commands."""

    def __init__(self, args):
        self.args = args

    def _print(self, resource, is_json, is_verbose=False, fields=None):
        if not is_json:
            if fields is None:
                all_resources = ["{0} {1}".format(element['id'], element['name']) for element in resource]
                print '\n'.join(all_resources)
            else:
                width = [max(len(str(value)) for _, value in resource.iteritems())][0] + 4
                template = '{0}\n{1}'
                headers = data = ''
                if is_verbose:
                    for field in fields:
                        headers += '{:{}}'.format(field, width)
                        data += '{:{}}'.format(resource[field], width)
                else:
                    for field in fields:
                        data += '{0}\t'.format(resource[field])

                print template.format(headers, data).strip()
        else:
            try:
                print json.dumps(resource, indent=4)
            except:
                print resource

    def check_login(self):
        if not self.args.token and not self.args.no_keychain:
            client.login_with_token()
            return
        if not self.args.token:
            self.args.token = raw_input('Authentication Token: ')
            if not self.args.token:
                raise AuthTokenException("You need to get your token before calling any functions")

        address = DEFAULT_URL if self.args.address is None else self.args.address
        client.log_in(address, self.args.token, self.args.no_keychain)

    def _extract_fields(self, resource, fields):
        if len(set(fields) - set(resource.keys())) != 0:
            raise UnexpectedFieldsException('You specified some unknown fields from resource {0}'.format(
                resource['id']))

        fields_to_remove = [key for key in resource if key not in fields]
        for field in fields_to_remove:
            del resource[field]
        return resource


class _RESTBase(object):
    # This is the base client; it provides basic CRUD operations. More specific REST API clients
    # (exception.g. InstancesCommands and ApplicationsCommands below) extend this class to provide more
    # specific commands; exception.g. InstancesCommands also has calls to start and stop instances.
    def __init__(self, token, base_url):
        self.token = token
        self.base_url = base_url

    def _add_token(self, payload):
        # We have to add the ElasticBox token to each http request
        if 'headers' not in payload:
            payload['headers'] = dict()
        payload['headers'][EB_TOKEN_HEADER] = self.token
        payload['headers']['content-type'] = 'application/json'
        return payload

    def _http_get(self, *args, **kwargs):
        kwargs['timeout'] = kwargs.get('timeout', REQUESTS_TIMEOUT_SECONDS)
        kwargs['verify'] = False
        response = requests.get(*args, **self._add_token(kwargs))
        response.raise_for_status()
        return response

    def _http_post(self, *args, **kwargs):
        kwargs['timeout'] = kwargs.get('timeout', REQUESTS_TIMEOUT_SECONDS)
        kwargs['verify'] = False
        response = requests.post(*args, **self._add_token(kwargs))
        response.raise_for_status()
        return response

    def _http_put(self, *args, **kwargs):
        kwargs['timeout'] = kwargs.get('timeout', REQUESTS_TIMEOUT_SECONDS)
        kwargs['verify'] = False
        response = requests.put(*args, **self._add_token(kwargs))
        response.raise_for_status()
        return response

    def _http_delete(self, *args, **kwargs):
        kwargs['timeout'] = kwargs.get('timeout', REQUESTS_TIMEOUT_SECONDS)
        kwargs['verify'] = False
        response = requests.delete(*args, **self._add_token(kwargs))
        response.raise_for_status()
        return response

    def _upload_file(self, file_path):
        if self.base_url.startswith('https'):
            host_address = 'https://{}'.format(urlparse.urlparse(self.base_url).hostname)
        elif self.base_url.startswith('http'):
            host_address = 'http://{}'.format(urlparse.urlparse(self.base_url).hostname)

        filename = file_path.split('/')[-1]
        absolute_url = urlparse.urljoin(host_address, UPLOAD_BOX_BLOB_TEMPLATE.format(filename))
        _, extension = os.path.splitext(file_path)
        content_type = 'application/octet-stream'

        if extension in types_map:
            content_type = types_map[extension]

        headers = {'Content-Type': content_type, USER_AGENT_HEADER: USER_AGENT_EB}

        with open(file_path, 'r') as body:
            return self._http_post(absolute_url, headers=headers, data=body)

    def _create(self, creation_dict):
        json_encoded = creation_dict if isinstance(creation_dict, str) else json.dumps(creation_dict)
        return self._http_post(self.base_url, json_encoded)

    def create(self, creation_dict):
        return self._create(creation_dict).json()

    def _get_all(self):
        return self._http_get(self.base_url)

    def get_all(self):
        all_resources = self._get_all().json()
        self.check_result(all_resources)

        return all_resources

    def _get_by_id(self, resource_id):
        return self._http_get(urlparse.urljoin(self.base_url, str(resource_id)))

    def get_by_id(self, resource_id):
        return self._get_by_id(resource_id).json()

    def _update(self, resource_id, update_dict):
        json_encoded = update_dict if isinstance(update_dict, str) else json.dumps(update_dict)
        return self._http_put(urlparse.urljoin(self.base_url, str(resource_id)), data=json_encoded)

    def update(self, resource_id, update_dict):
        return self._update(resource_id, update_dict).json()

    def _delete(self, resource_id):
        return self._http_delete(urlparse.urljoin(self.base_url, str(resource_id)))

    def delete(self, resource_id):
        self._delete(resource_id)

    def _filter_instances(self, instances, box_name, tag, service_id):
        filtered_instances = instances
        if box_name is not None:
            filtered_instances = [instance for instance in filtered_instances
                                  if instance['name'] == box_name]

        if tag is not None:
            filtered_instances = [instance for instance in filtered_instances if tag in instance['tags']]

        if service_id is not None:
            filtered_instances = [instance for instance in filtered_instances
                                  if instance['service']['id'] == service_id]

        self.check_result(filtered_instances)

        return filtered_instances

    def check_result(self, result):
        if result is None or len(result) == 0:
            raise ResourceNotFound('A total of {} resources were found'.format(0))


class LoginCommand(_BaseCommand):
    def login(self):
        token = self.args.token
        address = self.args.address
        if (not self.args.token and
                not self.args.no_keychain and
                keyring.get_password(EBX_CREDENTIALS_NAME, EBX_CREDENTIALS_ACCOUNT) is not None):

            credentials = keyring.get_password(EBX_CREDENTIALS_NAME, EBX_CREDENTIALS_ACCOUNT)
            credentials = credentials.split(",")
            token = credentials[0]
            address = credentials[1]

        elif ((not self.args.token and self.args.no_keychain) or
              (not self.args.token and not self.args.no_keychain and
               keyring.get_password(EBX_CREDENTIALS_NAME, EBX_CREDENTIALS_ACCOUNT) is None)):
            token = raw_input('Authentication Token: ')
            if not token:
                # Lets re-define the way the user your surf to our documenation or elasticbox.com website.
                print 'You need a token to access your elasticbox account. Log in to your elasticbox website ' \
                    'and create a token from Authentication Tokens under your profile drop-down menu.'
                raise AuthTokenException("You need to get your token before calling any functions")

        client.log_in(address, token, self.args.no_keychain)

        if not self.args.no_keychain:
            print 'Login successful on {0}, token saved in your keychain service as {1}'.format(address,
                                                                                                EBX_CREDENTIALS_NAME)
        else:
            print 'Login successful using token {0} on {1}'.format(token, address)

    @staticmethod
    def parser(subparsers):
        _subparser(subparsers, 'login', [ADDRESS_PARAM, TOKEN_PARAM, NO_KEYCHAIN_PARAM],
                   help_text='Log in to ElasticBox and get your Authentication token')


class BoxesCommand(_BaseCommand):
    DEFAULT_FIELDS = ['id', 'name', 'owner']

    def list(self):
        if self.args.id:
            output = client.workspaces.list_boxes(self.args.id, self.args.name, self.args.tags)
        else:
            output = client.boxes.list(self.args.name, self.args.tags)

        self._print(output, self.args.json)

    def get(self):
        box = client.boxes.get_by_id(self.args.id)
        if self.args.json:
            fields = self.args.fields if self.args.fields else box.keys()
        else:
            fields = self.args.fields if self.args.fields else BoxesCommand.DEFAULT_FIELDS

        box = self._extract_fields(box, fields)
        self._print(box, self.args.json, self.args.verbose, fields)

    def create(self):
        self._print(client.boxes.create_from_json(self.args.file), True)

    def delete(self):
        client.boxes.delete(self.args.id)

    def upload_script(self):
        self._print(client.boxes.upload_box_script(self.args.id, self.args.script_name, self.args.file), True)

    def set(self):
        variable_name = self.args.variable[0]
        new_value = self.args.variable[1]
        box = client.boxes.get_by_id(self.args.id)

        if not box:
            raise ResourceNotFound('Box with id {0} was not found'.format(self.args.id))

        client.boxes.update_variable(variable_name, new_value, box)

    @staticmethod
    def parser(subparsers):
        field_help_text = 'Fields of a box. Available fields for a box are: id, name, service,'\
            ' organizations, tags, variables, created, uri, events, members, owner, bindings, schema'
        parser_instance = subparsers.add_parser('boxes', help='Manage boxes (get, list, create, set'
                                                ', delete, upload_script)')
        box_subparser = parser_instance.add_subparsers(title='Boxes actions', dest='action')

        _subparser(box_subparser, 'list',
                   [_generate_resource_id_param(False, 'Workspace Id'),
                    _generate_resource_name_param(False, 'Box name'), TAGS_PARAM, TOKEN_PARAM, NO_KEYCHAIN_PARAM,
                    ADDRESS_PARAM, JSON_OUTPUT_PARAM],
                   help_text='List of existing boxes')
        _subparser(box_subparser,
                   'get',
                   [_generate_resource_id_param(True, 'Box Id'), _generate_field_param(field_help_text),
                    TOKEN_PARAM, ADDRESS_PARAM, JSON_OUTPUT_PARAM, NO_KEYCHAIN_PARAM],
                   help_text='Get specified fields of given box. Available fields are: id, name, service,'
                   ' organizations, tags, variables, created, uri, events, members, owner, bindings, schema')
        _subparser(box_subparser,
                   'create',
                   [INPUT_FILE_PARAM, TOKEN_PARAM, ADDRESS_PARAM, NO_KEYCHAIN_PARAM],
                   help_text='Create box from json definition')
        _subparser(box_subparser,
                   'set',
                   [_generate_resource_id_param(True, 'Box Id'), VARIABLE_PARAM, TOKEN_PARAM, NO_KEYCHAIN_PARAM,
                    ADDRESS_PARAM],
                   help_text='Update a variable of the given box')
        _subparser(box_subparser,
                   'delete',
                   [_generate_resource_id_param(True, 'Box Id'), TOKEN_PARAM, ADDRESS_PARAM, NO_KEYCHAIN_PARAM],
                   help_text='Delete given box')
        _subparser(box_subparser,
                   'upload_script',
                   [_generate_resource_id_param(True, 'Box Id'), SCRIPT_NAME_PARAM, INPUT_FILE_PARAM, NO_KEYCHAIN_PARAM,
                    TOKEN_PARAM, ADDRESS_PARAM],
                   help_text='Upload script to given box')


class ProfilesCommand(_BaseCommand):
    DEFAULT_FIELDS = ['id', 'name', 'owner']

    def create(self):
        self._print(client.profiles.create_from_json(self.args.file), True)

    def get(self):
        profile = client.profiles.get_by_id(self.args.id)
        if self.args.json:
            fields = self.args.fields if self.args.fields else profile.keys()
        else:
            fields = self.args.fields if self.args.fields else ProfilesCommand.DEFAULT_FIELDS

        self._extract_fields(profile, fields)
        self._print(profile, self.args.json, self.args.verbose, fields)

    def list(self):
        if self.args.id:
            self._print(client.workspaces.get_profiles(self.args.id, self.args.name), self.args.json)
        else:
            self._print(client.profiles.list(self.args.name), self.args.json)

    def delete(self):
        client.profiles.delete(self.args.id)

    @staticmethod
    def parser(subparsers):
        help_field_text = 'Fields of a deployment profile. Available fields for a profile are: id, name, box,'\
            ' updated, created, uri, instances, members, owner, schema'
        parser_profiles = subparsers.add_parser('profiles', help='Manage deployment profiles (get, list, create,'
                                                ' remove)')
        profile_subparser = parser_profiles.add_subparsers(title='Deployment profiles actions', dest='action')

        _subparser(profile_subparser,
                   'create',
                   [INPUT_FILE_PARAM, TOKEN_PARAM, ADDRESS_PARAM, NO_KEYCHAIN_PARAM],
                   help_text='Creates a new profile from a json file')
        _subparser(profile_subparser,
                   'get',
                   [_generate_resource_id_param(True, 'Profile Id'), _generate_field_param(help_field_text),
                    TOKEN_PARAM, ADDRESS_PARAM, JSON_OUTPUT_PARAM, NO_KEYCHAIN_PARAM],
                   help_text='Gets specified fields of given deployment profile. Available fields are: id, name, box,'
                   ' updated, created, uri, instances, members, owner, schema')
        _subparser(profile_subparser,
                   'list',
                   [_generate_resource_id_param(False, 'Workspace Id'), _generate_resource_name_param(True, 'Box name'),
                    TOKEN_PARAM, ADDRESS_PARAM, JSON_OUTPUT_PARAM, NO_KEYCHAIN_PARAM],
                   help_text='Lists all deployment profiles of a box')
        _subparser(profile_subparser,
                   'delete',
                   [_generate_resource_id_param(True, 'Profile Id'), TOKEN_PARAM, NO_KEYCHAIN_PARAM, ADDRESS_PARAM],
                   help_text='Deletes given profile')


class InstancesCommand(_BaseCommand):
    DEFAULT_FIELDS = ['id', 'name', 'created', 'updated', 'operation', 'state', 'owner']

    def list(self):
        if self.args.id:
            output = client.workspaces.list_instances(self.args.id, self.args.name, self.args.tag,
                                                      self.args.service)
        else:
            output = client.instances.list(self.args.name, self.args.tag, self.args.service)

        self._print(output, self.args.json)

    def check_status(self):
        print client.instances.check_status(self.args.id)

    def get(self):
        instance = client.instances.get_by_id(self.args.id)
        if self.args.json:
            fields = self.args.fields if self.args.fields else instance.keys()
        else:
            fields = self.args.fields if self.args.fields else InstancesCommand.DEFAULT_FIELDS

        instance = self._extract_fields(instance, fields)
        self._print(instance, self.args.json, self.args.verbose, fields)

    def deploy(self):
        self._print(client.instances.deploy(self.args.box_id, self.args.name, self.args.profile_name,
                                            self.args.workspace_id, self.args.tags), False)

    def power_on(self):
        client.instances.power_on(self.args.id)

    def shut_down(self):
        client.instances.shut_down(self.args.id)

    def reconfigure(self):
        client.instances.reconfigure(self.args.id)

    def reinstall(self):
        client.instances.reinstall(self.args.id)

    def terminate(self):
        client.instances.terminate(self.args.id)

    def force_terminate(self):
        client.instances.force_terminate(self.args.id)

    def delete(self):
        client.instances.delete(self.args.id)

    def set(self):
        variable_name = self.args.variable[0]
        new_value = self.args.variable[1]
        client.instances.update_variable(variable_name, new_value, self.args.id)

    @staticmethod
    def parser(subparsers):
        field_help_text = 'Fields of an instance. Available fields for an instance are: id, name, updated, '\
            'created, service, tags, variables, uri, boxes, operation, state, members, owner, bindings, schema'
        parser_instance = subparsers.add_parser('instances', help='Manage instances (get, \
            list, check_status, set, deploy, power_on, shut_down, reconfigure, reinstall, terminate,\
            force_terminate, delete and config)')
        instance_subparser = parser_instance.add_subparsers(title='Instance actions', dest='action')

        _subparser(instance_subparser,
                   'list',
                   [_generate_resource_id_param(False, 'Workspace Id'),
                    _generate_resource_name_param(False, 'Box name'), _generate_tag_param(False), SERVICE_ID_PARAM,
                    TOKEN_PARAM, ADDRESS_PARAM, JSON_OUTPUT_PARAM, NO_KEYCHAIN_PARAM],
                   help_text='Lists of existing instances')
        _subparser(instance_subparser,
                   'check_status',
                   [_generate_resource_id_param(True, 'Instance Id'), TOKEN_PARAM, ADDRESS_PARAM, NO_KEYCHAIN_PARAM],
                   help_text='Check status of given instance')
        _subparser(instance_subparser,
                   'get',
                   [_generate_resource_id_param(True, 'Instance Id'), _generate_field_param(field_help_text),
                    TOKEN_PARAM, ADDRESS_PARAM, JSON_OUTPUT_PARAM, NO_KEYCHAIN_PARAM],
                   help_text='Gets specified fields of given instance. Available fields are: id, name, updated, '
                   'created, service, tags, variables, uri, boxes, operation, state, members, owner, bindings, schema')
        _subparser(instance_subparser,
                   'deploy',
                   [PROFILE_NAME_PARAM, WORKSPACE_ID_PARAM, BOX_ID_PARAM,
                    _generate_resource_name_param(False, 'Box name'), TAGS_PARAM, TOKEN_PARAM, NO_KEYCHAIN_PARAM,
                    ADDRESS_PARAM],
                   help_text='Deploys given box with given deployment profile')
        _subparser(instance_subparser,
                   'power_on',
                   [_generate_resource_id_param(True, 'Instance Id'), TOKEN_PARAM, ADDRESS_PARAM, NO_KEYCHAIN_PARAM],
                   help_text='Power on given instance')
        _subparser(instance_subparser,
                   'shut_down',
                   [_generate_resource_id_param(True, 'Instance Id'), TOKEN_PARAM, ADDRESS_PARAM, NO_KEYCHAIN_PARAM],
                   help_text='Shutdown given instance')
        _subparser(instance_subparser,
                   'reconfigure',
                   [_generate_resource_id_param(True, 'Instance Id'), TOKEN_PARAM, ADDRESS_PARAM, NO_KEYCHAIN_PARAM],
                   help_text='Reconfigure given instance')
        _subparser(instance_subparser,
                   'reinstall',
                   [_generate_resource_id_param(True, 'Instance Id'), TOKEN_PARAM, ADDRESS_PARAM, NO_KEYCHAIN_PARAM],
                   help_text='Reinstall given instance')
        _subparser(instance_subparser,
                   'terminate',
                   [_generate_resource_id_param(True, 'Instance Id'), TOKEN_PARAM, ADDRESS_PARAM, NO_KEYCHAIN_PARAM],
                   help_text='Terminates given instance')
        _subparser(instance_subparser,
                   'force_terminate',
                   [_generate_resource_id_param(True, 'Instance Id'), TOKEN_PARAM, ADDRESS_PARAM, NO_KEYCHAIN_PARAM],
                   help_text='Forces terminate given instance')
        _subparser(instance_subparser,
                   'delete',
                   [_generate_resource_id_param(True, 'Instance Id'), TOKEN_PARAM, ADDRESS_PARAM, NO_KEYCHAIN_PARAM],
                   help_text='Deletes given instance')
        _subparser(instance_subparser,
                   'set',
                   [_generate_resource_id_param(True, 'Instance Id'), VARIABLE_PARAM, TOKEN_PARAM, NO_KEYCHAIN_PARAM,
                    ADDRESS_PARAM],
                   help_text='Updates a variable of the given instance')


class BoxesActions(_RESTBase):
    def __init__(self, token, host_address, controller_route):
        super(BoxesActions, self).__init__(token, urlparse.urljoin(host_address, controller_route))

    def list(self, box_name, tags):
        all_boxes = self.get_all()

        if box_name:
            all_boxes = [box for box in all_boxes if box['name'] == box_name]

        if tags:
            all_boxes = [box for box in all_boxes if len(set(tags) - set(box['tags'])) == 0]

        self.check_result(all_boxes)
        return all_boxes

    def _create_from_json(self, json_definition):
        with open(json_definition, 'r') as box_file:
            new_box = json.load(box_file)
            existing_boxes = [box for box in self.get_all() if box['name'] == new_box['name']]
            if len(existing_boxes) > 0:
                raise Exception('Box {0} already exists'.format(new_box['name']))

            for script_name in SCRIPT_EVENTS:
                if script_name in new_box:
                    uploaded_script = self._upload_file(new_box[script_name]).json()
                    new_box[script_name] = uploaded_script['destination_path'] = 'scripts'

        return self._create(new_box)

    def _update_variable(self, path, value, box, root_box, root_scope):
        scope = None
        if len(path) == 1:
            name = path.pop(0)
        else:
            name = path.pop(len(path) - 1)
            scope = '.'.join(path)

        for variable in box['variables']:
            if (len(root_scope) == 0 and variable['name'] == name) or \
                    ('scope' in variable and variable['scope'] == scope):
                variable['value'] = value
                return
            elif variable['name'] == name and len(path) == 0:
                root_box['variables'].append({'name': name,
                                              'type': variable['type'],
                                              'value': value,
                                              'scope': '.'.join(root_scope)})
                return
            elif len(path) > 0 and variable['name'] == path[0]:
                new_box = client.boxes.get_by_id(variable['value'])
                path.append(name)
                path.pop(0)
                self._update_variable(path, value, new_box, root_box, root_scope)
                return

    def update_variable(self, variable_name, new_value, box):
        path = variable_name.split('.')

        for variable in box['variables']:
            if variable['name'] == path[-1] and 'scope' in variable and variable['scope'] == '.'.join(path[:-1]):
                variable['value'] = new_value
                self.update(box['id'], box)
                return

        self._update_variable(path, new_value, box, box, path[:-1])
        self.update(box['id'], box)

    def create_from_json(self, json_definition):
        return self._create_from_json(json_definition).json()

    def _upload_box_script(self, box_id, script_name, script_path):
        if script_name not in SCRIPT_EVENTS:
            raise Exception('Script event {0} is currently not supported.'.format(script_name))

        box = self._get_by_id(box_id).json()
        script = self._upload_file(script_path).json()
        script['destination_path'] = 'scripts'
        box['events'][script_name] = script
        return self._update(box['id'], box)

    def upload_box_script(self, box_id, script_name, script_path):
        return self._upload_box_script(box_id, script_name, script_path).json()


class InstancesActions(_RESTBase):
    # Classes like this one (InstancesActions, BoxesActions, etc.) have all the commands from RESTBase
    # along with more specialist ones. E.g. to stop an instance with id instance_id, one could do
    # client.instances.stop(instance_id)
    def __init__(self, token, host_address, controller_route):
        super(InstancesActions, self).__init__(token, urlparse.urljoin(host_address, controller_route))

    def list(self, box_name, tag, service_id):
        return self._filter_instances(self.get_all(), box_name, tag, service_id)

    def deploy(self, box_id, box_name, profile_name, workspace_id, tags):
        if box_id is None and box_name is None:
            raise ArgumentException('You must specify a box name or box id')

        name = box_name
        if name is None:
            box = client.boxes.get_by_id(box_id)
            name = box['name']
        else:
            boxes = client.workspaces.list_boxes(workspace_id, name, None)
            if len(boxes) != 1:
                raise AmbigousResourceFilterException('There are some boxes with name "{0}", '
                                                      'you must specify an id'.format(box_name))

        profiles = client.workspaces.get_profiles(workspace_id, name)
        profile = next((profile for profile in profiles if profile['name'] == profile_name), None)

        if profile is None:
            raise ResourceNotFound('Deployment profile "{0}" for box "{1}" not found'.format(profile_name, name))

        environment = tags[0] if (tags and len(tags) > 0) else profile_name
        deployment = {'profile': profile,
                      'owner': workspace_id,
                      'environment': environment,
                      'schema': DEPLOY_SERVICE_REQUEST_SCHEMA}

        json_encoded = deployment if isinstance(deployment, str) else json.dumps(deployment)
        return [self._http_post(self.base_url, json_encoded).json()]

    def _power_on(self, instance_id):
        return self._http_put(urlparse.urljoin(self.base_url,
                                               START_INSTANCE_TEMPLATE.format(instance_id=instance_id)))

    def power_on(self, instance_id):
        self._power_on(instance_id)

    def _shut_down(self, instance_id):
        return self._http_put(urlparse.urljoin(self.base_url,
                                               STOP_INSTANCE_TEMPLATE.format(instance_id=instance_id)))

    def shut_down(self, instance_id):
        self._shut_down(instance_id)

    def _reconfigure(self, instance_id):
        return self._http_put(urlparse.urljoin(self.base_url,
                                               RECONFIGURE_INSTANCE_TEMPLATE.format(instance_id=instance_id)))

    def reconfigure(self, instance_id):
        self._reconfigure(instance_id)

    def _reinstall(self, instance_id):
        return self._http_put(urlparse.urljoin(self.base_url,
                                               REINSTALL_INSTANCE_TEMPLATE.format(instance_id=instance_id)))

    def reinstall(self, instance_id):
        self._reinstall(instance_id)

    def _delete(self, instance_id):
        return self._http_delete(urlparse.urljoin(self.base_url, instance_id),
                                 params={'operation': DELETE_INSTANCE_REST_TYPE})

    def delete(self, instance_id):
        self._delete(instance_id)

    def _terminate(self, instance_id):
        return self._http_delete(urlparse.urljoin(self.base_url, instance_id),
                                 params={'operation': TERMINATE_INSTANCE_REST_TYPE})

    def terminate(self, instance_id):
        self._terminate(instance_id)

    def _force_terminate(self, instance_id):
        return self._http_delete(urlparse.urljoin(self.base_url, instance_id),
                                 params={'operation': FORCE_TERMINATE_INSTANCE_REST_TYPE})

    def force_terminate(self, instance_id):
        self._force_terminate(instance_id)

    def check_status(self, instance):
        instance = self.get_by_id(instance)
        return instance['state']

    def _obtain_variable(self, box, variable_name):
        variable = next((variable for variable in box['variables'] if variable['name'] == variable_name), None)
        return variable

    def _obtain_instance_variable(self, instance, scope, variable):
        if variable['type'] == 'Box':
            for box in instance['boxes']:
                if box['id'] == variable['value']:
                    var = self._obtain_variable(box, scope.pop(0))
                    if var is not None and var['type'] == 'Box' and len(scope) > 0:
                        return self._obtain_instance_variable(instance, scope, var)
                    elif var is not None and var['type'] != 'Box' and var['type'] != 'File' and len(scope) == 0:
                        return var
        elif len(scope) == 0:
            return variable

    def _update_variable(self, variable_name, new_value, instance_id):
        instance = self.get_by_id(instance_id)
        name_parts = variable_name.split('.')
        scope = '.'.join(name_parts[:-1]) if len(name_parts[:-1]) > 0 else None
        for variable in instance['variables']:
            if variable['name'] == name_parts[-1]:
                if ((scope is None and 'scope' not in variable) or
                        ('scope' in variable and variable['scope'] == scope)):
                    variable['value'] = new_value
                    self.update(instance['id'], instance)
                    return

        variable = self._obtain_variable(instance['boxes'][0], name_parts.pop(0))
        wanted_variable = self._obtain_instance_variable(instance, name_parts, variable)
        if wanted_variable is None:
            print 'Variable {0} doesn\'t exist in instance {1}'.format(variable_name, instance['id'])
        else:
            variable = {'name': variable_name.split('.')[-1], 'type': wanted_variable['type'], 'value': new_value}
            if scope is not None:
                variable.update({'scope': scope})
            instance['variables'].append(variable)
            self.update(instance['id'], instance)

    def update_variable(self, variable_name, new_value, instance_id):
        self._update_variable(variable_name, new_value, instance_id)


class WorkspacesActions(_RESTBase):
    def __init__(self, token, host_address, controller_route):
        super(WorkspacesActions, self).__init__(token, urlparse.urljoin(host_address, controller_route))

    def _get_all_boxes(self, workspace):
        all_boxes = self._http_get(
            urlparse.urljoin(
                self.base_url, BOXES_TEMPLATE.format(workspace_id=workspace))).json()

        self.check_result(all_boxes)
        return all_boxes

    def list_instances(self, workspace, box_name, tag, service_id):
        instances = self._http_get(
            urlparse.urljoin(
                self.base_url, INSTANCES_TEMPLATE.format(workspace_id=workspace))).json()

        self.check_result(instances)
        return self._filter_instances(instances, box_name, tag, service_id)

    def list_boxes(self, workspace, box_name, tags):
        all_boxes = self._get_all_boxes(workspace)

        if box_name:
            all_boxes = [box for box in all_boxes if box['name'] == box_name]

        if tags:
            all_boxes = [box for box in all_boxes if len(set(tags) - set(box['tags'])) == 0]

        self.check_result(all_boxes)
        return all_boxes

    def get_profiles(self, workspace, box):
        profiles = self._http_get(
            urlparse.urljoin(
                self.base_url, PROFILES_TEMPLATE.format(workspace_id=workspace))).json()

        if box:
            profiles = [profile for profile in profiles if profile['box']['name'] == box]

        self.check_result(profiles)
        return profiles


class ProfilesActions(_RESTBase):
    def __init__(self, token, host_address, controller_route):
        super(ProfilesActions, self).__init__(token, urlparse.urljoin(host_address, controller_route))

    def list(self, box_name):
        all_resources = self.get_all()

        if box_name:
            all_resources = [profile for profile in all_resources if profile['box']['name'] == box_name]

        self.check_result(all_resources)

        return all_resources

    def _create_from_json(self, json_definition):
        with open(json_definition, 'r') as profile_file:
            new_profile = json.load(profile_file)

            return self._create(new_profile)

    def create_from_json(self, json_definition):
        return self._create_from_json(json_definition).json()


class ElasticBoxClient(object):
    '''
Example usage:

    client = ElasticBoxClient()
    ## To login you may have your EB Authentication Token.
    client.log_in('localhost', '7c94811c-dd3f-4a7f-a5db-edb2c9a358af')

    # Delete all instances
    for instance in client.instances.get_all():
        client.instances.delete(instance['id'])

    # List all boxes of a workspace :
    workspace_id = 'workspace_id'
    boxes = client.workspaces.list_boxes(workspace_id)
    for box in boxes :
        print box

    # Deploy an instance:
    box_name =  "my_box"
    profile_name = "deployment_profile"

    client.instances.deploy(box_name, profile)
'''

    def __init__(self):
        self.token = None
        self.host_address = None
        self.controller_routes = None
        self.no_keychain = False
        # We actually read the routes to the web service controllers from the web services itself.
        # So we don't assume that the route to the instances controller is services/instances; instead
        # we query services/roots to tell us what all the other routes are.
        # You can see this in log_in below.

    def _generate_header(self, token):
        return {EB_TOKEN_HEADER: token, USER_AGENT_HEADER: USER_AGENT_EB}

    def login_with_token(self):
        try:
            if not self.no_keychain:
                self.token, self.host_address = self.read_token_from_keychain()

            headers = self._generate_header(self.token)
            controller_routes_response = requests.get(
                '{}/services/roots'.format(self.host_address), headers=headers, verify=False)
            controller_routes_response.raise_for_status()
            if controller_routes_response.status_code in [httplib.FORBIDDEN, httplib.UNAUTHORIZED]:
                raise AuthTokenException("Authenticating with token from keychain {} failed."
                                         " Try logging in manually with login command")

            self.controller_routes = dict()
            for key, value in controller_routes_response.json().items():
                self.controller_routes[str(key)] = '{}/'.format(value.strip('/'))
        except ResourceNotFound:
            raise
        except Exception:
            if not self.no_keychain:
                raise AuthTokenException("Keychain service does not contain a valid "
                                         "{0}.".format(EBX_CREDENTIALS_NAME))
            else:
                raise AuthTokenException("This token {} is not valid".format(self.token))

    def read_token_from_keychain(self):
        credentials = keyring.get_password(EBX_CREDENTIALS_NAME, EBX_CREDENTIALS_ACCOUNT)
        if not credentials:
            raise AuthTokenException("ElasticBox Token doesn't exist in your keychain service")

        credentials = credentials.split(",")
        return (credentials[0], credentials[1])

    def log_in(self, host_address, token, no_keychain):
        payload = dict(token=token, remember='on')
        if not (host_address.startswith('http://') or host_address.startswith('https://')):
            revised_address = 'http://{}'.format(host_address.strip('/'))
        else:
            revised_address = host_address

        try:
            response = requests.post(
                urlparse.urljoin(revised_address, TOKEN_URL),
                data=payload,
                verify=False)
            response.raise_for_status()
        except requests.exceptions.HTTPError as error:
            if response.status_code in [httplib.FORBIDDEN, httplib.UNAUTHORIZED]:
                raise AuthTokenException("Failed to authenticate with token {0} because it's invalid or "
                                         "expired.".format(token))
            else:
                raise AuthTokenException(error.message)
        except requests.exceptions.ConnectionError as error:
            # nodename nor servname provided, or not known
            if error.args and error.args[0].reason and error.args[0].reason.errno == 8:
                raise AuthTokenException("Can't connect to {0}. Verify you can connect to the network and provide "
                                         "the right address.".format(revised_address))
            else:
                raise AuthTokenException(error.message)

        self.token = token
        self.host_address = revised_address
        self.no_keychain = no_keychain

        if not self.no_keychain:
            keyring.set_password(EBX_CREDENTIALS_NAME, EBX_CREDENTIALS_ACCOUNT, '{0},{1}'.format(self.token,
                                                                                                 self.host_address))

        headers = self._generate_header(self.token)
        raw_controller_info = requests.get(
            '{}/services/roots'.format(revised_address), headers=headers, verify=False).json()

        self.controller_routes = dict()
        for key, value in raw_controller_info.items():
            self.controller_routes[str(key)] = '{}/'.format(value.strip('/'))

    @property
    def instances(self):
        return InstancesActions(self.token, self.host_address, self.controller_routes['instances'])

    @property
    def workspaces(self):
        return WorkspacesActions(self.token, self.host_address, self.controller_routes['workspaces'])

    @property
    def boxes(self):
        return BoxesActions(self.token, self.host_address, self.controller_routes['boxes'])

    @property
    def profiles(self):
        return ProfilesActions(self.token, self.host_address, self.controller_routes['profiles'])

client = ElasticBoxClient()


def _run_command(args):
    class_name = args.command[0].upper() + args.command[1:] + 'Command'
    command = globals()[class_name](args)
    action = None
    if not hasattr(args, 'action'):
        action = args.command
    else:
        action = args.action

    if not issubclass(command.__class__, LoginCommand):
        command.check_login()
    getattr(command, action)()


def _subparser(subparser, action, arguments, help_text):
    parser = subparser.add_parser(action, help=help_text)
    parser.add_argument('--debug', required=False, action='store_true')
    parser.add_argument('--verbose', required=False, action='store_true')
    parser.set_defaults(func=_run_command)
    for arg in arguments:
        parser.add_argument(*arg[0], **arg[1])


def _parse_command_line(argv):
    parser = argparse.ArgumentParser(description='ElasticBox command line tool',
                                     epilog="See 'eb.py command --help' for more information on a specific command")

    subparsers = parser.add_subparsers(title='Commands', dest='command')

    # Register the subparser for every _BaseCommand subclass
    for name, value in globals().items():
        if inspect.isclass(value) and issubclass(value, _BaseCommand):
            if name != '_BaseCommand':
                value.parser(subparsers)

    args = parser.parse_args(argv)
    args.func(args)


def _generate_exit_code(exit_code, message):
    if '--verbose' in sys.argv[1:]:
        print message
    if '--debug' in sys.argv[1:]:
        traceback.print_exc()
    sys.exit(exit_code)


def start():
    try:
        _parse_command_line(sys.argv[1:])
    except AuthTokenException as error:
        print error.message
    except requests.exceptions.HTTPError as error:
        code = 1
        if error.response is not None:
            code = EXIT_CODES[error.response.status_code]
        _generate_exit_code(code, 'URL: {0} Response: {1}'.format(error.response.url, error.message))
    except ResourceNotFound as error:
        _generate_exit_code(6, error.message)
    except UnexpectedFieldsException as error:
        _generate_exit_code(11, error.message)
    except IOError as error:
        _generate_exit_code(12, error.message)
    except Exception as error:
        _generate_exit_code(1, error.message)


if __name__ == '__main__':
    sys.exit(start())
