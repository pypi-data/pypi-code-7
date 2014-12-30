#!/usr/bin/env python

# Copyright (C) 2014 The Genome Institute, Washington University Medical School
#
# nessy-cli is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# nessy-cli is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with nessy-cli.  If not, see <http://www.gnu.org/licenses/>.


from pprint import pprint
import argparse
import logging
import os
import requests
import urlparse

LOG = logging.getLogger()


URL_ENVLIST = [
    'NESSY_CLAIMS_URL',
    'GENOME_NESSY_SERVER',
]


def _get_claims(url, limit, offset, constraints):
    params = dict(constraints)
    params['limit'] = limit
    params['offset'] = offset
    response = requests.get(url, params=params)
    assert response.status_code == 200

    return [claim['url'] for claim in response.json()]


def _revoke_claims(claim_urls):
    revoked_count = 0
    for url in claim_urls:
        LOG.debug('Attempting to revoke claim %s', url)
        response = requests.patch(url, data={'status': 'revoked'})
        if response.status_code == 204:
            revoked_count += 1
            LOG.debug('Successfully revoked claim %s', url)
        else:
            LOG.warn('Failed to revoke claim %s.  HTTP %s: %s', url,
                    response.status_code, response.text)

    return revoked_count


def _list_claims(claim_urls):
    for url in claim_urls:
        response = requests.get(url)
        if response.status_code == 200:
            pprint(response.json())
        else:
            LOG.warn('Failed to get data for claim: %s', url)

    return 0


def _first_not_none(*args):
    for envname in args:
        if os.environ.get(envname):
            return os.environ[envname]


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--log-level', default='WARNING', dest='log_level',
                        choices=('DEBUG', 'INFO', 'WARNING', 'ERROR',
                                 'CRITICAL'),
                        help='Threshold for logging messages')

    parser.add_argument('--url', '-u',
                        default=_first_not_none(*URL_ENVLIST),
                        help='Claims url (http://nessy.example.com)')

    parser.add_argument('action', choices=['count', 'list', 'revoke'])
    parser.add_argument('--limit', type=int, default=10,
                        help='maximum claims returned per request')
    parser.add_argument('--max-claims', type=int, default=50, dest='max_claims',
                        help='maximum total claims acted on')


    constraints = parser.add_argument_group('constraints')

    constraints.add_argument('--status', choices=['active', 'released',
        'revoked', 'waiting'])
    constraints.add_argument('--resource')

    _add_mutex_group(constraints, [
        (['--max-ttl'], {'type': float, 'dest': 'maximum_tll'}),
        (['--min-ttl'], {'type': float, 'dest': 'minimum_tll'}),
    ])

    _add_mutex_group(constraints, [
        (['--max-waiting-duration'], {'type': float, 'dest': 'maximum_waiting_duration'}),
        (['--min-waiting-duration'], {'type': float, 'dest': 'minimum_waiting_duration'}),
    ])

    return parser.parse_args()


def _add_mutex_group(constraints, args):
    group = constraints.add_mutually_exclusive_group()
    for positional, keyword in args:
        group.add_argument(*positional, **keyword)


_NON_CONSTRAINT_ARGS = [
    'action',
    'limit',
    'log_level',
    'max_claims',
    'url',
]
def _build_constraints(args):
    constraints = vars(args)
    for nce in _NON_CONSTRAINT_ARGS:
        constraints.pop(nce)

    for key, value in constraints.items():
        if value is None:
            constraints.pop(key)

    return constraints


def _count_summary(offset, removed_count):
    print offset


def _apply_path(base_url):
    split_result = list(urlparse.urlsplit(base_url))
    split_result[2] = '/v1/claims'
    return urlparse.urlunsplit(split_result)


_ACTION_ITERATION_MAP = {
    'count': lambda x: 0,
    'list': _list_claims,
    'revoke': _revoke_claims,
}
_ACTION_SUMMARY_MAP = {
    'count': _count_summary
}
def run(url, action, limit, max_claims, constraints):
    action_function = _ACTION_ITERATION_MAP[action]

    found_claims = True
    removed_count = 0
    offset = 0
    while found_claims:
        if limit > max_claims:
            limit = max_claims
        claim_urls = _get_claims(url, limit, offset, constraints)
        max_claims -= len(claim_urls)
        LOG.debug('Found %d claims', len(claim_urls))
        if claim_urls:
            acted_this_time = action_function(claim_urls)
            claims_to_skip = len(claim_urls) - acted_this_time
            LOG.debug('Acted on %s claims, skipping %s claims',
                    acted_this_time, claims_to_skip)
            offset += claims_to_skip
            removed_count += acted_this_time
        else:
            found_claims = False

    LOG.info('Acted on %s claims.  Skipped %s claims.', removed_count, offset)
    if action in _ACTION_SUMMARY_MAP:
        _ACTION_SUMMARY_MAP[action](offset, removed_count)


def main():
    args = parse_args()
    logging.basicConfig(level=args.log_level)
    logging.getLogger('requests').setLevel(logging.WARNING)
    url = _apply_path(args.url)
    run(url, args.action, args.limit, args.max_claims,
            _build_constraints(args))


if __name__ == '__main__':
    main()
