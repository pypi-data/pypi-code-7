import json
import os

try:  # pragma: no cover
    from ._version import full_version as __version__
except ImportError:  # pragma: no cover
    __version__ = "no-built"


def get_schema(name):
    directory = os.path.dirname(__file__)
    schema_path = os.path.join(directory, name)
    with open(schema_path) as fp:
        return json.load(fp)
