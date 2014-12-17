import json, re, requests, urllib
from helga.plugins import command

_help_text = 'Define words from urbandictionary.com. \
Usage: helga lingo <term>'

@command('lingo', aliases=['urbandictionary', 'ud', 'urban'], help=_help_text)
def lingo(client, channel, nick, message, cmd, args):
    """ Define from urban dictionary """
    if len(args) == 0:
        return u'You need to give me a term to look up.'
    term, index = parse_args(args)
    try:
        data = execute_request(term)
        return define(term, data, index)
    except Exception as e:
        return 'Lingo returned exception for ' + term + ":" + str(e)

def execute_request(term):
    """ Invoke API to retrieve json hopefully representing term """
    api_url = 'http://api.urbandictionary.com/v0/define?term='
    response = requests.get(_api_url + term)
    if response.status_code != 200:
        raise Exception('Error status code returned: ' + str(response.status_code))
    response_json = json.loads(response.content)
    if not response_json:
        raise Exception('Response falsy for given term: ' + term)
    return response_json

def define(term, data, index=0, action='definition'):
    """ Retrieve the definition for the term """
    return data['list'][index][action]

def parse_args(args):
    """ Parse arguments to extract desired search term and index in def list """
    index = 0
    match = re.search(r'\d+$', args)
    if match is not None:
        index = int(match.group())
        args=args[:-len(str(index))-1]
    term = urllib.quote(''.join(args))
    return (term, index)
