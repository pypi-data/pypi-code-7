# -*- coding: UTF-8 -*-
from datetime import datetime
from lisa.server.plugins.IPlugin import IPlugin
import gettext
import inspect
import os

class UnitTest(IPlugin):
    def __init__(self):
        super(UnitTest, self).__init__()
        self.configuration_plugin = self.mongo.lisa.plugins.find_one({"name": "UnitTest"})
        self.path = os.path.realpath(os.path.abspath(os.path.join(os.path.split(
            inspect.getfile(inspect.currentframe()))[0],os.path.normpath("../lang/"))))
        self._ = translation = gettext.translation(domain='unittest',
                                                   localedir=self.path,
                                                   fallback=True,
                                                   languages=[self.configuration_lisa['lang']]).ugettext

    def test(self, jsonInput):
        return {"plugin": "UnitTest",
                "method": "test",
                "body": self._('This is a test')
        }
