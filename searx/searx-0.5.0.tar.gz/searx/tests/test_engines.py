from searx.tests.engines.test_dummy import *  # noqa
from searx.tests.engines.test_github import *  # noqa
from searx.engines import engines
from searx.search import default_request_params


def simple_engine_test(query):
    params = default_request_params()


class TestEngines(SearxTestCase):
    pass


