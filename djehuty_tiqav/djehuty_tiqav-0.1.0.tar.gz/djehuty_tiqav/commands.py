import requests

import random

from djehuty.command import Command


class Tiqav(Command):
    '''show random tiqav URL'''

    def get_parser(self, prog_name):
        parser = Command.get_parser(self, prog_name)
        parser.add_argument(
            'search',
            nargs='?',
            default=None,
            help='search word'
        )
        return parser

    def take_action(self, parsed_args):

        if parsed_args.search is None:
            r = requests.get('http://api.tiqav.com/search/random.json')
        else:
            r = requests.get('http://api.tiqav.com/search.json', params={
                'q': parsed_args.search.decode('utf-8')
            })

        if r.status_code == 404:
            return 'tiqav not found.'
        elif r.status_code != 200:
            return 'Looks Bad about tiqav.'

        image = random.sample(r.json(), 1)[0]
        return 'http://img.tiqav.com/{}.{}'.format(image['id'], image['ext'])
