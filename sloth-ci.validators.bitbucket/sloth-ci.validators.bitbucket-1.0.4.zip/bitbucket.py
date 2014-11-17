'''Bitbucket Sloth CI validator that validates the `Bitbucket <https://bitbucket.org/>`_ payload against username and repo name (obtained from the Sloth app config).'''


__title__ = 'sloth-ci.validators.bitbucket'
__description__ = 'Bitbucket validator for Sloth CI'
__version__ = '1.0.4'
__author__ = 'Konstantin Molchanov'
__author_email__ = 'moigagoo@live.com'
__license__ = 'MIT'


def validate(request, validation_data):
    '''Validate Bitbucket payload against repo name (obtained from the Sloth app config).

    :param request_params: payload to validate
    :param validation_data: dictionary with the key ``repo`` (in the form "username/repo")

    :returns: (True, success message, extracted data dict) if the payload is valid, (False, error message, extracted data dict) otherwise
    '''

    from json import loads

    if request.method != 'POST':
        return (405, 'Payload validation failed: Wrong method, POST expected, got {method}.', {'method': request.method})

    trusted_ips = ['131.103.20.165', '131.103.20.166']

    remote_ip = request.remote.ip

    if remote_ip not in trusted_ips:
        return (403, 'Payload validation failed: Unverified remote IP: {ip}.', {'ip': remote_ip})

    try:
        payload = request.params.get('payload')

        parsed_payload = loads(payload)

        repo = parsed_payload['repository']['owner'] + '/' + parsed_payload['repository']['slug']
        branch = parsed_payload['commits'][-1]['branch']

        if repo != validation_data['repo']:
            return (403, 'Payload validation failed: repo mismatch. Repo: {repo}', {'repo': repo})

        return (200, 'Payload validated. Branch: {branch}', {'branch': branch})

    except Exception as e:
        return (400, 'Payload validation failed: %s' % e, {})
