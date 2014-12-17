import pytest
from eggmonster import Environment
from ast import literal_eval

default_items = dict(
    a = 'a_default',
    b = 'b_default',
    c = 'c_default',
    )

local_items = dict(
    b = 'bee',
    d = 4,
    )

def test_as_obscured_dict():
    env = Environment()
    d = dict(not_a_password = 'public', password = 'SECRET1')
    env.update_defaults(dict(a = 1, b = 2.0, d = d, password = 'SECRET2'))
    env.update(dict(b = 'bee'))
    assert env.a == 1
    assert env.b == 'bee'
    assert env.d == d
    assert env.password == 'SECRET2'
    assert env.as_obscured_dict() == dict(
        a = 1,
        b = 'bee',
        password = '********',
        d = dict(not_a_password = 'public', password = '********')
        )

def test_attribute_access():
    '''Test that keys can also be accessed as attributes.
    '''
    env = Environment()
    env.update_defaults(default_items)
    env.update(local_items)
    assert env.a == 'a_default'
    assert env.b == 'bee'
    assert env.c == 'c_default'
    assert env.d == 4

def test_clear_defaults():
    env = Environment()
    env.update_defaults(default_items)
    env.update(local_items)
    env.clear_defaults()
    assert env == {'b': 'bee', 'd': 4}

def test_clear_locals():
    env = Environment()
    env.update_defaults(default_items)
    env.update(local_items)
    env.clear_locals()
    assert env == {'a': 'a_default', 'b': 'b_default', 'c': 'c_default'}

def test_defaults():
    env = Environment()
    env.update_defaults(default_items)
    env.update(local_items)
    assert env.a == 'a_default'
    assert env.b == 'bee'
    assert env.c == 'c_default'
    assert env.d == 4

def test_del():
    env = Environment()
    env.update_defaults(default_items)
    env.update(local_items)
    with pytest.raises(KeyError):
        del env['a']

    del env['b']
    assert env == {'a': 'a_default', 'b': 'b_default', 'c': 'c_default', 'd': 4}

def test_keys():
    '''Test the .keys() method.'''
    env = Environment()
    assert env.keys() == []

    env.update_defaults(default_items)
    # Ordering is hard to predict, so we use a non-ordered comparision.
    assert len(env.keys()) == 3
    assert set(env.keys()) == set(['a', 'b', 'c'])

    env.update(local_items)
    assert len(env.keys()) == 4
    assert set(env.keys()) == set(['a', 'b', 'c', 'd'])

def test_len():
    env = Environment()
    assert len(env) == 0

    env.update_defaults(default_items)
    assert len(env) == 3

    env.update(local_items)
    assert len(env) == 4

    env.clear()
    assert len(env) == 3

def test_repr():
    env = Environment()
    assert repr(env) == '{}'

    env.update_defaults(default_items)
    r = repr(env)
    # The order of items within r is indeterminite, so we can't simply do a
    # string comparison on it.
    assert literal_eval(r) == {'a': 'a_default', 'b': 'b_default', 'c': 'c_default'}

    env.update(local_items)
    r = repr(env)
    assert literal_eval(r) == {'a': 'a_default', 'b': 'bee', 'c': 'c_default', 'd': 4}

def test_repr_does_not_mutate_env():
    env = Environment()
    env.update_defaults(default_items)
    env.update(local_items)

    _ = repr(env)

    assert env.a == 'a_default'
    assert env.b == 'bee'
    assert env.c == 'c_default'
    assert env.d == 4

def test_setitem():
    env = Environment()
    env.update_defaults(default_items)
    env.update(local_items)
    env['b'] = 'b_new'
    assert env == {'a': 'a_default', 'b': 'b_new', 'c': 'c_default', 'd': 4}
    env['b'] = 'b_newer'
    assert env == {'a': 'a_default', 'b': 'b_newer', 'c': 'c_default', 'd': 4}

    del env['b']
    env['b'] = 'b_newest'
    assert env == {'a': 'a_default', 'b': 'b_newest', 'c': 'c_default', 'd': 4}

def test_str():
    env = Environment()
    assert repr(env) == '{}'

    env.update_defaults(default_items)
    s = str(env)
    # The order of items within s is indeterminite, so we can't simply do a
    # string comparison on it.
    assert literal_eval(s) == {'a': 'a_default', 'b': 'b_default', 'c': 'c_default'}

    env.update(local_items)
    s = str(env)
    assert literal_eval(s) == {'a': 'a_default', 'b': 'bee', 'c': 'c_default', 'd': 4}

def test_str_does_not_mutate_env():
    env = Environment()
    env.update_defaults(default_items)
    env.update(local_items)

    _ = str(env)

    assert env.a == 'a_default'
    assert env.b == 'bee'
    assert env.c == 'c_default'
    assert env.d == 4

def test_update_defaults():
    env = Environment()
    env.update_defaults(default_items)
    env.update(local_items)
    env.update_defaults({'a': 'a_new_default', 'x': 'x_default'})
    assert env == {'a': 'a_new_default', 'b': 'bee', 'c': 'c_default', 'd': 4, 'x': 'x_default'}

def test_update_locals():
    env = Environment()
    env.update_defaults(default_items)
    env.update(local_items)
    env.update_locals({'a': 'a_new', 'x': 'x_new'})
    assert env == {'a': 'a_new', 'b': 'bee', 'c': 'c_default', 'd': 4, 'x': 'x_new'}

