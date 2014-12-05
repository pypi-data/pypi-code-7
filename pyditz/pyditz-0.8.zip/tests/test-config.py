"""
Configuration tests.
"""

from ditz.config import config


def test_config():
    "Test configuration files"

    config.write_file("test-config.cfg")


if __name__ == "__main__":
    test_config()
