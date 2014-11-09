from fanery import (
    PyClient, WsgiClient,
    service,
    get_state,
    rand_num, rand_bytes,
    Hict, is_date,
    exc, config
)

import logging.config
config.LOGGING['loggers']['fanery']['level'] = 'ERROR'
logging.config.dictConfig(config.LOGGING)

# -- services definition -----------------------------


@service(safe=False, ssl=False)
def echo(term, *terms):
    return term if not terms else (term,) + terms


@service(ssl=False, auto_parse=False)
def profile():
    profile = get_state().profile
    return profile._indexer(profile)


def _outer_state(state):

    def _outer_inner_state():
        assert state is get_state()

    _outer_inner_state()
    return get_state()


@service(auto_parse=False)
def check_state():
    from fanery._state import get_state

    state = get_state()

    def _inner_state():

        def _inner_inner_state():
            assert get_state() is state

        _inner_inner_state()
        return get_state()

    assert state is _outer_state(state)
    assert state is _inner_state()
    assert state is get_state()

    assert state.service is check_state.urlpath


# -- test helpers -----------------------------------


def setup(db):
    from fanery import auth, get_state

    state = get_state()

    auth.setup(db)
    auth.add_user('admin', 'admin', domain=state.domain)
    profile = auth.hooks.fetch_profile(state.domain, 'admin')
    assert profile

    auth.hooks.destroy_user_sessions(state.domain, 'admin')
    try:
        auth.hooks.reset_origin_abuse_level(state.origin, state.domain)
    except:
        pass


def _login(client):
    assert client.login('admin', 'admin') is True


def _echo(client, terms=10):
    r = dict((rand_bytes(8), rand_num(dec=False)) for _ in xrange(terms))
    for k, v in r.items():
        for t in (k.encode('hex'), v, [v, v / 2]):
            ret = client.call('echo', term=v)
            assert ret == v, (ret, v)


def _profile(client):
    _login(client)
    data = Hict(client.safe_call('profile'))
    assert (data.username == 'admin' and
            data.domain == 'localhost' and
            data.email == 'admin@example.com' and
            'password_hash' not in data and
            'password_salt' not in data), data


def _check_state(client):
    _login(client)
    client.safe_call('check_state')


def _logout(client):
    _login(client)
    client.safe_call('check_state')
    assert client.logout() is True

    from fanery._auth import hooks
    abuse_level = hooks.abuse_level_by_origin

    state = get_state()
    origin = state.origin
    domain = state.domain

    level = abuse_level(origin, domain)
    try:
        client.safe_call('check_state')
        raise Exception('should raise UnknownSession')
    except exc.UnknownSession:
        assert level < abuse_level(origin, domain)


# -- test functions ------------------------------


def test_urlpath():
    assert echo.urlpath == 'echo'
    assert profile.urlpath == 'profile'


def test_safe_param():
    assert echo.safe is False
    assert profile.safe is True


def test_ssl_param():
    assert echo.ssl is False
    assert profile.ssl is False


def test_auto_parse_param():
    assert echo.auto_parse is True
    assert profile.auto_parse is False


def test_auto_parse_on_call():
    assert echo('1') == 1
    assert echo('1.1') == 1.1
    assert is_date(echo('1990-01-01'))


def test_lookup():
    from fanery._service import lookup, static, registry

    assert lookup('prefix/echo/1/2/3.json')[:-1] == (echo, ['1', '2', '3'], '.json')    # noqa
    assert lookup('/echo.doc') == (echo, [], '.doc', False)
    assert lookup('/a/profile') == (profile, [], '', None)
    assert lookup('profile.txt')[:-1] == (profile, [], '.txt')

    if '' not in registry:
        assert lookup('/index.html') == (None, ['index.html'], '.html', None)
        serve_file = static('/', '.')
        assert lookup('/index.html') == (serve_file, ['index.html'], '.html', False)    # noqa


def test_consume():
    from fanery._service import consume

    _state_ = get_state()
    assert consume(_state_, 'prefix/echo/1/2/3') == (echo, '', (1, 2, 3))
    assert consume(_state_, 'prefix/echo/1/2/3.json') == (echo, '.json', '[1,2,3]')     # noqa


def test_py_login():
    _login(PyClient())


def test_wsgi_login():
    _login(WsgiClient())


def test_py_echo():
    _echo(PyClient())


def test_wsgi_echo():
    _echo(WsgiClient())


def test_py_check_state():
    try:
        _check_state(PyClient())
        raise Exception('should raise RequireSSL')
    except exc.RequireSSL:
        _check_state(PyClient(ssl=True))


def test_wsgi_check_state():
    try:
        _check_state(WsgiClient())
        raise Exception('should raise RequireSSL')
    except exc.RequireSSL:
        _check_state(WsgiClient(ssl=True))


def test_py_profile():
    _profile(PyClient())


def test_wsgi_profile():
    _profile(WsgiClient())


def test_py_logout():
    _logout(PyClient(ssl=True))


def test_wsgi_logout():
    _logout(WsgiClient(ssl=True))


# -- tests run -------------------------------------------


def main():
    from fanery import DataStore, dbm, timecall  # , memory_profile, line_profile   # noqa
    from random import shuffle

    tests = [(k, v) for k, v in globals().iteritems()
             if k.startswith('test_') and callable(v)]

    for DS in (dbm.MemDictStore,
               #dbm.DSStore,
               #lambda: dbm.RTStore('192.168.122.61', indexer='self'),
               #lambda: dbm.HDStore('192.168.122.91', 2001, indexer='self'),
               ):

        shuffle(tests)
        db = DS()
        ds = DataStore(db, permission=db, state=db, abuse=db, profile=db, settings=db) # noqa
        timecall(setup)(ds)
        for name, test in tests:
            #memory_profile(test)()
            #line_profile(test)()
            timecall(test)()

if __name__ == '__main__':
    main()
