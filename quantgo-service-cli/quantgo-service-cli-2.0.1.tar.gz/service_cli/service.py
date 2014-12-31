# ======================= QuantGo Copyright Notice ============================
# Copyright 2013 QuantGo, LLC.  All rights reserved.
# Permission to use solely inside a QuantGo Virtual Quant Lab
# Written By: Nikolay
# Date: 12-12.2013
# ======================= QuantGo Copyright Notice ============================

import json
import config
import logging
import os

import errors

from functools import wraps
from service_cli import __version__
from client import SRClient

GET_DATA_SCHEMA = lambda action, name: \
    {"Action": action, "Parameters": {"ServiceName": name}}
GET_DATA_SCHEMA_BY_ID = lambda action, service_id: \
    {"Action": action, "Parameters": {"ServiceId": service_id}}
GET_SERVICE_SPECIFIC_SCHEMA = lambda action, name: \
    {"Action": action, "Parameters": {"ServiceName": name}}
GET_SERVICE_SPECIFIC_SCHEMA_BY_ID = lambda action, service_id: \
    {"Action": action, "Parameters": {"ServiceId": service_id}}
AVAILABLE_SCHEMA = lambda action: {"Action": action}
LIST_SCHEMA = lambda action: {"Action": action}
DESCRIPTION_SCHEMA = lambda action, name: {"Action": action, "Parameters": {"ServiceName": name}}
DESCRIPTION_SCHEMA_BY_ID = lambda action, service_id: {"Action": action, "Parameters": {"ServiceId": service_id}}
GET_ACTION_RESULT_SCHEMA = lambda id_value: \
    {"Action": "get-action-result", "Parameters": {"id": id_value}}
COUNTRIES_SCHEMA = lambda : {"Action": "countries"}
PARTNERS_SCHEMA = lambda : {"Action": "partners"}
DATA_TYPES_SCHEMA = lambda : {"Action": "data_types"}
SEARCH_SERVICES_SCHEMA = lambda : {"Action": "search_services"}


def with_client(f):
    """Wrapper which instantiates SRClient and passes it into wrapped function
    as first argument.
    """
    @wraps(f)
    def __wrapper(*args, **kwargs):
        logging.debug('ARGS %r, KWARGS %r', args, kwargs)
        host = kwargs.get('host', config.HOST)
        port = kwargs.get('port', config.PORT)
        stdout = kwargs.get('stdout')
        with SRClient(host, port, stdout=stdout) as client:
            return f(client, *args, **kwargs)
    return __wrapper


def service(command, args, **kwargs):
    if isinstance(args, dict):
        service = args['service'] if 'service' in args else None
        params = args['params'] if 'params' in args else None
    else:
        service = args.service if 'service' in args else None
        params = args.params if 'params' in args else None
    if command == 'get-data':
        return do_get_data(service, params, **kwargs)
    elif command == 'get-service-specific':
        return do_get_service_specific(service, params, **kwargs)
    elif command == 'available':
        return do_available(**kwargs)
    elif command == 'list':
        return do_list(**kwargs)
    elif command == 'description':
        return do_description(service, **kwargs)
    elif command == 'countries':
        return do_countries(**kwargs)
    elif command == 'partners':
        return do_partners(**kwargs)
    elif command == 'data-types':
        return do_data_types(**kwargs)
    elif command == 'search-services':
        return do_search_services(params, **kwargs)
    else:
        assert False, 'Programming mistake: command argument has value %s, ' \
                      'which normally should never happen.' % (command)


@with_client
def do_get_data(client, service, params=None, **kwargs):
    if params and isinstance(params, str):
        try:
            params = json.loads(params)
        except ValueError, e:
            raise ValueError('Please check --params argument value syntax. ' \
                             'It\'s value should be valid json blob. ' \
                             'Syntax error: %s' % (str(e)))
    if params.get('ticker-file'):
        filepath = params['ticker-file']
        logging.debug('Using tickers file %s', filepath)
        if os.path.exists(filepath) and os.path.isfile(filepath):
            with open(filepath, 'r') as fp:
                tickers = fp.read()
            del params['ticker-file']
            params['TickerNames'] = [t.strip() for t in tickers.split(',')]
            logging.debug('Setting TickerNames param to %r',
                          params['TickerNames'])
        else:
            raise ValueError('ticker-file  %s does not exist or is not a ' \
                             'valid file.' % (filepath,))

    service_id = convert_name_to_id(service)

    if service_id is not None:
        request = GET_DATA_SCHEMA_BY_ID('get-data', service_id)
    else:
        request = GET_DATA_SCHEMA('get-data', service)

    request['Parameters'].update(params)
    res = do_data_request(client, request, **kwargs)
    #client.close()
    return res


def check_response(response_json):
    try:
        response = json.loads(response_json)
    except ValueError:
        raise errors.ClientError('Invalid JSON blob from server-side: %s' % response_json)
    result = response['Result']
    if not isinstance(result, bool):
        raise errors.ClientError('Invalid response from server-side: %s' % response_json)
    if not result:
        raise errors.ServerError(response['Data']['ErrorMessage'])
    return response


@with_client
def check_execution(client, response, received):
    id_value = response['Data']['id']
    # do not check execution if id is not given (no data)
    if id_value is None:
        return
    request = GET_ACTION_RESULT_SCHEMA(id_value)
    client.send(json.dumps(request))
    exec_response = check_response(client.read_response())
    data = exec_response['Data']
    code = data['code']
    if code == 0:
        size = data['size']
        if received != size:
            raise errors.ClientError('Data size mismatch. Got %d bytes but should be %d bytes' % (received, size))
    else:
        raise errors.ServerError('Error code: %d. %s' % (code, data['error']))

def convert_name_to_id(service):
    if isinstance(service, (int, long)):
        return service

    try:
        return long(service)
    except Exception:
        pass

@with_client
def do_get_service_specific(client, service, params=None, **kwargs):
    if params and isinstance(params, str):
        try:
            params = json.loads(params)
        except ValueError, e:
            raise ValueError('Please check --params argument value syntax. ' \
                             'It\'s value should be valid json blob. ' \
                             'Syntax error: %s' % (str(e)))

    service_id = convert_name_to_id(service)
    
    if service_id is not None:
        request = GET_SERVICE_SPECIFIC_SCHEMA_BY_ID('get-service-specific', service_id)
    else:
        request = GET_SERVICE_SPECIFIC_SCHEMA('get-service-specific', service)

    request['Parameters'].update(params)
    return do_data_request(client, request, **kwargs)

@with_client
def do_search_services(client, params=None, **kwargs):
    if params and isinstance(params, str):
        try:
            params = json.loads(params)
        except ValueError, e:
            raise ValueError('Please check --params argument value syntax. ' \
                             'It\'s value should be valid json blob. ' \
                             'Syntax error: %s' % (str(e)))

    request = SEARCH_SERVICES_SCHEMA()

    request['Parameters'] = params
    return do_request(client, request, True, **kwargs)

@with_client
def do_available(client, **kwargs):
    request = AVAILABLE_SCHEMA('available')
    return do_request(client, request, True, **kwargs)


@with_client
def do_list(client, **kwargs):
    request = LIST_SCHEMA('list')
    return do_request(client, request, True, **kwargs)


@with_client
def do_countries(client, **kwargs):
    request = COUNTRIES_SCHEMA()
    return do_request(client, request, True, **kwargs)


@with_client
def do_partners(client, **kwargs):
    request = PARTNERS_SCHEMA()
    return do_request(client, request, True, **kwargs)


@with_client
def do_data_types(client, **kwargs):
    request = DATA_TYPES_SCHEMA()
    return do_request(client, request, True, **kwargs)


@with_client
def do_description(client, service, **kwargs):
    service_id = convert_name_to_id(service)

    if service_id is not None:
        request = DESCRIPTION_SCHEMA_BY_ID('description', service_id)
    else:
        request = DESCRIPTION_SCHEMA('description', service)
    return do_request(client, request, True, **kwargs)


def do_request(client, request, do_print, **kwargs):
    logging.debug('Request: %r', request)
    client.send(json.dumps(request))
    response = check_response(client.read_response())
    if do_print:
        stdout = kwargs.get('stdout')
        if stdout:
            stdout.write(json.dumps(response, indent=4, separators=(',', ': ')))
            stdout.write('\n')
    return response


def do_data_request(client, request, **kwargs):
    response = do_request(client, request, False, **kwargs)
    client.receive()
    check_execution(response, client.received)
    return response
