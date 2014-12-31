from ConfigParser import RawConfigParser
from os.path import join, expanduser
from xl_helper.FileUtils import FileUtils


class XlHelperConfig(object):

    config = None

    def __init__(self, config):
        assert config is not None
        self.config = config

    @staticmethod
    def load():
        config = RawConfigParser(allow_no_value=True)
        config.read(FileUtils.to_absolute_path("xl_helper/resources/.xl-helper-defaults"))
        config.read([join(expanduser("~"), '.xl-helper')])
        XlHelperConfig.config = config
        return config


XlHelperConfig.load()